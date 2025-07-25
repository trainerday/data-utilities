#!/usr/bin/env python3
"""
Check the status of blog content processing
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def check_blog_status():
    """Check the current status of blog processing"""
    
    # Database configuration
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('DB_SSLMODE', 'require')
    }
    
    try:
        # Connect to database
        conn = psycopg2.connect(**db_config)
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            
            # Check blog content specifically
            print(f"📝 Blog Content Status")
            print("=" * 30)
            
            cursor.execute("""
                SELECT COUNT(DISTINCT source_id) as unique_articles,
                       COUNT(*) as total_chunks,
                       AVG(LENGTH(content)) as avg_content_length
                FROM content_embeddings
                WHERE source = 'blog'
            """)
            
            blog_stats = cursor.fetchone()
            if blog_stats and blog_stats['total_chunks'] > 0:
                print(f"Unique Articles: {blog_stats['unique_articles']}")
                print(f"Total Chunks: {blog_stats['total_chunks']}")
                print(f"Avg Content Length: {blog_stats['avg_content_length']:.0f} chars")
                print(f"Avg Chunks per Article: {blog_stats['total_chunks']/blog_stats['unique_articles']:.1f}")
                
                # Get sample of recent blog entries
                cursor.execute("""
                    SELECT title, LEFT(content, 100) as content_preview, 
                           metadata->>'category' as category,
                           metadata->>'date' as date,
                           created_at
                    FROM content_embeddings
                    WHERE source = 'blog'
                    ORDER BY created_at DESC
                    LIMIT 8
                """)
                
                recent_entries = cursor.fetchall()
                print(f"\n📚 Recent Blog Entries:")
                for i, entry in enumerate(recent_entries, 1):
                    print(f"{i}. {entry['title']}")
                    print(f"   Category: {entry['category']} | Date: {entry['date']}")
                    print(f"   Content: {entry['content_preview']}...")
                    print()
                    
                # Get category breakdown
                cursor.execute("""
                    SELECT metadata->>'category' as category, COUNT(*) as count
                    FROM content_embeddings
                    WHERE source = 'blog'
                    GROUP BY metadata->>'category'
                    ORDER BY count DESC
                """)
                
                categories = cursor.fetchall()
                print(f"📊 Content by Category:")
                for cat in categories:
                    print(f"   {cat['category']}: {cat['count']} chunks")
                    
            else:
                print("No blog content found yet.")
            
            # Check for errors (long source_ids)
            cursor.execute("""
                SELECT source_id, LENGTH(source_id) as id_length
                FROM content_embeddings
                WHERE source = 'blog' AND LENGTH(source_id) > 90
                ORDER BY id_length DESC
                LIMIT 5
            """)
            
            long_ids = cursor.fetchall()
            if long_ids:
                print(f"\n⚠️ Articles with Long IDs (potential issues):")
                for item in long_ids:
                    print(f"   {item['source_id'][:80]}... ({item['id_length']} chars)")
                    
            # Source files vs database
            blog_dir = Path("source-data/blog_articles")
            if blog_dir.exists():
                md_files = list(blog_dir.glob("*.md"))
                print(f"\n📁 Source Files: {len(md_files)} markdown files")
                print(f"📊 Processing Rate: {blog_stats['unique_articles']}/{len(md_files)} articles processed")
                completion = (blog_stats['unique_articles'] / len(md_files)) * 100 if len(md_files) > 0 else 0
                print(f"📈 Completion: {completion:.1f}%")
                
    except Exception as e:
        print(f"❌ Database error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_blog_status()