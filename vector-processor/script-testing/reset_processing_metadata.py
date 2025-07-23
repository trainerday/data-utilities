#!/usr/bin/env python3
"""
Reset processing metadata for unprocessed YouTube videos
"""

import os
import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def reset_unprocessed_metadata():
    """Reset metadata for videos that weren't actually processed"""
    
    # Database configuration
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('DB_SSLMODE', 'require')
    }
    
    print("🔄 Resetting Processing Metadata for Unprocessed Videos")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(**db_config)
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            
            # Get list of actually processed video IDs
            cursor.execute("""
                SELECT DISTINCT source_id
                FROM content_embeddings
                WHERE source = 'youtube'
            """)
            
            processed_ids = {row['source_id'] for row in cursor.fetchall()}
            print(f"✅ Found {len(processed_ids)} processed videos in database")
            
            # Get all video files
            youtube_dir = Path("source-data/youtube_content")
            video_files = list(youtube_dir.glob("video_*.json"))
            
            source_ids = set()
            file_paths = {}
            for video_file in video_files:
                try:
                    with open(video_file, 'r') as f:
                        data = json.load(f)
                        video_id = data.get('video_id', video_file.stem.replace('video_', ''))
                        source_ids.add(video_id)
                        file_paths[video_id] = str(video_file)
                except Exception as e:
                    print(f"   ❌ Error reading {video_file.name}: {e}")
            
            print(f"📁 Found {len(source_ids)} source video files")
            
            # Find unprocessed videos
            unprocessed_ids = source_ids - processed_ids
            print(f"⚠️ Found {len(unprocessed_ids)} unprocessed videos")
            
            if unprocessed_ids:
                print(f"\n🗑️ Clearing metadata for unprocessed videos...")
                
                # Delete metadata entries for unprocessed videos
                deleted_count = 0
                for video_id in unprocessed_ids:
                    if video_id in file_paths:
                        file_path = file_paths[video_id]
                        cursor.execute("""
                            DELETE FROM content_processing_metadata
                            WHERE source = 'youtube' AND source_path = %s
                        """, (file_path,))
                        
                        if cursor.rowcount > 0:
                            deleted_count += 1
                            print(f"   - Cleared metadata for {video_id}")
                
                conn.commit()
                print(f"\n✅ Cleared metadata for {deleted_count} unprocessed videos")
                print(f"🔄 Ready to process {len(unprocessed_ids)} remaining videos!")
                
            else:
                print("✅ All videos appear to be processed correctly!")
                
            # Show summary
            cursor.execute("""
                SELECT COUNT(*) as remaining_metadata
                FROM content_processing_metadata
                WHERE source = 'youtube'
            """)
            
            remaining = cursor.fetchone()['remaining_metadata']
            print(f"\n📊 Processing metadata remaining: {remaining} entries")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    reset_unprocessed_metadata()