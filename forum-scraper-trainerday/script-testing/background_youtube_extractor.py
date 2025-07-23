#!/usr/bin/env python3
"""
Background YouTube extractor - runs slowly with very conservative rate limiting
to avoid blocking while extracting remaining videos.
"""

import sys
from youtube_subtitle_extractor_v2 import YouTubeSubtitleExtractor

def main():
    """Run background extraction with very conservative rate limiting."""
    print("🔄 Starting background YouTube extraction")
    print("   This will run very slowly to avoid rate limiting")
    print("   Stop with Ctrl+C if needed")
    print("="*60)
    
    extractor = YouTubeSubtitleExtractor("@trainerday")
    
    # Very conservative settings
    successful, failed = extractor.extract_all_subtitles(
        batch_size=2,             # Very small batches
        delay_between_batches=60  # 1 minute between batches
    )
    
    if successful:
        print(f"\n🎉 Background extraction complete!")
        print(f"   Successfully extracted: {len(successful)} videos")
        print(f"   Failed: {len(failed)} videos")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n⏹️  Background extraction stopped by user")
        print(f"   Progress has been saved - you can resume later")
        sys.exit(0)