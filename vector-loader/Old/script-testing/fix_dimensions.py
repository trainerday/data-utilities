#!/usr/bin/env python3
"""
Fix the embedding dimensions issue by updating the database table
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

def fix_embedding_dimensions():
    """Fix the vector dimensions in the database"""
    
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
            
            print("🔧 Fixing Embedding Dimensions Issue")
            print("=" * 45)
            
            # Check current table structure
            cursor.execute("""
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns
                WHERE table_name = 'content_embeddings'
                ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            print("Current table structure:")
            for col in columns:
                print(f"  {col['column_name']}: {col['data_type']}")
            
            # Check current record count
            cursor.execute("SELECT COUNT(*) as count FROM content_embeddings")
            count = cursor.fetchone()['count']
            print(f"\nCurrent records: {count}")
            
            if count > 0:
                print(f"\n⚠️ WARNING: This will delete {count} existing embeddings and recreate table!")
                print("Proceeding automatically to fix dimensions issue...")
            
            print("\n🗑️ Dropping and recreating table with correct dimensions...")
            
            # Drop the existing table
            cursor.execute("DROP TABLE IF EXISTS content_embeddings CASCADE")
            
            # Recreate table with correct dimensions (1536 for text-embedding-3-large with dimensions param)
            cursor.execute("""
                CREATE TABLE content_embeddings (
                    id SERIAL PRIMARY KEY,
                    source VARCHAR(20) NOT NULL,        -- 'forum', 'blog', 'youtube', 'project_feature_map'
                    source_id VARCHAR(100) NOT NULL,    -- topic_id, article_filename, video_id
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,              -- The actual text content for retrieval
                    embedding vector(1536) NOT NULL,    -- 1536 dimensions for compatibility with HNSW index
                    metadata JSONB,                     -- source-specific fields
                    chunk_index INTEGER DEFAULT 0,     -- for multi-chunk content
                    created_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(source, source_id, chunk_index)
                );
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX content_embeddings_source_idx ON content_embeddings(source);
                CREATE INDEX content_embeddings_embedding_idx ON content_embeddings USING hnsw (embedding vector_cosine_ops);
            """)
            
            # Clean up processing metadata
            cursor.execute("DELETE FROM content_processing_metadata WHERE source = 'youtube'")
            
            conn.commit()
            
            print("✅ Table recreated successfully with 1536 dimensions")
            print("✅ All indexes created")
            print("✅ Processing metadata cleared")
            print("\n🔄 Ready to re-process YouTube content with correct dimensions!")
                
    except Exception as e:
        print(f"❌ Database error: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    fix_embedding_dimensions()