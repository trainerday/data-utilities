#!/usr/bin/env python3
"""
Simple Parallel Processor - Uses a queue-based approach
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

def get_unprocessed_topics(limit=100):
    """Get list of unprocessed topics"""
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
            """, (limit,))
            
            results = cursor.fetchall()
            connection.close()
            return results
    except Exception as e:
        print(f"Error getting topics: {e}")
        return []

def worker_thread(worker_id, topic_queue, results_queue):
    """Worker thread that processes topics from queue"""
    print(f"Worker {worker_id}: Started")
    
    processed = 0
    while True:
        try:
            # Get topic from queue with timeout
            topic = topic_queue.get(timeout=5)
            if topic is None:  # Poison pill to stop worker
                break
            
            topic_id = topic['topic_id']
            title = topic['title']
            
            start_time = time.time()
            
            try:
                # Process topic
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
                
            except Exception as e:
                duration = time.time() - start_time
                result = {
                    'success': False,
                    'topic_id': topic_id,
                    'title': title,
                    'error': str(e),
                    'duration': duration,
                    'worker_id': worker_id
                }
            
            results_queue.put(result)
            processed += 1
            topic_queue.task_done()
            
        except queue.Empty:
            break  # No more work
        except Exception as e:
            print(f"Worker {worker_id}: Error: {e}")
            break
    
    print(f"Worker {worker_id}: Finished ({processed} topics)")

def main():
    print("🚀 Simple Parallel Topic Processor")
    print("=" * 40)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key required")
        return
    
    # Configuration
    NUM_WORKERS = 3  # Number of worker threads
    BATCH_SIZE = 60  # Topics to process in this batch
    
    print(f"Workers: {NUM_WORKERS}")
    print(f"Batch size: {BATCH_SIZE}")
    
    # Get unprocessed topics
    print("📋 Getting unprocessed topics...")
    topics = get_unprocessed_topics(BATCH_SIZE)
    
    if not topics:
        print("✅ No unprocessed topics found!")
        return
    
    print(f"Found {len(topics)} unprocessed topics")
    print("=" * 40)
    
    # Create queues
    topic_queue = queue.Queue()
    results_queue = queue.Queue()
    
    # Fill topic queue
    for topic in topics:
        topic_queue.put(topic)
    
    # Start worker threads
    workers = []
    start_time = time.time()
    
    for i in range(NUM_WORKERS):
        worker = threading.Thread(
            target=worker_thread,
            args=(i+1, topic_queue, results_queue)
        )
        worker.start()
        workers.append(worker)
    
    # Collect results
    successful = 0
    failed = 0
    total_qa_pairs = 0
    categories = {}
    durations = []
    
    processed = 0
    total_topics = len(topics)
    
    print("📊 Processing Results:")
    print("-" * 30)
    
    while processed < total_topics:
        try:
            result = results_queue.get(timeout=120)  # 2 minute timeout
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
            
            # Progress update
            if processed % 5 == 0:
                elapsed = time.time() - start_time
                print(f"\n📊 Progress: {processed}/{total_topics} ({processed/total_topics*100:.1f}%)")
                print(f"   Success: {successful}, Failed: {failed}")
                if successful > 0:
                    avg_time = sum(durations) / len(durations)
                    rate = successful / elapsed
                    print(f"   Avg time: {avg_time:.1f}s, Rate: {rate:.2f}/sec")
                print()
                
        except queue.Empty:
            print("Timeout waiting for results")
            break
    
    # Stop workers
    for _ in workers:
        topic_queue.put(None)  # Poison pill
    
    # Wait for workers to finish
    for worker in workers:
        worker.join()
    
    # Final summary
    total_time = time.time() - start_time
    
    print(f"\n🎯 PARALLEL PROCESSING COMPLETE")
    print("=" * 35)
    print(f"Duration: {total_time/60:.1f} minutes")
    print(f"Workers: {NUM_WORKERS}")
    print(f"Processed: {processed}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(successful/processed)*100:.1f}%" if processed > 0 else "0%")
    print(f"Q&A pairs: {total_qa_pairs}")
    
    if successful > 0 and durations:
        avg_time = sum(durations) / len(durations)
        rate = successful / total_time
        print(f"Avg time: {avg_time:.1f}s")
        print(f"Rate: {rate:.2f} topics/sec")
        print(f"Speedup: ~{NUM_WORKERS}x")
    
    if categories:
        print(f"\nCategories:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count}")

if __name__ == "__main__":
    main()