#!/usr/bin/env python3
"""
Blog-Only Content Processor for TrainerDay Vector Database
Processes blog articles from markdown files with frontmatter
"""

import os
import sys
import time
from pathlib import Path
import argparse

# Add parent directory to path to import the main processor
sys.path.append(str(Path(__file__).parent.parent))

from unified_content_processor import UnifiedContentProcessor

class BlogOnlyProcessor(UnifiedContentProcessor):
    """Modified processor that only handles blog content"""
    
    def process_blog_only(self, blog_dir: str = None):
        """Process only blog content"""
        print("🚀 Starting Blog-only content processing...")
        start_time = time.time()
        
        all_chunks = []
        
        # Only extract Blog Content (Markdown files)
        print("\n📝 Processing Blog Articles...")
        blog_chunks = self.extract_blog_content(blog_dir or "source-data/blog_articles")
        all_chunks.extend(blog_chunks)
        
        print(f"\n🔄 Processing {len(all_chunks)} blog content chunks...")
        
        # Store all chunks with embeddings
        processed_count = 0
        for i, chunk in enumerate(all_chunks, 1):
            print(f"[{i}/{len(all_chunks)}] Processing {chunk.source}: {chunk.title[:50]}...")
            
            if self.store_content_chunk(chunk):
                processed_count += 1
                print(f"  ✅ Stored successfully")
            else:
                print(f"  ❌ Failed to store")
            
            # Progress update every 5 items for blog
            if i % 5 == 0:
                elapsed = time.time() - start_time
                rate = i / elapsed if elapsed > 0 else 0
                print(f"\n📊 Progress: {i}/{len(all_chunks)} ({(i/len(all_chunks))*100:.1f}%) - {rate:.1f} items/sec")

        # Final statistics
        elapsed_time = time.time() - start_time
        print(f"\n🎯 BLOG CONTENT PROCESSING COMPLETE")
        print(f"=" * 50)
        print(f"Blog Articles: {self.stats['blog']['processed']} processed, {self.stats['blog']['errors']} errors")
        print(f"Total embeddings created: {self.stats['total_embeddings']}")
        print(f"Time elapsed: {elapsed_time:.1f} seconds")
        
        if processed_count > 0:
            rate = processed_count / elapsed_time
            print(f"Processing rate: {rate:.2f} chunks/second")
            
            # Estimate OpenAI cost (text-embedding-3-large: $0.00013 per 1K tokens)
            estimated_cost = self.stats['total_embeddings'] * 0.00013
            print(f"Estimated OpenAI cost: ${estimated_cost:.4f}")

def main():
    parser = argparse.ArgumentParser(description="Blog-only content processor for TrainerDay vector database")
    parser.add_argument("--blog-dir", help="Blog articles directory (default: source-data/blog_articles)")
    parser.add_argument("--search", help="Test search query in blog content")
    
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
        processor = BlogOnlyProcessor(db_config=db_config)
        processor.connect_db()
        
        if args.search:
            # Test search functionality in blog content only
            processor.similarity_search(args.search, source_filter="blog")
        else:
            # Process blog content only
            processor.process_blog_only(blog_dir=args.blog_dir)
        
        print("✅ Blog processing completed successfully!")
        
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
# Process blog content only:
# python scripts/blog_only_processor.py
#
# Process with custom blog directory:
# python scripts/blog_only_processor.py --blog-dir /path/to/blog
#
# Test search in blog content:
# python scripts/blog_only_processor.py --search "FTP testing methods"