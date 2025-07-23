#!/usr/bin/env python3
"""
Direct 200 Topic Processor - No subprocesses, direct function calls
"""

import os
import sys
import time
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

def get_next_unprocessed_topic():
    """Get the next unprocessed topic"""
    try:
        connection = psycopg2.connect(**get_db_config())
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT r.topic_id, r.title, r.posts_count, r.created_at_original
                FROM forum_topics_raw r
                LEFT JOIN forum_topics t ON r.topic_id = t.topic_id
                WHERE t.topic_id IS NULL
                AND (jsonb_array_length(COALESCE(r.raw_content -> 'posts', '[]'::jsonb)) > 0
                     OR jsonb_array_length(COALESCE(r.raw_content -> 'post_stream' -> 'posts', '[]'::jsonb)) > 0)
                ORDER BY r.topic_id DESC
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            connection.close()
            return result
    except Exception as e:
        print(f"Error getting next topic: {e}")
        return None

def analyze_topic_direct(topic_id, title):
    """Analyze a topic directly using the analyzer"""
    try:
        start_time = time.time()
        
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
                'category': 'Failed',
                'duration': duration,
                'error': 'Analysis returned None'
            }
            
    except Exception as e:
        duration = time.time() - start_time if 'start_time' in locals() else 0
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
    print("🚀 Direct 200 Topic Processor")
    print("=" * 35)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key required")
        return
    
    # Statistics
    successful = 0
    failed = 0
    total_qa_pairs = 0
    categories = {}
    durations = []
    start_time = time.time()
    target_topics = 200
    
    for i in range(target_topics):
        current_time = datetime.now().strftime('%H:%M:%S')
        
        # Get next topic
        topic_info = get_next_unprocessed_topic()
        
        if not topic_info:
            print(f"[{current_time}] ✅ No more unprocessed topics available!")
            break
        
        topic_id = topic_info['topic_id']
        title = topic_info['title']
        posts_count = topic_info['posts_count']
        
        print(f"[{current_time}] 🎯 {i+1}/{target_topics} Topic {topic_id}: {title[:40]}... ({posts_count} posts)")
        
        # Process topic
        result = analyze_topic_direct(topic_id, title)
        
        if result['success']:
            successful += 1
            total_qa_pairs += result['qa_count']
            category = result['category']
            categories[category] = categories.get(category, 0) + 1
            durations.append(result['duration'])
            
            print(f"   ✅ {result['qa_count']} Q&A, {category}, {result['duration']:.1f}s")
        else:
            failed += 1
            error_msg = result['error'][:30] + '...' if result['error'] and len(result['error']) > 30 else result['error']
            print(f"   ❌ Failed: {error_msg} ({result['duration']:.1f}s)")
        
        # Progress updates every 10 topics
        if (i + 1) % 10 == 0:
            elapsed = time.time() - start_time
            total_processed = successful + failed
            
            print(f"\n📊 Progress: {i+1}/{target_topics} ({((i+1)/target_topics)*100:.1f}%)")
            print(f"   Successful: {successful}, Failed: {failed}")
            print(f"   Success rate: {(successful/total_processed)*100:.1f}%")
            print(f"   Elapsed: {elapsed/60:.1f}m")
            
            if successful > 0 and durations:
                avg_time = sum(durations) / len(durations)
                rate = successful / elapsed
                remaining = target_topics - (i + 1)
                eta = (remaining / rate / 60) if rate > 0 else 0
                
                print(f"   Avg per topic: {avg_time:.1f}s")
                print(f"   Rate: {rate:.2f} topics/sec")
                print(f"   ETA: {eta:.1f}m")
            print()
    
    # Final summary
    total_time = time.time() - start_time
    total_processed = successful + failed
    
    print(f"🎯 PROCESSING COMPLETE")
    print("=" * 30)
    print(f"Duration: {total_time/60:.1f} minutes")
    print(f"Processed: {total_processed}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(successful/total_processed)*100:.1f}%")
    print(f"Q&A pairs: {total_qa_pairs}")
    
    if successful > 0 and durations:
        avg_time = sum(durations) / len(durations)
        rate = successful / total_time
        print(f"Avg time: {avg_time:.1f}s")
        print(f"Rate: {rate:.2f} topics/sec")
    
    if categories:
        print(f"\nCategories:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count}")

if __name__ == "__main__":
    main()