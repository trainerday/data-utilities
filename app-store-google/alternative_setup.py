#!/usr/bin/env python3
"""
Alternative approaches to set up Google Play Console API access.
"""

def show_alternative_approaches():
    """Show different approaches to set up API access."""
    print("🔄 Alternative Google Play Console API Setup")
    print("=" * 50)
    print()
    
    print("🎯 Current Status:")
    print("   ✅ Service Account: claude-access@claude-play-store-api-access.iam.gserviceaccount.com")
    print("   ✅ Package Name: trainerday.turbo (confirmed)")
    print("   ❌ Permissions: Service account needs access")
    print()
    
    print("🔍 Method 1: Developer Account Level")
    print("1. Go to https://play.google.com/console/")
    print("2. DON'T select an app yet")
    print("3. Look for account settings or developer settings")
    print("4. Look for 'API access' at the ACCOUNT level")
    print("5. This might be under your profile/settings")
    print()
    
    print("🔍 Method 2: All Apps View")
    print("1. Go to https://play.google.com/console/")
    print("2. Stay on the 'All apps' view (don't click into an app)")
    print("3. Look for 'Settings' or 'API access' in this view")
    print("4. Check the left sidebar or top menu")
    print()
    
    print("🔍 Method 3: Direct URLs")
    print("Try these direct links (they might work):")
    print("• https://play.google.com/console/api-access")
    print("• https://play.google.com/console/cloud-integration")
    print("• https://play.google.com/console/settings")
    print()
    
    print("🔍 Method 4: Google Cloud Console Approach")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Select project: claude-play-store-api-access")
    print("3. Go to 'APIs & Services' → 'Credentials'")
    print("4. Click on the service account")
    print("5. Look for 'Enable Google Play Console' or similar")
    print()
    
    print("🔍 Method 5: App-Specific (If Found)")
    print("Once you select TrainerDay app:")
    print("• Look for 'App information' → 'Advanced settings'")
    print("• Check 'Release' → 'Setup' → any subsections")
    print("• Look for 'Settings' or gear icons anywhere")
    print()
    
    print("📋 What the API Access Page Should Look Like:")
    print("• Title: 'API access' or 'Google Cloud integration'")
    print("• Section: 'Linked Google Cloud projects'")
    print("• Your project: claude-play-store-api-access")
    print("• Service accounts list with grant/revoke options")
    print()
    
    print("🆘 If Still Can't Find It:")
    print("1. Check if your Google account has API access permissions")
    print("2. Try a different browser or incognito mode")
    print("3. Make sure you're the owner/admin of the Play Console account")
    print("4. The feature might be restricted or moved")
    print()
    
    print("💡 Quick Test - Check Current Permissions:")
    print("   Let's see exactly what permissions we have...")

def test_current_permissions():
    """Test what we can access with current permissions."""
    print()
    print("🧪 Testing Current API Permissions...")
    print("-" * 30)
    
    try:
        from dotenv import load_dotenv
        from googleapiclient.discovery import build
        from google.oauth2 import service_account
        import os
        
        load_dotenv()
        
        service_account_file = os.getenv('SERVICE_ACCOUNT_FILE')
        service_account_path = os.path.join(os.path.dirname(__file__), service_account_file)
        
        scopes = ['https://www.googleapis.com/auth/androidpublisher']
        credentials = service_account.Credentials.from_service_account_file(
            service_account_path, scopes=scopes
        )
        
        service = build('androidpublisher', 'v3', credentials=credentials)
        
        # Try different endpoints to see what works
        test_calls = [
            ("Basic service", lambda: service._http),
            ("App without package", lambda: service.edits().insert(packageName="test", body={})),
        ]
        
        for test_name, test_func in test_calls:
            try:
                result = test_func()
                print(f"✅ {test_name}: Working")
            except Exception as e:
                print(f"❌ {test_name}: {str(e)[:100]}...")
        
    except Exception as e:
        print(f"❌ Error setting up test: {e}")

if __name__ == "__main__":
    show_alternative_approaches()
    test_current_permissions()