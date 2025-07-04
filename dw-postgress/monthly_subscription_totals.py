#!/usr/bin/env python3
"""
Get last completed month's subscription totals for cancelled and active subscriptions.
"""

import os
import sys
import psycopg2
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

def get_monthly_subscription_totals():
    """Get subscription totals for the last completed month."""
    
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
        
        # Calculate last completed month
        today = datetime.now()
        last_month = today.replace(day=1) - timedelta(days=1)  # Last day of previous month
        month_start = last_month.replace(day=1)  # First day of previous month
        next_month = month_start + relativedelta(months=1)  # First day of current month
        
        print(f"📊 SUBSCRIPTION TOTALS FOR {last_month.strftime('%B %Y')}")
        print(f"Period: {month_start.strftime('%Y-%m-%d')} to {(next_month - timedelta(days=1)).strftime('%Y-%m-%d')}")
        print("=" * 60)
        
        # Get new subscriptions (status changed to active)
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE created_at >= %s 
            AND created_at < %s 
            AND name = 'subscription status changed to active';
        """, (month_start, next_month))
        
        result = cursor.fetchone()
        new_subscriptions = result[0] if result else 0
        
        # Get canceled subscriptions
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE created_at >= %s 
            AND created_at < %s 
            AND (name = 'subscription status changed to canceled' 
                 OR name = 'subscription status changed to cancelled');
        """, (month_start, next_month))
        
        result = cursor.fetchone()
        canceled_subscriptions = result[0] if result else 0
        
        # Get suspended subscriptions
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE created_at >= %s 
            AND created_at < %s 
            AND name = 'subscription status changed to suspended';
        """, (month_start, next_month))
        
        result = cursor.fetchone()
        suspended_subscriptions = result[0] if result else 0
        
        # Get expired subscriptions
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE created_at >= %s 
            AND created_at < %s 
            AND name = 'subscription status changed to expired';
        """, (month_start, next_month))
        
        result = cursor.fetchone()
        expired_subscriptions = result[0] if result else 0
        
        # Get reactivation events
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE created_at >= %s 
            AND created_at < %s 
            AND name = 'billing: reactivation of subscription';
        """, (month_start, next_month))
        
        result = cursor.fetchone()
        reactivations = result[0] if result else 0
        
        # Calculate totals
        total_lost = canceled_subscriptions + suspended_subscriptions + expired_subscriptions
        net_change = new_subscriptions - total_lost + reactivations
        
        # Display results
        print(f"✅ NEW SUBSCRIPTIONS: {new_subscriptions}")
        print(f"❌ CANCELED SUBSCRIPTIONS: {canceled_subscriptions}")
        print(f"⏸️  SUSPENDED SUBSCRIPTIONS: {suspended_subscriptions}")
        print(f"⏰ EXPIRED SUBSCRIPTIONS: {expired_subscriptions}")
        print(f"🔄 REACTIVATIONS: {reactivations}")
        print("-" * 40)
        print(f"📉 TOTAL LOST: {total_lost}")
        print(f"📈 NET CHANGE: {net_change}")
        
        # Get some recent examples
        print(f"\n📋 RECENT ACTIVITY EXAMPLES:")
        cursor.execute("""
            SELECT name, created_at, user_id
            FROM events 
            WHERE created_at >= %s 
            AND created_at < %s 
            AND (name = 'subscription status changed to active' 
                 OR name = 'subscription status changed to canceled'
                 OR name = 'subscription status changed to cancelled')
            ORDER BY created_at DESC
            LIMIT 5;
        """, (month_start, next_month))
        
        examples = cursor.fetchall()
        for name, created_at, user_id in examples:
            status = "🟢 ACTIVE" if "active" in name else "🔴 CANCELED"
            print(f"  {created_at.strftime('%Y-%m-%d %H:%M')} - User {user_id} - {status}")
        
        # Calculate conversion metrics
        if new_subscriptions > 0:
            churn_rate = (total_lost / new_subscriptions) * 100
            print(f"\n📊 METRICS:")
            print(f"Churn Rate: {churn_rate:.1f}%")
            print(f"Retention Rate: {100 - churn_rate:.1f}%")
        
        # Close connection
        cursor.close()
        conn.close()
        
        return {
            'period': last_month.strftime('%B %Y'),
            'new_subscriptions': new_subscriptions,
            'canceled_subscriptions': canceled_subscriptions,
            'suspended_subscriptions': suspended_subscriptions,
            'expired_subscriptions': expired_subscriptions,
            'reactivations': reactivations,
            'total_lost': total_lost,
            'net_change': net_change
        }
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    get_monthly_subscription_totals()