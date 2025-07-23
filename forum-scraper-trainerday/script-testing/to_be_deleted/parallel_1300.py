#!/usr/bin/env python3
"""
Process Remaining 1300+ Topics with 4 Parallel Workers
Uses a simple coordinator pattern - one thread gets topics, others process them
"""

import os
import sys
import time
import threading
import queue
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

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
    return {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('DB_SSLMODE', 'require'),
        'sslrootcert': str(Path(__file__).parent.parent / os.getenv('DB_SSLROOTCERT')) if os.getenv('DB_SSLROOTCERT') else None
    }

def get_unprocessed_topics_batch(batch_size=100):
    """Get a batch of unprocessed topics"""
    try:
        connection = psycopg2.connect(**get_db_config())
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT r.topic_id, r.title, r.posts_count, r.created_at_original
                FROM forum_topics_raw r
                WHERE r.topic_id NOT IN (SELECT topic_id FROM forum_topics)
                AND (jsonb_array_length(COALESCE(r.raw_content -> 'posts', '[]'::jsonb)) > 0
                     OR jsonb_array_length(COALESCE(r.raw_content -> 'post_stream' -> 'posts', '[]'::jsonb)) > 0)
                ORDER BY r.topic_id DESC
                LIMIT %s
            """, (batch_size,))
            
            results = cursor.fetchall()
            connection.close()
            return [dict(topic) for topic in results]
    except Exception as e:
        print(f"Error getting topics batch: {e}")
        return []

def process_single_topic(topic_data, worker_id):
    """Process a single topic - this is the core processing function"""
    topic_id = topic_data['topic_id']
    title = topic_data['title']
    
    try:
        start_time = time.time()
        
        # Create analyzer
        analyzer = ForumTopicAnalyzerV2(db_config=get_db_config())
        analyzer.connect_to_database()
        
        # Check if already processed (race condition check)
        with analyzer.db_connection.cursor() as cursor:
            cursor.execute("SELECT topic_id FROM forum_topics WHERE topic_id = %s", (topic_id,))
            if cursor.fetchone():
                analyzer.close_database_connection()
                return {
                    'success': False,
                    'topic_id': topic_id,
                    'title': title,
                    'error': 'Already processed (race condition)',
                    'duration': time.time() - start_time,
                    'worker_id': worker_id
                }
        
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
        return result
        
    except Exception as e:
        duration = time.time() - start_time if 'start_time' in locals() else 0
        
        # Clean up
        if 'analyzer' in locals():
            try:
                analyzer.close_database_connection()
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

def coordinator_thread(topic_queue, stop_event):
    """Coordinator thread that feeds topics to workers"""
    batch_count = 0
    total_queued = 0
    
    while not stop_event.is_set():
        # Get current queue size
        current_queue_size = topic_queue.qsize()
        
        # If queue is getting low, add more topics
        if current_queue_size < 20:  # Keep at least 20 topics in queue
            print(f"📋 Coordinator: Queue low ({current_queue_size}), fetching more topics...")
            
            batch = get_unprocessed_topics_batch(50)  # Get 50 topics at a time
            
            if not batch:
                print("📋 Coordinator: No more topics available!")
                break
            
            for topic in batch:
                topic_queue.put(topic)
                total_queued += 1
            
            batch_count += 1
            print(f"📋 Coordinator: Added batch {batch_count} ({len(batch)} topics, {total_queued} total queued)")
        
        time.sleep(5)  # Check every 5 seconds
    
    print(f"📋 Coordinator: Finished ({total_queued} topics queued total)")

def worker_function(worker_id, topic_queue, results_queue, stop_event):
    """Worker function that processes topics from queue"""
    print(f"Worker {worker_id}: Started")
    processed = 0
    
    while not stop_event.is_set():
        try:
            # Get topic with timeout
            topic = topic_queue.get(timeout=10)
            
            # Process topic
            result = process_single_topic(topic, worker_id)
            results_queue.put(result)
            
            processed += 1
            topic_queue.task_done()
            
        except queue.Empty:
            # No topics available - check if we should continue
            if topic_queue.empty() and stop_event.is_set():
                break
            continue
        except Exception as e:
            print(f"Worker {worker_id}: Error: {e}")
            break
    
    print(f"Worker {worker_id}: Finished ({processed} topics)")

def main():
    print("🚀 Parallel Processor for Remaining 1300+ Topics")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key required")
        return
    
    # Configuration
    NUM_WORKERS = 4
    
    print(f"Workers: {NUM_WORKERS}")
    print("Target: Process ALL remaining unprocessed topics")
    
    # Check current status
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
        
        print("=" * 50)
        
    except Exception as e:
        print(f"Error checking status: {e}")
        return
    
    # Create queues and events
    topic_queue = queue.Queue(maxsize=100)  # Limit queue size
    results_queue = queue.Queue()
    stop_event = threading.Event()
    
    # Start coordinator thread
    coordinator = threading.Thread(
        target=coordinator_thread,
        args=(topic_queue, stop_event)
    )
    coordinator.start()
    
    # Wait for initial topics to be loaded
    print("⏳ Waiting for initial topics to load...")
    while topic_queue.empty():
        time.sleep(1)
    
    print(f"✅ Initial topics loaded ({topic_queue.qsize()} in queue)")
    
    # Start worker threads
    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        # Submit worker tasks
        worker_futures = []
        for i in range(NUM_WORKERS):
            future = executor.submit(worker_function, i+1, topic_queue, results_queue, stop_event)
            worker_futures.append(future)
        
        # Collect results
        successful = 0
        failed = 0
        total_qa_pairs = 0
        categories = {}
        durations = []
        start_time = time.time()
        
        print("\n📊 Processing Results:")
        print("-" * 40)
        
        # Process results until no more topics
        last_activity = time.time()
        no_activity_timeout = 300  # 5 minutes of no results = stop
        
        while True:
            try:
                result = results_queue.get(timeout=30)
                last_activity = time.time()
                
                total_processed = successful + failed + 1
                
                if result['success']:
                    successful += 1
                    total_qa_pairs += result['qa_count']
                    category = result['category']
                    categories[category] = categories.get(category, 0) + 1
                    durations.append(result['duration'])
                    
                    print(f"✅ W{result['worker_id']} Topic {result['topic_id']}: {result['qa_count']} Q&A, {category}, {result['duration']:.1f}s")
                else:
                    failed += 1
                    error = result.get('error', 'Unknown error')[:40]
                    print(f"❌ W{result['worker_id']} Topic {result['topic_id']}: {error}... ({result['duration']:.1f}s)")
                
                # Progress updates every 10 topics
                if total_processed % 10 == 0:
                    elapsed = time.time() - start_time
                    print(f"\n📊 Progress Update - {total_processed} topics processed")
                    print(f"   Successful: {successful} ({(successful/total_processed)*100:.1f}%)")
                    print(f"   Failed: {failed}")
                    print(f"   Elapsed: {elapsed/60:.1f}m")
                    print(f"   Queue size: {topic_queue.qsize()}")
                    
                    if successful > 0 and durations:
                        avg_time = sum(durations) / len(durations)
                        rate = successful / elapsed
                        print(f"   Avg time: {avg_time:.1f}s")
                        print(f"   Rate: {rate:.2f} topics/sec")
                        
                        # ETA calculation
                        if remaining > total_processed:
                            eta_minutes = (remaining - total_processed) / rate / 60
                            print(f"   ETA: {eta_minutes:.0f}m")
                    print()
                    
            except queue.Empty:
                # Check if we should stop
                if time.time() - last_activity > no_activity_timeout:
                    print("⏰ No activity for 5 minutes - stopping")
                    break
                
                # Check if coordinator is done and queue is empty
                if not coordinator.is_alive() and topic_queue.empty():
                    print("📋 Coordinator finished and queue empty - stopping")
                    # Wait a bit more for final results
                    time.sleep(10)
                    break
                
                continue
        
        # Stop everything
        print("\n🛑 Stopping all workers...")
        stop_event.set()
        
        # Wait for coordinator
        coordinator.join(timeout=10)
        
        # Wait for workers with timeout
        for future in worker_futures:
            try:
                future.result(timeout=10)
            except:
                pass
    
    # Final summary
    total_time = time.time() - start_time
    total_processed = successful + failed
    
    print(f"\n🎯 MASSIVE PARALLEL PROCESSING COMPLETE")
    print("=" * 45)
    print(f"Duration: {total_time/60:.1f} minutes ({total_time/3600:.1f} hours)")
    print(f"Workers: {NUM_WORKERS}")
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
        print(f"Parallel speedup: ~{NUM_WORKERS}x")
    
    if categories:
        print(f"\n📂 Categories Processed:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / successful) * 100 if successful > 0 else 0
            print(f"   {cat}: {count:,} ({percentage:.1f}%)")
    
    # Final database check
    try:
        connection = psycopg2.connect(**get_db_config())
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM forum_topics")
            final_processed = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM forum_topics_raw")
            total_raw = cursor.fetchone()[0]
            
            remaining_final = total_raw - final_processed
            
        connection.close()
        
        print(f"\n🏁 FINAL STATUS:")
        print(f"Total topics in database: {final_processed:,}/{total_raw:,} ({final_processed/total_raw*100:.1f}%)")
        print(f"Remaining unprocessed: {remaining_final:,}")
        
        if remaining_final == 0:
            print("🎉 ALL TOPICS PROCESSED!")
        else:
            print(f"📋 Run again to process remaining {remaining_final:,} topics")
            
    except Exception as e:
        print(f"Error checking final status: {e}")

if __name__ == "__main__":
    main()