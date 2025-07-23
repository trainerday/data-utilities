#!/usr/bin/env python3
"""
Analyze the YouTube content we've extracted so far.
"""

import json
from pathlib import Path
from collections import defaultdict, Counter

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "youtube_content"

def analyze_extracted_content():
    """Analyze the extracted YouTube content."""
    print("📊 Analyzing extracted YouTube content")
    print("="*50)
    
    # Find all video files
    video_files = list(OUTPUT_DIR.glob("video_*.json"))
    
    if not video_files:
        print("❌ No video files found")
        return
    
    print(f"📹 Found {len(video_files)} extracted videos")
    
    # Analyze content
    total_characters = 0
    total_segments = 0
    topics = Counter()
    videos_by_length = []
    
    for video_file in video_files:
        with open(video_file, 'r', encoding='utf-8') as f:
            video_data = json.load(f)
        
        # Extract metrics
        title = video_data['title']
        text_length = len(video_data['transcript']['full_text'])
        segment_count = video_data['transcript']['segment_count']
        video_topics = video_data['topics']
        
        total_characters += text_length
        total_segments += segment_count
        
        for topic in video_topics:
            topics[topic] += 1
        
        videos_by_length.append({
            'title': title,
            'text_length': text_length,
            'segment_count': segment_count,
            'topics': video_topics
        })
    
    # Sort by content length
    videos_by_length.sort(key=lambda x: x['text_length'], reverse=True)
    
    # Print analysis
    print(f"\n📈 Content Statistics:")
    print(f"   Total videos: {len(video_files)}")
    print(f"   Total characters: {total_characters:,}")
    print(f"   Total transcript segments: {total_segments:,}")
    print(f"   Average characters per video: {total_characters // len(video_files):,}")
    
    print(f"\n🏷️  Topics Coverage:")
    for topic, count in topics.most_common():
        print(f"   {topic}: {count} videos")
    
    print(f"\n📋 Videos by Content Length:")
    for i, video in enumerate(videos_by_length, 1):
        print(f"   {i:2d}. {video['text_length']:5,} chars | {video['title'][:60]}...")
        print(f"       Topics: {', '.join(video['topics'])}")
    
    # Content samples
    print(f"\n📝 Sample Content (first video):")
    if videos_by_length:
        longest_video = videos_by_length[0]
        
        # Read the full content for the longest video
        video_id = None
        for video_file in video_files:
            with open(video_file, 'r', encoding='utf-8') as f:
                video_data = json.load(f)
            if video_data['title'] == longest_video['title']:
                video_id = video_data['video_id']
                full_text = video_data['transcript']['full_text']
                break
        
        if full_text:
            # Show first 300 characters as sample
            sample = full_text[:300] + "..." if len(full_text) > 300 else full_text
            print(f"   Video: {longest_video['title']}")
            print(f"   Sample: {sample}")
    
    print(f"\n🎯 Next Steps:")
    print(f"1. Continue extracting remaining videos with rate limiting")
    print(f"2. Vectorize this content for semantic search")
    print(f"3. Integrate with forum Q&A and blog content")
    
    return {
        'total_videos': len(video_files),
        'total_characters': total_characters,
        'total_segments': total_segments,
        'topics': dict(topics),
        'videos': videos_by_length
    }

if __name__ == "__main__":
    analysis = analyze_extracted_content()