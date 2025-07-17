#!/usr/bin/env python3
"""
Database connection test script for PostgreSQL data warehouse.
Tests connection and queries events table.
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

def test_database_connection():
    """Test connection to PostgreSQL database and query events data."""
    
    # Load environment variables from parent directory
    load_dotenv('../.env')
    
    # Database connection parameters
    db_params = {
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('DB_SSLMODE', 'require'),
        'sslrootcert': '../postgres.crt'  # Use the correct certificate filename
    }
    
    print("Testing database connection...")
    print(f"Host: {db_params['host']}")
    print(f"Port: {db_params['port']}")
    print(f"Database: {db_params['database']}")
    print(f"User: {db_params['user']}")
    print(f"SSL Mode: {db_params['sslmode']}")
    print("-" * 50)
    
    try:
        # Establish connection
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connection successful!")
        print(f"PostgreSQL version: {version[0]}")
        
        # Test current database info
        cursor.execute("SELECT current_database(), current_user;")
        db_info = cursor.fetchone()
        print(f"Current database: {db_info[0]}")
        print(f"Current user: {db_info[1]}")
        
        # List tables
        cursor.execute("""
            SELECT schemaname, tablename 
            FROM pg_tables 
            WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
            ORDER BY schemaname, tablename;
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"\nFound {len(tables)} tables:")
            for schema, table in tables:
                print(f"  {schema}.{table}")
        else:
            print("\nNo user tables found.")
        
        # Check if events table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'events'
            );
        """)
        events_exists = cursor.fetchone()[0]
        
        if events_exists:
            print(f"\n✅ Events table found!")
            
            # Get events table structure
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'events'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            
            print(f"\nEvents table structure:")
            for col_name, data_type, nullable, default in columns:
                print(f"  {col_name}: {data_type} (nullable: {nullable}, default: {default})")
            
            # Count total events
            cursor.execute("SELECT COUNT(*) FROM events;")
            total_events = cursor.fetchone()[0]
            print(f"\nTotal events in table: {total_events}")
            
            # Get date range
            cursor.execute("SELECT MIN(created_at), MAX(created_at) FROM events;")
            date_range = cursor.fetchone()
            if date_range[0] and date_range[1]:
                print(f"Date range: {date_range[0]} to {date_range[1]}")
            
            # Get some sample events
            cursor.execute("""
                SELECT id, user_id, name, value, json_data, created_at
                FROM events
                ORDER BY created_at DESC
                LIMIT 10;
            """)
            sample_events = cursor.fetchall()
            
            print(f"\nSample events (latest 10):")
            for event in sample_events:
                id, user_id, name, value, json_data, created_at = event
                print(f"  ID: {id}, User: {user_id}, Name: {name}, Value: {value}, Date: {created_at}")
                if json_data:
                    print(f"    JSON: {json_data}")
        else:
            print(f"\n❌ Events table not found!")
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("\n✅ Database test completed successfully!")
        
    except psycopg2.Error as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_database_connection()