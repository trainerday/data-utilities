#!/usr/bin/env python3
"""
Quick YouTube extraction with visible progress
"""

import sys
from youtube_subtitle_extractor_v2 import YouTubeSubtitleExtractor
import time

def main():
    print("🎬 TrainerDay YouTube Content Extraction")
    print("="*50)
    
    extractor = YouTubeSubtitleExtractor("@trainerday")
    
    # Get videos first
    videos = extractor.get_channel_videos()
    if not videos:
        print("❌ No videos found")
        return
    
    # Check what we already have
    existing_files = list(extractor.output_dir.glob("video_*.json"))
    existing_ids = {f.stem.replace('video_', '') for f in existing_files}
    
    # Find videos we haven't processed
    remaining_videos = [v for v in videos if v['video_id'] not in existing_ids]
    
    print(f"📊 Status:")
    print(f"   Total videos found: {len(videos)}")
    print(f"   Already extracted: {len(existing_ids)}")
    print(f"   Remaining to extract: {len(remaining_videos)}")
    
    if not remaining_videos:
        print("✅ All videos already extracted!")
        return
    
    print(f"\n🔄 Starting extraction of {len(remaining_videos)} remaining videos...")
    print("   (3 second delay between videos to avoid rate limiting)")
    
    successful = 0
    failed = 0
    
    for i, video in enumerate(remaining_videos, 1):
        video_id = video['video_id']
        title = video['title'][:60]  # Truncate for display
        
        print(f"\n[{i:2d}/{len(remaining_videos)}] Processing: {title}...")
        print(f"   Video ID: {video_id}")
        
        try:
            result = extractor.extract_single_video(video_id, video['title'])
            if result:
                successful += 1
                print(f"   ✅ Success - {len(result.get('transcript', {}).get('full_text', ''))} characters extracted")
            else:
                failed += 1
                print(f"   ❌ Failed - no transcript available")
        except Exception as e:
            failed += 1
            print(f"   ❌ Error: {str(e)[:100]}...")
        
        # Rate limiting
        if i < len(remaining_videos):  # Don't wait after last video
            print(f"   ⏱️  Waiting 3 seconds...")
            time.sleep(3)
    
    print(f"\n🎉 Extraction Complete!")
    print(f"   Successfully extracted: {successful} videos")
    print(f"   Failed: {failed} videos")
    print(f"   Total videos now available: {len(existing_ids) + successful}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n⏹️  Extraction stopped by user")
        sys.exit(0)