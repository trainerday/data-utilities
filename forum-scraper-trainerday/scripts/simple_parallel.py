#!/usr/bin/env python3
"""
Simple Parallel Processor - No cleanup, just process
"""

import os
import sys
import time
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

def get_next_unprocessed_topic():
    """Get next unprocessed topic"""
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
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            connection.close()
            return dict(result) if result else None
            
    except Exception as e:
        print(f"❌ Error getting topic: {e}")
        return None

def process_single_topic(topic_data):
    """Process a single topic"""
    try:
        # Initialize analyzer with database config
        db_config = get_db_config()
        analyzer = ForumTopicAnalyzerV2(db_config=db_config)
        
        # Process the topic
        result = analyzer.analyze_single_topic_from_db(topic_data['topic_id'])
        return {
            'topic_id': topic_data['topic_id'],
            'title': topic_data['title'],
            'success': result is not None,
            'result': result
        }
        
    except Exception as e:
        return {
            'topic_id': topic_data['topic_id'],
            'title': topic_data['title'],
            'success': False,
            'error': str(e)
        }

def worker_task(worker_id):
    """Worker task that processes topics"""
    processed = 0
    while True:
        # Get next topic
        topic = get_next_unprocessed_topic()
        if not topic:
            print(f"Worker {worker_id}: No more topics to process")
            break
            
        print(f"Worker {worker_id}: Processing topic {topic['topic_id']}: {topic['title'][:50]}...")
        
        # Process the topic
        result = process_single_topic(topic)
        
        if result['success']:
            print(f"Worker {worker_id}: ✅ Completed topic {topic['topic_id']}")
            processed += 1
        else:
            print(f"Worker {worker_id}: ❌ Failed topic {topic['topic_id']}: {result.get('error', 'Unknown error')}")
        
        time.sleep(1)  # Brief pause between topics
    
    return processed

def main():
    print("🚀 Simple Parallel Processor")
    print("=" * 40)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key required")
        return
    
    NUM_WORKERS = 4
    print(f"Workers: {NUM_WORKERS}")
    print("=" * 40)
    
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
        
        print(f"Total topics: {total_raw}")
        print(f"Already processed: {processed}")
        print(f"Remaining: {remaining}")
        print("=" * 40)
        
        if remaining == 0:
            print("🎉 All topics already processed!")
            return
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return
    
    # Start processing with workers
    start_time = time.time()
    total_processed = 0
    
    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        # Submit worker tasks
        future_to_worker = {
            executor.submit(worker_task, worker_id): worker_id 
            for worker_id in range(1, NUM_WORKERS + 1)
        }
        
        # Collect results
        for future in as_completed(future_to_worker):
            worker_id = future_to_worker[future]
            try:
                processed_count = future.result()
                total_processed += processed_count
                print(f"Worker {worker_id} completed. Processed: {processed_count} topics")
            except Exception as e:
                print(f"Worker {worker_id} error: {e}")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 40)
    print("📊 PROCESSING COMPLETE")
    print(f"Total processed: {total_processed}")
    print(f"Time taken: {duration:.1f} seconds")
    print(f"Rate: {total_processed/duration:.1f} topics/second")

if __name__ == "__main__":
    main()