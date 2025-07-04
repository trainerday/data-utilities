#!/usr/bin/env python3
"""
Get detailed subscription information from Google Play Console API.
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2 import service_account

def get_detailed_subscriptions():
    """Get detailed subscription information."""
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
    
    print("💳 Detailed TrainerDay Subscription Analysis")
    print("=" * 50)
    print(f"📱 App: {package_name}")
    print()
    
    # Try to get subscription products configuration
    print("🔍 Getting subscription products configuration...")
    try:
        # List in-app products (subscriptions are a type of in-app product)
        products_result = service.inappproducts().list(packageName=package_name).execute()
        
        print(f"📦 Products API Response:")
        print(f"   Kind: {products_result.get('kind', 'Unknown')}")
        
        if 'inappproduct' in products_result:
            products = products_result['inappproduct']
            print(f"   Found {len(products)} in-app products")
            
            for product in products:
                print(f"     • SKU: {product.get('sku', 'Unknown')}")
                print(f"       Type: {product.get('purchaseType', 'Unknown')}")
                print(f"       Status: {product.get('status', 'Unknown')}")
                print()
        else:
            print("   No in-app products found")
            print("   This might mean:")
            print("   • No subscription products configured")
            print("   • Products not visible to API")
            print("   • Additional permissions needed")
        
    except Exception as e:
        print(f"❌ Error getting products: {e}")
    
    print()
    
    # Try to get subscription purchases
    print("🔍 Checking subscription purchases access...")
    try:
        # Try to access subscription purchases (requires financial permissions)
        subscriptions_result = service.purchases().subscriptions().list(packageName=package_name).execute()
        
        print(f"💰 Subscription Purchases Response:")
        print(f"   Kind: {subscriptions_result.get('kind', 'Unknown')}")
        
        if 'purchases' in subscriptions_result:
            purchases = subscriptions_result['purchases']
            print(f"   Found {len(purchases)} subscription purchases")
            
            # Analyze purchases for last month
            last_month = datetime.now().replace(day=1) - timedelta(days=1)
            month_start = last_month.replace(day=1)
            
            recent_purchases = []
            for purchase in purchases:
                # Check purchase date
                purchase_time = purchase.get('startTimeMillis')
                if purchase_time:
                    purchase_date = datetime.fromtimestamp(int(purchase_time) / 1000)
                    if purchase_date >= month_start:
                        recent_purchases.append(purchase)
            
            print(f"   Recent purchases (last month): {len(recent_purchases)}")
            
        else:
            print("   No subscription purchases data")
            print("   This typically means:")
            print("   • 'View financial data' permission required")
            print("   • No subscription purchases to show")
            print("   • Data restricted by Google")
        
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg:
            print("🔒 Subscription purchases require 'View financial data' permission")
        else:
            print(f"❌ Error getting purchases: {e}")
    
    print()
    
    # Check what permissions we actually have
    print("🔧 Permission Check:")
    print("Current service account permissions likely include:")
    print("✅ View app information")
    print("✅ Download bulk reports") 
    print("❓ View financial data (needed for subscription purchases)")
    print()
    print("💡 To get subscription counts, you may need to:")
    print("1. Add 'View financial data' permission to the service account")
    print("2. Use Google Play Console web interface manually")
    print("3. Set up BigQuery export for detailed analytics")

def check_current_permissions_detailed():
    """Check what the current permissions allow us to see."""
    print()
    print("🎯 What We Can Currently Access:")
    print("-" * 35)
    
    # Test basic access
    load_dotenv()
    service_account_file = os.getenv('SERVICE_ACCOUNT_FILE')
    package_name = os.getenv('PACKAGE_NAME')
    service_account_path = os.path.join(os.path.dirname(__file__), service_account_file)
    
    scopes = ['https://www.googleapis.com/auth/androidpublisher']
    credentials = service_account.Credentials.from_service_account_file(
        service_account_path, scopes=scopes
    )
    service = build('androidpublisher', 'v3', credentials=credentials)
    
    # Test different access levels
    access_tests = [
        ("App basic info", lambda: service.edits().insert(packageName=package_name, body={}).execute()),
        ("In-app products list", lambda: service.inappproducts().list(packageName=package_name).execute()),
        ("Reviews access", lambda: service.reviews().list(packageName=package_name, maxResults=1).execute()),
    ]
    
    for test_name, test_func in access_tests:
        try:
            result = test_func()
            if result:
                print(f"✅ {test_name}: Accessible")
                
                # Clean up edit if needed
                if 'id' in result:
                    service.edits().delete(packageName=package_name, editId=result['id']).execute()
            else:
                print(f"❓ {test_name}: Empty response")
        except Exception as e:
            if "403" in str(e):
                print(f"🔒 {test_name}: Permission denied")
            else:
                print(f"❌ {test_name}: Error")

if __name__ == "__main__":
    get_detailed_subscriptions()
    check_current_permissions_detailed()