#!/usr/bin/env python3
"""
Get subscription statistics from Google Play Console API.
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2 import service_account

def get_subscription_statistics():
    """Attempt to get subscription statistics for TrainerDay app."""
    load_dotenv()
    
    service_account_file = os.getenv('SERVICE_ACCOUNT_FILE')
    package_name = os.getenv('PACKAGE_NAME')
    
    service_account_path = os.path.join(os.path.dirname(__file__), service_account_file)
    
    # Build service
    scopes = ['https://www.googleapis.com/auth/androidpublisher']
    credentials = service_account.Credentials.from_service_account_file(
        service_account_path, scopes=scopes
    )
    service = build('androidpublisher', 'v3', credentials=credentials)
    
    print("💳 TrainerDay Subscription Statistics")
    print("=" * 45)
    print(f"📱 App: {package_name}")
    print()
    
    # Calculate last month
    today = datetime.now()
    last_month = today.replace(day=1) - timedelta(days=1)
    month_start = last_month.replace(day=1)
    
    print(f"📅 Period: {month_start.strftime('%B %Y')}")
    print(f"Date range: {month_start.strftime('%Y-%m-%d')} to {last_month.strftime('%Y-%m-%d')}")
    print()
    
    # Try different subscription-related endpoints
    approaches = [
        ("Purchases - Subscriptions", lambda: get_subscription_purchases(service, package_name)),
        ("Purchases - Products", lambda: get_product_purchases(service, package_name)),
        ("Subscription Management", lambda: get_subscription_management(service, package_name)),
        ("In-App Products", lambda: get_inapp_products(service, package_name)),
        ("Monetization Info", lambda: get_monetization_info(service, package_name)),
    ]
    
    subscription_data = {}
    
    for approach_name, approach_func in approaches:
        print(f"🔍 Trying {approach_name}...")
        try:
            result = approach_func()
            if result:
                print(f"✅ {approach_name}: Success")
                subscription_data[approach_name] = result
                
                # Display result summary
                if isinstance(result, dict):
                    if 'subscriptions' in result:
                        print(f"   Found {len(result['subscriptions'])} subscriptions")
                    elif 'inappproduct' in result:
                        print(f"   Found {len(result.get('inappproduct', []))} products")
                    elif 'purchases' in result:
                        print(f"   Found {len(result['purchases'])} purchases")
                    else:
                        print(f"   Data keys: {list(result.keys())}")
                elif isinstance(result, list):
                    print(f"   Found {len(result)} items")
                else:
                    print(f"   Result type: {type(result)}")
            else:
                print(f"❌ {approach_name}: No data returned")
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg:
                print(f"🔒 {approach_name}: Permission denied")
            elif "404" in error_msg:
                print(f"❓ {approach_name}: Not found/not available")
            elif "400" in error_msg:
                print(f"⚠️  {approach_name}: Bad request - {error_msg[:50]}...")
            else:
                print(f"❌ {approach_name}: {error_msg[:80]}...")
        print()
    
    # Summary
    print("📋 Subscription Access Summary:")
    if subscription_data:
        print("✅ Available subscription data:")
        for endpoint, data in subscription_data.items():
            print(f"   • {endpoint}")
        
        # Try to extract subscription counts
        analyze_subscription_data(subscription_data, month_start, last_month)
    else:
        print("❌ No subscription data accessible with current permissions")
        print("   • Subscription data often requires 'View financial data' permission")
        print("   • Or access through BigQuery export")
        print("   • Some data only available in web interface")

def get_subscription_purchases(service, package_name):
    """Try to get subscription purchase data."""
    # This usually requires financial permissions
    try:
        # First try to get list of subscription products
        result = service.purchases().subscriptions().list(packageName=package_name).execute()
        return result
    except Exception as e:
        # Try alternative approach
        return service.inappproducts().list(packageName=package_name).execute()

def get_product_purchases(service, package_name):
    """Try to get product purchase data."""
    try:
        result = service.purchases().products().list(packageName=package_name).execute()
        return result
    except:
        return None

def get_subscription_management(service, package_name):
    """Try subscription management endpoints."""
    try:
        # Check for subscription-related management
        edit_result = service.edits().insert(packageName=package_name, body={}).execute()
        edit_id = edit_result['id']
        
        try:
            # Try to get subscription info through edits
            result = service.edits().subscriptions().list(
                packageName=package_name,
                editId=edit_id
            ).execute()
            return result
        finally:
            service.edits().delete(packageName=package_name, editId=edit_id).execute()
    except:
        return None

def get_inapp_products(service, package_name):
    """Get in-app products (subscriptions are a type of in-app product)."""
    try:
        result = service.inappproducts().list(packageName=package_name).execute()
        return result
    except:
        return None

def get_monetization_info(service, package_name):
    """Try to get monetization information."""
    try:
        edit_result = service.edits().insert(packageName=package_name, body={}).execute()
        edit_id = edit_result['id']
        
        try:
            # Check for monetization details
            details = service.edits().details().get(
                packageName=package_name,
                editId=edit_id
            ).execute()
            
            # Look for subscription-related info
            if 'monetization' in details or 'subscriptions' in details:
                return details
                
        finally:
            service.edits().delete(packageName=package_name, editId=edit_id).execute()
    except:
        return None

def analyze_subscription_data(subscription_data, month_start, month_end):
    """Analyze any subscription data we found."""
    print()
    print("📊 Subscription Data Analysis:")
    print("-" * 30)
    
    for endpoint, data in subscription_data.items():
        print(f"\n🔍 Analyzing {endpoint}:")
        
        if isinstance(data, dict):
            # Look for subscription-related keys
            subscription_keys = ['subscriptions', 'inappproduct', 'purchases', 'products']
            
            for key in subscription_keys:
                if key in data:
                    items = data[key]
                    if isinstance(items, list):
                        print(f"   {key}: {len(items)} items")
                        
                        # Try to extract subscription info
                        for item in items[:3]:  # Show first 3
                            if isinstance(item, dict):
                                item_id = item.get('sku', item.get('productId', 'Unknown'))
                                item_type = item.get('purchaseType', item.get('type', 'Unknown'))
                                print(f"     • {item_id} ({item_type})")
                    else:
                        print(f"   {key}: {items}")
            
            # Check for other relevant keys
            other_keys = [k for k in data.keys() if k not in subscription_keys]
            if other_keys:
                print(f"   Other data: {other_keys}")

if __name__ == "__main__":
    get_subscription_statistics()