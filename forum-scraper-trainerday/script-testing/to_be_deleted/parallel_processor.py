#!/usr/bin/env python3
"""
Parallel Forum Topic Processor with Row-Level Locking
Uses PostgreSQL's FOR UPDATE SKIP LOCKED to ensure no duplicate processing
"""

import os
import sys
import time
import multiprocessing
from pathlib import Path
from datetime import datetime
from typing import Optional

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

def get_and_lock_next_topic(worker_id: int) -> Optional[dict]:
    """Get next unprocessed topic with row-level lock"""
    try:
        connection = psycopg2.connect(**get_db_config())
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            # Use FOR UPDATE SKIP LOCKED to get exclusive lock on one row
            # This ensures only one worker can process each topic
            cursor.execute("""
                SELECT r.topic_id, r.title, r.posts_count, r.created_at_original
                FROM forum_topics_raw r
                WHERE r.topic_id NOT IN (SELECT topic_id FROM forum_topics)
                AND (jsonb_array_length(COALESCE(r.raw_content -> 'posts', '[]'::jsonb)) > 0
                     OR jsonb_array_length(COALESCE(r.raw_content -> 'post_stream' -> 'posts', '[]'::jsonb)) > 0)
                ORDER BY r.topic_id DESC
                LIMIT 1
                FOR UPDATE SKIP LOCKED
            """)
            
            result = cursor.fetchone()
            
            if result:
                # Keep connection open to maintain lock
                return {
                    'topic_data': result,
                    'connection': connection,
                    'worker_id': worker_id
                }
            else:
                connection.close()
                return None
                
    except Exception as e:
        print(f"Worker {worker_id}: Error getting topic: {e}")
        return None

def process_single_topic(locked_data: dict) -> dict:
    """Process a single topic that's already locked"""
    if not locked_data:
        return {'success': False, 'error': 'No topic data'}
    
    topic_data = locked_data['topic_data']
    connection = locked_data['connection']
    worker_id = locked_data['worker_id']
    
    topic_id = topic_data['topic_id']
    title = topic_data['title']
    
    try:
        start_time = time.time()
        
        # Create analyzer with separate connection for analysis
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
            
            analyzer.close_database_connection()
            
            result = {
                'success': True,
                'topic_id': topic_id,
                'title': title,
                'qa_count': qa_count,
                'category': category,
                'duration': duration,
                'worker_id': worker_id,
                'error': None
            }
        else:
            duration = time.time() - start_time
            analyzer.close_database_connection()
            result = {
                'success': False,
                'topic_id': topic_id,
                'title': title,
                'qa_count': 0,
                'category': 'Failed',
                'duration': duration,
                'worker_id': worker_id,
                'error': 'Analysis returned None'
            }
        
        # Release the lock by closing connection
        connection.close()
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
            connection.close()
        except:
            pass
            
        return {
            'success': False,
            'topic_id': topic_id,
            'title': title,
            'qa_count': 0,
            'category': 'Error',
            'duration': duration,
            'worker_id': worker_id,
            'error': str(e)
        }

def worker_process(worker_id: int, target_per_worker: int, results_queue):
    """Worker process that processes topics"""
    print(f"Worker {worker_id}: Starting (target: {target_per_worker} topics)")
    
    processed = 0
    successful = 0
    failed = 0
    
    while processed < target_per_worker:
        # Get next topic with lock
        locked_data = get_and_lock_next_topic(worker_id)
        
        if not locked_data:
            print(f"Worker {worker_id}: No more topics available")
            break
        
        # Process the locked topic
        result = process_single_topic(locked_data)
        
        # Send result back to main process
        results_queue.put(result)
        
        processed += 1
        if result['success']:
            successful += 1
        else:
            failed += 1
        
        # Brief pause between topics
        time.sleep(0.5)
    
    print(f"Worker {worker_id}: Finished - {successful} successful, {failed} failed")

