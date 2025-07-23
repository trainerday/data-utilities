#!/usr/bin/env python3
"""
Debug script to check API response structure for failing topics
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def debug_api_response():
    api_key = os.getenv('DISCOURSE_API_KEY')
    base_url = 'https://forums.trainerday.com'
    headers = {'Api-Key': api_key, 'Api-Username': 'Alex'}
    
    print("🔍 Debugging API response structure...")
    
    # Test a topic that was failing - let's try topic 61960 from the log
    test_topic_id = 61960
    
    try:
        print(f"📥 Fetching topic {test_topic_id}...")
        response = requests.get(f'{base_url}/t/{test_topic_id}.json', headers=headers, timeout=15)
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API call successful")
            
            # Check the structure
            print(f"\n🔍 Response structure:")
            print(f"Root keys: {list(data.keys())}")
            
            if 'topic' in data:
                topic = data['topic']
                print(f"Topic keys: {list(topic.keys())}")
                print(f"Topic ID: {topic.get('id', 'NOT FOUND')}")
                print(f"Topic title: {topic.get('title', 'NOT FOUND')[:50]}...")
            else:
                print("❌ No 'topic' key in response")
                
            if 'posts' in data:
                posts = data['posts']
                print(f"Posts count: {len(posts)}")
            else:
                print("❌ No 'posts' key in response")
                
            # Show first few lines of raw response
            print(f"\n📄 Raw response preview:")
            print(json.dumps(data, indent=2)[:500] + "...")
            
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Debug error: {e}")

if __name__ == "__main__":
    debug_api_response()