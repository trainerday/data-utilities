#!/usr/bin/env python3
"""
Query events data from PostgreSQL data warehouse.
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

def query_events_data():
    """Query and analyze events data."""
    
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
        'sslrootcert': '../postgres.crt'
    }
    
    try:
        # Establish connection
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        print("🔍 Querying events data...")
        print("=" * 50)
        
        # Get basic stats
        cursor.execute("SELECT COUNT(*) FROM events;")
        total_events = cursor.fetchone()[0]
        print(f"Total events: {total_events:,}")
        
        # Get date range
        cursor.execute("SELECT MIN(created_at), MAX(created_at) FROM events;")
        date_range = cursor.fetchone()
        if date_range[0] and date_range[1]:
            print(f"Date range: {date_range[0]} to {date_range[1]}")
        
        # Get unique event names
        cursor.execute("SELECT name, COUNT(*) FROM events GROUP BY name ORDER BY COUNT(*) DESC LIMIT 20;")
        event_names = cursor.fetchall()
        print(f"\nTop 20 event names by frequency:")
        for name, count in event_names:
            print(f"  {name}: {count:,}")
        
        # Get some sample events
        cursor.execute("""
            SELECT user_id, name, value, json_data, created_at
            FROM events
            ORDER BY created_at DESC
            LIMIT 10;
        """)
        sample_events = cursor.fetchall()
        
        print(f"\nSample events (latest 10):")
        for event in sample_events:
            user_id, name, value, json_data, created_at = event
            print(f"  User: {user_id}, Name: {name}, Value: {value}, Date: {created_at}")
            if json_data:
                print(f"    JSON: {json_data}")
        
        # Look for subscription-related events
        print(f"\n🔍 Searching for subscription-related events...")
        cursor.execute("""
            SELECT COUNT(*) FROM events 
            WHERE (
                name ILIKE '%subscription%' 
                OR name ILIKE '%subscribe%'
                OR value ILIKE '%subscription%'
                OR value ILIKE '%subscribe%'
                OR json_data::text ILIKE '%subscription%'
                OR json_data::text ILIKE '%subscribe%'
            );
        """)
        
        subscription_count = cursor.fetchone()[0]
        print(f"Total subscription-related events: {subscription_count:,}")
        
        if subscription_count > 0:
            cursor.execute("""
                SELECT name, value, json_data, created_at 
                FROM events 
                WHERE (
                    name ILIKE '%subscription%' 
                    OR name ILIKE '%subscribe%'
                    OR value ILIKE '%subscription%'
                    OR value ILIKE '%subscribe%'
                    OR json_data::text ILIKE '%subscription%'
                    OR json_data::text ILIKE '%subscribe%'
                )
                ORDER BY created_at DESC
                LIMIT 10;
            """)
            
            subscription_events = cursor.fetchall()
            print(f"\nLatest subscription events:")
            for name, value, json_data, created_at in subscription_events:
                print(f"  {created_at}: {name} - {value}")
                if json_data:
                    print(f"    JSON: {json_data}")
        
        # Look for payment-related events
        print(f"\n🔍 Searching for payment-related events...")
        cursor.execute("""
            SELECT COUNT(*) FROM events 
            WHERE (
                name ILIKE '%payment%' 
                OR name ILIKE '%pay%'
                OR value ILIKE '%payment%'
                OR value ILIKE '%pay%'
                OR json_data::text ILIKE '%payment%'
                OR json_data::text ILIKE '%pay%'
            );
        """)
        
        payment_count = cursor.fetchone()[0]
        print(f"Total payment-related events: {payment_count:,}")
        
        if payment_count > 0:
            cursor.execute("""
                SELECT name, value, json_data, created_at 
                FROM events 
                WHERE (
                    name ILIKE '%payment%' 
                    OR name ILIKE '%pay%'
                    OR value ILIKE '%payment%'
                    OR value ILIKE '%pay%'
                    OR json_data::text ILIKE '%payment%'
                    OR json_data::text ILIKE '%pay%'
                )
                ORDER BY created_at DESC
                LIMIT 10;
            """)
            
            payment_events = cursor.fetchall()
            print(f"\nLatest payment events:")
            for name, value, json_data, created_at in payment_events:
                print(f"  {created_at}: {name} - {value}")
                if json_data:
                    print(f"    JSON: {json_data}")
        
        # Get recent events from the last 7 days
        print(f"\n🔍 Events from the last 7 days...")
        cursor.execute("""
            SELECT COUNT(*) FROM events 
            WHERE created_at >= NOW() - INTERVAL '7 days';
        """)
        
        recent_count = cursor.fetchone()[0]
        print(f"Events in last 7 days: {recent_count:,}")
        
        if recent_count > 0:
            cursor.execute("""
                SELECT name, COUNT(*) FROM events 
                WHERE created_at >= NOW() - INTERVAL '7 days'
                GROUP BY name 
                ORDER BY COUNT(*) DESC 
                LIMIT 10;
            """)
            
            recent_events = cursor.fetchall()
            print(f"\nTop event types in last 7 days:")
            for name, count in recent_events:
                print(f"  {name}: {count:,}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("\n✅ Events data query completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    query_events_data()