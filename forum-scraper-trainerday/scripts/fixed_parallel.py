#!/usr/bin/env python3
"""
Fixed Parallel Processor with Proper Database Locking
Uses PostgreSQL advisory locks to ensure no race conditions
"""

import os
import sys
import time
import threading
import queue
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.analyze_forum_topics import ForumTopicAnalyzerV2
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables
load_dotenv()

def get_db_config():
    """Get database configuration"""
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
    
    return db_config

def get_and_lock_next_topic(worker_id):
    """
    Get next unprocessed topic with PostgreSQL advisory lock
    This ensures only one worker can process each topic
    """
    connection = None
    try:
        connection = psycopg2.connect(**get_db_config())
        connection.autocommit = True  # Important for advisory locks
        
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            # Use advisory lock with topic selection in one atomic operation
            cursor.execute("""
                WITH candidate AS (
                    SELECT r.topic_id, r.title, r.posts_count, r.created_at_original
                    FROM forum_topics_raw r
                    WHERE r.topic_id NOT IN (SELECT topic_id FROM forum_topics)
                    AND (jsonb_array_length(COALESCE(r.raw_content -> 'posts', '[]'::jsonb)) > 0
                         OR jsonb_array_length(COALESCE(r.raw_content -> 'post_stream' -> 'posts', '[]'::jsonb)) > 0)
                    ORDER BY r.topic_id DESC
                    LIMIT 20
                ),
                locked_topic AS (
                    SELECT c.*, pg_try_advisory_lock(c.topic_id) as got_lock
                    FROM candidate c
                    ORDER BY c.topic_id DESC
                )
                SELECT topic_id, title, posts_count, created_at_original
                FROM locked_topic 
                WHERE got_lock = true
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            
            if result:
                topic_id = result['topic_id']
                print(f"Worker {worker_id}: 🔒 Locked topic {topic_id}")
                
                return {
                    'topic': dict(result),
                    'connection': connection,
                    'locked_topic_id': topic_id
                }
            else:
                connection.close()
                return None
                
    except Exception as e:
        if connection:
            connection.close()
        print(f"Worker {worker_id}: ❌ Error getting topic: {e}")
        return None

def release_topic_lock(connection, topic_id):
    """Release the advisory lock for a topic"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_advisory_unlock(%s)", (topic_id,))
        connection.close()
    except Exception as e:
        print(f"⚠️ Error releasing lock for topic {topic_id}: {e}")

def process_locked_topic(worker_id, locked_data):
    """Process a topic that has an advisory lock"""
    if not locked_data:
        return {'success': False, 'error': 'No locked topic data', 'worker_id': worker_id}
    
    topic = locked_data['topic']
    lock_connection = locked_data['connection']
    topic_id = locked_data['locked_topic_id']
    
    title = topic['title']
    
    try:
        start_time = time.time()
        
        # Double-check topic isn't already processed (final safety check)
        check_connection = psycopg2.connect(**get_db_config())
        with check_connection.cursor() as cursor:
            cursor.execute("SELECT topic_id FROM forum_topics WHERE topic_id = %s", (topic_id,))
            if cursor.fetchone():
                check_connection.close()
                release_topic_lock(lock_connection, topic_id)
                return {
                    'success': False,
                    'topic_id': topic_id,
                    'title': title,
                    'error': 'Already processed (final check)',
                    'duration': time.time() - start_time,
                    'worker_id': worker_id
                }
        check_connection.close()
        
        # Create analyzer for processing
        analyzer = ForumTopicAnalyzerV2(db_config=get_db_config())
        analyzer.connect_to_database()
        
        # Clean any existing partial data
        analyzer.delete_existing_analysis(topic_id)
        
        # Perform analysis with fast model
        analysis = analyzer.analyze_stored_topic(topic_id, model="gpt-4o-mini")
        
        if analysis:
            # Save all analysis data atomically
            analyzer.save_analysis_to_database(analysis)
            
            qa_count = len(analysis.get('qa_pairs', []))
            category = analysis.get('topic_summary', {}).get('analysis_category', 'Unknown')
            duration = time.time() - start_time
            
            result = {
                'success': True,
                'topic_id': topic_id,
                'title': title,
                'qa_count': qa_count,
                'category': category,
                'duration': duration,
                'worker_id': worker_id
            }
        else:
            duration = time.time() - start_time
            result = {
                'success': False,
                'topic_id': topic_id,
                'title': title,
                'error': 'Analysis returned None',
                'duration': duration,
                'worker_id': worker_id
            }
        
        # Cleanup
        analyzer.close_database_connection()
        release_topic_lock(lock_connection, topic_id)
        
        return result
        
    except Exception as e:
        duration = time.time() - start_time if 'start_time' in locals() else 0
        
        # Cleanup on error
        if 'analyzer' in locals():
            try:
                analyzer.close_database_connection()
            except:
                pass
        
        if 'check_connection' in locals():
            try:
                check_connection.close()
            except:
                pass
        
        release_topic_lock(lock_connection, topic_id)
        
        return {
            'success': False,
            'topic_id': topic_id,
            'title': title,
            'error': str(e),
            'duration': duration,
            'worker_id': worker_id
        }

