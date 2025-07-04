#!/usr/bin/env python3
"""
Count subscription events from the last month.
"""

import os
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv

def count_subscriptions():
    """Count subscription events from the last month."""
    
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
        
        # First, check the date range of data in the events table
        print("📅 Checking date range of events...")
        cursor.execute("SELECT MIN(created_at), MAX(created_at) FROM events;")
        date_range = cursor.fetchone()
        
        if date_range and date_range[0] and date_range[1]:
            print(f"Events date range: {date_range[0]} to {date_range[1]}")
            
            # Calculate one month ago from the max date in the database
            max_date = date_range[1]
            one_month_ago = max_date - timedelta(days=30)
            
            print(f"Looking for subscription events since {one_month_ago}")
            
            # Search for subscription-related events
            cursor.execute("""
                SELECT user_id, name, value, json_data, created_at 
                FROM events 
                WHERE created_at >= %s 
                AND (
                    json_data::text ILIKE '%subscription%' 
                    OR json_data::text ILIKE '%subscribe%'
                    OR name ILIKE '%subscription%'
                    OR name ILIKE '%subscribe%'
                    OR value ILIKE '%subscription%'
                    OR value ILIKE '%subscribe%'
                )
                ORDER BY created_at DESC;
            """, (one_month_ago,))
            
            subscription_events = cursor.fetchall()
            
            print(f"\n📊 Found {len(subscription_events)} subscription-related events in the last month")
            
            if subscription_events:
                print("\nSubscription events:")
                for event in subscription_events:
                    user_id, name, value, json_data, created_at = event
                    print(f"  {created_at}: User {user_id} - {name} - {value} - {json_data}")
                    
                # Try to identify new subscriptions
                new_subscription_patterns = [
                    'subscription_created',
                    'new_subscription',
                    'subscribe',
                    'subscription_started',
                    'premium_subscription'
                ]
                
                new_subscriptions = []
                for event in subscription_events:
                    user_id, name, value, json_data, created_at = event
                    for pattern in new_subscription_patterns:
                        if (name and pattern in name.lower()) or (value and pattern in value.lower()) or (json_data and pattern in str(json_data).lower()):
                            new_subscriptions.append(event)
                            break
                
                print(f"\n📈 Estimated new subscriptions in the last month: {len(new_subscriptions)}")
                
                if new_subscriptions:
                    print("\nNew subscription events:")
                    for event in new_subscriptions:
                        user_id, name, value, json_data, created_at = event
                        print(f"  {created_at}: User {user_id} - {name}")
                        
            else:
                print("❌ No subscription-related events found in the last month")
                
                # Look for any subscription events in the entire dataset
                print("\n🔍 Searching for any subscription events in the entire dataset...")
                cursor.execute("""
                    SELECT user_id, name, value, json_data, created_at 
                    FROM events 
                    WHERE (
                        json_data::text ILIKE '%subscription%' 
                        OR json_data::text ILIKE '%subscribe%'
                        OR name ILIKE '%subscription%'
                        OR name ILIKE '%subscribe%'
                        OR value ILIKE '%subscription%'
                        OR value ILIKE '%subscribe%'
                    )
                    ORDER BY created_at DESC
                    LIMIT 10;
                """)
                
                all_subscription_events = cursor.fetchall()
                
                if all_subscription_events:
                    print(f"Found {len(all_subscription_events)} subscription events in total (showing latest 10):")
                    for event in all_subscription_events:
                        user_id, name, value, json_data, created_at = event
                        print(f"  {created_at}: User {user_id} - {name} - {value}")
                else:
                    print("❌ No subscription events found in the entire dataset")
                    
                    # Let's check what event names we have
                    print("\n📋 Checking available event names...")
                    cursor.execute("SELECT DISTINCT name FROM events ORDER BY name LIMIT 50;")
                    event_names = cursor.fetchall()
                    print("Available event names:")
                    for name in event_names:
                        print(f"  {name[0]}")
                    
        else:
            print("❌ No date information found in events table")
        
        # Close connection
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error analyzing subscriptions: {e}")

if __name__ == "__main__":
    count_subscriptions()