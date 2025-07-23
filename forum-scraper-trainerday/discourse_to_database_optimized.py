#!/usr/bin/env python3
"""
Optimized Discourse Forum Scraper v3
- Only fetches full posts when topic metadata indicates changes
- Uses last_post_id and posts_count for efficient change detection
- Dramatically reduces API calls and processing time
"""

import os
import json
import requests
import time
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OptimizedDiscourseToDatabase:
    def __init__(self, base_url, api_key=None, api_username=None, db_config=None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.getenv("DISCOURSE_API_KEY")
        self.api_username = api_username or os.getenv("DISCOURSE_API_USERNAME") or "system"
        
        if not self.api_key:
            raise ValueError("Discourse API key required. Set DISCOURSE_API_KEY environment variable or pass api_key parameter.")
        
        # Database configuration
        self.db_config = db_config
        self.db_connection = None
        
        # API headers
        self.auth_headers = {
            'Api-Key': self.api_key,
            'Api-Username': self.api_username,
            'Content-Type': 'application/json',
            'User-Agent': 'TrainerDay Forum Scraper v3.0 (Optimized)'
        }
        
        self.public_headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'TrainerDay Forum Scraper v3.0 (Optimized)'
        }
        
        # Rate limiting and stats
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 1 second between requests
        self.stats = {
            'topics_processed': 0,
            'topics_stored': 0,
            'topics_updated': 0,
            'topics_skipped': 0,  # NEW: tracks efficiently skipped topics
            'posts_total': 0,
            'errors': 0,
            'failed_topics': [],
            'api_calls_saved': 0  # NEW: tracks efficiency gains
        }

    def connect_db(self):
        """Connect to PostgreSQL database"""
        try:
            self.db_connection = psycopg2.connect(**self.db_config)
            print("✓ Connected to database")
            self.setup_optimized_tables()
        except Exception as e:
            raise Exception(f"Failed to connect to database: {e}")
    
    def setup_optimized_tables(self):
        """Create optimized table structure with metadata for quick comparison"""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS forum_topics_raw (
            topic_id INTEGER PRIMARY KEY,
            raw_content JSONB NOT NULL,
            scraped_at TIMESTAMP,
            last_updated TIMESTAMP DEFAULT NOW(),
            title TEXT,
            posts_count INTEGER,
            created_at_original TIMESTAMP,
            -- NEW OPTIMIZATION FIELDS
            last_post_id INTEGER,
            last_posted_at TIMESTAMP,
            highest_post_number INTEGER
        );
        
        CREATE INDEX IF NOT EXISTS idx_forum_topics_raw_updated ON forum_topics_raw(last_updated);
        CREATE INDEX IF NOT EXISTS idx_forum_topics_raw_last_post ON forum_topics_raw(last_post_id);
        """
        
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute(schema_sql)
                self.db_connection.commit()
                print("✓ Optimized raw topics table ready")
        except Exception as e:
            self.db_connection.rollback()
            raise Exception(f"Failed to create optimized raw topics table: {e}")

    def get_existing_topic_metadata(self):
        """Get metadata for all existing topics for quick comparison"""
        if not self.db_connection:
            return {}
        
        try:
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT topic_id, posts_count, last_post_id, last_posted_at, highest_post_number
                    FROM forum_topics_raw
                """)
                
                existing_metadata = {}
                for row in cursor.fetchall():
                    existing_metadata[row['topic_id']] = {
                        'posts_count': row['posts_count'],
                        'last_post_id': row['last_post_id'],
                        'last_posted_at': row['last_posted_at'],
                        'highest_post_number': row['highest_post_number']
                    }
                
                print(f"✓ Retrieved metadata for {len(existing_metadata)} existing topics")
                return existing_metadata
        except Exception as e:
            print(f"Warning: Could not retrieve existing metadata: {e}")
            return {}

    def topic_needs_update(self, topic_from_list, existing_metadata):
        """
        Efficiently check if topic needs updating using lightweight metadata comparison
        Uses data from topic list API - NO expensive full topic fetch required!
        Returns True if topic needs full fetch, False if can be skipped
        """
        topic_id = topic_from_list['id']
        
        # If topic doesn't exist, definitely need to fetch
        if topic_id not in existing_metadata:
            return True
        
        existing = existing_metadata[topic_id]
        
        # Compare posts count (available in topic list)
        current_posts_count = topic_from_list.get('posts_count', 0)
        if existing['posts_count'] != current_posts_count:
            return True
        
        # Compare last posted time (available in topic list)
        current_last_posted_at = topic_from_list.get('last_posted_at')
        if current_last_posted_at:
            try:
                current_time = datetime.fromisoformat(current_last_posted_at.replace('Z', '+00:00'))
                # Convert to naive datetime for comparison (remove timezone info)
                current_time_naive = current_time.replace(tzinfo=None)
                if existing['last_posted_at'] and current_time_naive != existing['last_posted_at']:
                    return True
            except:
                return True  # If we can't parse, err on side of fetching
        
        # Compare highest post number if available
        current_highest_post = topic_from_list.get('highest_post_number', 0)
        if existing['highest_post_number'] and existing['highest_post_number'] != current_highest_post:
            return True
        
        # Topic appears unchanged - can skip expensive API call!
        return False

    def make_request(self, endpoint, params=None, use_auth=False):
        """Make a rate-limited request to the Discourse API"""
        # Rate limiting
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)
        
        url = f"{self.base_url}{endpoint}"
        if not url.endswith('.json'):
            url += '.json'
        
        headers = self.auth_headers if use_auth else self.public_headers
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                print(f"  ⚠️  Rate limited, waiting 60 seconds...")
                time.sleep(60)
                return self.make_request(endpoint, params, use_auth)
            else:
                print(f"  ❌ API error {response.status_code}: {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"  ❌ Request failed: {e}")
            return None

    def get_latest_topics(self, page=0):
        """Get latest topics list (lightweight metadata only)"""
        response_data = self.make_request(f"/latest.json", {'page': page}, use_auth=True)
        
        if not response_data:
            return [], False
        
        topic_list = response_data.get('topic_list', {})
        topics = topic_list.get('topics', [])
        has_more = len(topics) > 0 and page < 50  # Reasonable limit
        
        return topics, has_more

    def get_topic_with_posts(self, topic_id):
        """Fetch complete topic with all posts (expensive operation)"""
        response_data = self.make_request(f"/t/{topic_id}.json", use_auth=True)
        return response_data

    def store_topic_to_database(self, raw_content: dict) -> bool:
        """Store optimized raw topic content in database"""
        if not self.db_connection:
            raise ValueError("Database connection required.")
        
        try:
            # Handle both API response formats - try nested first, then root level
            topic_data = raw_content.get('topic', raw_content)  # Fallback to root if no 'topic' key
            topic_id = topic_data.get('id')
            if not topic_id:
                print(f"  ❌ FAILURE: Topic ID not found in content")
                return False
            
            # Extract metadata for future optimization
            title = topic_data.get('title', '')
            posts_count = topic_data.get('posts_count', 0)
            created_at_str = topic_data.get('created_at', '')
            last_posted_at_str = topic_data.get('last_posted_at', '')
            highest_post_number = topic_data.get('highest_post_number', 0)
            scraped_at = datetime.now()
            
            # Find highest post ID for future comparison - handle both formats
            posts = raw_content.get('posts', [])
            if not posts and 'post_stream' in raw_content:
                posts = raw_content.get('post_stream', {}).get('posts', [])
            last_post_id = max([post.get('id', 0) for post in posts]) if posts else 0
            
            # Generate a simple checksum for database compatibility (still required by existing schema)
            checksum = f"{topic_id}_{posts_count}_{last_post_id}_{last_posted_at_str}"
            import hashlib
            checksum = hashlib.md5(checksum.encode()).hexdigest()
            
            # Parse timestamps
            created_at = None
            last_posted_at = None
            try:
                if created_at_str:
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                if last_posted_at_str:
                    last_posted_at = datetime.fromisoformat(last_posted_at_str.replace('Z', '+00:00'))
            except ValueError:
                pass
            
            with self.db_connection.cursor() as cursor:
                # Check if exists
                cursor.execute("SELECT topic_id FROM forum_topics_raw WHERE topic_id = %s", (topic_id,))
                exists = cursor.fetchone() is not None
                
                # Store or update with optimized metadata
                cursor.execute("""
                    INSERT INTO forum_topics_raw (
                        topic_id, raw_content, checksum, scraped_at, 
                        title, posts_count, created_at_original,
                        last_post_id, last_posted_at, highest_post_number
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (topic_id) DO UPDATE SET
                        raw_content = EXCLUDED.raw_content,
                        checksum = EXCLUDED.checksum,
                        last_updated = NOW(),
                        title = EXCLUDED.title,
                        posts_count = EXCLUDED.posts_count,
                        scraped_at = EXCLUDED.scraped_at,
                        created_at_original = EXCLUDED.created_at_original,
                        last_post_id = EXCLUDED.last_post_id,
                        last_posted_at = EXCLUDED.last_posted_at,
                        highest_post_number = EXCLUDED.highest_post_number
                """, (
                    topic_id, json.dumps(raw_content), checksum, scraped_at,
                    title, posts_count, created_at,
                    last_post_id, last_posted_at, highest_post_number
                ))
                
                self.db_connection.commit()
                
                if exists:
                    print(f"  ✅ Updated topic {topic_id}: {title[:50]}...")
                    self.stats['topics_updated'] += 1
                else:
                    print(f"  ✅ Stored new topic {topic_id}: {title[:50]}...")
                    self.stats['topics_stored'] += 1
                
                self.stats['posts_total'] += len(posts)
                return True
                
        except Exception as e:
            self.db_connection.rollback()
            print(f"  ❌ FAILURE: Database error for topic {topic_id}: {e}")
            self.stats['errors'] += 1
            return False

    def scrape_topics_optimized(self, max_pages=None, incremental=True, skip_existing=False):
        """Main scraping method with optimization"""
        print(f"🚀 Starting OPTIMIZED forum scraping...")
        print(f"   Mode: {'incremental' if incremental else 'full'}")
        print(f"   Max pages: {max_pages or 'unlimited'}")
        print(f"   Skip existing: {skip_existing}")
        
        start_time = time.time()
        
        # Get existing metadata for quick comparison OR skipping
        existing_metadata = self.get_existing_topic_metadata() if (incremental or skip_existing) else {}
        
        page = 0
        while max_pages is None or page < max_pages:
            print(f"\n📄 Processing page {page}...")
            topics, has_more = self.get_latest_topics(page=page)
            
            if not topics:
                print("📄 No more topics found")
                break
            
            for topic in topics:
                topic_id = topic['id']
                topic_title = topic.get('title', '')
                
                print(f"\n[{self.stats['topics_processed'] + 1}] Topic {topic_id}: {topic_title[:50]}...")
                
                # 🚀 SKIP EXISTING: Skip topics we already have entirely
                if skip_existing and topic_id in existing_metadata:
                    print(f"  ⏭️  SKIPPED: Already exists in database (skip mode)")
                    self.stats['topics_skipped'] += 1
                    self.stats['api_calls_saved'] += 1
                    self.stats['topics_processed'] += 1
                    continue
                
                # 🚀 OPTIMIZATION: Check if topic needs update BEFORE expensive API call
                # Always optimize - check both incremental and full modes
                if existing_metadata and not self.topic_needs_update(topic, existing_metadata):
                    print(f"  ⚡ SKIPPED: No changes detected (efficient)")
                    self.stats['topics_skipped'] += 1
                    self.stats['api_calls_saved'] += 1
                    self.stats['topics_processed'] += 1
                    continue
                
                # Only now make the expensive API call to get all posts
                print(f"  📥 Fetching full topic data...")
                topic_data = self.get_topic_with_posts(topic_id)
                
                if topic_data:
                    stored = self.store_topic_to_database(topic_data)
                    self.stats['topics_processed'] += 1
                    time.sleep(0.5)  # Rate limiting
                else:
                    print(f"  ❌ FAILURE: Could not fetch topic {topic_id}")
                    self.stats['errors'] += 1
                    self.stats['failed_topics'].append({
                        'topic_id': topic_id,
                        'title': topic_title,
                        'error': 'Could not fetch topic data'
                    })
            
            if not has_more:
                print("📄 Reached end of topics")
                break
            
            page += 1
        
        # Print optimization results
        elapsed_time = time.time() - start_time
        print(f"\n🎯 OPTIMIZATION RESULTS")
        print(f"=====================================")
        print(f"Topics processed: {self.stats['topics_processed']}")
        print(f"Topics skipped (no changes): {self.stats['topics_skipped']}")
        print(f"API calls saved: {self.stats['api_calls_saved']}")
        print(f"Topics stored: {self.stats['topics_stored']}")
        print(f"Topics updated: {self.stats['topics_updated']}")
        print(f"Total posts: {self.stats['posts_total']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"Time elapsed: {elapsed_time:.1f} seconds")
        
        if self.stats['api_calls_saved'] > 0:
            efficiency_percent = (self.stats['api_calls_saved'] / self.stats['topics_processed']) * 100
            print(f"⚡ EFFICIENCY GAIN: {efficiency_percent:.1f}% fewer API calls!")

        # Close database connection
        if self.db_connection:
            self.db_connection.close()
            print("Database connection closed")


def main():
    parser = argparse.ArgumentParser(description="Optimized Discourse Forum Scraper v3")
    parser.add_argument("--mode", choices=['full', 'incremental'], default='incremental',
                       help="Scraping mode (default: incremental)")
    parser.add_argument("--max-pages", type=int,
                       help="Maximum pages to process (default: all)")
    parser.add_argument("--base-url", default="https://forums.trainerday.com",
                       help="Discourse forum base URL (default: https://forums.trainerday.com)")
    parser.add_argument("--api-key", help="Discourse API key (or set DISCOURSE_API_KEY env var)")
    parser.add_argument("--api-username", help="Discourse API username (or set DISCOURSE_API_USERNAME env var)")
    parser.add_argument("--skip-existing", action="store_true", 
                       help="Skip topics that already exist in database (to reach older topics)")
    
    args = parser.parse_args()
    
    # Database configuration from environment
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('DB_SSLMODE', 'require')
    }
    
    # Validate database configuration
    if not all([db_config['host'], db_config['database'], db_config['user'], db_config['password']]):
        print("❌ Database configuration incomplete. Please set environment variables:")
        print("   Required: DB_HOST, DB_DATABASE, DB_USERNAME, DB_PASSWORD")
        sys.exit(1)
    
    try:
        scraper = OptimizedDiscourseToDatabase(
            base_url=args.base_url,
            api_key=args.api_key,
            api_username=args.api_username,
            db_config=db_config
        )
        
        scraper.connect_db()
        
        incremental = args.mode == 'incremental'
        scraper.scrape_topics_optimized(
            max_pages=args.max_pages,
            incremental=incremental,
            skip_existing=args.skip_existing
        )
        
        print("✅ Scraping completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()