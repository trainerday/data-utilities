#!/usr/bin/env python3
"""
Quick database connectivity and status test
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from pathlib import Path
import time

# Load environment variables
load_dotenv()

def test_db_connection():
    """Test database connection and get current status"""
    
    # Database configuration
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('DB_SSLMODE', 'require')
    }
    
    # Add SSL certificate if specified
    if os.getenv('DB_SSLROOTCERT'):
        ssl_cert_filename = os.getenv('DB_SSLROOTCERT')
        ssl_cert_path = Path(__file__).parent.parent / ssl_cert_filename
        if ssl_cert_path.exists():
            db_config['sslrootcert'] = str(ssl_cert_path)
            print(f"Using SSL certificate: {ssl_cert_path}")
    
    print("🔌 Testing database connection...")
    start_time = time.time()
    
    try:
        # Test connection
        connection = psycopg2.connect(**db_config)
        connection_time = time.time() - start_time
        print(f"✅ Connected in {connection_time:.2f} seconds")
        
        # Get basic stats
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            print("\n📊 Current database status:")
            
            # Raw topics count
            cursor.execute("SELECT COUNT(*) as total FROM forum_topics_raw")
            raw_total = cursor.fetchone()['total']
            
            # Topics with posts
            cursor.execute("""
                SELECT COUNT(*) as with_posts FROM forum_topics_raw 
                WHERE (jsonb_array_length(COALESCE(raw_content -> 'posts', '[]'::jsonb)) > 0
                       OR jsonb_array_length(COALESCE(raw_content -> 'post_stream' -> 'posts', '[]'::jsonb)) > 0)
            """)
            with_posts = cursor.fetchone()['with_posts']
            
            # Analyzed topics count
            cursor.execute("SELECT COUNT(*) as analyzed FROM forum_topics")
            analyzed = cursor.fetchone()['analyzed']
            
            # Q&A pairs count
            cursor.execute("SELECT COUNT(*) as qa_pairs FROM forum_qa_pairs")
            qa_pairs = cursor.fetchone()['qa_pairs']
            
            print(f"  Raw topics total: {raw_total}")
            print(f"  Topics with posts: {with_posts}")
            print(f"  Analyzed topics: {analyzed}")
            print(f"  Q&A pairs extracted: {qa_pairs}")
            
            progress_pct = (analyzed / with_posts) * 100 if with_posts > 0 else 0
            print(f"  Analysis progress: {progress_pct:.1f}%")
            
            # Get next unprocessed topics
            cursor.execute("""
                SELECT r.topic_id, r.title, r.posts_count
                FROM forum_topics_raw r
                LEFT JOIN forum_topics t ON r.topic_id = t.topic_id
                WHERE t.topic_id IS NULL
                AND (jsonb_array_length(COALESCE(r.raw_content -> 'posts', '[]'::jsonb)) > 0
                     OR jsonb_array_length(COALESCE(r.raw_content -> 'post_stream' -> 'posts', '[]'::jsonb)) > 0)
                ORDER BY r.topic_id
                LIMIT 5
            """)
            
            next_topics = cursor.fetchall()
            print(f"\n🎯 Next {len(next_topics)} topics to analyze:")
            for topic in next_topics:
                print(f"  {topic['topic_id']}: {topic['title'][:50]}... ({topic['posts_count']} posts)")
        
        connection.close()
        print("\n✅ Database test completed successfully")
        return True
        
    except Exception as e:
        connection_time = time.time() - start_time
        print(f"❌ Connection failed after {connection_time:.2f} seconds")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_db_connection()