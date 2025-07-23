#!/usr/bin/env python3
"""
Debug script to check what's wrong with the timestamp comparison
"""

import os
import requests
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def debug_comparison():
    # Test API connection
    api_key = os.getenv('DISCOURSE_API_KEY')
    base_url = 'https://forums.trainerday.com'
    headers = {'Api-Key': api_key, 'Api-Username': 'Alex'}
    
    print("🔍 Debugging timestamp comparison logic...")
    
    try:
        # Get first page of topics
        response = requests.get(f'{base_url}/latest.json?page=0', headers=headers, timeout=15)
        topics = response.json().get('topic_list', {}).get('topics', [])
        
        # Connect to database
        db_config = {
            'host': os.getenv('DB_HOST'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'database': os.getenv('DB_DATABASE'),
            'user': os.getenv('DB_USERNAME'),
            'password': os.getenv('DB_PASSWORD'),
            'sslmode': os.getenv('DB_SSLMODE', 'require')
        }
        
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Get one specific topic to debug in detail
        test_topic = topics[0]
        topic_id = test_topic['id']
        
        print(f"\n🔍 Debugging Topic {topic_id}: {test_topic.get('title', '')[:50]}...")
        
        # Get from database
        cursor.execute("""
            SELECT posts_count, last_post_id, last_posted_at, 
                   raw_content->'topic'->>'last_posted_at' as raw_last_posted_at,
                   raw_content->'topic'->>'posts_count' as raw_posts_count
            FROM forum_topics_raw 
            WHERE topic_id = %s
        """, (topic_id,))
        
        db_row = cursor.fetchone()
        if not db_row:
            print("❌ Topic not found in database")
            return
        
        db_posts_count, db_last_post_id, db_last_posted_at, raw_last_posted_at, raw_posts_count = db_row
        
        # Get from API  
        api_posts_count = test_topic.get('posts_count', 0)
        api_last_posted_at = test_topic.get('last_posted_at')
        
        print(f"\n📊 COMPARISON DETAILS:")
        print(f"   Posts Count:")
        print(f"     API: {api_posts_count}")
        print(f"     DB:  {db_posts_count}")
        print(f"     Raw: {raw_posts_count}")
        print(f"     Match: {api_posts_count == db_posts_count}")
        
        print(f"\n   Last Posted At:")
        print(f"     API: {api_last_posted_at}")
        print(f"     DB:  {db_last_posted_at}")
        print(f"     Raw: {raw_last_posted_at}")
        
        if api_last_posted_at and db_last_posted_at:
            try:
                api_time = datetime.fromisoformat(api_last_posted_at.replace('Z', '+00:00'))
                print(f"     API parsed: {api_time}")
                print(f"     DB parsed:  {db_last_posted_at}")
                print(f"     Time match: {api_time == db_last_posted_at}")
                print(f"     Time diff: {abs((api_time - db_last_posted_at).total_seconds())} seconds")
            except Exception as e:
                print(f"     Parse error: {e}")
        
        print(f"\n🤔 WHY IS IT DETECTING CHANGE?")
        
        # Test the actual comparison logic
        if db_posts_count != api_posts_count:
            print(f"   ❌ Posts count changed: {db_posts_count} != {api_posts_count}")
        else:
            print(f"   ✅ Posts count unchanged")
        
        if api_last_posted_at:
            try:
                api_time = datetime.fromisoformat(api_last_posted_at.replace('Z', '+00:00'))
                if db_last_posted_at and api_time != db_last_posted_at:
                    print(f"   ❌ Last posted time changed")
                    print(f"      Difference: {(api_time - db_last_posted_at).total_seconds()} seconds")
                else:
                    print(f"   ✅ Last posted time unchanged")
            except Exception as e:
                print(f"   ⚠️  Could not parse timestamp: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Debug error: {e}")

if __name__ == "__main__":
    debug_comparison()