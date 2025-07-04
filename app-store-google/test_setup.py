#!/usr/bin/env python3
"""
Test script to verify Google Play Console API setup.
"""

import os
from dotenv import load_dotenv

def check_setup():
    """Check the current setup status."""
    print("🔍 Google Play Console API Setup Check")
    print("=" * 50)
    
    load_dotenv()
    
    # Check environment variables
    service_account_file = os.getenv('SERVICE_ACCOUNT_FILE', 'service-account.json')
    package_name = os.getenv('PACKAGE_NAME')
    track = os.getenv('TRACK', 'production')
    
    print(f"📁 Service Account File: {service_account_file}")
    print(f"📦 Package Name: {package_name}")
    print(f"🎯 Track: {track}")
    print()
    
    # Check if service account file exists
    service_account_path = os.path.join(os.path.dirname(__file__), service_account_file)
    
    if os.path.exists(service_account_path):
        print(f"✅ Service account file found: {service_account_file}")
        
        try:
            import json
            with open(service_account_path, 'r') as f:
                sa_data = json.load(f)
            
            print(f"📧 Service Account Email: {sa_data.get('client_email', 'Unknown')}")
            print(f"🏢 Project ID: {sa_data.get('project_id', 'Unknown')}")
            
        except Exception as e:
            print(f"⚠️  Could not read service account file: {e}")
    else:
        print(f"❌ Service account file not found: {service_account_file}")
        print("   Download it from Google Cloud Console")
    
    print()
    
    # Check package name
    if package_name and package_name != 'com.trainerday.app':
        print(f"📱 Package name configured: {package_name}")
    else:
        print("⚠️  Default package name in use")
        print("   Update .env with your actual package name")
        print("   Common formats:")
        print("   - com.trainerday.app")
        print("   - com.company.appname")
        print("   - Find it in Google Play Console > App information")
    
    print()
    
    # Check if we can import required packages
    try:
        from googleapiclient.discovery import build
        from google.oauth2 import service_account
        print("✅ Required packages installed")
    except ImportError as e:
        print(f"❌ Missing packages: {e}")
        print("   Run: pip install -r requirements.txt")
    
    print()
    
    # Setup status
    has_service_account = os.path.exists(service_account_path)
    has_package_name = package_name and package_name != 'com.trainerday.app'
    
    if has_service_account and has_package_name:
        print("🎉 Setup looks complete! Try running: python3 play_console_api.py")
    elif has_service_account:
        print("🔧 Almost ready! Update the package name in .env")
    elif has_package_name:
        print("🔧 Almost ready! Add the service-account.json file")
    else:
        print("📋 Setup needed:")
        print("   1. Follow SETUP.md instructions")
        print("   2. Download service-account.json")
        print("   3. Update package name in .env")

if __name__ == "__main__":
    check_setup()