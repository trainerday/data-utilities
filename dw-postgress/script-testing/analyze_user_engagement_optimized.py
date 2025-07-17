#!/usr/bin/env python3
"""
Optimized analysis of user engagement within 3 days of registration (last 30 days).
"""

import os
import sys
import psycopg2
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

def analyze_user_engagement_optimized():
    """Optimized analysis of user engagement."""
    
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
        
        print("📊 Analyzing user engagement after registration (last 30 days)...")
        print("=" * 70)
        
        # First, get total count of new users
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE name = 'new user registered' 
            AND created_at >= NOW() - INTERVAL '30 days'
            AND user_id IS NOT NULL;
        """)
        
        total_new_users = cursor.fetchone()[0]
        print(f"Total new registrations in last 30 days: {total_new_users:,}")
        
        if total_new_users == 0:
            print("No new registrations found.")
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
        
        # Use a single optimized query to find engaged users
        print(f"\nRunning optimized engagement analysis...")
        
        cursor.execute("""
            WITH new_users AS (
                SELECT user_id, created_at as registration_date
                FROM events 
                WHERE name = 'new user registered' 
                AND created_at >= NOW() - INTERVAL '30 days'
                AND user_id IS NOT NULL
            ),
            meaningful_activities AS (
                SELECT DISTINCT e.user_id
                FROM events e
                INNER JOIN new_users nu ON e.user_id = nu.user_id
                WHERE e.name IN ('workout downloaded', 'plan downloaded', 'activity downloaded', 
                               'subscription status changed to active', 'turbo activity created')
                AND e.created_at BETWEEN nu.registration_date AND nu.registration_date + INTERVAL '3 days'
            )
            SELECT 
                (SELECT COUNT(*) FROM meaningful_activities) as engaged_users,
                (SELECT COUNT(*) FROM new_users) as total_users;
        """)
        
        result = cursor.fetchone()
        engaged_count, total_count = result
        inactive_count = total_count - engaged_count
        engagement_rate = (engaged_count / total_count) * 100 if total_count > 0 else 0
        
        print(f"\n📈 ENGAGEMENT ANALYSIS RESULTS:")
        print(f"=" * 50)
        print(f"Total new users (last 30 days): {total_count:,}")
        print(f"Users who took meaningful action within 3 days: {engaged_count:,} ({engagement_rate:.1f}%)")
        print(f"Users who remained inactive: {inactive_count:,} ({(inactive_count/total_count)*100:.1f}%)")
        
        # Break down by specific meaningful actions
        print(f"\n🎯 MEANINGFUL ACTIONS BREAKDOWN:")
        
        for action in meaningful_actions:
            cursor.execute("""
                WITH new_users AS (
                    SELECT user_id, created_at as registration_date
                    FROM events 
                    WHERE name = 'new user registered' 
                    AND created_at >= NOW() - INTERVAL '30 days'
                    AND user_id IS NOT NULL
                )
                SELECT COUNT(DISTINCT e.user_id)
                FROM events e
                INNER JOIN new_users nu ON e.user_id = nu.user_id
                WHERE e.name = %s
                AND e.created_at BETWEEN nu.registration_date AND nu.registration_date + INTERVAL '3 days';
            """, (action,))
            
            action_users = cursor.fetchone()[0]
            percentage = (action_users / total_count) * 100 if total_count > 0 else 0
            print(f"  {action}: {action_users:,} users ({percentage:.1f}%)")
        
        # Additional engagement metrics
        print(f"\n📱 ADDITIONAL ENGAGEMENT ACTIVITIES:")
        
        additional_actions = [
            'workout search performed',
            'workout sent',
            'cj save answer',
            'workout file uploaded',
            'cj create new plan click'
        ]
        
        for action in additional_actions:
            cursor.execute("""
                WITH new_users AS (
                    SELECT user_id, created_at as registration_date
                    FROM events 
                    WHERE name = 'new user registered' 
                    AND created_at >= NOW() - INTERVAL '30 days'
                    AND user_id IS NOT NULL
                )
                SELECT COUNT(DISTINCT e.user_id)
                FROM events e
                INNER JOIN new_users nu ON e.user_id = nu.user_id
                WHERE e.name = %s
                AND e.created_at BETWEEN nu.registration_date AND nu.registration_date + INTERVAL '3 days';
            """, (action,))
            
            action_users = cursor.fetchone()[0]
            percentage = (action_users / total_count) * 100 if total_count > 0 else 0
            print(f"  {action}: {action_users:,} users ({percentage:.1f}%)")
        
        # Show some example engaged users
        print(f"\n🌟 SAMPLE ENGAGED USERS:")
        cursor.execute("""
            WITH new_users AS (
                SELECT user_id, created_at as registration_date, json_data->>'username' as username
                FROM events 
                WHERE name = 'new user registered' 
                AND created_at >= NOW() - INTERVAL '30 days'
                AND user_id IS NOT NULL
            ),
            engaged_users AS (
                SELECT DISTINCT nu.user_id, nu.username, nu.registration_date
                FROM new_users nu
                INNER JOIN events e ON e.user_id = nu.user_id
                WHERE e.name IN ('workout downloaded', 'plan downloaded', 'activity downloaded', 
                               'subscription status changed to active', 'turbo activity created')
                AND e.created_at BETWEEN nu.registration_date AND nu.registration_date + INTERVAL '3 days'
                LIMIT 10
            )
            SELECT user_id, username, registration_date
            FROM engaged_users;
        """)
        
        engaged_samples = cursor.fetchall()
        for user_id, username, reg_date in engaged_samples:
            print(f"  User {username} (ID: {user_id}) - Registered: {reg_date}")
        
        # Show daily registration trend
        print(f"\n📅 RECENT REGISTRATION TREND:")
        cursor.execute("""
            SELECT 
                DATE(created_at) as reg_date,
                COUNT(*) as daily_registrations
            FROM events 
            WHERE name = 'new user registered' 
            AND created_at >= NOW() - INTERVAL '14 days'
            GROUP BY DATE(created_at)
            ORDER BY reg_date DESC;
        """)
        
        daily_registrations = cursor.fetchall()
        for date, count in daily_registrations:
            print(f"  {date}: {count:,} new users")
        
        # Summary insights
        print(f"\n💡 KEY INSIGHTS:")
        print(f"  • {engagement_rate:.1f}% of new users take meaningful action within 3 days")
        print(f"  • {(inactive_count/total_count)*100:.1f}% register but don't engage meaningfully")
        
        if engagement_rate < 20:
            print(f"  ⚠️  Low engagement rate - consider onboarding improvements")
        elif engagement_rate > 40:
            print(f"  ✅ Good engagement rate!")
        else:
            print(f"  📊 Moderate engagement rate - room for improvement")
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("\n✅ User engagement analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_user_engagement_optimized()