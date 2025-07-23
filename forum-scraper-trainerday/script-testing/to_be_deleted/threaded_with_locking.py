#!/usr/bin/env python3
"""
Threaded Forum Processor with Database Row Locking
Uses SELECT FOR UPDATE SKIP LOCKED for thread-safe topic selection
"""

import os
import sys
import time
import threading
import queue
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

def get_and_lock_topic(worker_id):
    """Get and lock the next unprocessed topic - thread-safe"""
    connection = None
    try:
        connection = psycopg2.connect(**get_db_config())
        connection.autocommit = False  # Important for locking
        
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            # Use a subquery to avoid the JOIN issue with FOR UPDATE
            cursor.execute("""
                WITH unprocessed AS (
                    SELECT r.topic_id, r.title, r.posts_count, r.created_at_original
                    FROM forum_topics_raw r
                    WHERE NOT EXISTS (SELECT 1 FROM forum_topics t WHERE t.topic_id = r.topic_id)
                    AND (jsonb_array_length(COALESCE(r.raw_content -> 'posts', '[]'::jsonb)) > 0
                         OR jsonb_array_length(COALESCE(r.raw_content -> 'post_stream' -> 'posts', '[]'::jsonb)) > 0)
                    ORDER BY r.topic_id DESC
                )
                SELECT * FROM unprocessed
                LIMIT 1
                FOR UPDATE SKIP LOCKED
            """)
            
            result = cursor.fetchone()
            
            if result:
                print(f"Worker {worker_id}: Locked topic {result['topic_id']}")
                return {
                    'topic': result,
                    'connection': connection,  # Keep connection open to maintain lock
                    'locked': True
                }
            else:
                connection.close()
                return None
                
    except Exception as e:
        if connection:
            connection.close()
        print(f"Worker {worker_id}: Error getting topic: {e}")
        return None

def process_locked_topic(worker_id, locked_data):
    """Process a topic that's already locked"""
    if not locked_data or not locked_data.get('locked'):
        return {'success': False, 'error': 'No locked topic data'}
    
    topic = locked_data['topic']
    lock_connection = locked_data['connection']
    
    topic_id = topic['topic_id']
    title = topic['title']
    
    try:
        start_time = time.time()
        
        # Create analyzer with separate connection for processing
        analyzer = ForumTopicAnalyzerV2(db_config=get_db_config())
        analyzer.connect_to_database()
        analyzer.delete_existing_analysis(topic_id)
        
        # Use fast model
        analysis = analyzer.analyze_stored_topic(topic_id, model="gpt-4o-mini")
        
        if analysis:
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
        
        analyzer.close_database_connection()
        
        # Release lock by closing connection
        lock_connection.close()
        
        return result
        
    except Exception as e:
        duration = time.time() - start_time if 'start_time' in locals() else 0
        
        # Clean up connections
        if 'analyzer' in locals():
            try:
                analyzer.close_database_connection()
            except:
                pass
        
        try:
            lock_connection.close()
        except:
            pass
            
        return {
            'success': False,
            'topic_id': topic_id,
            'title': title,
            'error': str(e),
            'duration': duration,
            'worker_id': worker_id
        }

def worker_thread(worker_id, results_queue, stop_event):
    """Worker thread that processes topics with locking"""
    print(f"Worker {worker_id}: Started")
    
    processed = 0
    while not stop_event.is_set():
        try:
            # Get and lock next topic
            locked_data = get_and_lock_topic(worker_id)
            
            if not locked_data:
                print(f"Worker {worker_id}: No more topics available")
                break
            
            # Process the locked topic
            result = process_locked_topic(worker_id, locked_data)
            
            # Send result back
            results_queue.put(result)
            processed += 1
            
            # Brief pause between topics
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Worker {worker_id}: Error: {e}")
            break
    
    print(f"Worker {worker_id}: Finished ({processed} topics)")

