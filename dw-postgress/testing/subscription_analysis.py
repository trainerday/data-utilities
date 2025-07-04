#!/usr/bin/env python3
"""
Analyze subscription events from the last month.
"""

import os
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv

def analyze_subscriptions():
    """Analyze subscription events from the last month."""
    
    # Load environment variables
    load_dotenv()
    
    # Database connection parameters
    db_params = {
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('DB_SSLMODE', 'require'),
        'sslrootcert': 'ca-certificate.crt'
    }
    
    try:
        # Establish connection
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        # First, examine the events table structure
        print("📊 Examining events table structure...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'events' AND table_schema = 'public'
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        
        print("Events table columns:")
        for col_name, data_type, nullable in columns:
            print(f"  {col_name}: {data_type} ({'nullable' if nullable == 'YES' else 'not null'})")
        
        # Get sample data to understand the structure
        print("\n📋 Sample events data:")
        cursor.execute("SELECT * FROM events LIMIT 5;")
        sample_data = cursor.fetchall()
        
        if sample_data:
            col_names = [desc[0] for desc in cursor.description]
            print(f"Columns: {', '.join(col_names)}")
            for i, row in enumerate(sample_data, 1):
                print(f"Row {i}: {row}")
        
        # Look for subscription-related events in the last month
        one_month_ago = datetime.now() - timedelta(days=30)
        
        print(f"\n🔍 Looking for subscription events since {one_month_ago.strftime('%Y-%m-%d')}...")
        
        # Check if there's a timestamp/date column
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'events' 
            AND table_schema = 'public' 
            AND (data_type LIKE '%timestamp%' OR data_type LIKE '%date%' OR column_name ILIKE '%time%' OR column_name ILIKE '%date%' OR column_name ILIKE '%created%')
            ORDER BY ordinal_position;
        """)
        date_columns = cursor.fetchall()
        
        if date_columns:
            print(f"Found date/time columns: {[col[0] for col in date_columns]}")
            date_col = date_columns[0][0]  # Use the first date column
            
            # Query for subscription events
            cursor.execute(f"""
                SELECT * FROM events 
                WHERE {date_col} >= %s 
                AND (
                    json_data::text ILIKE '%subscription%' 
                    OR json_data::text ILIKE '%subscribe%'
                    OR name ILIKE '%subscription%'
                    OR name ILIKE '%subscribe%'
                    OR value ILIKE '%subscription%'
                    OR value ILIKE '%subscribe%'
                )
                ORDER BY {date_col} DESC;
            """, (one_month_ago,))
            
            subscription_events = cursor.fetchall()
            
            if subscription_events:
                print(f"\n✅ Found {len(subscription_events)} subscription-related events in the last month:")
                col_names = [desc[0] for desc in cursor.description]
                
                for event in subscription_events:
                    print(f"  Event: {dict(zip(col_names, event))}")
                    
                # Try to count new subscriptions specifically
                cursor.execute(f"""
                    SELECT COUNT(*) FROM events 
                    WHERE {date_col} >= %s 
                    AND (
                        json_data::text ILIKE '%new%subscription%' 
                        OR json_data::text ILIKE '%subscription%created%'
                        OR name ILIKE '%subscription%created%'
                        OR name ILIKE '%new%subscription%'
                        OR name ILIKE '%subscribe%'
                    );
                """, (one_month_ago,))
                
                result = cursor.fetchone()
                new_subscription_count = result[0] if result else 0
                print(f"\n📈 Estimated new subscriptions in the last month: {new_subscription_count}")
                
            else:
                print("❌ No subscription-related events found in the last month")
                
        else:
            print("❌ No date/timestamp columns found in events table")
            
            # Still try to look for subscription events without date filtering
            cursor.execute("""
                SELECT * FROM events 
                WHERE (
                    json_data::text ILIKE '%subscription%' 
                    OR json_data::text ILIKE '%subscribe%'
                    OR name ILIKE '%subscription%'
                    OR name ILIKE '%subscribe%'
                    OR value ILIKE '%subscription%'
                    OR value ILIKE '%subscribe%'
                )
                LIMIT 10;
            """)
            
            subscription_events = cursor.fetchall()
            
            if subscription_events:
                print(f"\n✅ Found {len(subscription_events)} subscription-related events (showing first 10):")
                col_names = [desc[0] for desc in cursor.description]
                
                for event in subscription_events:
                    print(f"  Event: {dict(zip(col_names, event))}")
            else:
                print("❌ No subscription-related events found")
        
        # Close connection
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error analyzing subscriptions: {e}")

if __name__ == "__main__":
    analyze_subscriptions()