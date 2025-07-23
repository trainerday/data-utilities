#!/usr/bin/env python3
"""
Test script to verify the optimization logic works
"""

import os
import requests
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def test_optimization():
    # Test API connection
    api_key = os.getenv('DISCOURSE_API_KEY')
    base_url = 'https://forums.trainerday.com'
    headers = {'Api-Key': api_key, 'Api-Username': 'Alex'}
    
    print("🔍 Testing optimization logic...")
    
    try:
        # Get first page of topics
        print("📥 Fetching latest topics...")
        response = requests.get(f'{base_url}/latest.json?page=0', headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"❌ API error: {response.status_code}")
            return
        
        topics = response.json().get('topic_list', {}).get('topics', [])
        print(f"✅ Got {len(topics)} topics from API")
        
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
        
        # Get existing metadata for first few topics
        topic_ids = [t['id'] for t in topics[:5]]  # Just test first 5
        format_strings = ','.join(['%s'] * len(topic_ids))
        
        cursor.execute(f"""
            SELECT topic_id, posts_count, last_post_id, last_posted_at 
            FROM forum_topics_raw 
            WHERE topic_id IN ({format_strings})
        """, topic_ids)
        
        existing_data = {row[0]: {'posts_count': row[1], 'last_post_id': row[2], 'last_posted_at': row[3]} 
                        for row in cursor.fetchall()}
        
        print(f"✅ Got metadata for {len(existing_data)} existing topics")
        
        # Test optimization logic on each topic
        api_calls_saved = 0
        for i, topic in enumerate(topics[:5]):
            topic_id = topic['id']
            topic_title = topic.get('title', '')[:50]
            
            print(f"\n[{i+1}] Topic {topic_id}: {topic_title}...")
            
            if topic_id not in existing_data:
                print("  🆕 New topic - needs full fetch")
                continue
            
            existing = existing_data[topic_id]
            current_posts_count = topic.get('posts_count', 0)
            current_last_posted_at = topic.get('last_posted_at')
            
            # Check if posts count changed
            if existing['posts_count'] != current_posts_count:
                print(f"  📊 Posts count changed: {existing['posts_count']} -> {current_posts_count}")
                continue
            
            # Check if last posted time changed  
            if current_last_posted_at:
                try:
                    current_time = datetime.fromisoformat(current_last_posted_at.replace('Z', '+00:00'))
                    # Convert to naive datetime for comparison
                    current_time_naive = current_time.replace(tzinfo=None)
                    if existing['last_posted_at'] and current_time_naive != existing['last_posted_at']:
                        print(f"  ⏰ Last posted time changed: {existing['last_posted_at']} -> {current_time_naive}")
                        continue
                except Exception as e:
                    print(f"  ⚠️  Could not parse timestamp, will fetch: {e}")
                    continue
            
            # Topic appears unchanged - we can skip expensive API call
            print(f"  ⚡ SKIP: No changes detected - API call saved!")
            api_calls_saved += 1
        
        print(f"\n🎯 OPTIMIZATION TEST RESULTS:")
        print(f"   Topics tested: 5")
        print(f"   API calls that could be saved: {api_calls_saved}")
        print(f"   Efficiency gain: {(api_calls_saved/5)*100:.1f}%")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_optimization()