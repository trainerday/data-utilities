#!/usr/bin/env python3
"""
Check if all YouTube data has been processed
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

def check_completion_status():
    """Check completion status of YouTube processing"""
    
    # Database configuration
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('DB_SSLMODE', 'require')
    }
    
    print("📊 YouTube Processing Completion Status")
    print("=" * 50)
    
    # Check source files
    youtube_dir = Path("source-data/youtube_content")
    video_files = list(youtube_dir.glob("video_*.json"))
    extraction_files = list(youtube_dir.glob("extraction_summary_*.json"))
    
    total_source_files = len(video_files)
    print(f"📁 Source Files Available: {total_source_files} video files")
    print(f"📁 Extraction Summary Files: {len(extraction_files)} files")
    
    # Check database
    try:
        conn = psycopg2.connect(**db_config)
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            
            # Get unique videos in database
            cursor.execute("""
                SELECT COUNT(DISTINCT source_id) as unique_videos,
                       COUNT(*) as total_chunks
                FROM content_embeddings
                WHERE source = 'youtube'
            """)
            
            db_stats = cursor.fetchone()
            processed_videos = db_stats['unique_videos']
            total_chunks = db_stats['total_chunks']
            
            print(f"💾 Database Status:")
            print(f"   - Processed Videos: {processed_videos}/{total_source_files}")
            print(f"   - Total Chunks: {total_chunks}")
            print(f"   - Average Chunks per Video: {total_chunks/processed_videos if processed_videos > 0 else 0:.1f}")
            
            # Check completion percentage
            completion_percent = (processed_videos / total_source_files) * 100 if total_source_files > 0 else 0
            print(f"   - Completion: {completion_percent:.1f}%")
            
            if completion_percent == 100:
                print("   ✅ ALL YouTube videos processed!")
            else:
                missing_count = total_source_files - processed_videos
                print(f"   ⚠️ {missing_count} videos still need processing")
            
            # Get list of processed video IDs
            cursor.execute("""
                SELECT DISTINCT source_id
                FROM content_embeddings
                WHERE source = 'youtube'
                ORDER BY source_id
            """)
            
            processed_ids = {row['source_id'] for row in cursor.fetchall()}
            
            # Check which files are missing
            source_ids = set()
            for video_file in video_files:
                try:
                    with open(video_file, 'r') as f:
                        data = json.load(f)
                        source_ids.add(data.get('video_id', video_file.stem))
                except Exception as e:
                    print(f"   ❌ Error reading {video_file.name}: {e}")
            
            missing_ids = source_ids - processed_ids
            
            if missing_ids:
                print(f"\n📝 Missing Videos ({len(missing_ids)}):")
                for video_id in sorted(missing_ids):
                    print(f"   - {video_id}")
                    
                # Check if there are corresponding files
                print(f"\n🔍 Checking Missing Files:")
                for video_id in sorted(missing_ids):
                    video_file = youtube_dir / f"video_{video_id}.json"
                    if video_file.exists():
                        print(f"   ✅ {video_file.name} exists but not processed")
                    else:
                        print(f"   ❌ {video_file.name} file missing")
            
            # Check processing metadata
            cursor.execute("""
                SELECT COUNT(*) as processed_files
                FROM content_processing_metadata
                WHERE source = 'youtube'
            """)
            
            metadata_count = cursor.fetchone()['processed_files']
            print(f"\n🔄 Processing Metadata: {metadata_count} files tracked")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    check_completion_status()