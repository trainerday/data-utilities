#!/usr/bin/env python3
"""
Search for YouTube transcript data in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_connection import get_db_connection
from psycopg2.extras import RealDictCursor

def search_youtube_content():
    """Search YouTube content in the database"""
    print("🔍 Searching YouTube content in database")
    print("="*50)
    
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            
            # Get all YouTube entries
            cursor.execute("""
                SELECT 
                    id,
                    content_id,
                    title,
                    LENGTH(content) as content_length,
                    metadata
                FROM content_embeddings 
                WHERE source = 'youtube'
                ORDER BY content_length DESC
                LIMIT 10
            """)
            
            youtube_entries = cursor.fetchall()
            
            print(f"📹 Found {len(youtube_entries)} YouTube entries (showing top 10 by content length):")
            print()
            
            for i, entry in enumerate(youtube_entries, 1):
                print(f"{i:2d}. ID: {entry['id']}")
                print(f"    Content ID: {entry['content_id']}")
                print(f"    Title: {entry['title']}")
                print(f"    Content Length: {entry['content_length']:,} characters")
                
                # Try to parse metadata
                metadata = entry['metadata']
                if metadata:
                    print(f"    Metadata keys: {list(metadata.keys()) if isinstance(metadata, dict) else 'N/A'}")
                
                print()
            
            # Get a sample of the actual content
            if youtube_entries:
                cursor.execute("""
                    SELECT content, metadata
                    FROM content_embeddings 
                    WHERE source = 'youtube'
                    ORDER BY LENGTH(content) DESC
                    LIMIT 1
                """)
                
                sample = cursor.fetchone()
                if sample:
                    content = sample['content']
                    metadata = sample['metadata']
                    
                    print("📝 Sample content from longest YouTube entry:")
                    print(f"   First 500 characters: {content[:500]}...")
                    print()
                    print(f"📋 Sample metadata:")
                    if isinstance(metadata, dict):
                        for key, value in metadata.items():
                            if isinstance(value, str) and len(value) > 100:
                                print(f"   {key}: {str(value)[:100]}...")
                            else:
                                print(f"   {key}: {value}")
                    else:
                        print(f"   {metadata}")
            
            # Get total stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_count,
                    SUM(LENGTH(content)) as total_characters,
                    AVG(LENGTH(content)) as avg_characters
                FROM content_embeddings 
                WHERE source = 'youtube'
            """)
            
            stats = cursor.fetchone()
            print(f"\n📊 YouTube Content Statistics:")
            print(f"   Total entries: {stats['total_count']}")
            print(f"   Total characters: {stats['total_characters']:,}")
            print(f"   Average characters per entry: {int(stats['avg_characters']):,}")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error searching YouTube content: {e}")
        return False
    
    return True

if __name__ == "__main__":
    search_youtube_content()