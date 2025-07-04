#!/usr/bin/env python3
"""
Simple subscription count from the last month.
"""

import os
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv

def simple_count():
    """Simple subscription count."""
    
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
        
        # Get the last month's date range
        cursor.execute("SELECT MAX(created_at) FROM events;")
        max_date_result = cursor.fetchone()
        max_date = max_date_result[0] if max_date_result else None
        
        if max_date:
            one_month_ago = max_date - timedelta(days=30)
            print(f"Searching for subscription events from {one_month_ago} to {max_date}")
            
            # Count subscription events
            cursor.execute("""
                SELECT COUNT(*) FROM events 
                WHERE created_at >= %s 
                AND (
                    name ILIKE '%subscription%' 
                    OR name ILIKE '%subscribe%'
                    OR value ILIKE '%subscription%'
                    OR value ILIKE '%subscribe%'
                    OR json_data::text ILIKE '%subscription%'
                    OR json_data::text ILIKE '%subscribe%'
                );
            """, (one_month_ago,))
            
            result = cursor.fetchone()
            count = result[0] if result else 0
            print(f"📊 Total subscription-related events in last month: {count}")
            
            # Get some examples if any exist
            if count > 0:
                cursor.execute("""
                    SELECT name, value, json_data, created_at 
                    FROM events 
                    WHERE created_at >= %s 
                    AND (
                        name ILIKE '%subscription%' 
                        OR name ILIKE '%subscribe%'
                        OR value ILIKE '%subscription%'
                        OR value ILIKE '%subscribe%'
                        OR json_data::text ILIKE '%subscription%'
                        OR json_data::text ILIKE '%subscribe%'
                    )
                    ORDER BY created_at DESC
                    LIMIT 5;
                """, (one_month_ago,))
                
                examples = cursor.fetchall()
                print(f"\nExamples of subscription events:")
                for name, value, json_data, created_at in examples:
                    print(f"  {created_at}: {name} - {value} - {json_data}")
            else:
                print("❌ No subscription events found in the last month")
                
                # Check for any subscription events ever
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
                
                total_result = cursor.fetchone()
                total_count = total_result[0] if total_result else 0
                print(f"📊 Total subscription-related events in entire dataset: {total_count}")
                
                if total_count > 0:
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
                        LIMIT 5;
                    """)
                    
                    examples = cursor.fetchall()
                    print(f"\nLatest subscription events:")
                    for name, value, json_data, created_at in examples:
                        print(f"  {created_at}: {name} - {value} - {json_data}")
        
        # Close connection
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_count()