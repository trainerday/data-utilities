#!/usr/bin/env python3
"""
Comprehensive test of what data is accessible via Google Play Console API.
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2 import service_account

def show_all_accessible_data():
    """Show all data that is currently accessible via the API."""
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
    
    print("📊 Complete Google Play Console API Data Access Report")
    print("=" * 60)
    print(f"📱 App: {package_name}")
    print(f"🕐 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. App Basic Information
    print("1️⃣ APP BASIC INFORMATION")
    print("-" * 30)
    try:
        edit_result = service.edits().insert(packageName=package_name, body={}).execute()
        edit_id = edit_result['id']
        
        try:
            # App details
            details = service.edits().details().get(packageName=package_name, editId=edit_id).execute()
            print("✅ App Details:")
            print(f"   Default Language: {details.get('defaultLanguage', 'Unknown')}")
            print(f"   Contact Email: {details.get('contactEmail', 'Unknown')}")
            print(f"   Contact Website: {details.get('contactWebsite', 'Unknown')}")
            print(f"   Contact Phone: {details.get('contactPhone', 'Unknown')}")
            
            # App listings
            listings = service.edits().listings().list(packageName=package_name, editId=edit_id).execute()
            print(f"\n✅ App Listings ({len(listings.get('listings', []))} languages):")
            for listing in listings.get('listings', []):
                lang = listing.get('language', 'unknown')
                title = listing.get('title', 'No title')
                short_desc = listing.get('shortDescription', 'No description')
                full_desc = listing.get('fullDescription', 'No description')
                
                print(f"   📍 {lang.upper()}:")
                print(f"      Title: {title}")
                print(f"      Short Description: {short_desc[:100]}{'...' if len(short_desc) > 100 else ''}")
                print(f"      Full Description: {len(full_desc)} characters")
                
                # Recent changes
                recent_changes = listing.get('recentChanges', 'No recent changes')
                print(f"      Recent Changes: {recent_changes[:100]}{'...' if len(recent_changes) > 100 else ''}")
                print()
        finally:
            service.edits().delete(packageName=package_name, editId=edit_id).execute()
            
    except Exception as e:
        print(f"❌ Error getting app details: {e}")
    
    print()
    
    # 2. App Versions
    print("2️⃣ APP VERSIONS")
    print("-" * 20)
    try:
        edit_result = service.edits().insert(packageName=package_name, body={}).execute()
        edit_id = edit_result['id']
        
        try:
            # APKs
            apks = service.edits().apks().list(packageName=package_name, editId=edit_id).execute()
            print(f"✅ APK Versions ({len(apks.get('apks', []))} found):")
            for apk in apks.get('apks', []):
                print(f"   Version Code: {apk.get('versionCode', 'Unknown')}")
                print(f"   Binary SHA1: {apk.get('binary', {}).get('sha1', 'Unknown')}")
                
            # Bundles (App Bundles)
            try:
                bundles = service.edits().bundles().list(packageName=package_name, editId=edit_id).execute()
                print(f"\n✅ App Bundles ({len(bundles.get('bundles', []))} found):")
                for bundle in bundles.get('bundles', []):
                    print(f"   Version Code: {bundle.get('versionCode', 'Unknown')}")
                    print(f"   SHA1: {bundle.get('sha1', 'Unknown')}")
            except:
                print("\n❌ App Bundles: Not accessible or none exist")
                
        finally:
            service.edits().delete(packageName=package_name, editId=edit_id).execute()
            
    except Exception as e:
        print(f"❌ Error getting versions: {e}")
    
    print()
    
    # 3. In-App Products
    print("3️⃣ IN-APP PRODUCTS & SUBSCRIPTIONS")
    print("-" * 40)
    try:
        products = service.inappproducts().list(packageName=package_name).execute()
        print(f"✅ In-App Products Response:")
        print(f"   Kind: {products.get('kind', 'Unknown')}")
        
        if products.get('inappproduct'):
            print(f"   Found {len(products['inappproduct'])} products:")
            for product in products['inappproduct']:
                print(f"     • SKU: {product.get('sku', 'Unknown')}")
                print(f"       Type: {product.get('purchaseType', 'Unknown')}")
                print(f"       Status: {product.get('status', 'Unknown')}")
                print(f"       Default Language: {product.get('defaultLanguage', 'Unknown')}")
        else:
            print("   📝 No in-app products found")
            print("      This could mean:")
            print("      • No subscriptions/products configured")
            print("      • Products not visible to API")
            print("      • Different permission level needed")
            
    except Exception as e:
        print(f"❌ Error getting in-app products: {e}")
    
    print()
    
    # 4. Reviews
    print("4️⃣ CUSTOMER REVIEWS")
    print("-" * 25)
    try:
        reviews = service.reviews().list(packageName=package_name, maxResults=10).execute()
        
        if reviews.get('reviews'):
            print(f"✅ Found {len(reviews['reviews'])} reviews:")
            
            for i, review in enumerate(reviews['reviews'][:5], 1):
                user_comment = review.get('comments', [{}])[-1]
                user_comment_details = user_comment.get('userComment', {})
                
                rating = user_comment_details.get('starRating', 0)
                text = user_comment_details.get('text', 'No text')
                last_modified = user_comment_details.get('lastModified', {})
                
                if 'seconds' in last_modified:
                    date = datetime.fromtimestamp(int(last_modified['seconds']))
                    date_str = date.strftime('%Y-%m-%d')
                else:
                    date_str = 'Unknown date'
                
                print(f"   {i}. {rating}⭐ ({date_str})")
                print(f"      {text[:100]}{'...' if len(text) > 100 else ''}")
                print()
        else:
            print("📝 No reviews found")
            print("   This could mean:")
            print("   • No reviews exist")
            print("   • Reviews not accessible via API")
            print("   • Different permission needed for reviews")
            
    except Exception as e:
        print(f"❌ Error getting reviews: {e}")
    
    print()
    
    # 5. Track Information
    print("5️⃣ RELEASE TRACKS")
    print("-" * 20)
    try:
        edit_result = service.edits().insert(packageName=package_name, body={}).execute()
        edit_id = edit_result['id']
        
        try:
            tracks = service.edits().tracks().list(packageName=package_name, editId=edit_id).execute()
            
            if tracks.get('tracks'):
                print(f"✅ Found {len(tracks['tracks'])} release tracks:")
                for track in tracks['tracks']:
                    track_name = track.get('track', 'Unknown')
                    releases = track.get('releases', [])
                    print(f"   📦 {track_name.upper()}: {len(releases)} releases")
                    
                    for release in releases[:2]:  # Show first 2 releases
                        version_codes = release.get('versionCodes', [])
                        status = release.get('status', 'Unknown')
                        print(f"      Version codes: {version_codes} ({status})")
            else:
                print("📝 No track information found")
                
        finally:
            service.edits().delete(packageName=package_name, editId=edit_id).execute()
            
    except Exception as e:
        print(f"❌ Error getting tracks: {e}")
    
    print()
    
    # 6. What We CAN'T Access
    print("❌ WHAT WE CANNOT ACCESS")
    print("-" * 30)
    print("🔒 Download Statistics:")
    print("   • Install counts")
    print("   • Active users")
    print("   • Uninstall rates")
    print()
    print("🔒 Financial Data:")
    print("   • Revenue information")
    print("   • Subscription purchase details")
    print("   • Individual transaction data")
    print()
    print("🔒 Advanced Analytics:")
    print("   • User acquisition data")
    print("   • Crash reports")
    print("   • Performance metrics")
    print()
    
    # Summary
    print("📋 SUMMARY")
    print("-" * 15)
    print("✅ What the API CAN provide:")
    print("   • Complete app metadata and descriptions")
    print("   • App version information and release tracks")
    print("   • In-app product configuration (if any)")
    print("   • Customer reviews (if accessible)")
    print("   • App listing details in multiple languages")
    print("   • Contact information and app details")
    print()
    print("❌ What requires additional permissions or methods:")
    print("   • Download/install statistics")
    print("   • Subscription purchase counts")
    print("   • Revenue and financial data")
    print("   • Advanced user analytics")

if __name__ == "__main__":
    show_all_accessible_data()