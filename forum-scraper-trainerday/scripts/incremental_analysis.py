#!/usr/bin/env python3
"""
Incremental Forum Analysis v2 with Raw Content Storage
Efficiently handles new and updated topics using raw content storage.
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from openai import OpenAI
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded environment variables from: {env_path}")
    else:
        print("No .env file found, using system environment variables")
except ImportError:
    print("python-dotenv not installed, using system environment variables")

# Import the main analyzer class
sys.path.append(str(Path(__file__).parent))
from analyze_forum_topics_v2 import ForumTopicAnalyzerV2

class IncrementalForumAnalyzerV2(ForumTopicAnalyzerV2):
    def __init__(self, openai_api_key: str = None, db_config: dict = None):
        super().__init__(openai_api_key, db_config)
    
    def get_existing_raw_topics(self) -> Dict[int, dict]:
        """Get existing topics and their checksums from raw content table."""
        if not self.db_connection:
            self.connect_to_database()
        
        existing_topics = {}
        try:
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT topic_id, checksum, title, posts_count, 
                           last_updated, created_at_original
                    FROM forum_topics_raw
                    ORDER BY topic_id
                """)
                
                for row in cursor.fetchall():
                    existing_topics[row['topic_id']] = {
                        'checksum': row['checksum'],
                        'title': row['title'],
                        'posts_count': row['posts_count'],
                        'last_updated': row['last_updated'],
                        'created_at_original': row['created_at_original']
                    }
                
                print(f"Found {len(existing_topics)} existing topics in raw content table")
                return existing_topics
                
        except Exception as e:
            print(f"Error getting existing raw topics: {e}")
            return {}
    
    def identify_topics_to_process(self, forum_data_dir: str, force_reanalyze: bool = False) -> Dict[str, List]:
        """Identify which topics need processing based on raw content changes."""
        forum_path = Path(forum_data_dir)
        if not forum_path.exists():
            raise FileNotFoundError(f"Forum data directory not found: {forum_data_dir}")
        
        # Get all topic files (limit to first 10 for testing)
        topic_files = list(forum_path.glob("topic_*.json"))
        topic_files.sort(key=lambda x: int(x.stem.split('_')[1]))
        topic_files = topic_files[:10]  # Limit file scanning for testing
        
        # Get existing database state
        existing_topics = self.get_existing_raw_topics()
        
        new_topics = []
        updated_topics = []
        unchanged_topics = []
        
        print(f"\nAnalyzing {len(topic_files)} topic files for changes...")
        
        for topic_file in topic_files:
            try:
                # Load topic data
                with open(topic_file, 'r', encoding='utf-8') as f:
                    topic_data = json.load(f)
                
                topic_id = topic_data.get('topic', {}).get('id')
                if not topic_id:
                    continue
                
                # Generate current checksum
                current_checksum = self.get_topic_checksum(topic_data)
                title = topic_data.get('topic', {}).get('title', '')
                posts_count = topic_data.get('topic', {}).get('posts_count', 0)
                
                # Check if topic exists in database
                if topic_id not in existing_topics:
                    # New topic
                    new_topics.append({
                        'file': topic_file,
                        'topic_id': topic_id,
                        'title': title,
                        'posts_count': posts_count,
                        'reason': 'new_topic'
                    })
                else:
                    # Existing topic - check for changes
                    stored_checksum = existing_topics[topic_id]['checksum']
                    stored_posts_count = existing_topics[topic_id]['posts_count'] or 0
                    
                    if force_reanalyze or current_checksum != stored_checksum:
                        # Topic has changed or force reanalyze
                        reason = 'force_reanalyze' if force_reanalyze else 'content_changed'
                        updated_topics.append({
                            'file': topic_file,
                            'topic_id': topic_id,
                            'title': title,
                            'reason': reason,
                            'old_posts': stored_posts_count,
                            'new_posts': posts_count,
                            'last_updated': existing_topics[topic_id]['last_updated']
                        })
                    else:
                        # Topic unchanged
                        unchanged_topics.append({
                            'topic_id': topic_id,
                            'title': title,
                            'posts_count': posts_count,
                            'last_updated': existing_topics[topic_id]['last_updated']
                        })
                
            except Exception as e:
                print(f"Error processing {topic_file.name}: {e}")
                continue
        
        return {
            'new_topics': new_topics,
            'updated_topics': updated_topics,
            'unchanged_topics': unchanged_topics
        }
    
    def process_incremental_updates(self, forum_data_dir: str, max_topics: int = None, 
                                  force_reanalyze: bool = False) -> Dict:
        """Process incremental updates with raw content storage."""
        
        if not self.db_config:
            raise ValueError("Database configuration required for incremental updates")
        
        # Setup database connections
        self.connect_to_database()
        self.create_database_schema()
        
        # Identify topics to process
        topics_to_process = self.identify_topics_to_process(forum_data_dir, force_reanalyze)
        
        # Combine new and updated topics for processing
        process_list = topics_to_process['new_topics'] + topics_to_process['updated_topics']
        
        if max_topics:
            process_list = process_list[:max_topics]
        
        print(f"\n📊 INCREMENTAL PROCESSING SUMMARY")
        print(f"New topics: {len(topics_to_process['new_topics'])}")
        print(f"Updated topics: {len(topics_to_process['updated_topics'])}")
        print(f"Unchanged topics: {len(topics_to_process['unchanged_topics'])}")
        print(f"Will process: {len(process_list)} topics")
        
        if not process_list:
            print("✓ No topics require processing!")
            self.close_database_connection()
            return {
                "analysis_metadata": {
                    "analyzed_at": datetime.now().isoformat(),
                    "new_topics": len(topics_to_process['new_topics']),
                    "updated_topics": len(topics_to_process['updated_topics']),
                    "unchanged_topics": len(topics_to_process['unchanged_topics']),
                    "total_processed": 0,
                    "successful_analyses": 0,
                    "failed_analyses": 0,
                    "topics_stored_raw": 0
                }
            }
        
        # Process topics
        results = {
            "analysis_metadata": {
                "analyzed_at": datetime.now().isoformat(),
                "new_topics": len(topics_to_process['new_topics']),
                "updated_topics": len(topics_to_process['updated_topics']),
                "unchanged_topics": len(topics_to_process['unchanged_topics']),
                "total_processed": 0,
                "successful_analyses": 0,
                "failed_analyses": 0,
                "topics_stored_raw": 0,
                "topics_by_category": {},
                "failed_topics": []  # Track specific failures
            }
        }
        
        print(f"\n🔄 PROCESSING TOPICS")
        print("-" * 25)
        
        for i, topic_info in enumerate(process_list):
            topic_file = topic_info['file']
            topic_id = topic_info['topic_id']
            reason = topic_info['reason']
            
            print(f"\n[{i+1}/{len(process_list)}] Topic {topic_id}: {topic_info['title'][:50]}...")
            print(f"  Reason: {reason}")
            
            if 'old_posts' in topic_info:
                print(f"  Posts: {topic_info['old_posts']} → {topic_info['new_posts']}")
            
            try:
                # Load topic data
                with open(topic_file, 'r', encoding='utf-8') as f:
                    raw_content = json.load(f)
                
                # Step 1: Store raw content (will detect changes automatically)
                content_changed = self.store_raw_topic(raw_content)
                results["analysis_metadata"]["topics_stored_raw"] += 1
                
                # Step 2: If this is an update, delete existing analysis first
                if reason in ['content_changed', 'force_reanalyze']:
                    self.delete_existing_analysis(topic_id)
                
                # Step 3: Analyze from stored raw content
                analysis = self.analyze_stored_topic(topic_id)
                
                if analysis:
                    # Step 4: Save analysis results
                    try:
                        self.save_analysis_to_database(analysis)
                        results["analysis_metadata"]["successful_analyses"] += 1
                        
                        # Track categories
                        category = analysis.get("topic_summary", {}).get("analysis_category", "Unknown")
                        results["analysis_metadata"]["topics_by_category"][category] = \
                            results["analysis_metadata"]["topics_by_category"].get(category, 0) + 1
                        
                        print(f"  ✅ SUCCESS: Analysis complete")
                    except Exception as save_error:
                        print(f"  ❌ FAILURE: Database save error: {save_error}")
                        results["analysis_metadata"]["failed_analyses"] += 1
                        results["analysis_metadata"]["failed_topics"].append({
                            "topic_id": topic_id,
                            "title": topic_info['title'],
                            "failure_reason": f"Database save error: {save_error}",
                            "failure_stage": "save_analysis"
                        })
                else:
                    results["analysis_metadata"]["failed_analyses"] += 1
                    results["analysis_metadata"]["failed_topics"].append({
                        "topic_id": topic_id,
                        "title": topic_info['title'],
                        "failure_reason": "OpenAI analysis returned None - check logs above for details",
                        "failure_stage": "openai_analysis"
                    })
                    print(f"  ❌ FAILURE: Analysis failed")
                
                results["analysis_metadata"]["total_processed"] += 1
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"  Error processing: {e}")
                results["analysis_metadata"]["failed_analyses"] += 1
                continue
        
        # Close database connection
        self.close_database_connection()
        
        print(f"\n🏁 INCREMENTAL UPDATE COMPLETE!")
        print("=" * 50)
        print(f"📊 SUMMARY:")
        print(f"  Topics processed: {results['analysis_metadata']['total_processed']}")
        print(f"  Raw content stored: {results['analysis_metadata']['topics_stored_raw']}")
        print(f"  ✅ Successful analyses: {results['analysis_metadata']['successful_analyses']}")
        print(f"  ❌ Failed analyses: {results['analysis_metadata']['failed_analyses']}")
        print(f"  📁 Categories: {results['analysis_metadata']['topics_by_category']}")
        
        # Show detailed failure information
        if results['analysis_metadata']['failed_analyses'] > 0:
            print(f"\n🚨 FAILURE DETAILS:")
            print("=" * 30)
            for failure in results['analysis_metadata']['failed_topics']:
                print(f"❌ Topic {failure['topic_id']}: {failure['title']}")
                print(f"   Stage: {failure['failure_stage']}")
                print(f"   Reason: {failure['failure_reason']}")
                print()
        else:
            print(f"\n🎉 ALL TOPICS PROCESSED SUCCESSFULLY - NO FAILURES!")
        
        print("=" * 50)
        
        return results

