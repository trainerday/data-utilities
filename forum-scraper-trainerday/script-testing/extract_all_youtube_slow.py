#!/usr/bin/env python3
"""
Extract All YouTube Videos - Slow and Safe
30-second delays between videos to avoid rate limiting
"""

import sys
from youtube_subtitle_extractor_v2 import YouTubeSubtitleExtractor
import time
import json
from datetime import datetime

def main():
    print("🎬 TrainerDay Complete YouTube Extraction")
    print("=" * 60)
    print("⏱️  Using 30-second delays to avoid rate limiting")
    print("🛑 Press Ctrl+C to stop anytime (progress is saved)")
    print("=" * 60)
    
    extractor = YouTubeSubtitleExtractor("@trainerday")
    
    # Get all videos
    print("📋 Getting complete video list...")
    videos = extractor.get_channel_videos()
    if not videos:
        print("❌ No videos found")
        return
    
    # Check what we already have
    existing_files = list(extractor.output_dir.glob("video_*.json"))
    existing_ids = {f.stem.replace('video_', '') for f in existing_files}
    
    # Find remaining videos
    remaining_videos = [v for v in videos if v['video_id'] not in existing_ids]
    
    print(f"\n📊 EXTRACTION STATUS:")
    print(f"   Total videos on channel: {len(videos)}")
    print(f"   Already extracted: {len(existing_ids)}")
    print(f"   Remaining to extract: {len(remaining_videos)}")
    
    if not remaining_videos:
        print("\n🎉 ALL VIDEOS ALREADY EXTRACTED!")
        print("✅ Nothing more to do")
        return
    
    print(f"\n🚀 Starting extraction of {len(remaining_videos)} videos...")
    print(f"   Estimated time: {(len(remaining_videos) * 30) // 60} minutes")
    print("\n" + "=" * 60)
    
    successful = 0
    failed = 0
    start_time = datetime.now()
    
    for i, video in enumerate(remaining_videos, 1):
        video_id = video['video_id']
        title = video['title']
        title_display = title[:55] + "..." if len(title) > 55 else title
        
        print(f"\n[{i:2d}/{len(remaining_videos)}] 🎥 {title_display}")
        print(f"   📺 Video ID: {video_id}")
        print(f"   🕐 {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            # Extract subtitles
            extraction_start = time.time()
            result = extractor.get_video_subtitles(video_id, video['title'])
            extraction_time = time.time() - extraction_start
            
            if isinstance(result, tuple):
                subtitle_data, error = result
            else:
                subtitle_data, error = result, None
            
            if subtitle_data and not error:
                # Save the video
                video_data = {
                    'video_id': video_id,
                    'title': video['title'], 
                    'url': video['url'],
                    'upload_date': video.get('upload_date'),
                    'duration': video.get('duration'),
                    'topics': extractor.extract_topics_from_title(video['title']),
                    'transcript': subtitle_data,
                    'processed_at': datetime.now().isoformat()
                }
                
                video_file = extractor.output_dir / f'video_{video_id}.json'
                with open(video_file, 'w', encoding='utf-8') as f:
                    json.dump(video_data, f, indent=2, ensure_ascii=False)
                
                successful += 1
                chars = len(subtitle_data['full_text'])
                segments = subtitle_data['segment_count']
                
                print(f"   ✅ SUCCESS: {chars:,} characters, {segments} segments")
                print(f"   📁 Saved: {video_file.name}")
                print(f"   ⚡ Extraction: {extraction_time:.1f}s")
                
            else:
                failed += 1
                print(f"   ❌ FAILED: {error or 'No transcript available'}")
                
        except Exception as e:
            failed += 1
            print(f"   💥 ERROR: {str(e)[:100]}...")
        
        # Progress summary
        total_extracted = len(existing_ids) + successful
        remaining_count = len(remaining_videos) - i
        elapsed = datetime.now() - start_time
        
        print(f"   📊 Progress: {successful}/{len(remaining_videos)} successful, {failed} failed")
        print(f"   🎯 Total extracted: {total_extracted}/{len(videos)} videos")
        
        if remaining_count > 0:
            # Estimate remaining time
            avg_time_per_video = elapsed.total_seconds() / i
            remaining_time_mins = (remaining_count * avg_time_per_video) / 60
            print(f"   ⏰ Estimated remaining: {remaining_time_mins:.0f} minutes")
            
            print(f"   ⏱️  Waiting 30 seconds before next video...")
            print("   " + "." * 50)
            
            # Countdown with dots
            for countdown in range(30):
                time.sleep(1)
                if countdown % 5 == 4:  # Print dot every 5 seconds
                    print(".", end="", flush=True)
            print()  # New line after countdown
    
    # Final summary
    elapsed = datetime.now() - start_time
    total_extracted = len(existing_ids) + successful
    
    print("\n" + "=" * 60)
    print("🎉 EXTRACTION COMPLETE!")
    print("=" * 60)
    print(f"📊 FINAL RESULTS:")
    print(f"   Videos successfully extracted this session: {successful}")
    print(f"   Videos failed this session: {failed}")
    print(f"   Total videos now available: {total_extracted}/{len(videos)}")
    print(f"   Time elapsed: {elapsed}")
    
    if failed > 0:
        print(f"\n⚠️  {failed} videos failed - they may be:")
        print(f"   • Private/unlisted videos")
        print(f"   • Videos without transcripts") 
        print(f"   • Rate limiting issues")
    
    if total_extracted == len(videos):
        print(f"\n🏆 ALL VIDEOS EXTRACTED! Ready for content analysis.")
    else:
        remaining = len(videos) - total_extracted
        print(f"\n📋 {remaining} videos remaining for future extraction")
    
    print(f"\n💾 All video files saved in: {extractor.output_dir}")
    print(f"🔍 Run 'python analyze_youtube_content.py' to analyze results")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n⏹️  EXTRACTION STOPPED BY USER")
        print(f"✅ All progress has been saved")
        print(f"🔄 You can resume by running this script again")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        print(f"✅ All progress has been saved")
        sys.exit(1)