#!/usr/bin/env python3
"""
Analyze user engagement within 3 days of registration for users who registered in the last 30 days.
Track meaningful actions: downloads, subscriptions, and activity saves.
"""

import os
import sys
import psycopg2
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

def analyze_user_engagement():
    """Analyze user engagement within 3 days of registration."""
    
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
        
        # Get all users who registered in the last 30 days
        cursor.execute("""
            SELECT user_id, created_at, json_data->>'username' as username
            FROM events 
            WHERE name = 'new user registered' 
            AND created_at >= NOW() - INTERVAL '30 days'
            AND user_id IS NOT NULL
            ORDER BY created_at DESC;
        """)
        
        new_users = cursor.fetchall()
        total_new_users = len(new_users)
        
        print(f"Total new registrations in last 30 days: {total_new_users:,}")
        
        if total_new_users == 0:
            print("No new registrations found in the last 30 days.")
            return
        
        # Define meaningful actions
        meaningful_actions = [
            'workout downloaded',
            'plan downloaded', 
            'activity downloaded',
            'subscription status changed to active',
            'turbo activity created'  # This is saving/completing an activity
        ]
        
        # Additional engagement indicators
        engagement_actions = [
            'workout search performed',
            'workout sent',
            'cj save answer',
            'workout file uploaded',
            'cj create new plan click',
            'cj questions answered'
        ]
        
        all_tracked_actions = meaningful_actions + engagement_actions
        
        engaged_users = []
        inactive_users = []
        user_activity_summary = []
        
        print(f"\nAnalyzing engagement for {total_new_users} new users...")
        
        # Analyze each new user
        for i, (user_id, registration_date, username) in enumerate(new_users):
            if i % 50 == 0:  # Progress indicator
                print(f"  Processed {i}/{total_new_users} users...")
            
            # Look for activities within 3 days of registration
            three_days_later = registration_date + timedelta(days=3)
            
            cursor.execute("""
                SELECT name, COUNT(*) as count
                FROM events 
                WHERE user_id = %s 
                AND created_at BETWEEN %s AND %s
                AND name IN %s
                GROUP BY name
                ORDER BY count DESC;
            """, (user_id, registration_date, three_days_later, tuple(all_tracked_actions)))
            
            user_actions = cursor.fetchall()
            
            # Check for meaningful actions
            has_meaningful_action = any(
                action[0] in meaningful_actions for action in user_actions
            )
            
            # Categorize user
            if has_meaningful_action:
                engaged_users.append({
                    'user_id': user_id,
                    'username': username,
                    'registration_date': registration_date,
                    'actions': user_actions
                })
            else:
                inactive_users.append({
                    'user_id': user_id,
                    'username': username,
                    'registration_date': registration_date,
                    'actions': user_actions
                })
            
            user_activity_summary.append({
                'user_id': user_id,
                'username': username,
                'registration_date': registration_date,
                'actions': user_actions,
                'engaged': has_meaningful_action
            })
        
        # Calculate percentages
        engaged_count = len(engaged_users)
        inactive_count = len(inactive_users)
        engagement_rate = (engaged_count / total_new_users) * 100
        
        print(f"\n📈 ENGAGEMENT ANALYSIS RESULTS:")
        print(f"=" * 50)
        print(f"Total new users (last 30 days): {total_new_users:,}")
        print(f"Users who took meaningful action within 3 days: {engaged_count:,} ({engagement_rate:.1f}%)")
        print(f"Users who remained inactive: {inactive_count:,} ({(inactive_count/total_new_users)*100:.1f}%)")
        
        # Break down meaningful actions
        print(f"\n🎯 MEANINGFUL ACTIONS BREAKDOWN:")
        print(f"(Actions within 3 days of registration)")
        
        action_counts = {}
        for user in engaged_users:
            for action_name, count in user['actions']:
                if action_name in meaningful_actions:
                    if action_name not in action_counts:
                        action_counts[action_name] = 0
                    action_counts[action_name] += 1
        
        for action in meaningful_actions:
            count = action_counts.get(action, 0)
            percentage = (count / total_new_users) * 100
            print(f"  {action}: {count:,} users ({percentage:.1f}%)")
        
        # Show engagement activities breakdown
        print(f"\n📱 ALL ENGAGEMENT ACTIVITIES:")
        print(f"(Any activity within 3 days of registration)")
        
        all_action_counts = {}
        for user in user_activity_summary:
            for action_name, count in user['actions']:
                if action_name not in all_action_counts:
                    all_action_counts[action_name] = 0
                all_action_counts[action_name] += 1
        
        # Sort by frequency
        sorted_actions = sorted(all_action_counts.items(), key=lambda x: x[1], reverse=True)
        
        for action_name, user_count in sorted_actions:
            percentage = (user_count / total_new_users) * 100
            is_meaningful = "⭐" if action_name in meaningful_actions else "  "
            print(f"{is_meaningful} {action_name}: {user_count:,} users ({percentage:.1f}%)")
        
        # Show examples of engaged users
        print(f"\n🌟 EXAMPLES OF ENGAGED USERS:")
        for i, user in enumerate(engaged_users[:10]):
            print(f"  User {user['username']} (ID: {user['user_id']}):")
            print(f"    Registered: {user['registration_date']}")
            for action_name, count in user['actions'][:3]:  # Show top 3 actions
                print(f"    - {action_name}: {count} times")
            print()
        
        # Show examples of inactive users
        print(f"\n😴 EXAMPLES OF INACTIVE USERS:")
        inactive_sample = inactive_users[:10]
        for user in inactive_sample:
            action_summary = f" (did: {', '.join([a[0] for a in user['actions'][:2]])})" if user['actions'] else " (no tracked actions)"
            print(f"  User {user['username']} (ID: {user['user_id']}){action_summary}")
        
        # Daily engagement trend
        print(f"\n📅 DAILY REGISTRATION & ENGAGEMENT TREND:")
        cursor.execute("""
            SELECT 
                DATE(created_at) as reg_date,
                COUNT(*) as daily_registrations
            FROM events 
            WHERE name = 'new user registered' 
            AND created_at >= NOW() - INTERVAL '30 days'
            GROUP BY DATE(created_at)
            ORDER BY reg_date DESC
            LIMIT 10;
        """)
        
        daily_registrations = cursor.fetchall()
        print(f"Recent daily registration numbers:")
        for date, count in daily_registrations:
            print(f"  {date}: {count:,} new users")
        
        # Summary insights
        print(f"\n💡 KEY INSIGHTS:")
        print(f"  • {engagement_rate:.1f}% of new users take meaningful action within 3 days")
        print(f"  • Top meaningful action: {max(action_counts.items(), key=lambda x: x[1]) if action_counts else 'None'}")
        print(f"  • {(inactive_count/total_new_users)*100:.1f}% of users register but don't engage meaningfully")
        
        if engagement_rate < 20:
            print(f"  ⚠️  Low engagement rate - consider onboarding improvements")
        elif engagement_rate > 40:
            print(f"  ✅ Good engagement rate!")
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("\n✅ User engagement analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_user_engagement()