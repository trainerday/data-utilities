#!/usr/bin/env python3
"""
Clear Database Tables
Clears all forum analysis tables for fresh start.
"""

import os
from pathlib import Path
import psycopg2

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

def main():
    print("Database Cleanup - Clear All Forum Analysis Tables")
    print("=" * 55)
    
    # Database configuration
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('DB_SSLMODE', 'require')
    }
    
    if os.getenv('DB_SSLROOTCERT'):
        ssl_cert_filename = os.getenv('DB_SSLROOTCERT')
        ssl_cert_path = Path(__file__).parent.parent / ssl_cert_filename
        if ssl_cert_path.exists():
            db_config['sslrootcert'] = str(ssl_cert_path)
    
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        print("\nClearing database tables...")
        
        # Drop tables in reverse dependency order
        drop_sql = """
        DROP TABLE IF EXISTS forum_insights CASCADE;
        DROP TABLE IF EXISTS forum_voice_patterns CASCADE;  
        DROP TABLE IF EXISTS forum_qa_pairs CASCADE;
        DROP TABLE IF EXISTS forum_topics CASCADE;
        DROP TABLE IF EXISTS forum_topics_raw CASCADE;
        DROP TABLE IF EXISTS forum_topic_checksums CASCADE;
        """
        
        cursor.execute(drop_sql)
        conn.commit()
        
        print("✓ All forum analysis tables cleared")
        print("✓ Ready for fresh analysis with v2 system")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()