def main():
    print("🚀 Threaded Forum Processor with Database Locking")
    print("=" * 55)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key required")
        return
    
    # Configuration
    NUM_THREADS = 4  # Number of worker threads
    TARGET_TOTAL = 50  # Total topics to process in this run
    
    print(f"Threads: {NUM_THREADS}")
    print(f"Target: {TARGET_TOTAL} topics")
    
    # Check current progress
    try:
        connection = psycopg2.connect(**get_db_config())
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM forum_topics")
            already_processed = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM forum_topics_raw WHERE NOT EXISTS (SELECT 1 FROM forum_topics t WHERE t.topic_id = forum_topics_raw.topic_id)")
            remaining = cursor.fetchone()[0]
            
        connection.close()
        
        print(f"Already processed: {already_processed}")
        print(f"Remaining unprocessed: {remaining}")
        
        if remaining == 0:
            print("✅ No more topics to process!")
            return
        
        actual_target = min(TARGET_TOTAL, remaining)
        print(f"Will process up to: {actual_target} topics")
        print("=" * 55)
        
    except Exception as e:
        print(f"Error checking progress: {e}")
        return
    
    # Create results queue and stop event
    results_queue = queue.Queue()
    stop_event = threading.Event()
    
    # Start worker threads
    threads = []
    start_time = time.time()
    
    for i in range(NUM_THREADS):
        thread = threading.Thread(
            target=worker_thread,
            args=(i + 1, results_queue, stop_event)
        )
        thread.start()
        threads.append(thread)
        
        # Stagger thread starts slightly
        time.sleep(0.2)
    
    # Collect results
    successful = 0
    failed = 0
    total_qa_pairs = 0
    categories = {}
    durations = []
    
    processed = 0
    
    print("📊 Processing Results:")
    print("-" * 40)
    
    while processed < actual_target:
        try:
            # Get result with timeout
            result = results_queue.get(timeout=90)  # 90 second timeout
            processed += 1
            
            if result['success']:
                successful += 1
                total_qa_pairs += result['qa_count']
                category = result['category']
                categories[category] = categories.get(category, 0) + 1
                durations.append(result['duration'])
                
                print(f"✅ W{result['worker_id']} Topic {result['topic_id']}: {result['qa_count']} Q&A, {category}, {result['duration']:.1f}s")
            else:
                failed += 1
                error = result.get('error', 'Unknown error')[:30]
                print(f"❌ W{result['worker_id']} Topic {result['topic_id']}: {error}... ({result['duration']:.1f}s)")
            
            # Progress updates
            if processed % 5 == 0:
                elapsed = time.time() - start_time
                print(f"\n📊 Progress: {processed}/{actual_target} ({processed/actual_target*100:.1f}%)")
                print(f"   Success: {successful}, Failed: {failed}")
                if successful > 0:
                    avg_time = sum(durations) / len(durations)
                    rate = successful / elapsed
                    print(f"   Avg time: {avg_time:.1f}s, Rate: {rate:.2f}/sec")
                print()
                
        except queue.Empty:
            # Check if any threads are still alive
            alive_threads = [t for t in threads if t.is_alive()]
            if not alive_threads:
                print("All threads finished")
                break
            else:
                print(f"Timeout waiting for results ({len(alive_threads)} threads still alive)")
                continue
    
    # Signal threads to stop and wait for them
    stop_event.set()
    for thread in threads:
        thread.join(timeout=5)
    
    # Final summary
    total_time = time.time() - start_time
    
    print(f"\n🎯 THREADED PROCESSING COMPLETE")
    print("=" * 40)
    print(f"Duration: {total_time/60:.1f} minutes")
    print(f"Threads: {NUM_THREADS}")
    print(f"Processed: {processed}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(successful/processed)*100:.1f}%" if processed > 0 else "0%")
    print(f"Q&A pairs: {total_qa_pairs}")
    
    if successful > 0 and durations:
        avg_time = sum(durations) / len(durations)
        rate = successful / total_time
        single_thread_time = avg_time * successful
        speedup = single_thread_time / total_time
        
        print(f"Avg time per topic: {avg_time:.1f}s")
        print(f"Parallel rate: {rate:.2f} topics/sec")
        print(f"Theoretical speedup: {speedup:.1f}x")
    
    if categories:
        print(f"\nCategories processed:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count}")
    
    # Final progress check
    try:
        connection = psycopg2.connect(**get_db_config())
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM forum_topics")
            total_now = cursor.fetchone()[0]
        connection.close()
        
        print(f"\n🏁 Total topics analyzed: {total_now}")
        remaining_to_200 = 200 - total_now
        if remaining_to_200 <= 0:
            print("🎉 200 TOPIC GOAL ACHIEVED!")
        else:
            print(f"📋 {remaining_to_200} more topics needed to reach 200 goal")
            
    except Exception as e:
        print(f"Error checking final progress: {e}")

if __name__ == "__main__":
    main()