#!/usr/bin/env python3
"""
Complete missing blog articles only - identifies and processes only missing ones
"""

import os
import sys
import time
from pathlib import Path
import argparse

# Add parent directory to path to import the main processor
sys.path.append(str(Path(__file__).parent.parent))

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from unified_content_processor import UnifiedContentProcessor

load_dotenv()

class BlogMissingProcessor(UnifiedContentProcessor):
    """Process only missing blog articles"""
    
    def get_processed_blog_articles(self):
        """Get list of blog articles already in database"""
        processed_articles = set()
        
        with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT DISTINCT source_id 
                FROM content_embeddings 
                WHERE source = 'blog'
            """)
            
            results = cursor.fetchall()
            for row in results:
                processed_articles.add(row['source_id'])
                
        return processed_articles
    
    def find_missing_articles(self, blog_dir: str = None):
        """Find articles that haven't been processed yet"""
        blog_path = Path(blog_dir or "source-data/blog_articles")
        
        if not blog_path.exists():
            print(f"⚠️ Blog directory not found: {blog_path}")
            return []
            
        # Get all markdown files
        all_md_files = list(blog_path.glob("*.md"))
        print(f"✓ Found {len(all_md_files)} total blog articles")
        
        # Get processed articles from database
        processed_articles = self.get_processed_blog_articles()
        print(f"✓ Found {len(processed_articles)} already processed articles")
        
        # Find missing ones
        missing_files = []
        for md_file in all_md_files:
            # Check both full filename and truncated version (due to 95 char limit)
            source_id = md_file.stem[:95] if len(md_file.stem) > 95 else md_file.stem
            
            if source_id not in processed_articles:
                missing_files.append(md_file)
        
        print(f"✓ Found {len(missing_files)} missing articles to process")
        
        # Show what's missing
        if missing_files:
            print("\n📝 Missing articles:")
            for i, f in enumerate(missing_files[:10], 1):  # Show first 10
                print(f"  {i}. {f.name}")
            if len(missing_files) > 10:
                print(f"  ... and {len(missing_files) - 10} more")
        
        return missing_files
    
    def process_missing_only(self, blog_dir: str = None):
        """Process only missing blog articles"""
        print("🚀 Starting Missing Blog Articles Processing...")
        start_time = time.time()
        
        # Find missing articles
        missing_files = self.find_missing_articles(blog_dir or "source-data/blog_articles")
        
        if not missing_files:
            print("✅ No missing articles found - all blog content is up to date!")
            return
        
        print(f"\n🔄 Processing {len(missing_files)} missing articles...")
        
        # Process each missing file
        total_chunks = 0
        processed_count = 0
        
        for i, md_file in enumerate(missing_files, 1):
            print(f"\n[{i}/{len(missing_files)}] Processing: {md_file.name}")
            
            try:
                # Process this specific file using the parent class method but override the file list
                chunks = self.process_single_blog_file(md_file)
                
                for chunk in chunks:
                    if self.store_content_chunk(chunk):
                        processed_count += 1
                        print(f"  ✅ Stored chunk: {chunk.title[:50]}...")
                    else:
                        print(f"  ❌ Failed to store chunk")
                
                total_chunks += len(chunks)
                
                # Mark file as processed
                self.update_processing_metadata('blog', source_path=str(md_file), 
                                              file_hash=self.get_file_hash(md_file))
                
                print(f"  📊 Article complete: {len(chunks)} chunks created")
                
            except Exception as e:
                print(f"  ❌ Error processing {md_file.name}: {e}")
                self.stats['blog']['errors'] += 1
                continue

        # Final statistics
        elapsed_time = time.time() - start_time
        print(f"\n🎯 MISSING BLOG PROCESSING COMPLETE")
        print(f"=" * 50)
        print(f"Missing Articles: {len(missing_files)} processed")
        print(f"Total chunks created: {total_chunks}")
        print(f"Total embeddings stored: {processed_count}")
        print(f"Time elapsed: {elapsed_time:.1f} seconds")
        
        if processed_count > 0:
            rate = processed_count / elapsed_time
            print(f"Processing rate: {rate:.2f} chunks/second")
            
            # Estimate OpenAI cost
            estimated_cost = processed_count * 0.00013
            print(f"Estimated OpenAI cost: ${estimated_cost:.4f}")
    
    def process_single_blog_file(self, md_file: Path):
        """Process a single blog markdown file"""
        import frontmatter
        
        chunks = []
        
        try:
            # Parse frontmatter and content
            with open(md_file, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            title = post.metadata.get('title', md_file.stem)
            content = post.content
            
            if not content.strip():
                return chunks
            
            # Chunk by sections (headers)
            blog_chunks = self.chunk_blog_content(content, post.metadata)
            
            for i, chunk_content in enumerate(blog_chunks):
                # Truncate source_id to fit database constraint (100 chars)
                source_id = md_file.stem[:95] if len(md_file.stem) > 95 else md_file.stem
                
                from unified_content_processor import ContentChunk
                chunk = ContentChunk(
                    source='blog',
                    source_id=source_id,
                    title=f"{title} (Section {i+1})" if len(blog_chunks) > 1 else title,
                    content=chunk_content,
                    metadata={
                        'article_title': title,
                        'filename': md_file.name,
                        'category': post.metadata.get('category', 'general'),
                        'tags': post.metadata.get('tags', []),
                        'engagement': post.metadata.get('engagement', 'unknown'),
                        'date': str(post.metadata.get('date', '')),
                        'description': post.metadata.get('description', ''),
                        'section_index': i
                    },
                    chunk_index=i
                )
                chunks.append(chunk)
            
        except Exception as e:
            print(f"❌ Error processing blog file {md_file}: {e}")
            raise
        
        return chunks

def main():
    parser = argparse.ArgumentParser(description="Complete missing blog articles only")
    parser.add_argument("--blog-dir", help="Blog articles directory (default: source-data/blog_articles)")
    parser.add_argument("--dry-run", action="store_true", help="Only show what would be processed")
    
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
        
    if not args.dry_run and not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key required. Please set OPENAI_API_KEY environment variable.")
        sys.exit(1)

    try:
        processor = BlogMissingProcessor(db_config=db_config)
        processor.connect_db()
        
        if args.dry_run:
            # Just show what would be processed
            processor.find_missing_articles(blog_dir=args.blog_dir)
        else:
            # Process missing articles
            processor.process_missing_only(blog_dir=args.blog_dir)
        
        print("✅ Missing blog analysis/processing completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()