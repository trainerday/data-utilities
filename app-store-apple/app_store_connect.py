#!/usr/bin/env python3
"""
Apple App Store Connect API client for TrainerDay.
"""

import os
import jwt
import time
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

class AppStoreConnectAPI:
    """Client for Apple App Store Connect API."""
    
    def __init__(self):
        """Initialize App Store Connect API client."""
        load_dotenv()
        
        self.key_id = os.getenv('KEY_ID')
        self.key_file = os.getenv('KEY_FILE')
        self.issuer_id = os.getenv('ISSUER_ID')
        self.bundle_id = os.getenv('BUNDLE_ID')
        
        if not self.key_id or not self.key_file:
            raise ValueError("KEY_ID and KEY_FILE are required in .env file")
        
        self.base_url = "https://api.appstoreconnect.apple.com/v1"
        self.private_key = self._load_private_key()
        
    def _load_private_key(self):
        """Load the private key from .p8 file."""
        try:
            key_path = os.path.join(os.path.dirname(__file__), self.key_file)
            with open(key_path, 'r') as key_file:
                return key_file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Private key file {self.key_file} not found")
        except Exception as e:
            raise Exception(f"Error loading private key: {e}")
    
    def _generate_jwt_token(self):
        """Generate JWT token for API authentication."""
        if not self.issuer_id:
            raise ValueError("ISSUER_ID is required for JWT token generation")
        
        # JWT header
        headers = {
            'alg': 'ES256',
            'kid': self.key_id,
            'typ': 'JWT'
        }
        
        # JWT payload
        now = int(time.time())
        payload = {
            'iss': self.issuer_id,
            'iat': now,
            'exp': now + 1200,  # Token expires in 20 minutes
            'aud': 'appstoreconnect-v1'
        }
        
        # Generate token
        token = jwt.encode(payload, self.private_key, algorithm='ES256', headers=headers)
        return token
    
    def _make_request(self, endpoint, params=None):
        """Make authenticated request to App Store Connect API."""
        try:
            token = self._generate_jwt_token()
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ API request failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error making API request: {e}")
            return None
    
    def test_connection(self):
        """Test connection to App Store Connect API."""
        print("🔍 Testing App Store Connect API connection...")
        
        if not self.issuer_id:
            print("⚠️  ISSUER_ID not set - cannot generate JWT token")
            print("   Add ISSUER_ID to .env file to test API connection")
            return False
        
        try:
            # Test with a simple API call
            result = self._make_request("/apps")
            
            if result:
                apps = result.get('data', [])
                print(f"✅ API connection successful!")
                print(f"📱 Found {len(apps)} apps")
                return True
            else:
                print("❌ API connection failed")
                return False
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def get_apps(self):
        """Get list of apps."""
        print("📱 Getting apps...")
        result = self._make_request("/apps")
        
        if result:
            apps = result.get('data', [])
            print(f"Found {len(apps)} apps:")
            
            for app in apps:
                attributes = app.get('attributes', {})
                print(f"  - {attributes.get('name', 'Unknown')} ({attributes.get('bundleId', 'Unknown')})")
                
            return apps
        return []
    
    def get_app_analytics(self, app_id, metrics=['installs'], start_date=None, end_date=None):
        """Get analytics data for an app."""
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        params = {
            'filter[apps]': app_id,
            'filter[reportDate]': f"{start_date}..{end_date}",
            'filter[reportType]': 'SALES',
            'filter[reportSubType]': 'SUMMARY'
        }
        
        print(f"📊 Getting analytics for app {app_id} from {start_date} to {end_date}...")
        result = self._make_request("/salesReports", params)
        
        if result:
            print(f"✅ Analytics data retrieved")
            return result
        else:
            print("❌ Failed to get analytics data")
            return None
    
    def get_reviews(self, app_id=None):
        """Get customer reviews."""
        if app_id:
            endpoint = f"/apps/{app_id}/customerReviews"
        else:
            endpoint = "/customerReviews"
        
        print(f"📝 Getting reviews...")
        result = self._make_request(endpoint)
        
        if result:
            reviews = result.get('data', [])
            print(f"Found {len(reviews)} reviews")
            
            for review in reviews[:5]:  # Show first 5
                attributes = review.get('attributes', {})
                print(f"  - Rating: {attributes.get('rating', 'N/A')}/5")
                print(f"    Review: {attributes.get('body', 'No content')[:100]}...")
                
            return reviews
        return []
    
    def show_config(self):
        """Show current configuration."""
        print("🔧 App Store Connect API Configuration:")
        print(f"  Key ID: {self.key_id}")
        print(f"  Key File: {self.key_file}")
        print(f"  Issuer ID: {self.issuer_id or 'Not set'}")
        print(f"  Bundle ID: {self.bundle_id or 'Not set'}")
        print(f"  Private Key: {'Loaded' if self.private_key else 'Not loaded'}")

def main():
    """Main function to test App Store Connect API."""
    print("🍎 Apple App Store Connect API Test")
    print("=" * 50)
    
    try:
        client = AppStoreConnectAPI()
        
        # Show configuration
        client.show_config()
        print()
        
        # Test connection
        if client.test_connection():
            print()
            
            # Get apps
            apps = client.get_apps()
            
            if apps and len(apps) > 0:
                app_id = apps[0]['id']
                print(f"\n📊 Testing analytics for first app (ID: {app_id})...")
                client.get_app_analytics(app_id)
                
                print(f"\n📝 Testing reviews for first app...")
                client.get_reviews(app_id)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 To complete setup:")
        print("   1. Add ISSUER_ID to .env file (from App Store Connect)")
        print("   2. Optionally add BUNDLE_ID for your specific app")

if __name__ == "__main__":
    main()