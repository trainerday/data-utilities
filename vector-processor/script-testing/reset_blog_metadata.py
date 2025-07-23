#!/usr/bin/env python3
"""
Reset processing metadata for blog articles due to serialization fix
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

def reset_blog_metadata():
    """Reset metadata for blog articles that had serialization errors"""
    
    # Database configuration
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('DB_SSLMODE', 'require')
    }
    
    print("🔄 Resetting Blog Processing Metadata")
    print("=" * 40)
    
    try:
        conn = psycopg2.connect(**db_config)
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            
            # Check current blog embeddings
            cursor.execute("""
                SELECT COUNT(*) as blog_count
                FROM content_embeddings
                WHERE source = 'blog'
            """)
            
            blog_count = cursor.fetchone()['blog_count']
            print(f"📊 Current blog embeddings in database: {blog_count}")
            
            # Check blog processing metadata
            cursor.execute("""
                SELECT COUNT(*) as metadata_count
                FROM content_processing_metadata
                WHERE source = 'blog'
            """)
            
            metadata_count = cursor.fetchone()['metadata_count']
            print(f"📊 Blog processing metadata entries: {metadata_count}")
            
            if metadata_count > 0:
                print(f"\n🗑️ Clearing all blog processing metadata due to serialization fix...")
                
                cursor.execute("""
                    DELETE FROM content_processing_metadata
                    WHERE source = 'blog'
                """)
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                print(f"✅ Cleared {deleted_count} blog metadata entries")
                print(f"🔄 Ready to reprocess all blog articles with fixed serialization!")
                
            else:
                print("✅ No blog metadata found - ready to process!")
                
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    reset_blog_metadata()