def worker_task(worker_id):
    """Single worker task - gets and processes one topic"""
    locked_data = get_and_lock_next_topic(worker_id)
    if not locked_data:
        return None  # No more topics available
    
    return process_locked_topic(worker_id, locked_data)

def cleanup_incomplete_topics():
    """Clean up any incomplete topics before starting"""
    try:
        connection = psycopg2.connect(**get_db_config())
        with connection.cursor() as cursor:
            # Find incomplete topics
            cursor.execute("""
                SELECT ft.topic_id, ft.title
                FROM forum_topics ft
                LEFT JOIN forum_qa_pairs qa ON ft.topic_id = qa.topic_id
                WHERE qa.topic_id IS NULL
            """)
            
            incomplete = cursor.fetchall()
            
            if incomplete:
                print(f"🧹 Cleaning up {len(incomplete)} incomplete topics...")
                
                for topic_id, title in incomplete:
                    cursor.execute("DELETE FROM forum_insights WHERE topic_id = %s", (topic_id,))
                    cursor.execute("DELETE FROM forum_voice_patterns WHERE topic_id = %s", (topic_id,))
                    cursor.execute("DELETE FROM forum_qa_pairs WHERE topic_id = %s", (topic_id,))
                    cursor.execute("DELETE FROM forum_topics WHERE topic_id = %s", (topic_id,))
                
                connection.commit()
                print(f"✅ Cleaned up {len(incomplete)} incomplete topics")
            else:
                print("✅ No incomplete topics to clean up")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

