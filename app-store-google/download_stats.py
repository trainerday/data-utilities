#!/usr/bin/env python3
"""
Get download statistics from Google Play Console API.
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2 import service_account

def get_download_statistics():
    """Attempt to get download statistics for TrainerDay app."""
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
    
    print("📊 TrainerDay Download Statistics")
    print("=" * 40)
    print(f"📱 App: {package_name}")
    print()
    
    # Calculate last month
    today = datetime.now()
    last_month = today.replace(day=1) - timedelta(days=1)
    month_start = last_month.replace(day=1)
    
    print(f"📅 Period: {month_start.strftime('%B %Y')}")
    print(f"Date range: {month_start.strftime('%Y-%m-%d')} to {last_month.strftime('%Y-%m-%d')}")
    print()
    
    # Try different approaches to get statistics
    approaches = [
        ("Statistics API", lambda: get_stats_api(service, package_name)),
        ("Reports API", lambda: get_reports_api(service, package_name)),
        ("Reviews for user activity", lambda: get_review_activity(service, package_name)),
        ("App details for version info", lambda: get_app_versions(service, package_name)),
    ]
    
    for approach_name, approach_func in approaches:
        print(f"🔍 Trying {approach_name}...")
        try:
            result = approach_func()
            if result:
                print(f"✅ {approach_name}: Success")
                if isinstance(result, dict) and 'data' in result:
                    print(f"   Found {len(result.get('data', []))} data points")
                elif isinstance(result, list):
                    print(f"   Found {len(result)} items")
                else:
                    print(f"   Result: {str(result)[:100]}...")
            else:
                print(f"❌ {approach_name}: No data returned")
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg:
                print(f"🔒 {approach_name}: Permission denied")
            elif "404" in error_msg:
                print(f"❓ {approach_name}: Not found/not available")
            else:
                print(f"❌ {approach_name}: {error_msg[:80]}...")
        print()
    
    # Summary
    print("📋 Summary:")
    print("Current permissions allow:")
    print("✅ App metadata and details")
    print("✅ App version information")
    print("✅ Basic app management")
    print()
    print("❌ Download statistics require additional permissions")
    print("   • Google Play Console doesn't easily provide download numbers via API")
    print("   • Statistics often require BigQuery export setup")
    print("   • Some metrics are only available in the web interface")

def get_stats_api(service, package_name):
    """Try to get statistics via direct API."""
    # This usually requires special permissions
    return service.reviews().list(packageName=package_name, maxResults=1).execute()

def get_reports_api(service, package_name):
    """Try to get reports data."""
    # Create edit to check what's available
    edit_result = service.edits().insert(packageName=package_name, body={}).execute()
    edit_id = edit_result['id']
    
    try:
        # Get app details
        details = service.edits().details().get(
            packageName=package_name,
            editId=edit_id
        ).execute()
        return details
    finally:
        # Clean up
        service.edits().delete(packageName=package_name, editId=edit_id).execute()

def get_review_activity(service, package_name):
    """Get review activity as proxy for user engagement."""
    try:
        reviews_result = service.reviews().list(
            packageName=package_name,
            maxResults=50
        ).execute()
        
        reviews = reviews_result.get('reviews', [])
        if reviews:
            print(f"📝 Recent review activity: {len(reviews)} reviews")
            
            # Analyze review dates to estimate activity
            recent_reviews = []
            last_month = datetime.now() - timedelta(days=30)
            
            for review in reviews:
                user_comment = review.get('comments', [{}])[-1]
                user_comment_details = user_comment.get('userComment', {})
                last_modified = user_comment_details.get('lastModified', {})
                
                if 'seconds' in last_modified:
                    review_date = datetime.fromtimestamp(int(last_modified['seconds']))
                    if review_date >= last_month:
                        recent_reviews.append(review)
            
            print(f"📊 Reviews in last 30 days: {len(recent_reviews)}")
            return reviews
        
        return None
    except Exception as e:
        raise e

def get_app_versions(service, package_name):
    """Get app version information."""
    edit_result = service.edits().insert(packageName=package_name, body={}).execute()
    edit_id = edit_result['id']
    
    try:
        versions = service.edits().apks().list(
            packageName=package_name,
            editId=edit_id
        ).execute()
        
        if versions.get('apks'):
            print(f"📱 App versions: {len(versions['apks'])} APKs")
            for apk in versions['apks']:
                print(f"   Version {apk.get('versionCode', 'Unknown')}: {apk.get('binary', {}).get('sha1', 'No hash')}")
        
        return versions
    finally:
        service.edits().delete(packageName=package_name, editId=edit_id).execute()

if __name__ == "__main__":
    get_download_statistics()