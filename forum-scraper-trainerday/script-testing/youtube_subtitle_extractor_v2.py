#!/usr/bin/env python3
"""
YouTube Subtitle Extractor for @trainerday channel - Version 2

Uses the correct YouTube Transcript API pattern.
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
import time

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "youtube_content"

class YouTubeSubtitleExtractor:
    def __init__(self, channel_handle="@trainerday"):
        self.channel_handle = channel_handle
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True)
        
        # yt-dlp configuration
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,  # Only get video metadata, not download
        }
    
    def get_channel_videos(self):
        """Get all video IDs from the channel."""
        print(f"🎥 Getting all videos from {self.channel_handle}...")
        
        channel_url = f"https://www.youtube.com/{self.channel_handle}/videos"
        
        videos = []
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # Extract playlist info (channel videos)
                playlist_info = ydl.extract_info(channel_url, download=False)
                
                if 'entries' in playlist_info:
                    for entry in playlist_info['entries']:
                        if entry:  # Some entries might be None
                            videos.append({
                                'video_id': entry.get('id'),
                                'title': entry.get('title', 'Unknown Title'),
                                'url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                                'duration': entry.get('duration'),
                                'upload_date': entry.get('upload_date')
                            })
        
        except Exception as e:
            print(f"   ❌ Error getting channel videos: {e}")
            return []
        
        print(f"   ✅ Found {len(videos)} videos")
        return videos
    
    def get_video_subtitles(self, video_id, title):
        """Get subtitles for a specific video using the correct API."""
        try:
            # Create API instance and fetch transcript
            api = YouTubeTranscriptApi()
            transcript = api.fetch(video_id, languages=['en'])
            
            # Process transcript into readable text
            full_text = []
            segments = []
            
            for entry in transcript:
                text = entry.text.strip()
                start = entry.start
                duration = getattr(entry, 'duration', 0)
                
                # Clean up auto-generated transcript artifacts
                text = re.sub(r'\[.*?\]', '', text)  # Remove [Music], [Applause], etc.
                text = re.sub(r'\s+', ' ', text).strip()  # Normalize whitespace
                
                if text:  # Only add non-empty segments
                    full_text.append(text)
                    segments.append({
                        'start': start,
                        'duration': duration,
                        'text': text
                    })
            
            return {
                'full_text': ' '.join(full_text),
                'segments': segments,
                'type': 'auto',  # Assume auto-generated for simplicity
                'segment_count': len(segments)
            }, None
            
        except Exception as e:
            return None, f"error: {str(e)}"
    
    def clean_subtitle_text(self, text):
        """Clean and normalize subtitle text for better processing."""
        if not text:
            return ""
        
        # Remove common subtitle artifacts
        text = re.sub(r'\[.*?\]', '', text)  # [Music], [Applause], etc.
        text = re.sub(r'\(.*?\)', '', text)  # (inaudible), etc.
        text = re.sub(r'>>.*?<<', '', text)  # >>Speaker name<<
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove very short segments (likely artifacts)
        sentences = text.split('. ')
        cleaned_sentences = [s for s in sentences if len(s.split()) >= 3]
        
        return '. '.join(cleaned_sentences)
    
    def extract_topics_from_title(self, title):
        """Extract topic keywords from video title."""
        title_lower = title.lower()
        
        # TrainerDay-specific topic patterns
        topics = []
        topic_patterns = {
            'garmin': r'\b(garmin|connect|edge|watch)\b',
            'zwift': r'\b(zwift|virtual|game)\b',
            'coach-jack': r'\b(coach\s*jack|ai\s*coach|training\s*plan)\b',
            'power-zones': r'\b(power|zone|ftp|threshold)\b',
            'heart-rate': r'\b(heart\s*rate|hr|bpm)\b',
            'mobile-app': r'\b(app|mobile|phone|ios|android)\b',
            'workout-creator': r'\b(workout|create|editor|interval)\b',
            'sync': r'\b(sync|export|send|upload)\b',
            'trainer': r'\b(trainer|smart|erg|resistance)\b',
            'setup': r'\b(setup|install|connect|pairing)\b',
            'review': r'\b(review|vs|compare|comparison)\b',
            'tutorial': r'\b(how\s*to|tutorial|guide|step)\b'
        }
        
        for topic, pattern in topic_patterns.items():
            if re.search(pattern, title_lower):
                topics.append(topic)
        
        return topics if topics else ['general']
    
    def save_video_data(self, video_info, subtitle_data):
        """Save processed video data to JSON file."""
        if not subtitle_data:
            return None
        
        video_data = {
            'video_id': video_info['video_id'],
            'title': video_info['title'],
            'url': video_info['url'],
            'upload_date': video_info.get('upload_date'),
            'duration': video_info.get('duration'),
            'topics': self.extract_topics_from_title(video_info['title']),
            'transcript': {
                'type': subtitle_data['type'],
                'full_text': self.clean_subtitle_text(subtitle_data['full_text']),
                'segment_count': subtitle_data['segment_count'],
                'segments': subtitle_data['segments']  # Keep original segments for timestamp reference
            },
            'processed_at': datetime.now().isoformat()
        }
        
        # Save individual video file
        video_file = self.output_dir / f"video_{video_info['video_id']}.json"
        with open(video_file, 'w', encoding='utf-8') as f:
            json.dump(video_data, f, indent=2, ensure_ascii=False)
        
        return video_data
    
    def extract_all_subtitles(self, max_videos=None, batch_size=5, delay_between_batches=30):
        """Extract subtitles from all channel videos with rate limiting."""
        print("🚀 Starting YouTube subtitle extraction with rate limiting")
        print("="*50)
        
        # Get all videos from channel
        videos = self.get_channel_videos()
        
        if not videos:
            print("❌ No videos found")
            return
        
        if max_videos:
            videos = videos[:max_videos]
            print(f"🎯 Processing first {max_videos} videos")
        
        print(f"📊 Rate limiting: {batch_size} videos per batch, {delay_between_batches}s delay between batches")
        
        # Check for existing extractions to resume
        existing_files = list(self.output_dir.glob("video_*.json"))
        existing_ids = {f.stem.replace('video_', '') for f in existing_files}
        
        # Filter out already processed videos
        remaining_videos = [v for v in videos if v['video_id'] not in existing_ids]
        
        if len(remaining_videos) < len(videos):
            print(f"📋 Resuming: {len(existing_ids)} already extracted, {len(remaining_videos)} remaining")
        
        # Process videos in batches
        successful_extractions = []
        failed_extractions = []
        total_processed = len(existing_ids)  # Count existing as processed
        
        for batch_start in range(0, len(remaining_videos), batch_size):
            batch_end = min(batch_start + batch_size, len(remaining_videos))
            batch = remaining_videos[batch_start:batch_end]
            batch_num = (batch_start // batch_size) + 1
            total_batches = (len(remaining_videos) + batch_size - 1) // batch_size
            
            print(f"\n🎯 Batch {batch_num}/{total_batches}: Processing {len(batch)} videos")
            print("-" * 30)
            
            batch_successful = 0
            batch_failed = 0
            
            for i, video in enumerate(batch, 1):
                global_index = total_processed + batch_start + i
                print(f"\n📹 [{global_index}/{len(videos)}] {video['title']}")
                print(f"   🔗 {video['url']}")
                
                # Get subtitles
                subtitle_data, error = self.get_video_subtitles(video['video_id'], video['title'])
                
                if subtitle_data:
                    # Save processed data
                    video_data = self.save_video_data(video, subtitle_data)
                    if video_data:
                        successful_extractions.append(video_data)
                        batch_successful += 1
                        print(f"   ✅ Extracted {subtitle_data['segment_count']} segments ({subtitle_data['type']} transcript)")
                        
                        # Show preview of content
                        preview = video_data['transcript']['full_text'][:100]
                        print(f"   📝 Preview: {preview}...")
                else:
                    failed_extractions.append({
                        'video': video,
                        'error': error
                    })
                    batch_failed += 1
                    
                    # Check if we hit rate limit
                    if "YouTube is blocking requests" in error or "blocked" in error.lower():
                        print(f"   🚫 Rate limited: {error[:100]}...")
                        print(f"   ⏰ Extending delay to avoid further blocks")
                        time.sleep(60)  # Wait longer if rate limited
                    else:
                        print(f"   ❌ Failed: {error}")
                
                # Rate limiting between individual videos
                time.sleep(2)
            
            # Print batch summary
            print(f"\n📊 Batch {batch_num} complete:")
            print(f"   ✅ Successful: {batch_successful}")
            print(f"   ❌ Failed: {batch_failed}")
            
            # Delay between batches (except for the last batch)
            if batch_end < len(remaining_videos):
                print(f"   ⏳ Waiting {delay_between_batches}s before next batch...")
                time.sleep(delay_between_batches)
        
        # Save summary
        summary = {
            'channel': self.channel_handle,
            'total_videos_found': len(videos),
            'successful_extractions': len(successful_extractions),
            'failed_extractions': len(failed_extractions),
            'extraction_date': datetime.now().isoformat(),
            'successful_videos': [
                {
                    'video_id': v['video_id'],
                    'title': v['title'],
                    'topics': v['topics'],
                    'transcript_type': v['transcript']['type'],
                    'text_length': len(v['transcript']['full_text'])
                }
                for v in successful_extractions
            ],
            'failed_videos': failed_extractions
        }
        
        summary_file = self.output_dir / f"extraction_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # Print final results
        print(f"\n{'='*50}")
        print("🎉 YouTube subtitle extraction complete!")
        print(f"✅ Successfully extracted: {len(successful_extractions)} videos")
        print(f"❌ Failed extractions: {len(failed_extractions)} videos")
        print(f"📊 Total text content: {sum(len(v['transcript']['full_text']) for v in successful_extractions):,} characters")
        print(f"📁 Content saved to: {self.output_dir}")
        print(f"📋 Summary saved to: {summary_file.name}")
        
        return successful_extractions, failed_extractions

def main():
    """Main extraction function."""
    extractor = YouTubeSubtitleExtractor("@trainerday")
    
    # Extract subtitles with rate limiting: 3 videos per batch, 45 second delays
    successful, failed = extractor.extract_all_subtitles(
        batch_size=3,           # Small batches to avoid rate limits
        delay_between_batches=45 # Longer delays between batches
    )
    
    if successful:
        print(f"\n🎯 Next steps:")
        print(f"1. Review extracted content in: {OUTPUT_DIR}")
        print(f"2. Run content vectorization on the extracted text")
        print(f"3. Integrate with content strategy pipeline")

if __name__ == "__main__":
    main()