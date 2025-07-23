#!/usr/bin/env python3
"""
Incremental Forum Topic Processor
Only processes unanalyzed topics, with option to force refresh and process latest topics first
"""

import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.analyze_forum_topics import ForumTopicAnalyzerV2
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables
load_dotenv()

def get_topics_to_process(limit=100, latest_first=False, force_refresh=False):
    """Get topics that need processing"""
    
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('DB_SSLMODE', 'require')
    }
    
    if os.getenv('DB_SSLROOTCERT'):
        ssl_cert_filename = os.getenv('DB_SSLROOTCERT')
        ssl_cert_path = Path(__file__).parent.parent / ssl_cert_filename
        if ssl_cert_path.exists():
            db_config['sslrootcert'] = str(ssl_cert_path)
    
    try:
        connection = psycopg2.connect(**db_config)
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            
            if force_refresh:
                # Get all topics (will reprocess everything)
                order_clause = "ORDER BY r.topic_id DESC" if latest_first else "ORDER BY r.topic_id ASC"
                cursor.execute(f"""
                    SELECT r.topic_id, r.title, r.posts_count, r.created_at_original
                    FROM forum_topics_raw r
                    WHERE (jsonb_array_length(COALESCE(r.raw_content -> 'posts', '[]'::jsonb)) > 0
                           OR jsonb_array_length(COALESCE(r.raw_content -> 'post_stream' -> 'posts', '[]'::jsonb)) > 0)
                    {order_clause}
                    LIMIT %s
                """, (limit,))
            else:
                # Get only unprocessed topics
                order_clause = "ORDER BY r.topic_id DESC" if latest_first else "ORDER BY r.topic_id ASC"
                cursor.execute(f"""
                    SELECT r.topic_id, r.title, r.posts_count, r.created_at_original
                    FROM forum_topics_raw r
                    LEFT JOIN forum_topics t ON r.topic_id = t.topic_id
                    WHERE t.topic_id IS NULL
                    AND (jsonb_array_length(COALESCE(r.raw_content -> 'posts', '[]'::jsonb)) > 0
                         OR jsonb_array_length(COALESCE(r.raw_content -> 'post_stream' -> 'posts', '[]'::jsonb)) > 0)
                    {order_clause}
                    LIMIT %s
                """, (limit,))
            
            topics = cursor.fetchall()
            
            # Get current stats
            cursor.execute("SELECT COUNT(*) as analyzed FROM forum_topics")
            analyzed = cursor.fetchone()['analyzed']
            
            cursor.execute("""
                SELECT COUNT(*) as total FROM forum_topics_raw 
                WHERE (jsonb_array_length(COALESCE(raw_content -> 'posts', '[]'::jsonb)) > 0
                       OR jsonb_array_length(COALESCE(raw_content -> 'post_stream' -> 'posts', '[]'::jsonb)) > 0)
            """)
            total = cursor.fetchone()['total']
            
        connection.close()
        return topics, analyzed, total
        
    except Exception as e:
        print(f"Error getting topics: {e}")
        return [], 0, 0

def analyze_single_topic(topic_id, title):
    """Analyze a single topic and return results"""
    
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('DB_SSLMODE', 'require')
    }
    
    if os.getenv('DB_SSLROOTCERT'):
        ssl_cert_filename = os.getenv('DB_SSLROOTCERT')
        ssl_cert_path = Path(__file__).parent.parent / ssl_cert_filename
        if ssl_cert_path.exists():
            db_config['sslrootcert'] = str(ssl_cert_path)
    
    try:
        start_time = time.time()
        
        # Initialize analyzer
        analyzer = ForumTopicAnalyzerV2(db_config=db_config)
        analyzer.connect_to_database()
        
        # Clear existing analysis (important for force refresh)
        analyzer.delete_existing_analysis(topic_id)
        
        # Analyze topic
        analysis = analyzer.analyze_stored_topic(topic_id)
        
        if analysis:
            # Save to database
            analyzer.save_analysis_to_database(analysis)
            
            # Extract results
            qa_count = len(analysis.get('qa_pairs', []))
            category = analysis.get('topic_summary', {}).get('analysis_category', 'Unknown')
            
            duration = time.time() - start_time
            analyzer.close_database_connection()
            
            return {
                'success': True,
                'qa_count': qa_count,
                'category': category,
                'duration': duration,
                'error': None
            }
        else:
            duration = time.time() - start_time
            analyzer.close_database_connection()
            return {
                'success': False,
                'qa_count': 0,
                'category': 'Analysis Failed',
                'duration': duration,
                'error': 'Analysis returned None'
            }
            
    except Exception as e:
        duration = time.time() - start_time
        if 'analyzer' in locals():
            try:
                analyzer.close_database_connection()
            except:
                pass
        return {
            'success': False,
            'qa_count': 0,
            'category': 'Error',
            'duration': duration,
            'error': str(e)
        }

