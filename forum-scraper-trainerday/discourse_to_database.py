#!/usr/bin/env python3
"""
Enhanced Discourse Forum Scraper v2
Pulls forum data from Discourse API and stores directly to raw database table.
Replaces file-based scraping with direct database storage.
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
import hashlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DiscourseToDatabase:
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
            'User-Agent': 'TrainerDay Forum Scraper v2.0'
        }
        
        self.public_headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'TrainerDay Forum Scraper v2.0'
        }
        
        # Rate limiting: Discourse typically allows 60 requests per minute
        self.rate_limit_delay = 1  # 1 second between requests
        
        # Statistics tracking
        self.stats = {
            'topics_processed': 0,
            'topics_stored': 0,
            'topics_updated': 0,
            'topics_unchanged': 0,
            'posts_total': 0,
            'api_calls': 0,
            'errors': 0,
            'failed_topics': []
        }
    
    def connect_to_database(self):
        """Connect to PostgreSQL database."""
        if not self.db_config:
            raise ValueError("Database configuration required for PostgreSQL storage.")
        
        try:
            print("Connecting to PostgreSQL database...")
            print(f"Host: {self.db_config['host']}")
            print(f"Database: {self.db_config['database']}")
            self.db_connection = psycopg2.connect(**self.db_config)
            print("✓ Connected to PostgreSQL database")
        except Exception as e:
            raise Exception(f"Failed to connect to database: {e}")
    
    def create_raw_topics_table(self):
        """Create the forum_topics_raw table if it doesn't exist."""
        if not self.db_connection:
            raise ValueError("Database connection required.")
        
        schema_sql = """
        CREATE TABLE IF NOT EXISTS forum_topics_raw (
            topic_id INTEGER PRIMARY KEY,
            raw_content JSONB NOT NULL,
            checksum VARCHAR(32) NOT NULL,
            scraped_at TIMESTAMP,
            last_updated TIMESTAMP DEFAULT NOW(),
            title TEXT,
            posts_count INTEGER,
            created_at_original TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_forum_topics_raw_checksum ON forum_topics_raw(checksum);
        CREATE INDEX IF NOT EXISTS idx_forum_topics_raw_updated ON forum_topics_raw(last_updated);
        """
        
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute(schema_sql)
                self.db_connection.commit()
                print("✓ Raw topics table ready")
        except Exception as e:
            self.db_connection.rollback()
            raise Exception(f"Failed to create raw topics table: {e}")
    
    def get_topic_checksum(self, raw_content: dict) -> str:
        """Generate checksum for raw topic content to detect changes."""
        checksum_data = {
            'topic_id': raw_content.get('topic', {}).get('id'),
            'title': raw_content.get('topic', {}).get('title', ''),
            'posts_count': raw_content.get('topic', {}).get('posts_count', 0),
            'last_posted_at': raw_content.get('topic', {}).get('last_posted_at', ''),
            'posts_preview': []
        }
        
        # Include first few characters of each post for change detection
        for post in raw_content.get('posts', []):
            post_preview = {
                'id': post.get('id'),
                'username': post.get('username'),
                'created_at': post.get('created_at'),
                'content_preview': post.get('cooked', '')[:100]
            }
            checksum_data['posts_preview'].append(post_preview)
        
        content_str = json.dumps(checksum_data, sort_keys=True)
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def store_topic_to_database(self, raw_content: dict) -> bool:
        """Store raw topic content in database. Returns True if stored/updated, False if unchanged."""
        if not self.db_connection:
            raise ValueError("Database connection required.")
        
        try:
            topic_data = raw_content.get('topic', {})
            topic_id = topic_data.get('id')
            if not topic_id:
                print(f"  ❌ FAILURE: Topic ID not found in content")
                return False
            
            # Generate checksum
            checksum = self.get_topic_checksum(raw_content)
            
            # Extract key metadata
            title = topic_data.get('title', '')
            posts_count = topic_data.get('posts_count', 0)
            created_at_str = topic_data.get('created_at', '')
            scraped_at = datetime.now()
            
            # Parse timestamp
            created_at = None
            try:
                if created_at_str:
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            except ValueError:
                pass
            
            with self.db_connection.cursor() as cursor:
                # Check if topic exists and if checksum has changed
                cursor.execute("""
                    SELECT checksum FROM forum_topics_raw WHERE topic_id = %s
                """, (topic_id,))
                
                result = cursor.fetchone()
                if result and result[0] == checksum:
                    print(f"  → Topic {topic_id} unchanged (checksum match)")
                    self.stats['topics_unchanged'] += 1
                    return False
                
                # Store or update raw content
                cursor.execute("""
                    INSERT INTO forum_topics_raw (
                        topic_id, raw_content, checksum, scraped_at, 
                        title, posts_count, created_at_original
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (topic_id) DO UPDATE SET
                        raw_content = EXCLUDED.raw_content,
                        checksum = EXCLUDED.checksum,
                        last_updated = NOW(),
                        title = EXCLUDED.title,
                        posts_count = EXCLUDED.posts_count,
                        scraped_at = EXCLUDED.scraped_at,
                        created_at_original = EXCLUDED.created_at_original
                """, (
                    topic_id, 
                    json.dumps(raw_content),
                    checksum,
                    scraped_at,
                    title,
                    posts_count,
                    created_at
                ))
                
                self.db_connection.commit()
                
                if result:
                    print(f"  ✅ Updated topic {topic_id}: {title[:50]}...")
                    self.stats['topics_updated'] += 1
                else:
                    print(f"  ✅ Stored new topic {topic_id}: {title[:50]}...")
                    self.stats['topics_stored'] += 1
                
                self.stats['posts_total'] += len(raw_content.get('posts', []))
                return True
                
        except Exception as e:
            self.db_connection.rollback()
            print(f"  ❌ FAILURE: Database error for topic {topic_id}: {e}")
            self.stats['errors'] += 1
            self.stats['failed_topics'].append({
                'topic_id': topic_id,
                'title': title,
                'error': str(e)
            })
            return False
    
    def make_request(self, endpoint, params=None, use_auth=False):
        """Make a rate-limited request to the Discourse API with enhanced error handling"""
        url = f"{self.base_url}{endpoint}"
        
        # Add .json extension if not present
        if not url.endswith('.json'):
            url += '.json'
        
        headers = self.auth_headers if use_auth else self.public_headers
        
        try:
            time.sleep(self.rate_limit_delay)
            self.stats['api_calls'] += 1
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                print(f"  ⏱️  Rate limited, waiting 60 seconds...")
                time.sleep(60)
                return self.make_request(endpoint, params, use_auth)  # Retry
            elif response.status_code == 403 and not use_auth:
                print(f"  🔐 Public access failed, trying with authentication...")
                return self.make_request(endpoint, params, use_auth=True)
            elif response.status_code == 404:
                print(f"  ⚠️  Topic not found (404): {endpoint}")
                return None
            else:
                print(f"  ❌ API Error {response.status_code}: {endpoint}")
                self.stats['errors'] += 1
                return None
                
        except Exception as e:
            print(f"  ❌ Request failed for {endpoint}: {e}")
            self.stats['errors'] += 1
            return None
    
    def get_latest_topics(self, page=0, per_page=30):
        """Get latest topics with pagination"""
        params = {
            'page': page,
            'per_page': per_page
        }
        
        data = self.make_request('/latest', params)
        
        if data and 'topic_list' in data:
            return data['topic_list']['topics'], data['topic_list'].get('more_topics_url') is not None
        
        return [], False
    
    def get_topic_with_posts(self, topic_id):
        """Get complete topic data with all posts"""
        data = self.make_request(f'/t/{topic_id}')
        
        if data and 'post_stream' in data:
            # Create complete topic data structure
            topic_data = {
                'topic': {
                    'id': data.get('id'),
                    'title': data.get('title'),
                    'slug': data.get('slug'),
                    'posts_count': data.get('posts_count'),
                    'reply_count': data.get('reply_count'),
                    'highest_post_number': data.get('highest_post_number'),
                    'image_url': data.get('image_url'),
                    'created_at': data.get('created_at'),
                    'last_posted_at': data.get('last_posted_at'),
                    'bumped': data.get('bumped'),
                    'bumped_at': data.get('bumped_at'),
                    'archetype': data.get('archetype'),
                    'unseen': data.get('unseen'),
                    'pinned': data.get('pinned'),
                    'unpinned': data.get('unpinned'),
                    'visible': data.get('visible'),
                    'closed': data.get('closed'),
                    'archived': data.get('archived'),
                    'bookmarked': data.get('bookmarked'),
                    'liked': data.get('liked'),
                    'tags_descriptions': data.get('tags_descriptions'),
                    'views': data.get('views'),
                    'like_count': data.get('like_count'),
                    'has_summary': data.get('has_summary'),
                    'last_poster_username': data.get('last_poster_username'),
                    'category_id': data.get('category_id'),
                    'pinned_globally': data.get('pinned_globally'),
                    'featured_link': data.get('featured_link'),
                    'can_vote': data.get('can_vote'),
                    'posters': data.get('posters', [])
                },
                'posts': data['post_stream'].get('posts', []),
                'scraped_at': datetime.now().isoformat()
            }
            
            return topic_data
        
        return None
    
    def get_existing_topic_checksums(self):
        """Get existing topic checksums for incremental updates."""
        if not self.db_connection:
            return {}
        
        checksums = {}
        try:
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT topic_id, checksum, last_updated 
                    FROM forum_topics_raw
                """)
                
                for row in cursor.fetchall():
                    checksums[row['topic_id']] = {
                        'checksum': row['checksum'],
                        'last_updated': row['last_updated']
                    }
                
                print(f"Found {len(checksums)} existing topics in database")
        except Exception as e:
            print(f"Error getting existing checksums: {e}")
        
        return checksums
    
    def scrape_topics_to_database(self, start_page=0, max_pages=None, incremental=True):
        """Scrape topics from Discourse API and store directly to database"""
        print(f"🚀 Starting forum scraping to database...")
        print(f"Mode: {'Incremental' if incremental else 'Full'}")
        print(f"Starting from page: {start_page}")
        if max_pages:
            print(f"Max pages: {max_pages}")
        
        # Connect to database and setup
        self.connect_to_database()
        self.create_raw_topics_table()
        
        # Get existing checksums for incremental mode
        existing_checksums = {}
        if incremental:
            existing_checksums = self.get_existing_topic_checksums()
        
        page = start_page
        start_time = time.time()
        
        print(f"\n🔄 PROCESSING TOPICS")
        print("-" * 30)
        
        while True:
            if max_pages and page >= max_pages:
                break
            
            print(f"\n📄 Processing page {page}...")
            topics, has_more = self.get_latest_topics(page=page)
            
            if not topics:
                print("📄 No more topics found")
                break
            
            for topic in topics:
                topic_id = topic['id']
                topic_title = topic.get('title', '')
                
                print(f"\n[{self.stats['topics_processed'] + 1}] Topic {topic_id}: {topic_title[:50]}...")
                
                # Skip if incremental and topic exists with same checksum
                if incremental and topic_id in existing_checksums:
                    # We'll still fetch to check for updates
                    pass
                
                # Get complete topic with posts
                topic_data = self.get_topic_with_posts(topic_id)
                
                if topic_data:
                    # Store to database
                    stored = self.store_topic_to_database(topic_data)
                    self.stats['topics_processed'] += 1
                    
                    # Rate limiting between topics
                    time.sleep(0.5)
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
        
        # Close database connection
        if self.db_connection:
            self.db_connection.close()
            print("Database connection closed")
        
        elapsed_time = time.time() - start_time
        
        # Print final statistics
        print(f"\n🏁 SCRAPING COMPLETE!")
        print("=" * 50)
        print(f"📊 STATISTICS:")
        print(f"  Topics processed: {self.stats['topics_processed']}")
        print(f"  ✅ New topics stored: {self.stats['topics_stored']}")
        print(f"  🔄 Topics updated: {self.stats['topics_updated']}")
        print(f"  ⏭️  Topics unchanged: {self.stats['topics_unchanged']}")
        print(f"  💬 Total posts: {self.stats['posts_total']}")
        print(f"  📡 API calls made: {self.stats['api_calls']}")
        print(f"  ❌ Errors: {self.stats['errors']}")
        print(f"  ⏱️  Total time: {elapsed_time/60:.1f} minutes")
        
        # Show failed topics if any
        if self.stats['failed_topics']:
            print(f"\n🚨 FAILED TOPICS:")
            print("=" * 30)
            for failure in self.stats['failed_topics'][:5]:  # Show first 5
                print(f"❌ Topic {failure['topic_id']}: {failure['title'][:40]}...")
                print(f"   Error: {failure['error']}")
            
            if len(self.stats['failed_topics']) > 5:
                print(f"   ... and {len(self.stats['failed_topics']) - 5} more")
        else:
            print(f"\n🎉 ALL TOPICS PROCESSED SUCCESSFULLY!")
        
        print("=" * 50)
        
        return self.stats

def main():
    parser = argparse.ArgumentParser(description="Enhanced Discourse Forum Scraper v2 - Direct to Database")
    parser.add_argument("--base-url", default="https://forums.trainerday.com", 
                       help="Discourse forum base URL (default: https://forums.trainerday.com)")
    parser.add_argument("--mode", choices=["incremental", "full"], default="incremental",
                       help="Scraping mode: incremental (check for changes) or full (ignore existing)")
    parser.add_argument("--start-page", type=int, default=0, 
                       help="Starting page number (default: 0)")
    parser.add_argument("--max-pages", type=int, 
                       help="Maximum pages to process (default: all)")
    parser.add_argument("--api-key", help="Discourse API key (or set DISCOURSE_API_KEY env var)")
    parser.add_argument("--api-username", help="Discourse API username (or set DISCOURSE_API_USERNAME env var)")
    
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
    
    # Add SSL certificate if specified
    if os.getenv('DB_SSLROOTCERT'):
        ssl_cert_filename = os.getenv('DB_SSLROOTCERT')
        ssl_cert_path = Path(__file__).parent / ssl_cert_filename
        if ssl_cert_path.exists():
            db_config['sslrootcert'] = str(ssl_cert_path)
    
    # Validate database configuration
    if not all([db_config['host'], db_config['database'], db_config['user'], db_config['password']]):
        print("❌ Database configuration incomplete. Please set environment variables:")
        print("   Required: DB_HOST, DB_DATABASE, DB_USERNAME, DB_PASSWORD")
        sys.exit(1)
    
    try:
        # Create scraper
        scraper = DiscourseToDatabase(
            base_url=args.base_url,
            api_key=args.api_key,
            api_username=args.api_username,
            db_config=db_config
        )
        
        # Run scraping
        stats = scraper.scrape_topics_to_database(
            start_page=args.start_page,
            max_pages=args.max_pages,
            incremental=(args.mode == "incremental")
        )
        
        print(f"\n✅ Scraping completed successfully!")
        print(f"🎯 Forum data is now stored in PostgreSQL database!")
        print(f"📈 Ready for analysis with analyze_forum_topics_v2.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()