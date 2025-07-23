#!/usr/bin/env python3
"""
Test the true optimization - check if we can skip unchanged topics
"""

import os
import requests
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def test_topic_needs_update(topic_from_list, existing_metadata):
    """Same logic as in optimized scraper"""
    topic_id = topic_from_list['id']
    
    # If topic doesn't exist, definitely need to fetch
    if topic_id not in existing_metadata:
        return True
    
    existing = existing_metadata[topic_id]
    
    # Compare posts count (available in topic list)
    current_posts_count = topic_from_list.get('posts_count', 0)
    if existing['posts_count'] != current_posts_count:
        return True
    
    # Compare last posted time (available in topic list)
    current_last_posted_at = topic_from_list.get('last_posted_at')
    if current_last_posted_at:
        try:
            current_time = datetime.fromisoformat(current_last_posted_at.replace('Z', '+00:00'))
            current_time_naive = current_time.replace(tzinfo=None)
            if existing['last_posted_at'] and current_time_naive != existing['last_posted_at']:
                return True
        except:
            return True
    
    # Compare highest post number if available
    current_highest_post = topic_from_list.get('highest_post_number', 0)
    if existing['highest_post_number'] and existing['highest_post_number'] != current_highest_post:
        return True
    
    return False

def test_optimization():
    print("🔍 Testing true optimization logic...")
    
    # Get API data
    api_key = os.getenv('DISCOURSE_API_KEY')
    base_url = 'https://forums.trainerday.com'
    headers = {'Api-Key': api_key, 'Api-Username': 'Alex'}
    
    response = requests.get(f'{base_url}/latest.json?page=0', headers=headers, timeout=15)
    topics = response.json().get('topic_list', {}).get('topics', [])[:5]  # Just test first 5
    
    # Get database data
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
    cursor.execute("""
        SELECT topic_id, posts_count, last_post_id, last_posted_at, highest_post_number
        FROM forum_topics_raw
    """)
    
    existing_metadata = {}
    for row in cursor.fetchall():
        existing_metadata[row[0]] = {
            'posts_count': row[1],
            'last_post_id': row[2], 
            'last_posted_at': row[3],
            'highest_post_number': row[4]
        }
    
    print(f"✅ Got {len(existing_metadata)} existing topics from DB")
    
    # Test each topic
    skipped = 0
    for topic in topics:
        topic_id = topic['id']
        title = topic.get('title', '')[:50]
        
        needs_update = test_topic_needs_update(topic, existing_metadata)
        
        if needs_update:
            print(f"📥 Topic {topic_id}: {title} - NEEDS UPDATE")
        else:
            print(f"⚡ Topic {topic_id}: {title} - SKIP")
            skipped += 1
    
    print(f"\n🎯 RESULT: {skipped}/{len(topics)} topics can be skipped!")
    print(f"   Efficiency: {(skipped/len(topics))*100:.1f}%")

if __name__ == "__main__":
    test_optimization()