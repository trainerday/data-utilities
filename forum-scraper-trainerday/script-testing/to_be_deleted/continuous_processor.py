#!/usr/bin/env python3
"""
Continuous Topic Processor
Processes topics one by one in a simple loop
"""

import os
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.analyze_forum_topics import ForumTopicAnalyzerV2
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables
load_dotenv()

def get_next_unprocessed_topic():
    """Get the next topic that needs analysis"""
    
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
            cursor.execute("""
                SELECT r.topic_id, r.title, r.posts_count
                FROM forum_topics_raw r
                LEFT JOIN forum_topics t ON r.topic_id = t.topic_id
                WHERE t.topic_id IS NULL
                AND (jsonb_array_length(COALESCE(r.raw_content -> 'posts', '[]'::jsonb)) > 0
                     OR jsonb_array_length(COALESCE(r.raw_content -> 'post_stream' -> 'posts', '[]'::jsonb)) > 0)
                ORDER BY r.topic_id
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            connection.close()
            return result
    except Exception as e:
        print(f"Error getting next topic: {e}")
        return None

def analyze_topic(topic_id):
    """Analyze a single topic"""
    
    # Database configuration
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
        analyzer = ForumTopicAnalyzerV2(db_config=db_config)
        analyzer.connect_to_database()
        
        # Clear existing analysis
        analyzer.delete_existing_analysis(topic_id)
        
        # Analyze topic
        analysis = analyzer.analyze_stored_topic(topic_id)
        
        if analysis:
            # Save to database
            analyzer.save_analysis_to_database(analysis)
            qa_count = len(analysis.get('qa_pairs', []))
            category = analysis.get('topic_summary', {}).get('analysis_category', 'Unknown')
            analyzer.close_database_connection()
            return True, qa_count, category
        else:
            analyzer.close_database_connection()
            return False, 0, "Failed"
            
    except Exception as e:
        print(f"  Error analyzing topic {topic_id}: {e}")
        if 'analyzer' in locals():
            analyzer.close_database_connection()
        return False, 0, f"Error: {e}"

def run_continuous_processing():
    """Run continuous topic processing"""
    
    print("🔄 Continuous Topic Processor")
    print("=" * 40)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key required")
        return
    
    # Configuration
    MAX_TOPICS = 20  # Process 20 topics then stop
    
    print(f"Will process up to {MAX_TOPICS} topics")
    
    processed = 0
    successful = 0
    failed = 0
    start_time = time.time()
    
    try:
        while processed < MAX_TOPICS:
            # Get next topic
            topic_info = get_next_unprocessed_topic()
            
            if not topic_info:
                print("✅ No more topics to process!")
                break
            
            topic_id = topic_info['topic_id']
            title = topic_info['title']
            posts_count = topic_info['posts_count']
            
            print(f"\n[{processed+1}/{MAX_TOPICS}] Topic {topic_id}: {title[:50]}... ({posts_count} posts)")
            
            topic_start = time.time()
            success, qa_count, category = analyze_topic(topic_id)
            topic_duration = time.time() - topic_start
            
            processed += 1
            
            if success:
                successful += 1
                print(f"  ✅ Success: {qa_count} Q&A pairs, {category} ({topic_duration:.1f}s)")
            else:
                failed += 1
                print(f"  ❌ Failed: {category} ({topic_duration:.1f}s)")
            
            # Progress update every 5 topics
            if processed % 5 == 0:
                elapsed = time.time() - start_time
                rate = successful / elapsed if elapsed > 0 else 0
                print(f"\n📊 Progress: {processed} processed, {successful} successful, {failed} failed")
                print(f"   Rate: {rate:.2f} topics/second, {elapsed/60:.1f} minutes elapsed")
        
        # Final summary
        total_time = time.time() - start_time
        print(f"\n🎯 PROCESSING COMPLETE")
        print("=" * 30)
        print(f"Total processed: {processed}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Success rate: {(successful/processed)*100:.1f}%")
        print(f"Total time: {total_time/60:.1f} minutes")
        
        if successful > 0:
            avg_time = total_time / successful
            rate = successful / total_time
            print(f"Average per topic: {avg_time:.1f} seconds")
            print(f"Processing rate: {rate:.2f} topics/second")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Interrupted by user after {processed} topics")
        elapsed = time.time() - start_time
        if successful > 0:
            rate = successful / elapsed
            print(f"Partial rate: {rate:.2f} topics/second")

if __name__ == "__main__":
    run_continuous_processing()