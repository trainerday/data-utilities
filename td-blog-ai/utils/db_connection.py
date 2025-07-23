#!/usr/bin/env python3
"""
Database connection utility for TrainerDay vector database
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_db_config():
    """Get database configuration from environment variables"""
    return {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('DB_SSLMODE', 'require')
    }

def get_db_connection():
    """Create and return a database connection"""
    config = get_db_config()
    
    if not all([config['host'], config['database'], config['user'], config['password']]):
        raise ValueError("Database configuration incomplete. Check environment variables.")
    
    return psycopg2.connect(**config)

def test_connection():
    """Test database connection"""
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ Database connection successful!")
            print(f"PostgreSQL version: {version['version']}")
            
            # Test content_embeddings table
            cursor.execute("""
                SELECT 
                    source,
                    COUNT(*) as count
                FROM content_embeddings 
                GROUP BY source 
                ORDER BY source
            """)
            
            results = cursor.fetchall()
            print(f"\n📊 Content embeddings by source:")
            for row in results:
                print(f"  {row['source']:10}: {row['count']:4} embeddings")
                
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()