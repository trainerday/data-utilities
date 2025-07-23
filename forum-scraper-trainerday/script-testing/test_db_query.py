#!/usr/bin/env python3
"""
Test the database query that's causing the hang
"""

import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

def test_topic_query():
    """Test the specific query that's used in process_topics_with_raw_storage"""
    
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
        connection = psycopg2.connect(**db_config)
        print("✅ Connected to database")
        
        # Test different variations of the query that might be hanging
        
        print("\n🔍 Testing query variations:")
        
        # Test 1: Small limit
        print("Test 1: Small limit (5 topics)")
        start_time = time.time()
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT topic_id, title, posts_count 
                FROM forum_topics_raw 
                WHERE (jsonb_array_length(COALESCE(raw_content -> 'posts', '[]'::jsonb)) > 0
                       OR jsonb_array_length(COALESCE(raw_content -> 'post_stream' -> 'posts', '[]'::jsonb)) > 0)
                ORDER BY topic_id
                LIMIT %s OFFSET %s
            """, (5, 0))
            
            results = cursor.fetchall()
            duration = time.time() - start_time
            print(f"  ✅ Returned {len(results)} topics in {duration:.2f}s")
        
        # Test 2: No offset (start from beginning)
        print("\nTest 2: Moderate limit with no offset (10 topics)")
        start_time = time.time()
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT topic_id, title, posts_count 
                FROM forum_topics_raw 
                WHERE (jsonb_array_length(COALESCE(raw_content -> 'posts', '[]'::jsonb)) > 0
                       OR jsonb_array_length(COALESCE(raw_content -> 'post_stream' -> 'posts', '[]'::jsonb)) > 0)
                ORDER BY topic_id
                LIMIT %s
            """, (10,))
            
            results = cursor.fetchall()
            duration = time.time() - start_time
            print(f"  ✅ Returned {len(results)} topics in {duration:.2f}s")
        
        # Test 3: The problematic version - skip already analyzed
        print("\nTest 3: Skip already analyzed topics (this might hang)")
        start_time = time.time()
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            # Get count of analyzed topics first
            cursor.execute("SELECT COUNT(*) as count FROM forum_topics")
            analyzed_count = cursor.fetchone()['count']
            print(f"  Currently analyzed: {analyzed_count} topics")
            
            # Now try the query with offset
            cursor.execute("""
                SELECT topic_id, title, posts_count 
                FROM forum_topics_raw 
                WHERE (jsonb_array_length(COALESCE(raw_content -> 'posts', '[]'::jsonb)) > 0
                       OR jsonb_array_length(COALESCE(raw_content -> 'post_stream' -> 'posts', '[]'::jsonb)) > 0)
                ORDER BY topic_id
                LIMIT %s OFFSET %s
            """, (10, analyzed_count))
            
            results = cursor.fetchall()
            duration = time.time() - start_time
            print(f"  ✅ Returned {len(results)} topics in {duration:.2f}s")
        
        # Test 4: The actual problematic version - NULL limit
        print("\nTest 4: With NULL limit (1000 default) - this is likely the problem")
        start_time = time.time()
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            # This is what happens when max_topics=None
            limit_value = None or 1000
            cursor.execute("""
                SELECT topic_id, title, posts_count 
                FROM forum_topics_raw 
                WHERE (jsonb_array_length(COALESCE(raw_content -> 'posts', '[]'::jsonb)) > 0
                       OR jsonb_array_length(COALESCE(raw_content -> 'post_stream' -> 'posts', '[]'::jsonb)) > 0)
                ORDER BY topic_id
                LIMIT %s OFFSET %s
            """, (limit_value, 0))
            
            results = cursor.fetchall()
            duration = time.time() - start_time
            print(f"  ✅ Returned {len(results)} topics in {duration:.2f}s")
            
        # Test 5: Skip already analyzed with better approach
        print("\nTest 5: Anti-join approach (only unanalyzed topics)")
        start_time = time.time()
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT r.topic_id, r.title, r.posts_count 
                FROM forum_topics_raw r
                LEFT JOIN forum_topics t ON r.topic_id = t.topic_id
                WHERE t.topic_id IS NULL
                AND (jsonb_array_length(COALESCE(r.raw_content -> 'posts', '[]'::jsonb)) > 0
                     OR jsonb_array_length(COALESCE(r.raw_content -> 'post_stream' -> 'posts', '[]'::jsonb)) > 0)
                ORDER BY r.topic_id
                LIMIT %s
            """, (10,))
            
            results = cursor.fetchall()
            duration = time.time() - start_time
            print(f"  ✅ Returned {len(results)} topics in {duration:.2f}s")
            
            # Show what we got
            print("  Next unprocessed topics:")
            for r in results[:3]:
                print(f"    {r['topic_id']}: {r['title'][:50]}...")
        
        connection.close()
        print("\n✅ All query tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Database query test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_topic_query()