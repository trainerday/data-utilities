#!/usr/bin/env python3
"""
Check the current status of the YouTube embedding process in the database
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

def check_database_status():
    """Check the current status of content processing"""
    
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
            
            # Check total embeddings by source
            print("📊 Current Database Status")
            print("=" * 50)
            
            cursor.execute("""
                SELECT source, COUNT(*) as count
                FROM content_embeddings
                GROUP BY source
                ORDER BY count DESC
            """)
            
            results = cursor.fetchall()
            total_embeddings = sum(row['count'] for row in results)
            
            if results:
                for row in results:
                    print(f"{row['source'].upper()}: {row['count']} embeddings")
                print(f"TOTAL: {total_embeddings} embeddings")
            else:
                print("No embeddings found in database yet.")
            
            # Check YouTube content specifically
            print(f"\n🎥 YouTube Content Details")
            print("=" * 30)
            
            cursor.execute("""
                SELECT COUNT(DISTINCT source_id) as unique_videos,
                       COUNT(*) as total_chunks
                FROM content_embeddings
                WHERE source = 'youtube'
            """)
            
            youtube_stats = cursor.fetchone()
            if youtube_stats and youtube_stats['total_chunks'] > 0:
                print(f"Unique Videos: {youtube_stats['unique_videos']}")
                print(f"Total Chunks: {youtube_stats['total_chunks']}")
                
                # Get sample of recent YouTube entries
                cursor.execute("""
                    SELECT title, LEFT(content, 100) as content_preview, created_at
                    FROM content_embeddings
                    WHERE source = 'youtube'
                    ORDER BY created_at DESC
                    LIMIT 5
                """)
                
                recent_entries = cursor.fetchall()
                print(f"\n📝 Recent YouTube Entries:")
                for i, entry in enumerate(recent_entries, 1):
                    print(f"{i}. {entry['title']}")
                    print(f"   Content: {entry['content_preview']}...")
                    print(f"   Created: {entry['created_at']}")
                    print()
            else:
                print("No YouTube content found yet.")
            
            # Check processing metadata
            print(f"\n🔄 Processing Metadata")
            print("=" * 25)
            
            cursor.execute("""
                SELECT source, source_path, updated_at
                FROM content_processing_metadata
                WHERE source = 'youtube'
                ORDER BY updated_at DESC
                LIMIT 10
            """)
            
            metadata_entries = cursor.fetchall()
            if metadata_entries:
                print(f"Recently processed files:")
                for entry in metadata_entries:
                    filename = entry['source_path'].split('/')[-1] if entry['source_path'] else 'Unknown'
                    print(f"- {filename} (Updated: {entry['updated_at']})")
            else:
                print("No processing metadata found yet.")
                
    except Exception as e:
        print(f"❌ Database error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_database_status()