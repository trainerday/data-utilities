#!/usr/bin/env python3
"""
Check what metadata we get from the topic list API (without fetching all posts)
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def check_topic_list_metadata():
    api_key = os.getenv('DISCOURSE_API_KEY')
    base_url = 'https://forums.trainerday.com'
    headers = {'Api-Key': api_key, 'Api-Username': 'Alex'}
    
    print("🔍 Checking what metadata we get from topic list...")
    
    try:
        # Get latest topics list (this is lightweight)
        response = requests.get(f'{base_url}/latest.json?page=0', headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            topics = data.get('topic_list', {}).get('topics', [])
            
            if topics:
                # Show what metadata we get for first topic
                first_topic = topics[0]
                print(f"\n📊 Topic List Metadata for Topic {first_topic['id']}:")
                print(f"Title: {first_topic.get('title', 'N/A')}")
                
                # Show ALL available fields
                print(f"\n🔑 All available fields from topic list:")
                for key, value in first_topic.items():
                    print(f"  {key}: {value}")
                
                print(f"\n🎯 KEY FIELDS WE CAN USE:")
                useful_fields = [
                    'posts_count', 'last_posted_at', 'last_poster_username',
                    'created_at', 'views', 'reply_count', 'like_count'
                ]
                
                for field in useful_fields:
                    if field in first_topic:
                        print(f"  ✅ {field}: {first_topic[field]}")
                    else:
                        print(f"  ❌ {field}: NOT AVAILABLE")
                
                # Check if we can avoid the expensive /t/{id}.json call
                print(f"\n🚀 OPTIMIZATION POTENTIAL:")
                if 'posts_count' in first_topic and 'last_posted_at' in first_topic:
                    print(f"  ✅ We can compare posts_count and last_posted_at without expensive API call!")
                    print(f"  ✅ Only fetch full posts when these change!")
                else:
                    print(f"  ❌ We need the expensive API call to get change detection data")
        
        else:
            print(f"❌ API error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_topic_list_metadata()