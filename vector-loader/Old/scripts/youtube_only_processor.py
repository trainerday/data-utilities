#!/usr/bin/env python3
"""
YouTube-Only Content Processor for TrainerDay Vector Database
Modified version that processes only YouTube content for testing
"""

import os
import sys
import time
from pathlib import Path

# Add parent directory to path to import the main processor
sys.path.append(str(Path(__file__).parent.parent))

from unified_content_processor import UnifiedContentProcessor

class YouTubeOnlyProcessor(UnifiedContentProcessor):
    """Modified processor that only handles YouTube content"""
    
    def process_youtube_only(self, youtube_dir: str = None):
        """Process only YouTube content"""
        print("🚀 Starting YouTube-only content processing...")
        start_time = time.time()
        
        all_chunks = []
        
        # Only extract YouTube Content (JSON files)
        print("\n🎥 Processing YouTube Content...")
        youtube_chunks = self.extract_youtube_content(youtube_dir or "source-data/youtube_content")
        all_chunks.extend(youtube_chunks)
        
        print(f"\n🔄 Processing {len(all_chunks)} YouTube content chunks...")
        
        # Store all chunks with embeddings
        processed_count = 0
        for i, chunk in enumerate(all_chunks, 1):
            print(f"[{i}/{len(all_chunks)}] Processing {chunk.source}: {chunk.title[:50]}...")
            
            if self.store_content_chunk(chunk):
                processed_count += 1
                print(f"  ✅ Stored successfully")
            else:
                print(f"  ❌ Failed to store")
            
            # Progress update every 5 items for YouTube
            if i % 5 == 0:
                elapsed = time.time() - start_time
                rate = i / elapsed if elapsed > 0 else 0
                print(f"\n📊 Progress: {i}/{len(all_chunks)} ({(i/len(all_chunks))*100:.1f}%) - {rate:.1f} items/sec")

        # Final statistics
        elapsed_time = time.time() - start_time
        print(f"\n🎯 YOUTUBE CONTENT PROCESSING COMPLETE")
        print(f"=" * 50)
        print(f"YouTube: {self.stats['youtube']['processed']} processed, {self.stats['youtube']['errors']} errors")
        print(f"Total embeddings created: {self.stats['total_embeddings']}")
        print(f"Time elapsed: {elapsed_time:.1f} seconds")
        
        if processed_count > 0:
            rate = processed_count / elapsed_time
            print(f"Processing rate: {rate:.2f} chunks/second")
            
            # Estimate OpenAI cost (text-embedding-3-large: $0.00013 per 1K tokens)
            estimated_cost = self.stats['total_embeddings'] * 0.00013
            print(f"Estimated OpenAI cost: ${estimated_cost:.4f}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="YouTube-only content processor for TrainerDay vector database")
    parser.add_argument("--youtube-dir", help="YouTube content directory (default: source-data/youtube_content)")
    parser.add_argument("--search", help="Test search query in youtube content")
    
    args = parser.parse_args()
    
    # Database configuration from environment
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('DB_SSLMODE', 'require')
    }
    
    # Validate configuration
    if not all([db_config['host'], db_config['database'], db_config['user'], db_config['password']]):
        print("❌ Database configuration incomplete. Please set environment variables:")
        print("   Required: DB_HOST, DB_DATABASE, DB_USERNAME, DB_PASSWORD")
        sys.exit(1)
        
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key required. Please set OPENAI_API_KEY environment variable.")
        sys.exit(1)

    try:
        processor = YouTubeOnlyProcessor(db_config=db_config)
        processor.connect_db()
        
        if args.search:
            # Test search functionality in YouTube content only
            processor.similarity_search(args.search, source_filter="youtube")
        else:
            # Process YouTube content only
            processor.process_youtube_only(youtube_dir=args.youtube_dir)
        
        print("✅ YouTube processing completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# USAGE EXAMPLES:
#
# Process YouTube content only:
# python youtube_only_processor.py
#
# Process with custom YouTube directory:
# python youtube_only_processor.py --youtube-dir /path/to/youtube
#
# Test search in YouTube content:
# python youtube_only_processor.py --search "how to use power zones"