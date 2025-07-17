#!/usr/bin/env python3
"""
Analyze user registrations over the last 100 days and their sources.
"""

import os
import sys
import psycopg2
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

def analyze_registrations():
    """Analyze user registrations over the last 100 days."""
    
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
        
        print("📊 Analyzing registrations over the last 100 days...")
        print("=" * 60)
        
        # Total registrations in last 100 days
        cursor.execute("""
            SELECT COUNT(*) FROM events 
            WHERE name = 'new user registered' 
            AND created_at >= NOW() - INTERVAL '100 days';
        """)
        
        total_registrations = cursor.fetchone()[0]
        print(f"Total registrations in last 100 days: {total_registrations:,}")
        
        # Daily registrations for last 100 days
        cursor.execute("""
            SELECT DATE(created_at) as registration_date, COUNT(*) as daily_count
            FROM events 
            WHERE name = 'new user registered' 
            AND created_at >= NOW() - INTERVAL '100 days'
            GROUP BY DATE(created_at)
            ORDER BY registration_date DESC;
        """)
        
        daily_registrations = cursor.fetchall()
        print(f"\nDaily registrations (last 30 days):")
        for date, count in daily_registrations[:30]:
            print(f"  {date}: {count:,}")
        
        # Registration types analysis
        cursor.execute("""
            SELECT value, COUNT(*) as count
            FROM events 
            WHERE name = 'new user registered' 
            AND created_at >= NOW() - INTERVAL '100 days'
            GROUP BY value
            ORDER BY count DESC;
        """)
        
        registration_types = cursor.fetchall()
        print(f"\nRegistration types in last 100 days:")
        for reg_type, count in registration_types:
            print(f"  {reg_type}: {count:,}")
        
        # Country analysis from JSON data
        cursor.execute("""
            SELECT json_data->>'countryCode' as country, COUNT(*) as count
            FROM events 
            WHERE name = 'new user registered' 
            AND created_at >= NOW() - INTERVAL '100 days'
            AND json_data->>'countryCode' IS NOT NULL
            GROUP BY json_data->>'countryCode'
            ORDER BY count DESC
            LIMIT 20;
        """)
        
        country_registrations = cursor.fetchall()
        print(f"\nTop 20 countries by registrations (last 100 days):")
        for country, count in country_registrations:
            print(f"  {country}: {count:,}")
        
        # Language analysis from JSON data
        cursor.execute("""
            SELECT json_data->>'lang' as language, COUNT(*) as count
            FROM events 
            WHERE name = 'new user registered' 
            AND created_at >= NOW() - INTERVAL '100 days'
            AND json_data->>'lang' IS NOT NULL
            GROUP BY json_data->>'lang'
            ORDER BY count DESC
            LIMIT 10;
        """)
        
        language_registrations = cursor.fetchall()
        print(f"\nTop 10 languages by registrations (last 100 days):")
        for language, count in language_registrations:
            print(f"  {language}: {count:,}")
        
        # Analyze referrer sources
        print(f"\n🔍 Analyzing referrer sources...")
        cursor.execute("""
            SELECT value, COUNT(*) as count
            FROM events 
            WHERE name = 'user came from referrer' 
            AND created_at >= NOW() - INTERVAL '100 days'
            GROUP BY value
            ORDER BY count DESC
            LIMIT 20;
        """)
        
        referrer_sources = cursor.fetchall()
        print(f"\nTop 20 referrer sources (last 100 days):")
        for referrer, count in referrer_sources:
            print(f"  {referrer}: {count:,}")
        
        # Subscription page visits
        cursor.execute("""
            SELECT COUNT(*) FROM events 
            WHERE name = 'Subscribe Page Visited' 
            AND created_at >= NOW() - INTERVAL '100 days';
        """)
        
        subscription_visits = cursor.fetchone()[0]
        print(f"\nSubscription page visits (last 100 days): {subscription_visits:,}")
        
        # Subscription conversions
        cursor.execute("""
            SELECT COUNT(*) FROM events 
            WHERE name = 'subscription status changed to active' 
            AND created_at >= NOW() - INTERVAL '100 days';
        """)
        
        subscription_conversions = cursor.fetchone()[0]
        print(f"Subscription conversions (last 100 days): {subscription_conversions:,}")
        
        if subscription_visits > 0:
            conversion_rate = (subscription_conversions / subscription_visits) * 100
            print(f"Conversion rate: {conversion_rate:.2f}%")
        
        # Weekly trend analysis
        cursor.execute("""
            SELECT 
                DATE_TRUNC('week', created_at) as week_start,
                COUNT(*) as weekly_registrations
            FROM events 
            WHERE name = 'new user registered' 
            AND created_at >= NOW() - INTERVAL '100 days'
            GROUP BY DATE_TRUNC('week', created_at)
            ORDER BY week_start DESC;
        """)
        
        weekly_trends = cursor.fetchall()
        print(f"\nWeekly registration trends (last 100 days):")
        for week_start, count in weekly_trends:
            print(f"  Week of {week_start.strftime('%Y-%m-%d')}: {count:,}")
        
        # Sample recent registrations with details
        cursor.execute("""
            SELECT value, json_data, created_at
            FROM events 
            WHERE name = 'new user registered' 
            AND created_at >= NOW() - INTERVAL '100 days'
            ORDER BY created_at DESC
            LIMIT 10;
        """)
        
        recent_registrations = cursor.fetchall()
        print(f"\nSample recent registrations:")
        for reg_type, json_data, created_at in recent_registrations:
            print(f"  {created_at}: {reg_type}")
            if json_data:
                # Parse JSON to extract key info
                try:
                    data = json_data if isinstance(json_data, dict) else json.loads(json_data)
                    username = data.get('username', 'N/A')
                    country = data.get('countryCode', 'N/A')
                    language = data.get('lang', 'N/A')
                    print(f"    User: {username}, Country: {country}, Language: {language}")
                except:
                    print(f"    JSON: {json_data}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("\n✅ Registration analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_registrations()