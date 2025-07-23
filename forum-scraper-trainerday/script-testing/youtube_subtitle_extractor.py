#!/usr/bin/env python3
"""
YouTube Subtitle Extractor for @trainerday channel

This script:
1. Gets all videos from the @trainerday YouTube channel
2. Downloads available subtitles/transcripts for each video
3. Processes and cleans the subtitle text
4. Saves structured data for vectorization

Requirements:
pip install yt-dlp youtube-transcript-api
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
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
        """Get subtitles for a specific video."""
        try:
            # Create API instance and get transcript
            api = YouTubeTranscriptApi()
            transcript_list = api.list(video_id)
            
            # Try to get English transcript
            transcript_data = None
            transcript_type = "unknown"
            
            # Look for English transcript
            for transcript_info in transcript_list:
                if transcript_info['language_code'] == 'en':
                    transcript_data = api.fetch(video_id, transcript_info['name'])
                    transcript_type = "auto" if transcript_info.get('is_generated', True) else "manual"
                    break
            
            if not transcript_data:
                return None, "no_english_transcript"
            
            # Process transcript into readable text
            full_text = []
            segments = []
            
            for entry in transcript_data:
                text = entry['text'].strip()
                start = entry['start']
                duration = entry['duration']
                
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
                'type': transcript_type,
                'segment_count': len(segments)
            }, None
            
        except NoTranscriptFound:
            return None, "no_transcript_found"
        except TranscriptsDisabled:
            return None, "transcripts_disabled"
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
    
    def extract_all_subtitles(self, max_videos=None):
        """Extract subtitles from all channel videos."""
        print("🚀 Starting YouTube subtitle extraction")
        print("="*50)
        
        # Get all videos from channel
        videos = self.get_channel_videos()
        
        if not videos:
            print("❌ No videos found")
            return
        
        if max_videos:
            videos = videos[:max_videos]
            print(f"🎯 Processing first {max_videos} videos")
        
        # Process each video
        successful_extractions = []
        failed_extractions = []
        
        for i, video in enumerate(videos, 1):
            print(f"\n📹 [{i}/{len(videos)}] {video['title']}")
            print(f"   🔗 {video['url']}")
            
            # Get subtitles
            subtitle_data, error = self.get_video_subtitles(video['video_id'], video['title'])
            
            if subtitle_data:
                # Save processed data
                video_data = self.save_video_data(video, subtitle_data)
                if video_data:
                    successful_extractions.append(video_data)
                    print(f"   ✅ Extracted {subtitle_data['segment_count']} segments ({subtitle_data['type']} transcript)")
                    
                    # Show preview of content
                    preview = video_data['transcript']['full_text'][:100]
                    print(f"   📝 Preview: {preview}...")
            else:
                failed_extractions.append({
                    'video': video,
                    'error': error
                })
                print(f"   ❌ Failed: {error}")
            
            # Rate limiting - be nice to YouTube
            time.sleep(1)
        
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
    
    # Extract subtitles (set max_videos=10 for testing, remove for all videos)
    successful, failed = extractor.extract_all_subtitles(max_videos=10)  # Remove max_videos for all
    
    if successful:
        print(f"\n🎯 Next steps:")
        print(f"1. Review extracted content in: {OUTPUT_DIR}")
        print(f"2. Run content vectorization on the extracted text")
        print(f"3. Integrate with content strategy pipeline")

if __name__ == "__main__":
    main()