def main():
    print("🚀 Fixed Parallel Processor with Advisory Locks")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key required")
        return
    
    # Configuration
    NUM_WORKERS = 4
    BATCH_SIZE = 50  # Process in batches
    
    print(f"Workers: {NUM_WORKERS}")
    print(f"Batch size: {BATCH_SIZE}")
    print("Using PostgreSQL advisory locks for coordination")
    print("=" * 50)
    
    # Cleanup incomplete topics first
    cleanup_incomplete_topics()
    
    # Check status
    try:
        connection = psycopg2.connect(**get_db_config())
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM forum_topics_raw")
            total_raw = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM forum_topics")
            processed = cursor.fetchone()[0]
            
            remaining = total_raw - processed
        connection.close()
        
        print(f"Total topics: {total_raw:,}")
        print(f"Already processed: {processed:,}")
        print(f"Remaining: {remaining:,}")
        
        if remaining == 0:
            print("✅ All topics already processed!")
            return
        
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return
    
    # Statistics
    successful = 0
    failed = 0
    total_qa_pairs = 0
    categories = {}
    durations = []
    start_time = time.time()
    
    print(f"\n📊 Processing Results:")
    print("-" * 40)
    
    # Process topics in batches using ThreadPoolExecutor
    batch_count = 0
    
    while remaining > 0:
        batch_count += 1
        current_batch_size = min(BATCH_SIZE, remaining)
        
        print(f"\n🎯 Batch {batch_count} - Processing {current_batch_size} topics with {NUM_WORKERS} workers")
        
        # Use ThreadPoolExecutor for this batch
        with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
            # Submit worker tasks
            future_to_worker = {
                executor.submit(worker_task, worker_id): worker_id 
                for worker_id in range(1, NUM_WORKERS + 1)
            }
            
            batch_successful = 0
            batch_failed = 0
            topics_in_batch = 0
            
            # Collect results as they complete
            for future in as_completed(future_to_worker, timeout=300):  # 5 minute timeout per batch
                worker_id = future_to_worker[future]
                
                try:
                    result = future.result()
                    
                    if result is None:
                        # No more topics for this worker
                        continue
                    
                    topics_in_batch += 1
                    
                    if result['success']:
                        successful += 1
                        batch_successful += 1
                        total_qa_pairs += result['qa_count']
                        category = result['category']
                        categories[category] = categories.get(category, 0) + 1
                        durations.append(result['duration'])
                        
                        print(f"✅ W{result['worker_id']} Topic {result['topic_id']}: {result['qa_count']} Q&A, {category}, {result['duration']:.1f}s")
                    else:
                        failed += 1
                        batch_failed += 1
                        error = result.get('error', 'Unknown error')[:40]
                        print(f"❌ W{result['worker_id']} Topic {result['topic_id']}: {error}... ({result['duration']:.1f}s)")
                
                except Exception as e:
                    failed += 1
                    batch_failed += 1
                    print(f"❌ W{worker_id}: Exception: {e}")
        
        # Batch summary
        elapsed = time.time() - start_time
        total_processed = successful + failed
        
        print(f"\n📊 Batch {batch_count} Complete:")
        print(f"   Topics processed: {topics_in_batch}")
        print(f"   Successful: {batch_successful}")
        print(f"   Failed: {batch_failed}")
        print(f"   Elapsed: {elapsed/60:.1f}m")
        
        if successful > 0:
            avg_time = sum(durations) / len(durations)
            rate = successful / elapsed
            print(f"   Avg time per topic: {avg_time:.1f}s")
            print(f"   Processing rate: {rate:.2f} topics/sec")
        
        # Update remaining count
        try:
            connection = psycopg2.connect(**get_db_config())
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM forum_topics_raw")
                total_raw = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM forum_topics")
                current_processed = cursor.fetchone()[0]
                
                remaining = total_raw - current_processed
            connection.close()
        except Exception as e:
            print(f"Error updating count: {e}")
            break
        
        if remaining == 0:
            print("🎉 All topics processed!")
            break
        
        print(f"   Remaining: {remaining:,} topics")
        
        # Brief pause between batches
        if remaining > 0:
            print("   Pausing 5 seconds before next batch...")
            time.sleep(5)
    
    # Final summary
    total_time = time.time() - start_time
    
    print(f"\n🎯 FIXED PARALLEL PROCESSING COMPLETE")
    print("=" * 45)
    print(f"Duration: {total_time/60:.1f} minutes ({total_time/3600:.1f} hours)")
    print(f"Workers: {NUM_WORKERS}")
    print(f"Batches processed: {batch_count}")
    print(f"Topics processed: {total_processed:,}")
    print(f"Successful: {successful:,}")
    print(f"Failed: {failed:,}")
    print(f"Success rate: {(successful/total_processed)*100:.1f}%" if total_processed > 0 else "0%")
    print(f"Q&A pairs extracted: {total_qa_pairs:,}")
    
    if successful > 0 and durations:
        avg_time = sum(durations) / len(durations)
        rate = successful / total_time
        print(f"Average time per topic: {avg_time:.1f}s")
        print(f"Overall rate: {rate:.2f} topics/sec")
        print(f"Theoretical speedup: {NUM_WORKERS}x")
    
    if categories:
        print(f"\n📂 Categories Processed:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / successful) * 100 if successful > 0 else 0
            print(f"   {cat}: {count:,} ({percentage:.1f}%)")

if __name__ == "__main__":
    main()