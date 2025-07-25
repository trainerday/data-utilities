#!/usr/bin/env python3
"""
Debug facts table issue - check what tables exist and where facts might be
"""

import os
import sys
import sqlalchemy
from dotenv import load_dotenv

load_dotenv()

def debug_facts_tables():
    """Check what tables exist and search for facts"""
    
    # Local PostgreSQL configuration
    local_db_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'trainerday_local',
        'user': os.getenv('USER', 'alex'),
        'password': '',
    }
    
    try:
        connection_string = f"postgresql://{local_db_config['user']}@{local_db_config['host']}:{local_db_config['port']}/{local_db_config['database']}"
        engine = sqlalchemy.create_engine(connection_string)
        
        with engine.connect() as conn:
            # List all tables
            result = conn.execute(sqlalchemy.text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            ))
            tables = [row[0] for row in result.fetchall()]
            
            print("📊 ALL TABLES IN DATABASE:")
            print("=" * 40)
            for table in sorted(tables):
                print(f"  • {table}")
            print()
            
            # Check for any llamaindex related tables
            print("🔍 LLAMAINDEX TABLES:")
            print("=" * 40)
            for table in tables:
                if 'llamaindex' in table.lower() or 'data_' in table.lower():
                    # Get row count
                    try:
                        result = conn.execute(sqlalchemy.text(f"SELECT COUNT(*) FROM {table}"))
                        count = result.fetchone()[0]
                        print(f"  • {table}: {count:,} rows")
                        
                        # Check if it has facts
                        if count > 0:
                            result = conn.execute(sqlalchemy.text(f"SELECT metadata_->>'source' as source, COUNT(*) as count FROM {table} WHERE metadata_->>'source' IS NOT NULL GROUP BY metadata_->>'source'"))
                            sources = result.fetchall()
                            if sources:
                                print(f"    Sources: {dict(sources)}")
                    except Exception as e:
                        print(f"    Error checking {table}: {e}")
            print()
            
            # Check if there are any rows with source='facts'
            print("🔍 SEARCHING FOR FACTS IN ALL TABLES:")
            print("=" * 40)
            for table in tables:
                if 'llamaindex' in table.lower() or 'data_' in table.lower():
                    try:
                        result = conn.execute(sqlalchemy.text(f"SELECT COUNT(*) FROM {table} WHERE metadata_->>'source' = 'facts'"))
                        count = result.fetchone()[0]
                        if count > 0:
                            print(f"  • {table}: {count} facts found!")
                    except:
                        pass
                        
    except Exception as e:
        print(f"Error debugging tables: {e}")

if __name__ == "__main__":
    debug_facts_tables()