#!/usr/bin/env python3
"""
Extract YouTube Videos using Official YouTube Data API
Uses API key instead of scraping - much higher rate limits
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import requests
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables
load_dotenv()

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "youtube_content"

class YouTubeAPIExtractor:
    def __init__(self, channel_handle="@trainerday"):
        self.channel_handle = channel_handle
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True)
        
        if not self.api_key:
            print("❌ YOUTUBE_API_KEY not found in environment variables")
            print("   Please add YOUTUBE_API_KEY=your_key_here to your .env file")
            print("   Get API key from: https://console.developers.google.com/")
            sys.exit(1)
        
        # API endpoints
        self.base_url = "https://www.googleapis.com/youtube/v3"
    
    def get_channel_id(self):
        """Convert channel handle to channel ID using API."""
        print(f"🔍 Getting channel ID for {self.channel_handle}...")
        
        # Remove @ from handle if present
        handle = self.channel_handle.replace('@', '')
        
        url = f"{self.base_url}/channels"
        params = {
            'part': 'id,snippet',
            'forHandle': handle,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'items' in data and len(data['items']) > 0:
                channel_id = data['items'][0]['id']
                channel_name = data['items'][0]['snippet']['title']
                print(f"   ✅ Found channel: {channel_name} (ID: {channel_id})")
                return channel_id
            else:
                print(f"   ❌ Channel not found: {self.channel_handle}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error getting channel ID: {e}")
            return None
    
    def get_channel_videos(self, channel_id):
        """Get all videos from channel using API."""
        print(f"📺 Getting all videos from channel...")
        
        videos = []
        next_page_token = None
        page_count = 0
        
        while True:
            page_count += 1
            print(f"   📄 Fetching page {page_count}...")
            
            url = f"{self.base_url}/search"
            params = {
                'part': 'snippet',
                'channelId': channel_id,
                'type': 'video',
                'order': 'date',
                'maxResults': 50,  # Max per page
                'key': self.api_key
            }
            
            if next_page_token:
                params['pageToken'] = next_page_token
            
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Process videos from this page
                for item in data.get('items', []):
                    video_info = {
                        'video_id': item['id']['videoId'],
                        'title': item['snippet']['title'],
                        'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                        'upload_date': item['snippet']['publishedAt'],
                        'description': item['snippet']['description']
                    }
                    videos.append(video_info)
                
                # Check for next page
                next_page_token = data.get('nextPageToken')
                if not next_page_token:
                    break
                    
            except Exception as e:
                print(f"   ❌ Error fetching page {page_count}: {e}")
                break
        
        print(f"   ✅ Found {len(videos)} total videos")
        return videos
    
    def extract_topics_from_title(self, title):
        """Extract topic tags from video title."""
        title_lower = title.lower()
        topics = []
        
        # Topic mapping
        topic_keywords = {
            'mobile-app': ['app', 'mobile', 'ios', 'android'],
            'workout-creator': ['workout', 'create', 'editor', 'custom'],
            'trainer': ['trainer', 'smart trainer', 'kinetic', 'wahoo', 'tacx'],
            'power-zones': ['power', 'ftp', 'zones', 'threshold'],
            'heart-rate': ['heart rate', 'hr', 'hrv'],
            'tutorial': ['how to', 'tutorial', 'guide', 'setup'],
            'zwift': ['zwift'],
            'review': ['vs', 'comparison', 'review', 'better'],
            'features': ['feature', 'update', 'new'],
            'sync': ['sync', 'strava', 'garmin', 'trainingpeaks']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                topics.append(topic)
        
        return topics if topics else ['general']
    
    def get_video_subtitles(self, video_id, title):
        """Get subtitles using youtube-transcript-api."""
        try:
            api = YouTubeTranscriptApi()
            transcript = api.fetch(video_id)
            
            # Process transcript
            full_text = []
            segments = []
            
            for entry in transcript:
                text = entry.text.strip()
                start = entry.start
                duration = getattr(entry, 'duration', 0)
                
                # Clean transcript
                import re
                text = re.sub(r'\\[.*?\\]', '', text)  # Remove [Music], etc.
                text = re.sub(r'\\s+', ' ', text).strip()
                
                if text:
                    full_text.append(text)
                    segments.append({
                        'start': start,
                        'duration': duration,
                        'text': text
                    })
            
            return {
                'full_text': ' '.join(full_text),
                'segments': segments,
                'type': 'auto',
                'segment_count': len(segments)
            }, None
            
        except Exception as e:
            return None, str(e)
    
    def extract_all_videos(self):
        """Main extraction method using API."""
        print("🚀 YouTube API Extraction Started")
        print("=" * 60)
        
        # Get channel ID
        channel_id = self.get_channel_id()
        if not channel_id:
            return
        
        # Get all videos
        videos = self.get_channel_videos(channel_id)
        if not videos:
            print("❌ No videos found")
            return
        
        # Check existing extractions
        existing_files = list(self.output_dir.glob("video_*.json"))
        existing_ids = {f.stem.replace('video_', '') for f in existing_files}
        remaining_videos = [v for v in videos if v['video_id'] not in existing_ids]
        
        print(f"\\n📊 EXTRACTION STATUS:")
        print(f"   Total videos found: {len(videos)}")
        print(f"   Already extracted: {len(existing_ids)}")
        print(f"   Remaining to extract: {len(remaining_videos)}")
        
        if not remaining_videos:
            print("\\n🎉 ALL VIDEOS ALREADY EXTRACTED!")
            return
        
        print(f"\\n🔄 Starting extraction of {len(remaining_videos)} videos...")
        print("   (Using official API - much faster and more reliable)")
        print("\\n" + "=" * 60)
        
        successful = 0
        failed = 0
        start_time = datetime.now()
        
        for i, video in enumerate(remaining_videos, 1):
            video_id = video['video_id']
            title = video['title']
            title_display = title[:55] + "..." if len(title) > 55 else title
            
            print(f"\\n[{i:2d}/{len(remaining_videos)}] 🎥 {title_display}")
            print(f"   📺 Video ID: {video_id}")
            
            try:
                # Extract subtitles
                extraction_start = time.time()
                subtitle_data, error = self.get_video_subtitles(video_id, title)
                extraction_time = time.time() - extraction_start
                
                if subtitle_data and not error:
                    # Save video data
                    video_data = {
                        'video_id': video_id,
                        'title': title,
                        'url': video['url'],
                        'upload_date': video.get('upload_date'),
                        'description': video.get('description', ''),
                        'topics': self.extract_topics_from_title(title),
                        'transcript': subtitle_data,
                        'processed_at': datetime.now().isoformat()
                    }
                    
                    video_file = self.output_dir / f'video_{video_id}.json'
                    with open(video_file, 'w', encoding='utf-8') as f:
                        json.dump(video_data, f, indent=2, ensure_ascii=False)
                    
                    successful += 1
                    chars = len(subtitle_data['full_text'])
                    segments = subtitle_data['segment_count']
                    
                    print(f"   ✅ SUCCESS: {chars:,} characters, {segments} segments")
                    print(f"   ⚡ Extracted in {extraction_time:.1f}s")
                    
                else:
                    failed += 1
                    print(f"   ❌ FAILED: {error or 'No transcript available'}")
                    
            except Exception as e:
                failed += 1
                print(f"   💥 ERROR: {str(e)[:100]}...")
            
            # Progress update
            if i % 5 == 0 or i == len(remaining_videos):
                elapsed = datetime.now() - start_time
                rate = i / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0
                print(f"   📊 Progress: {successful} successful, {failed} failed")
                print(f"   ⚡ Rate: {rate:.1f} videos/second")
        
        # Final summary
        elapsed = datetime.now() - start_time
        total_extracted = len(existing_ids) + successful
        
        print("\\n" + "=" * 60)
        print("🎉 API EXTRACTION COMPLETE!")
        print("=" * 60)
        print(f"📊 RESULTS:")
        print(f"   Successfully extracted: {successful} videos")
        print(f"   Failed: {failed} videos")
        print(f"   Total videos available: {total_extracted}/{len(videos)}")
        print(f"   Time elapsed: {elapsed}")
        print(f"   Average speed: {successful/elapsed.total_seconds():.1f} videos/second")
        
        print(f"\\n💾 Files saved in: {self.output_dir}")
        print(f"🔍 Run 'python analyze_youtube_content.py' to analyze results")

def main():
    extractor = YouTubeAPIExtractor("@trainerday")
    extractor.extract_all_videos()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\\n⏹️  Extraction stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\\n💥 Error: {e}")
        sys.exit(1)