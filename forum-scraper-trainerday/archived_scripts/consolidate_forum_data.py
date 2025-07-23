#!/usr/bin/env python3
"""
Consolidate all forum topics and posts into a single file for ChromaDB ingestion.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List

def load_categories(categories_file: str) -> Dict[int, Dict]:
    """Load categories mapping from categories.json"""
    with open(categories_file, 'r', encoding='utf-8') as f:
        categories = json.load(f)
    
    # Create a mapping of category_id to category info
    category_map = {}
    for category in categories:
        category_map[category['id']] = {
            'name': category['name'],
            'slug': category['slug'],
            'description': category.get('description_text', '')
        }
    
    return category_map

def clean_html_content(html_content: str) -> str:
    """Remove HTML tags and clean up content for text processing"""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', html_content)
    
    # Replace HTML entities
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&amp;', '&')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_topic_data(topic_file: str, category_map: Dict[int, Dict]) -> List[Dict]:
    """Extract data from a single topic file"""
    with open(topic_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    topic = data['topic']
    posts = data['posts']
    
    # Get category information
    category_id = topic.get('category_id', 1)
    category_info = category_map.get(category_id, {
        'name': 'Unknown',
        'slug': 'unknown',
        'description': ''
    })
    
    extracted_data = []
    
    for post in posts:
        # Extract relevant information
        post_data = {
            'topic_id': topic['id'],
            'topic_title': topic['title'],
            'topic_slug': topic['slug'],
            'category_id': category_id,
            'category_name': category_info['name'],
            'category_slug': category_info['slug'],
            'category_description': category_info['description'],
            'post_id': post['id'],
            'post_number': post['post_number'],
            'username': post['username'],
            'display_name': post.get('display_username', post.get('name', '')),
            'user_id': post['user_id'],
            'created_at': post['created_at'],
            'updated_at': post.get('updated_at', ''),
            'content_raw': post.get('cooked', ''),
            'content_clean': clean_html_content(post.get('cooked', '')),
            'reply_count': post.get('reply_count', 0),
            'like_count': post.get('actions_summary', []),
            'is_staff': post.get('staff', False),
            'is_admin': post.get('admin', False),
            'topic_views': topic.get('views', 0),
            'topic_posts_count': topic.get('posts_count', 0),
            'topic_like_count': topic.get('like_count', 0),
            'topic_created_at': topic['created_at'],
            'topic_last_posted_at': topic.get('last_posted_at', ''),
            'is_original_post': post['post_number'] == 1
        }
        
        # Parse date for easier filtering
        try:
            post_date = datetime.fromisoformat(post['created_at'].replace('Z', '+00:00'))
            post_data['date'] = post_date.strftime('%Y-%m-%d')
            post_data['year'] = post_date.year
            post_data['month'] = post_date.month
        except:
            post_data['date'] = ''
            post_data['year'] = None
            post_data['month'] = None
        
        # Extract like count from actions_summary
        like_count = 0
        for action in post.get('actions_summary', []):
            if action.get('id') == 2:  # Like action
                like_count = action.get('count', 0)
        post_data['post_like_count'] = like_count
        
        extracted_data.append(post_data)
    
    return extracted_data

def consolidate_forum_data(forum_data_dir: str, output_file: str):
    """Consolidate all forum data into a single JSON file"""
    
    # Load categories
    categories_file = os.path.join(forum_data_dir, 'categories.json')
    category_map = load_categories(categories_file)
    
    print(f"📋 Loaded {len(category_map)} categories")
    
    # Find all topic files
    topic_files = []
    for file in os.listdir(forum_data_dir):
        if file.startswith('topic_') and file.endswith('.json'):
            topic_files.append(os.path.join(forum_data_dir, file))
    
    print(f"🔍 Found {len(topic_files)} topic files")
    
    # Process all topics
    all_posts = []
    processed_topics = 0
    
    for topic_file in topic_files:
        try:
            topic_data = extract_topic_data(topic_file, category_map)
            all_posts.extend(topic_data)
            processed_topics += 1
            
            if processed_topics % 100 == 0:
                print(f"📊 Processed {processed_topics} topics...")
                
        except Exception as e:
            print(f"❌ Error processing {topic_file}: {e}")
    
    # Sort by date (newest first)
    all_posts.sort(key=lambda x: x['created_at'], reverse=True)
    
    # Create summary statistics
    summary = {
        'total_posts': len(all_posts),
        'total_topics': processed_topics,
        'categories': list(category_map.values()),
        'date_range': {
            'earliest': min(post['created_at'] for post in all_posts if post['created_at']),
            'latest': max(post['created_at'] for post in all_posts if post['created_at'])
        },
        'consolidated_at': datetime.now().isoformat(),
        'unique_users': len(set(post['username'] for post in all_posts)),
        'posts_by_category': {}
    }
    
    # Count posts by category
    for post in all_posts:
        category = post['category_name']
        summary['posts_by_category'][category] = summary['posts_by_category'].get(category, 0) + 1
    
    # Create final output
    consolidated_data = {
        'summary': summary,
        'posts': all_posts
    }
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(consolidated_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Consolidation complete!")
    print(f"📊 Total posts: {len(all_posts)}")
    print(f"📝 Total topics: {processed_topics}")
    print(f"👥 Unique users: {summary['unique_users']}")
    print(f"📅 Date range: {summary['date_range']['earliest'][:10]} to {summary['date_range']['latest'][:10]}")
    print(f"💾 Output file: {output_file}")
    
    # Print category breakdown
    print(f"\n📋 Posts by category:")
    for category, count in sorted(summary['posts_by_category'].items(), key=lambda x: x[1], reverse=True):
        print(f"   {category}: {count} posts")

def create_chromadb_format(consolidated_file: str, chromadb_file: str):
    """Create a simplified format specifically for ChromaDB ingestion"""
    
    with open(consolidated_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    chromadb_docs = []
    
    for post in data['posts']:
        # Create document for ChromaDB
        doc = {
            'id': f"post_{post['post_id']}",
            'text': post['content_clean'],
            'metadata': {
                'topic_id': post['topic_id'],
                'topic_title': post['topic_title'],
                'category': post['category_name'],
                'username': post['username'],
                'date': post['date'],
                'year': post['year'],
                'month': post['month'],
                'is_original_post': post['is_original_post'],
                'post_number': post['post_number'],
                'topic_views': post['topic_views'],
                'like_count': post['post_like_count']
            }
        }
        
        # Only include posts with meaningful content
        if len(post['content_clean'].strip()) > 10:
            chromadb_docs.append(doc)
    
    # Write ChromaDB format
    with open(chromadb_file, 'w', encoding='utf-8') as f:
        json.dump(chromadb_docs, f, indent=2, ensure_ascii=False)
    
    print(f"📄 ChromaDB format created: {chromadb_file}")
    print(f"📊 Documents for ChromaDB: {len(chromadb_docs)}")

if __name__ == "__main__":
    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    forum_data_dir = os.path.join(script_dir, 'forum_data')
    output_file = os.path.join(script_dir, 'consolidated_forum_data.json')
    chromadb_file = os.path.join(script_dir, 'forum_data_for_chromadb.json')
    
    print("🔄 TrainerDay Forum Data Consolidation")
    print("=" * 50)
    
    # Consolidate all forum data
    consolidate_forum_data(forum_data_dir, output_file)
    
    print("\n" + "=" * 50)
    
    # Create ChromaDB-specific format
    create_chromadb_format(output_file, chromadb_file)
    
    print(f"\n✅ Done! Files created:")
    print(f"   📋 Full data: {output_file}")
    print(f"   🔍 ChromaDB ready: {chromadb_file}")