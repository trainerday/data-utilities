#!/usr/bin/env python3
"""
Migration script to add optimization columns to existing forum_topics_raw table
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def migrate_table():
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
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        print("🔧 Adding optimization columns to forum_topics_raw table...")
        
        # Add new columns for optimization
        migration_sql = """
        -- Add optimization columns if they don't exist
        ALTER TABLE forum_topics_raw 
        ADD COLUMN IF NOT EXISTS last_post_id INTEGER;
        
        ALTER TABLE forum_topics_raw 
        ADD COLUMN IF NOT EXISTS last_posted_at TIMESTAMP;
        
        ALTER TABLE forum_topics_raw 
        ADD COLUMN IF NOT EXISTS highest_post_number INTEGER;
        
        -- Create indexes for the new columns
        CREATE INDEX IF NOT EXISTS idx_forum_topics_raw_last_post 
        ON forum_topics_raw(last_post_id);
        """
        
        cursor.execute(migration_sql)
        conn.commit()
        
        print("✅ Migration completed successfully!")
        
        # Now populate the new columns with data from existing raw_content
        print("📊 Populating optimization columns from existing data...")
        
        cursor.execute("""
            UPDATE forum_topics_raw 
            SET 
                last_post_id = (
                    SELECT MAX((post_data->>'id')::int) 
                    FROM jsonb_array_elements(raw_content->'posts') AS post_data
                ),
                last_posted_at = (raw_content->'topic'->>'last_posted_at')::timestamp,
                highest_post_number = (raw_content->'topic'->>'highest_post_number')::int
            WHERE last_post_id IS NULL
        """)
        
        updated_rows = cursor.rowcount
        conn.commit()
        
        print(f"✅ Updated {updated_rows} rows with optimization data!")
        
        # Show some stats
        cursor.execute("SELECT COUNT(*) FROM forum_topics_raw WHERE last_post_id IS NOT NULL")
        optimized_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM forum_topics_raw")
        total_count = cursor.fetchone()[0]
        
        print(f"📊 Table stats:")
        print(f"   Total topics: {total_count}")
        print(f"   Optimized topics: {optimized_count}")
        print(f"   Optimization ready: {(optimized_count/total_count*100):.1f}%")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        raise

if __name__ == "__main__":
    migrate_table()