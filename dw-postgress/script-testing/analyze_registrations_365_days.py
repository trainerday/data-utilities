#!/usr/bin/env python3
"""
Analyze user registrations over the last 365 days and their sources.
"""

import os
import sys
import psycopg2
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

def analyze_registrations_365_days():
    """Analyze user registrations over the last 365 days."""
    
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
        
        print("📊 Analyzing registrations over the last 365 days...")
        print("=" * 60)
        
        # Total registrations in last 365 days
        cursor.execute("""
            SELECT COUNT(*) FROM events 
            WHERE name = 'new user registered' 
            AND created_at >= NOW() - INTERVAL '365 days';
        """)
        
        total_registrations = cursor.fetchone()[0]
        print(f"Total registrations in last 365 days: {total_registrations:,}")
        
        # Monthly trend analysis
        cursor.execute("""
            SELECT 
                DATE_TRUNC('month', created_at) as month,
                COUNT(*) as monthly_registrations
            FROM events 
            WHERE name = 'new user registered' 
            AND created_at >= NOW() - INTERVAL '365 days'
            GROUP BY DATE_TRUNC('month', created_at)
            ORDER BY month DESC;
        """)
        
        monthly_trends = cursor.fetchall()
        print(f"\nMonthly registration trends (last 365 days):")
        for month, count in monthly_trends:
            print(f"  {month.strftime('%Y-%m')}: {count:,}")
        
        # Registration types analysis
        cursor.execute("""
            SELECT value, COUNT(*) as count
            FROM events 
            WHERE name = 'new user registered' 
            AND created_at >= NOW() - INTERVAL '365 days'
            GROUP BY value
            ORDER BY count DESC;
        """)
        
        registration_types = cursor.fetchall()
        print(f"\nRegistration types in last 365 days:")
        for reg_type, count in registration_types:
            percentage = (count / total_registrations) * 100
            print(f"  {reg_type}: {count:,} ({percentage:.1f}%)")
        
        # Top countries analysis
        cursor.execute("""
            SELECT json_data->>'countryCode' as country, COUNT(*) as count
            FROM events 
            WHERE name = 'new user registered' 
            AND created_at >= NOW() - INTERVAL '365 days'
            AND json_data->>'countryCode' IS NOT NULL
            GROUP BY json_data->>'countryCode'
            ORDER BY count DESC
            LIMIT 30;
        """)
        
        country_registrations = cursor.fetchall()
        print(f"\nTop 30 countries by registrations (last 365 days):")
        for country, count in country_registrations:
            percentage = (count / total_registrations) * 100
            print(f"  {country}: {count:,} ({percentage:.1f}%)")
        
        # Language analysis
        cursor.execute("""
            SELECT json_data->>'lang' as language, COUNT(*) as count
            FROM events 
            WHERE name = 'new user registered' 
            AND created_at >= NOW() - INTERVAL '365 days'
            AND json_data->>'lang' IS NOT NULL
            GROUP BY json_data->>'lang'
            ORDER BY count DESC
            LIMIT 15;
        """)
        
        language_registrations = cursor.fetchall()
        print(f"\nTop 15 languages by registrations (last 365 days):")
        for language, count in language_registrations:
            percentage = (count / total_registrations) * 100
            print(f"  {language}: {count:,} ({percentage:.1f}%)")
        
        # Analyze referrer sources
        print(f"\n🔍 Analyzing referrer sources (last 365 days)...")
        cursor.execute("""
            SELECT value, COUNT(*) as count
            FROM events 
            WHERE name = 'user came from referrer' 
            AND created_at >= NOW() - INTERVAL '365 days'
            GROUP BY value
            ORDER BY count DESC
            LIMIT 30;
        """)
        
        referrer_sources = cursor.fetchall()
        print(f"\nTop 30 referrer sources (last 365 days):")
        total_referrers = sum(count for _, count in referrer_sources)
        for referrer, count in referrer_sources:
            percentage = (count / total_referrers) * 100
            print(f"  {referrer}: {count:,} ({percentage:.1f}%)")
        
        # Subscription metrics
        cursor.execute("""
            SELECT COUNT(*) FROM events 
            WHERE name = 'Subscribe Page Visited' 
            AND created_at >= NOW() - INTERVAL '365 days';
        """)
        
        subscription_visits = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM events 
            WHERE name = 'subscription status changed to active' 
            AND created_at >= NOW() - INTERVAL '365 days';
        """)
        
        subscription_conversions = cursor.fetchone()[0]
        
        print(f"\nSubscription metrics (last 365 days):")
        print(f"  Subscription page visits: {subscription_visits:,}")
        print(f"  Subscription conversions: {subscription_conversions:,}")
        
        if subscription_visits > 0:
            conversion_rate = (subscription_conversions / subscription_visits) * 100
            print(f"  Conversion rate: {conversion_rate:.2f}%")
        
        # Quarterly breakdown
        cursor.execute("""
            SELECT 
                EXTRACT(QUARTER FROM created_at) as quarter,
                EXTRACT(YEAR FROM created_at) as year,
                COUNT(*) as quarterly_registrations
            FROM events 
            WHERE name = 'new user registered' 
            AND created_at >= NOW() - INTERVAL '365 days'
            GROUP BY EXTRACT(QUARTER FROM created_at), EXTRACT(YEAR FROM created_at)
            ORDER BY year DESC, quarter DESC;
        """)
        
        quarterly_trends = cursor.fetchall()
        print(f"\nQuarterly registration trends (last 365 days):")
        for quarter, year, count in quarterly_trends:
            print(f"  Q{int(quarter)} {int(year)}: {count:,}")
        
        # Top referrer domains grouped
        print(f"\n🔍 Analyzing referrer domains (grouped)...")
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN value LIKE '%google%' THEN 'Google'
                    WHEN value LIKE '%strava%' THEN 'Strava'
                    WHEN value LIKE '%trainingpeaks%' THEN 'TrainingPeaks'
                    WHEN value LIKE '%wahoo%' THEN 'Wahoo'
                    WHEN value LIKE '%intervals.icu%' THEN 'Intervals.icu'
                    WHEN value LIKE '%garmin%' THEN 'Garmin'
                    WHEN value LIKE '%reddit%' THEN 'Reddit'
                    WHEN value LIKE '%youtube%' THEN 'YouTube'
                    WHEN value LIKE '%facebook%' THEN 'Facebook'
                    WHEN value LIKE '%zwift%' THEN 'Zwift'
                    WHEN value LIKE '%chatgpt%' THEN 'ChatGPT'
                    WHEN value LIKE '%github%' THEN 'GitHub'
                    WHEN value LIKE '%duckduckgo%' THEN 'DuckDuckGo'
                    WHEN value LIKE '%bing%' THEN 'Bing'
                    WHEN value LIKE '%brave%' THEN 'Brave'
                    ELSE 'Other'
                END as referrer_group,
                COUNT(*) as count
            FROM events 
            WHERE name = 'user came from referrer' 
            AND created_at >= NOW() - INTERVAL '365 days'
            GROUP BY referrer_group
            ORDER BY count DESC;
        """)
        
        grouped_referrers = cursor.fetchall()
        print(f"\nReferrer sources grouped by platform (last 365 days):")
        total_grouped = sum(count for _, count in grouped_referrers)
        for referrer_group, count in grouped_referrers:
            percentage = (count / total_grouped) * 100
            print(f"  {referrer_group}: {count:,} ({percentage:.1f}%)")
        
        # Daily average
        daily_average = total_registrations / 365
        print(f"\nDaily average registrations: {daily_average:.1f}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("\n✅ 365-day registration analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_registrations_365_days()