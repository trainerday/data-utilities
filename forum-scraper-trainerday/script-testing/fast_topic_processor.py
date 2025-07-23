#!/usr/bin/env python3
"""
Fast Topic Processor - Uses gpt-4o-mini for 10x speed improvement
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
    """Get the next unprocessed topic"""
    
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

def main():
    """Process the next topic with FAST gpt-4o-mini model"""
    
    print("⚡ FAST Topic Processor (using gpt-4o-mini)")
    print("=" * 45)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key required")
        return
    
    # Get the next unprocessed topic
    topic_info = get_next_unprocessed_topic()
    
    if not topic_info:
        print("✅ No unprocessed topics found!")
        return
    
    topic_id = topic_info['topic_id']
    title = topic_info['title']
    posts_count = topic_info['posts_count']
    created_date = topic_info['created_at_original'].strftime('%Y-%m-%d') if topic_info['created_at_original'] else 'Unknown'
    
    print(f"📝 Processing with FAST model:")
    print(f"   ID: {topic_id}")
    print(f"   Date: {created_date}")
    print(f"   Title: {title}")
    print(f"   Posts: {posts_count}")
    print()
    
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
        start_time = time.time()
        
        print("🔍 Analyzing topic with gpt-4o-mini (FAST)...")
        
        analyzer = ForumTopicAnalyzerV2(db_config=db_config)
        analyzer.connect_to_database()
        analyzer.delete_existing_analysis(topic_id)
        
        # THE KEY CHANGE: Use gpt-4o-mini instead of gpt-4
        analysis = analyzer.analyze_stored_topic(topic_id, model="gpt-4o-mini")  # ⚡ FAST MODEL
        
        if analysis:
            analyzer.save_analysis_to_database(analysis)
            qa_count = len(analysis.get('qa_pairs', []))
            category = analysis.get('topic_summary', {}).get('analysis_category', 'Unknown')
            
            duration = time.time() - start_time
            print(f"✅ FAST Success!")
            print(f"   Model: gpt-4o-mini")
            print(f"   Q&A pairs extracted: {qa_count}")
            print(f"   Category: {category}")
            print(f"   Duration: {duration:.1f}s (should be ~3-5s with fast model)")
        else:
            print("❌ Analysis failed - no results returned")
        
        analyzer.close_database_connection()
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")

if __name__ == "__main__":
    main()