def main():
    parser = argparse.ArgumentParser(description='Incremental Forum Topic Processor')
    parser.add_argument('--limit', type=int, default=100, help='Maximum number of topics to process (default: 100)')
    parser.add_argument('--latest-first', action='store_true', help='Process latest topics first (descending order)')
    parser.add_argument('--force-refresh', action='store_true', help='Reprocess all topics, including already analyzed ones')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be processed without actually processing')
    
    args = parser.parse_args()
    
    print("🔄 Incremental Forum Topic Processor")
    print("=" * 45)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\nConfiguration:")
    print(f"  Limit: {args.limit} topics")
    print(f"  Order: {'Latest first (DESC)' if args.latest_first else 'Oldest first (ASC)'}")
    print(f"  Mode: {'Force refresh (reprocess all)' if args.force_refresh else 'Incremental (unprocessed only)'}")
    print(f"  Dry run: {'Yes (no processing)' if args.dry_run else 'No (will process)'}")
    
    if not os.getenv('OPENAI_API_KEY') and not args.dry_run:
        print("\n❌ OpenAI API key required for processing")
        return
    
    # Get topics to process
    print(f"\n📊 Getting topics to process...")
    topics, analyzed, total = get_topics_to_process(
        limit=args.limit,
        latest_first=args.latest_first,
        force_refresh=args.force_refresh
    )
    
    if not topics:
        print("✅ No topics found to process!")
        return
    
    # Show current status
    remaining = total - analyzed
    progress_pct = (analyzed / total) * 100 if total > 0 else 0
    
    print(f"\n📈 Current Status:")
    print(f"  Total topics with posts: {total}")
    print(f"  Already analyzed: {analyzed}")
    print(f"  Remaining unprocessed: {remaining}")
    print(f"  Progress: {progress_pct:.1f}%")
    
    print(f"\n🎯 Topics to process: {len(topics)}")
    if args.force_refresh:
        print(f"  Mode: Will reprocess these topics (force refresh)")
    else:
        print(f"  Mode: Will process only unanalyzed topics")
    
    # Show first few topics
    print(f"\nNext topics to process:")
    for i, topic in enumerate(topics[:5]):
        created_date = topic['created_at_original'].strftime('%Y-%m-%d') if topic['created_at_original'] else 'Unknown'
        print(f"  {i+1}. Topic {topic['topic_id']} ({created_date}): {topic['title'][:60]}... ({topic['posts_count']} posts)")
    
    if len(topics) > 5:
        print(f"  ... and {len(topics) - 5} more topics")
    
    if args.dry_run:
        print(f"\n🔍 DRY RUN COMPLETE - No topics were processed")
        return
    
    # Process topics
    print(f"\n🚀 Starting processing...")
    
    successful = 0
    failed = 0
    total_qa_pairs = 0
    categories = {}
    start_time = time.time()
    
    for i, topic in enumerate(topics):
        topic_id = topic['topic_id']
        title = topic['title']
        posts_count = topic['posts_count']
        created_date = topic['created_at_original'].strftime('%Y-%m-%d') if topic['created_at_original'] else 'Unknown'
        
        print(f"\n[{i+1}/{len(topics)}] Topic {topic_id} ({created_date})")
        print(f"  Title: {title[:70]}...")
        print(f"  Posts: {posts_count}")
        
        # Analyze topic
        result = analyze_single_topic(topic_id, title)
        
        if result['success']:
            successful += 1
            total_qa_pairs += result['qa_count']
            category = result['category']
            categories[category] = categories.get(category, 0) + 1
            
            print(f"  ✅ Success: {result['qa_count']} Q&A pairs, {category} ({result['duration']:.1f}s)")
        else:
            failed += 1
            print(f"  ❌ Failed: {result['error'][:50]}... ({result['duration']:.1f}s)")
        
        # Progress update every 5 topics
        if (i + 1) % 5 == 0:
            elapsed = time.time() - start_time
            rate = successful / elapsed if elapsed > 0 else 0
            avg_time = elapsed / (i + 1)
            
            print(f"\n📊 Progress Update:")
            print(f"  Processed: {i + 1}/{len(topics)}")
            print(f"  Successful: {successful}")
            print(f"  Failed: {failed}")
            print(f"  Rate: {rate:.2f} successful/second")
            print(f"  Average time per topic: {avg_time:.1f}s")
            
            # ETA calculation
            remaining_topics = len(topics) - (i + 1)
            if rate > 0:
                eta_seconds = remaining_topics / rate
                eta_minutes = eta_seconds / 60
                print(f"  ETA: {eta_minutes:.1f} minutes")
    
    # Final summary
    total_duration = time.time() - start_time
    final_analyzed = analyzed + successful
    final_progress = (final_analyzed / total) * 100 if total > 0 else 0
    
    print(f"\n🎯 PROCESSING COMPLETE")
    print("=" * 40)
    print(f"Duration: {total_duration/60:.1f} minutes")
    print(f"Topics processed: {len(topics)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(successful/len(topics))*100:.1f}%")
    print(f"Total Q&A pairs extracted: {total_qa_pairs}")
    
    if successful > 0:
        rate = successful / total_duration
        avg_time = total_duration / successful
        print(f"Processing rate: {rate:.2f} topics/second")
        print(f"Average time per successful topic: {avg_time:.1f}s")
    
    print(f"\n📈 Updated Progress:")
    print(f"Total analyzed: {final_analyzed}/{total} ({final_progress:.1f}%)")
    
    remaining_after = total - final_analyzed
    if remaining_after > 0:
        if successful > 0:
            eta_hours = (remaining_after * avg_time) / 3600
            print(f"Remaining topics: {remaining_after}")
            print(f"Estimated time to complete all: {eta_hours:.1f} hours")
    else:
        print("🎉 ALL TOPICS COMPLETED!")
    
    if categories:
        print(f"\n📂 Categories processed:")
        for category, count in sorted(categories.items()):
            print(f"  {category}: {count} topics")

if __name__ == "__main__":
    main()