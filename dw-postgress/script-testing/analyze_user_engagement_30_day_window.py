#!/usr/bin/env python3
"""
Analyze user engagement within 30 DAYS of registration for users who registered 30-60 days ago.
This gives us a longer engagement window to compare with the 3-day analysis.
"""

import os
import sys
import psycopg2
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

def analyze_user_engagement_30_day_window():
    """Analyze user engagement within 30 days of registration for users who registered 30-60 days ago."""
    
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
        
        print("📊 Analyzing user engagement within 30 DAYS of registration...")
        print("(For users who registered 30-60 days ago)")
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
        
        print(f"\nAnalyzing engagement within 30 DAYS of registration for:")
        for action in meaningful_actions:
            print(f"  - {action}")
        
        # Use optimized query to find engaged users within 30 days of registration
        print(f"\nRunning 30-day engagement analysis...")
        
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
                AND e.created_at BETWEEN ou.registration_date AND ou.registration_date + INTERVAL '30 days'
            )
            SELECT 
                (SELECT COUNT(*) FROM meaningful_activities) as engaged_users,
                (SELECT COUNT(*) FROM old_users) as total_users;
        """)
        
        result = cursor.fetchone()
        engaged_count, total_count = result
        inactive_count = total_count - engaged_count
        engagement_rate = (engaged_count / total_count) * 100 if total_count > 0 else 0
        
        print(f"\n📈 30-DAY ENGAGEMENT ANALYSIS RESULTS:")
        print(f"=" * 50)
        print(f"Total users from 30-60 days ago: {total_count:,}")
        print(f"Users who took meaningful action within 30 days: {engaged_count:,} ({engagement_rate:.1f}%)")
        print(f"Users who remained inactive after 30 days: {inactive_count:,} ({(inactive_count/total_count)*100:.1f}%)")
        
        # Break down by specific meaningful actions
        print(f"\n🎯 MEANINGFUL ACTIONS BREAKDOWN (within 30 days):")
        
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
                AND e.created_at BETWEEN ou.registration_date AND ou.registration_date + INTERVAL '30 days';
            """, (action,))
            
            action_users = cursor.fetchone()[0]
            percentage = (action_users / total_count) * 100 if total_count > 0 else 0
            print(f"  {action}: {action_users:,} users ({percentage:.1f}%)")
        
        # Additional engagement metrics
        print(f"\n📱 ADDITIONAL ENGAGEMENT ACTIVITIES (within 30 days):")
        
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
                AND e.created_at BETWEEN ou.registration_date AND ou.registration_date + INTERVAL '30 days';
            """, (action,))
            
            action_users = cursor.fetchone()[0]
            percentage = (action_users / total_count) * 100 if total_count > 0 else 0
            print(f"  {action}: {action_users:,} users ({percentage:.1f}%)")
        
        # Compare 3-day vs 30-day engagement for the same user cohort
        print(f"\n🔄 COMPARISON: 3-DAY vs 30-DAY ENGAGEMENT (same cohort):")
        
        # Get 3-day engagement for the same cohort
        cursor.execute("""
            WITH old_users AS (
                SELECT user_id, created_at as registration_date
                FROM events 
                WHERE name = 'new user registered' 
                AND created_at >= NOW() - INTERVAL '60 days'
                AND created_at < NOW() - INTERVAL '30 days'
                AND user_id IS NOT NULL
            ),
            three_day_activities AS (
                SELECT DISTINCT e.user_id
                FROM events e
                INNER JOIN old_users ou ON e.user_id = ou.user_id
                WHERE e.name IN ('workout downloaded', 'plan downloaded', 'activity downloaded', 
                               'subscription status changed to active', 'turbo activity created')
                AND e.created_at BETWEEN ou.registration_date AND ou.registration_date + INTERVAL '3 days'
            )
            SELECT COUNT(*) FROM three_day_activities;
        """)
        
        three_day_engaged = cursor.fetchone()[0]
        three_day_rate = (three_day_engaged / total_count) * 100 if total_count > 0 else 0
        
        print(f"  3-day engagement:  {three_day_rate:.1f}% ({three_day_engaged:,}/{total_count:,})")
        print(f"  30-day engagement: {engagement_rate:.1f}% ({engaged_count:,}/{total_count:,})")
        
        # Calculate improvement from 3 days to 30 days
        improvement = engagement_rate - three_day_rate
        additional_users = engaged_count - three_day_engaged
        
        print(f"  Additional users engaged between day 4-30: {additional_users:,} (+{improvement:.1f} percentage points)")
        
        # Show breakdown by time periods
        print(f"\n⏰ ENGAGEMENT BY TIME PERIODS:")
        
        time_periods = [
            ('1-3 days', '1 day', '3 days'),
            ('4-7 days', '4 days', '7 days'), 
            ('8-14 days', '8 days', '14 days'),
            ('15-30 days', '15 days', '30 days')
        ]
        
        for period_name, start_days, end_days in time_periods:
            cursor.execute("""
                WITH old_users AS (
                    SELECT user_id, created_at as registration_date
                    FROM events 
                    WHERE name = 'new user registered' 
                    AND created_at >= NOW() - INTERVAL '60 days'
                    AND created_at < NOW() - INTERVAL '30 days'
                    AND user_id IS NOT NULL
                ),
                period_activities AS (
                    SELECT DISTINCT e.user_id
                    FROM events e
                    INNER JOIN old_users ou ON e.user_id = ou.user_id
                    WHERE e.name IN ('workout downloaded', 'plan downloaded', 'activity downloaded', 
                                   'subscription status changed to active', 'turbo activity created')
                    AND e.created_at BETWEEN ou.registration_date + INTERVAL %s AND ou.registration_date + INTERVAL %s
                    AND e.user_id NOT IN (
                        SELECT DISTINCT e2.user_id
                        FROM events e2
                        INNER JOIN old_users ou2 ON e2.user_id = ou2.user_id
                        WHERE e2.name IN ('workout downloaded', 'plan downloaded', 'activity downloaded', 
                                        'subscription status changed to active', 'turbo activity created')
                        AND e2.created_at BETWEEN ou2.registration_date AND ou2.registration_date + INTERVAL %s
                    )
                )
                SELECT COUNT(*) FROM period_activities;
            """, (start_days, end_days, start_days))
            
            period_engaged = cursor.fetchone()[0]
            period_rate = (period_engaged / total_count) * 100 if total_count > 0 else 0
            print(f"  {period_name}: {period_engaged:,} users ({period_rate:.1f}%) - first engaged in this period")
        
        # Summary insights
        print(f"\n💡 KEY INSIGHTS:")
        print(f"  • 30-day engagement: {engagement_rate:.1f}% (vs {three_day_rate:.1f}% at 3 days)")
        print(f"  • {improvement:.1f} percentage points gained between day 4-30")
        print(f"  • {(inactive_count/total_count)*100:.1f}% never engaged even after 30 days")
        
        if improvement > 10:
            print(f"  ✅ Good long-term engagement - users do come back!")
        elif improvement < 5:
            print(f"  ⚠️  Limited long-term engagement - most users decide quickly")
        else:
            print(f"  📊 Moderate long-term engagement")
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("\n✅ 30-day engagement analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_user_engagement_30_day_window()