def main():
    """Main function for incremental analysis v2."""
    
    # Configuration
    FORUM_DATA_DIR = "../forum_data"
    MAX_TOPICS = 5  # Limit for testing - set to None for production
    FORCE_REANALYZE = False  # Set to True to reanalyze all topics
    
    print("TrainerDay Incremental Forum Analysis v2 - With Raw Content Storage")
    print("=" * 75)
    
    # Check OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("Please set your OpenAI API key in the .env file")
        return
    
    # Database configuration
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
        ssl_cert_path = Path(__file__).parent.parent / ssl_cert_filename
        if ssl_cert_path.exists():
            db_config['sslrootcert'] = str(ssl_cert_path)
    
    if not all([db_config['host'], db_config['database'], db_config['user'], db_config['password']]):
        print("Database configuration incomplete. Please check .env file.")
        return
    
    try:
        # Initialize analyzer
        analyzer = IncrementalForumAnalyzerV2(db_config=db_config)
        
        # Run incremental analysis
        results = analyzer.process_incremental_updates(
            forum_data_dir=FORUM_DATA_DIR,
            max_topics=MAX_TOPICS,
            force_reanalyze=FORCE_REANALYZE
        )
        
        print("\n🎯 Ready for next incremental run!")
        print("Raw content is stored in database for future re-analysis!")
        
    except Exception as e:
        print(f"Error: {e}")
        return

if __name__ == "__main__":
    main()