def main():
    print("🚀 Parallel Forum Topic Processor with Row Locking")
    print("=" * 55)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key required")
        return
    
    # Configuration
    TOTAL_TARGET = 200  # Total topics to process
    NUM_WORKERS = 2     # Number of parallel workers (start with 2 for testing)
    TARGET_PER_WORKER = TOTAL_TARGET // NUM_WORKERS  # Topics per worker
    
    print(f"Target: {TOTAL_TARGET} topics")
    print(f"Workers: {NUM_WORKERS}")
    print(f"Per worker: {TARGET_PER_WORKER} topics")
    print("=" * 55)
    
    # Check current progress
    try:
        connection = psycopg2.connect(**get_db_config())
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM forum_topics")
            already_processed = cursor.fetchone()[0]
        connection.close()
        
        print(f"Already processed: {already_processed} topics")
        remaining = TOTAL_TARGET - already_processed
        
        if remaining <= 0:
            print("✅ Target already reached!")
            return
        
        # Adjust targets based on what's already done
        actual_target = min(remaining, TOTAL_TARGET - already_processed)
        actual_per_worker = max(1, actual_target // NUM_WORKERS)
        
        print(f"Remaining to process: {actual_target} topics")
        print(f"Adjusted per worker: {actual_per_worker} topics")
        print()
        
    except Exception as e:
        print(f"Error checking progress: {e}")
        return
    
    # Create multiprocessing queue for results
    manager = multiprocessing.Manager()
    results_queue = manager.Queue()
    
    # Start worker processes
    processes = []
    start_time = time.time()
    
    for worker_id in range(NUM_WORKERS):
        p = multiprocessing.Process(
            target=worker_process,
            args=(worker_id + 1, actual_per_worker, results_queue)
        )
        processes.append(p)
        p.start()
        
        # Stagger worker starts slightly
        time.sleep(0.1)
    
    # Collect results
    total_processed = 0
    successful = 0
    failed = 0
    total_qa_pairs = 0
    categories = {}
    durations = []
    
    print("📊 Processing Results:")
    print("-" * 40)
    
    # Monitor results as they come in
    expected_total = actual_per_worker * NUM_WORKERS
    while total_processed < expected_total:
        try:
            # Get result with timeout
            result = results_queue.get(timeout=120)  # 2 minute timeout
            
            total_processed += 1
            
            if result['success']:
                successful += 1
                total_qa_pairs += result['qa_count']
                category = result['category']
                categories[category] = categories.get(category, 0) + 1
                durations.append(result['duration'])
                
                print(f"✅ W{result['worker_id']} Topic {result['topic_id']}: {result['qa_count']} Q&A, {category}, {result['duration']:.1f}s")
            else:
                failed += 1
                error_msg = result['error'][:30] + '...' if result['error'] and len(result['error']) > 30 else result['error']
                print(f"❌ W{result['worker_id']} Topic {result['topic_id']}: {error_msg} ({result['duration']:.1f}s)")
            
            # Progress update every 10 topics
            if total_processed % 10 == 0:
                elapsed = time.time() - start_time
                print(f"\n📊 Progress: {total_processed}/{expected_total}")
                print(f"   Success: {successful}, Failed: {failed}")
                if successful > 0:
                    avg_time = sum(durations) / len(durations)
                    rate = successful / elapsed
                    print(f"   Avg time: {avg_time:.1f}s, Rate: {rate:.2f}/sec")
                print()
                
        except:
            # Timeout or queue empty - check if workers are still alive
            alive_workers = [p for p in processes if p.is_alive()]
            if not alive_workers:
                print("All workers finished")
                break
    
    # Wait for all processes to complete
    for p in processes:
        p.join()
    
    # Final summary
    total_time = time.time() - start_time
    
    print(f"\n🎯 PARALLEL PROCESSING COMPLETE")
    print("=" * 40)
    print(f"Duration: {total_time/60:.1f} minutes")
    print(f"Workers: {NUM_WORKERS}")
    print(f"Total processed: {total_processed}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(successful/total_processed)*100:.1f}%" if total_processed > 0 else "0%")
    print(f"Q&A pairs: {total_qa_pairs}")
    
    if successful > 0 and durations:
        avg_time = sum(durations) / len(durations)
        rate = successful / total_time
        print(f"Avg time per topic: {avg_time:.1f}s")
        print(f"Overall rate: {rate:.2f} topics/sec")
        print(f"Parallel speedup: ~{NUM_WORKERS}x")
    
    if categories:
        print(f"\nCategories processed:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count}")

if __name__ == "__main__":
    main()