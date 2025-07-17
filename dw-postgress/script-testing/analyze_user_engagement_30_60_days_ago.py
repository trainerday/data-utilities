#!/usr/bin/env python3
"""
Analyze user engagement within 3 days of registration for users who registered 30-60 days ago.
This gives us a comparison baseline to the recent 30-day analysis.
"""

import os
import sys
import psycopg2
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

def analyze_user_engagement_30_60_days_ago():
    """Analyze user engagement for users who registered 30-60 days ago."""
    
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
        
        print("📊 Analyzing user engagement for registrations 30-60 days ago...")
        print("=" * 70)
        
        # First, get total count of users who registered 30-60 days ago
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE name = 'new user registered' 
            AND created_at >= NOW() - INTERVAL '60 days'
            AND created_at < NOW() - INTERVAL '30 days'
            AND user_id IS NOT NULL;
        """)
        
        total_users = cursor.fetchone()[0]
        print(f"Total registrations 30-60 days ago: {total_users:,}")
        
        if total_users == 0:
            print("No registrations found in that period.")
            return
        
        # Define meaningful actions
        meaningful_actions = [
            'workout downloaded',
            'plan downloaded', 
            'activity downloaded',
            'subscription status changed to active',
            'turbo activity created'
        ]
        
        print(f"\nAnalyzing engagement for meaningful actions:")
        for action in meaningful_actions:
            print(f"  - {action}")
        
        # Use optimized query to find engaged users from 30-60 days ago
        print(f"\nRunning engagement analysis for 30-60 day old registrations...")
        
        cursor.execute("""
            WITH old_users AS (
                SELECT user_id, created_at as registration_date
                FROM events 
                WHERE name = 'new user registered' 
                AND created_at >= NOW() - INTERVAL '60 days'
                AND created_at < NOW() - INTERVAL '30 days'
                AND user_id IS NOT NULL
            ),
            meaningful_activities AS (
                SELECT DISTINCT e.user_id
                FROM events e
                INNER JOIN old_users ou ON e.user_id = ou.user_id
                WHERE e.name IN ('workout downloaded', 'plan downloaded', 'activity downloaded', 
                               'subscription status changed to active', 'turbo activity created')
                AND e.created_at BETWEEN ou.registration_date AND ou.registration_date + INTERVAL '3 days'
            )
            SELECT 
                (SELECT COUNT(*) FROM meaningful_activities) as engaged_users,
                (SELECT COUNT(*) FROM old_users) as total_users;
        """)
        
        result = cursor.fetchone()
        engaged_count, total_count = result
        inactive_count = total_count - engaged_count
        engagement_rate = (engaged_count / total_count) * 100 if total_count > 0 else 0
        
        print(f"\n📈 ENGAGEMENT ANALYSIS RESULTS (30-60 days ago):")
        print(f"=" * 55)
        print(f"Total users from that period: {total_count:,}")
        print(f"Users who took meaningful action within 3 days: {engaged_count:,} ({engagement_rate:.1f}%)")
        print(f"Users who remained inactive: {inactive_count:,} ({(inactive_count/total_count)*100:.1f}%)")
        
        # Break down by specific meaningful actions
        print(f"\n🎯 MEANINGFUL ACTIONS BREAKDOWN (30-60 days ago):")
        
        for action in meaningful_actions:
            cursor.execute("""
                WITH old_users AS (
                    SELECT user_id, created_at as registration_date
                    FROM events 
                    WHERE name = 'new user registered' 
                    AND created_at >= NOW() - INTERVAL '60 days'
                    AND created_at < NOW() - INTERVAL '30 days'
                    AND user_id IS NOT NULL
                )
                SELECT COUNT(DISTINCT e.user_id)
                FROM events e
                INNER JOIN old_users ou ON e.user_id = ou.user_id
                WHERE e.name = %s
                AND e.created_at BETWEEN ou.registration_date AND ou.registration_date + INTERVAL '3 days';
            """, (action,))
            
            action_users = cursor.fetchone()[0]
            percentage = (action_users / total_count) * 100 if total_count > 0 else 0
            print(f"  {action}: {action_users:,} users ({percentage:.1f}%)")
        
        # Additional engagement metrics
        print(f"\n📱 ADDITIONAL ENGAGEMENT ACTIVITIES (30-60 days ago):")
        
        additional_actions = [
            'workout search performed',
            'workout sent',
            'cj save answer',
            'workout file uploaded',
            'cj create new plan click'
        ]
        
        for action in additional_actions:
            cursor.execute("""
                WITH old_users AS (
                    SELECT user_id, created_at as registration_date
                    FROM events 
                    WHERE name = 'new user registered' 
                    AND created_at >= NOW() - INTERVAL '60 days'
                    AND created_at < NOW() - INTERVAL '30 days'
                    AND user_id IS NOT NULL
                )
                SELECT COUNT(DISTINCT e.user_id)
                FROM events e
                INNER JOIN old_users ou ON e.user_id = ou.user_id
                WHERE e.name = %s
                AND e.created_at BETWEEN ou.registration_date AND ou.registration_date + INTERVAL '3 days';
            """, (action,))
            
            action_users = cursor.fetchone()[0]
            percentage = (action_users / total_count) * 100 if total_count > 0 else 0
            print(f"  {action}: {action_users:,} users ({percentage:.1f}%)")
        
        # Show registration dates for this period
        print(f"\n📅 REGISTRATION DATES IN ANALYSIS PERIOD:")
        cursor.execute("""
            SELECT 
                DATE(created_at) as reg_date,
                COUNT(*) as daily_registrations
            FROM events 
            WHERE name = 'new user registered' 
            AND created_at >= NOW() - INTERVAL '60 days'
            AND created_at < NOW() - INTERVAL '30 days'
            GROUP BY DATE(created_at)
            ORDER BY reg_date DESC
            LIMIT 15;
        """)
        
        daily_registrations = cursor.fetchall()
        for date, count in daily_registrations:
            print(f"  {date}: {count:,} new users")
        
        # Compare with recent data (last 30 days)
        print(f"\n🔄 COMPARISON WITH RECENT DATA (last 30 days):")
        
        # Get recent engagement rate for comparison
        cursor.execute("""
            WITH recent_users AS (
                SELECT user_id, created_at as registration_date
                FROM events 
                WHERE name = 'new user registered' 
                AND created_at >= NOW() - INTERVAL '30 days'
                AND user_id IS NOT NULL
            ),
            recent_meaningful_activities AS (
                SELECT DISTINCT e.user_id
                FROM events e
                INNER JOIN recent_users ru ON e.user_id = ru.user_id
                WHERE e.name IN ('workout downloaded', 'plan downloaded', 'activity downloaded', 
                               'subscription status changed to active', 'turbo activity created')
                AND e.created_at BETWEEN ru.registration_date AND ru.registration_date + INTERVAL '3 days'
            )
            SELECT 
                (SELECT COUNT(*) FROM recent_meaningful_activities) as recent_engaged_users,
                (SELECT COUNT(*) FROM recent_users) as recent_total_users;
        """)
        
        recent_result = cursor.fetchone()
        recent_engaged, recent_total = recent_result
        recent_engagement_rate = (recent_engaged / recent_total) * 100 if recent_total > 0 else 0
        
        print(f"  30-60 days ago: {engagement_rate:.1f}% engagement ({engaged_count:,}/{total_count:,})")
        print(f"  Last 30 days:  {recent_engagement_rate:.1f}% engagement ({recent_engaged:,}/{recent_total:,})")
        
        # Calculate trend
        trend = recent_engagement_rate - engagement_rate
        trend_direction = "📈 UP" if trend > 0 else "📉 DOWN" if trend < 0 else "➡️ FLAT"
        print(f"  Trend: {trend_direction} {abs(trend):.1f} percentage points")
        
        # Summary insights
        print(f"\n💡 KEY INSIGHTS:")
        print(f"  • Historical engagement rate: {engagement_rate:.1f}%")
        print(f"  • Current vs Historical: {trend:+.1f} percentage points")
        
        if trend > 2:
            print(f"  ✅ Engagement is improving!")
        elif trend < -2:
            print(f"  ⚠️  Engagement is declining")
        else:
            print(f"  📊 Engagement rate is stable")
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("\n✅ Historical engagement analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_user_engagement_30_60_days_ago()