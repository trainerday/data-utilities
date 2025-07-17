#!/usr/bin/env python3
"""
Search for user login events, especially app logins.
"""

import os
import sys
import psycopg2
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

def analyze_login_events():
    """Search for and analyze user login events."""
    
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
        
        print("🔍 Searching for login-related events...")
        print("=" * 60)
        
        # Search for login-related event names
        cursor.execute("""
            SELECT name, COUNT(*) as count
            FROM events 
            WHERE (
                name ILIKE '%login%' 
                OR name ILIKE '%log%in%'
                OR name ILIKE '%signin%'
                OR name ILIKE '%sign%in%'
                OR name ILIKE '%auth%'
                OR name ILIKE '%session%'
                OR name ILIKE '%access%'
                OR name ILIKE '%visited%'
                OR name ILIKE '%opened%'
                OR name ILIKE '%launched%'
                OR name ILIKE '%started%'
            )
            GROUP BY name
            ORDER BY count DESC
            LIMIT 30;
        """)
        
        login_events = cursor.fetchall()
        print(f"Event names that might be login-related:")
        for name, count in login_events:
            print(f"  {name}: {count:,}")
        
        # Look for app-specific events
        print(f"\n🔍 Searching for app-specific events...")
        cursor.execute("""
            SELECT name, COUNT(*) as count
            FROM events 
            WHERE (
                name ILIKE '%app%' 
                OR value ILIKE '%app%'
                OR json_data::text ILIKE '%app%'
            )
            GROUP BY name
            ORDER BY count DESC
            LIMIT 20;
        """)
        
        app_events = cursor.fetchall()
        print(f"App-related events:")
        for name, count in app_events:
            print(f"  {name}: {count:,}")
        
        # Look for turbo activity events (seems to be app usage)
        print(f"\n🔍 Analyzing 'turbo activity created' events (app usage indicator)...")
        cursor.execute("""
            SELECT COUNT(*) FROM events 
            WHERE name = 'turbo activity created' 
            AND created_at >= NOW() - INTERVAL '30 days';
        """)
        
        turbo_30_days = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM events 
            WHERE name = 'turbo activity created' 
            AND created_at >= NOW() - INTERVAL '365 days';
        """)
        
        turbo_365_days = cursor.fetchone()[0]
        
        print(f"Turbo activities (app usage) in last 30 days: {turbo_30_days:,}")
        print(f"Turbo activities (app usage) in last 365 days: {turbo_365_days:,}")
        
        # Daily breakdown of turbo activities
        cursor.execute("""
            SELECT DATE(created_at) as activity_date, COUNT(*) as daily_count
            FROM events 
            WHERE name = 'turbo activity created' 
            AND created_at >= NOW() - INTERVAL '30 days'
            GROUP BY DATE(created_at)
            ORDER BY activity_date DESC;
        """)
        
        daily_turbo = cursor.fetchall()
        print(f"\nDaily turbo activities (last 30 days):")
        for date, count in daily_turbo:
            print(f"  {date}: {count:,}")
        
        # Monthly breakdown
        cursor.execute("""
            SELECT 
                DATE_TRUNC('month', created_at) as month,
                COUNT(*) as monthly_count
            FROM events 
            WHERE name = 'turbo activity created' 
            AND created_at >= NOW() - INTERVAL '365 days'
            GROUP BY DATE_TRUNC('month', created_at)
            ORDER BY month DESC;
        """)
        
        monthly_turbo = cursor.fetchall()
        print(f"\nMonthly turbo activities (last 365 days):")
        for month, count in monthly_turbo:
            print(f"  {month.strftime('%Y-%m')}: {count:,}")
        
        # Look for unique users creating turbo activities
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) FROM events 
            WHERE name = 'turbo activity created' 
            AND created_at >= NOW() - INTERVAL '30 days';
        """)
        
        unique_users_30 = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) FROM events 
            WHERE name = 'turbo activity created' 
            AND created_at >= NOW() - INTERVAL '365 days';
        """)
        
        unique_users_365 = cursor.fetchone()[0]
        
        print(f"\nUnique users creating turbo activities:")
        print(f"  Last 30 days: {unique_users_30:,}")
        print(f"  Last 365 days: {unique_users_365:,}")
        
        # Look for workout-related events as app usage indicators
        print(f"\n🔍 Analyzing workout-related events (app usage indicators)...")
        
        workout_events = [
            'workout search performed',
            'workout sent',
            'workout downloaded',
            'workout file uploaded'
        ]
        
        for event_name in workout_events:
            cursor.execute("""
                SELECT COUNT(*) FROM events 
                WHERE name = %s 
                AND created_at >= NOW() - INTERVAL '30 days';
            """, (event_name,))
            
            count_30 = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(DISTINCT user_id) FROM events 
                WHERE name = %s 
                AND created_at >= NOW() - INTERVAL '30 days';
            """, (event_name,))
            
            unique_users = cursor.fetchone()[0]
            
            print(f"  {event_name}: {count_30:,} events, {unique_users:,} unique users (30 days)")
        
        # Look for access-related events
        print(f"\n🔍 Searching for access and visit events...")
        cursor.execute("""
            SELECT name, COUNT(*) as count, COUNT(DISTINCT user_id) as unique_users
            FROM events 
            WHERE (
                name ILIKE '%visited%' 
                OR name ILIKE '%access%'
                OR name ILIKE '%page%'
                OR name ILIKE '%view%'
            )
            AND created_at >= NOW() - INTERVAL '30 days'
            GROUP BY name
            ORDER BY count DESC
            LIMIT 15;
        """)
        
        access_events = cursor.fetchall()
        print(f"Access/visit events (last 30 days):")
        for name, count, unique_users in access_events:
            print(f"  {name}: {count:,} events, {unique_users:,} unique users")
        
        # Look for Coach Jack usage (AI feature)
        print(f"\n🔍 Analyzing Coach Jack usage (AI feature)...")
        cursor.execute("""
            SELECT name, COUNT(*) as count, COUNT(DISTINCT user_id) as unique_users
            FROM events 
            WHERE name ILIKE '%cj%'
            AND created_at >= NOW() - INTERVAL '30 days'
            GROUP BY name
            ORDER BY count DESC;
        """)
        
        cj_events = cursor.fetchall()
        print(f"Coach Jack events (last 30 days):")
        for name, count, unique_users in cj_events:
            print(f"  {name}: {count:,} events, {unique_users:,} unique users")
        
        # Summary of active users
        print(f"\n📊 Active User Summary (last 30 days):")
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) FROM events 
            WHERE created_at >= NOW() - INTERVAL '30 days';
        """)
        
        total_active_users = cursor.fetchone()[0]
        print(f"  Total active users: {total_active_users:,}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("\n✅ Login event analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_login_events()