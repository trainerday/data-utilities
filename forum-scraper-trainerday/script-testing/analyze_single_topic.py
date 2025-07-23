#!/usr/bin/env python3
"""
Single Topic Analysis Test
Process one topic at a time to debug performance issues
"""

import os
import sys
import time
from pathlib import Path

# Add parent directory to path to import the analyzer
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

def analyze_single_topic(topic_id):
    """Analyze a single topic with detailed timing"""
    
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
    
    print(f"🔍 Analyzing topic {topic_id}")
    
    try:
        # Step 1: Initialize analyzer
        step1_start = time.time()
        analyzer = ForumTopicAnalyzerV2(db_config=db_config)
        analyzer.connect_to_database()
        step1_time = time.time() - step1_start
        print(f"  ✓ Analyzer initialized in {step1_time:.2f}s")
        
        # Step 2: Clear existing analysis
        step2_start = time.time()
        analyzer.delete_existing_analysis(topic_id)
        step2_time = time.time() - step2_start
        print(f"  ✓ Cleared existing analysis in {step2_time:.2f}s")
        
        # Step 3: Analyze topic
        step3_start = time.time()
        analysis = analyzer.analyze_stored_topic(topic_id)
        step3_time = time.time() - step3_start
        print(f"  ✓ Topic analysis completed in {step3_time:.2f}s")
        
        if analysis:
            # Step 4: Save to database
            step4_start = time.time()
            analyzer.save_analysis_to_database(analysis)
            step4_time = time.time() - step4_start
            print(f"  ✓ Analysis saved to database in {step4_time:.2f}s")
            
            # Summary
            qa_count = len(analysis.get('qa_pairs', []))
            category = analysis.get('topic_summary', {}).get('analysis_category', 'Unknown')
            print(f"  ✅ Success: {qa_count} Q&A pairs, category: {category}")
            
            total_time = step1_time + step2_time + step3_time + step4_time
            print(f"  📊 Total time: {total_time:.2f}s")
            
            return True
        else:
            print(f"  ❌ Analysis failed - no results returned")
            return False
            
    except Exception as e:
        print(f"  ❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'analyzer' in locals():
            analyzer.close_database_connection()

def main():
    """Run single topic analysis"""
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key required")
        return
    
    print("🎯 Single Topic Analysis Mode")
    print("=" * 40)
    
    # Get next topic to process
    topic_info = get_next_unprocessed_topic()
    
    if not topic_info:
        print("✅ No more topics to process!")
        return
    
    print(f"📝 Next topic: {topic_info['topic_id']}")
    print(f"   Title: {topic_info['title']}")
    print(f"   Posts: {topic_info['posts_count']}")
    print()
    
    # Analyze the topic
    success = analyze_single_topic(topic_info['topic_id'])
    
    if success:
        print("\n🎉 Topic successfully analyzed!")
        
        # Show what would be next
        next_topic = get_next_unprocessed_topic()
        if next_topic:
            print(f"\n🔍 Next up: Topic {next_topic['topic_id']} - {next_topic['title']}")
        else:
            print("\n✅ That was the last topic!")
    else:
        print("\n💥 Analysis failed for this topic")

if __name__ == "__main__":
    main()