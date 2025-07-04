#!/usr/bin/env python3
"""
Test direct access to Google Play Console API without edit permissions.
"""

import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2 import service_account

def test_direct_api_access():
    """Test different API endpoints to see what works."""
    print("🧪 Testing Direct Google Play API Access")
    print("=" * 50)
    
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
    
    print(f"📱 Testing package: {package_name}")
    print()
    
    # Test different endpoints
    tests = [
        ("Reviews (read-only)", lambda: service.reviews().list(packageName=package_name).execute()),
        ("Purchases (read-only)", lambda: service.purchases().products().list(packageName=package_name).execute()),
        ("Internal App Sharing", lambda: service.internalappsharingartifacts().uploadapk(packageName=package_name).execute()),
        ("Edit (requires write access)", lambda: service.edits().insert(packageName=package_name, body={}).execute()),
    ]
    
    working_endpoints = []
    
    for test_name, test_func in tests:
        print(f"🔍 Testing {test_name}...")
        try:
            result = test_func()
            print(f"✅ {test_name}: SUCCESS")
            working_endpoints.append(test_name)
            
            # Show some data if it's reviews
            if "Reviews" in test_name and result:
                reviews = result.get('reviews', [])
                print(f"   📊 Found {len(reviews)} reviews")
                if reviews:
                    sample_review = reviews[0]
                    user_comment = sample_review.get('comments', [{}])[-1]
                    user_comment_details = user_comment.get('userComment', {})
                    rating = user_comment_details.get('starRating', 0)
                    print(f"   ⭐ Sample rating: {rating}/5")
                    
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg:
                print(f"❌ {test_name}: Permission denied")
            elif "404" in error_msg:
                print(f"❌ {test_name}: Not found")
            elif "400" in error_msg:
                print(f"❌ {test_name}: Bad request")
            else:
                print(f"❌ {test_name}: {error_msg[:100]}...")
        print()
    
    print("📋 Summary:")
    if working_endpoints:
        print(f"✅ Working endpoints: {', '.join(working_endpoints)}")
        
        if "Reviews" in working_endpoints:
            print("🎉 Reviews API is working! You can get review data.")
            
        print("\n💡 Next steps:")
        print("   1. Create a reviews-only script")
        print("   2. Skip the edit-based functionality")
        print("   3. Focus on read-only data")
        
    else:
        print("❌ No endpoints working - need to grant permissions in Play Console")
        print("   The service account needs access to your app")
    
    return working_endpoints

if __name__ == "__main__":
    test_direct_api_access()