#!/usr/bin/env python3
"""
TrainerDay App Store analytics and review monitoring.
"""

import os
import jwt
import time
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

class TrainerDayAppAnalytics:
    """TrainerDay specific App Store analytics client."""
    
    def __init__(self):
        """Initialize TrainerDay analytics client."""
        load_dotenv()
        
        self.key_id = os.getenv('KEY_ID')
        self.key_file = os.getenv('KEY_FILE')
        self.issuer_id = os.getenv('ISSUER_ID')
        self.app_id = os.getenv('APP_ID')
        self.bundle_id = os.getenv('BUNDLE_ID')
        
        self.base_url = "https://api.appstoreconnect.apple.com/v1"
        self.private_key = self._load_private_key()
        
    def _load_private_key(self):
        """Load the private key from .p8 file."""
        key_path = os.path.join(os.path.dirname(__file__), self.key_file)
        with open(key_path, 'r') as key_file:
            return key_file.read()
    
    def _generate_jwt_token(self):
        """Generate JWT token for API authentication."""
        headers = {
            'alg': 'ES256',
            'kid': self.key_id,
            'typ': 'JWT'
        }
        
        now = int(time.time())
        payload = {
            'iss': self.issuer_id,
            'iat': now,
            'exp': now + 1200,  # 20 minutes
            'aud': 'appstoreconnect-v1'
        }
        
        return jwt.encode(payload, self.private_key, algorithm='ES256', headers=headers)
    
    def _make_request(self, endpoint, params=None):
        """Make authenticated request to App Store Connect API."""
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
    
    def get_app_info(self):
        """Get TrainerDay app information."""
        print("📱 Getting TrainerDay app information...")
        result = self._make_request(f"/apps/{self.app_id}")
        
        if result:
            app_data = result.get('data', {})
            attributes = app_data.get('attributes', {})
            
            print(f"✅ App: {attributes.get('name', 'Unknown')}")
            print(f"📦 Bundle ID: {attributes.get('bundleId', 'Unknown')}")
            print(f"🏪 Primary Locale: {attributes.get('primaryLocale', 'Unknown')}")
            print(f"🔗 SKU: {attributes.get('sku', 'Unknown')}")
            
            return app_data
        return None
    
    def get_recent_reviews(self, limit=20, days_back=30):
        """Get recent customer reviews for TrainerDay."""
        print(f"📝 Getting last {limit} reviews from past {days_back} days...")
        
        params = {
            'limit': limit,
            'sort': '-createdDate'
        }
        
        result = self._make_request(f"/apps/{self.app_id}/customerReviews", params)
        
        if result:
            reviews = result.get('data', [])
            print(f"Found {len(reviews)} reviews")
            
            # Analyze reviews
            ratings = []
            recent_reviews = []
            
            from datetime import timezone
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
            
            for review in reviews:
                attributes = review.get('attributes', {})
                created_date = attributes.get('createdDate')
                
                if created_date:
                    review_date = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                    if review_date >= cutoff_date:
                        recent_reviews.append(review)
                        ratings.append(attributes.get('rating', 0))
            
            # Process all reviews for analysis since we got them
            for review in reviews:
                attributes = review.get('attributes', {})
                recent_reviews.append(review)
                ratings.append(attributes.get('rating', 0))
            
            if recent_reviews:
                avg_rating = sum(ratings) / len(ratings) if ratings else 0
                print(f"\n📊 Recent Reviews Analysis ({len(recent_reviews)} reviews):")
                print(f"⭐ Average Rating: {avg_rating:.1f}/5")
                print(f"📈 Rating Distribution:")
                for i in range(1, 6):
                    count = ratings.count(i)
                    percentage = (count / len(ratings)) * 100 if ratings else 0
                    print(f"   {i}⭐: {count} ({percentage:.1f}%)")
                
                print(f"\n📋 Latest Reviews:")
                for review in recent_reviews[:5]:
                    attributes = review.get('attributes', {})
                    rating = attributes.get('rating', 0)
                    title = attributes.get('title', 'No title')
                    body = attributes.get('body', 'No content')
                    date = attributes.get('createdDate', '')
                    
                    print(f"\n{rating}⭐ {title}")
                    print(f"Date: {date[:10] if date else 'Unknown'}")
                    print(f"Review: {body[:150]}{'...' if len(body) > 150 else ''}")
            
            return recent_reviews
        return []
    
    def get_app_versions(self):
        """Get app version information."""
        print("📱 Getting app versions...")
        result = self._make_request(f"/apps/{self.app_id}/appStoreVersions")
        
        if result:
            versions = result.get('data', [])
            print(f"Found {len(versions)} versions")
            
            for version in versions[:5]:  # Show latest 5
                attributes = version.get('attributes', {})
                print(f"  Version {attributes.get('versionString', 'Unknown')}")
                print(f"    State: {attributes.get('appStoreState', 'Unknown')}")
                print(f"    Created: {attributes.get('createdDate', 'Unknown')[:10]}")
                
            return versions
        return []
    
    def monitor_reviews(self):
        """Monitor and summarize review trends."""
        print("🔍 TrainerDay App Store Review Monitor")
        print("=" * 50)
        
        # Get app info
        self.get_app_info()
        print()
        
        # Get recent reviews
        reviews = self.get_recent_reviews(limit=50, days_back=30)
        
        if reviews:
            # Language analysis
            languages = {}
            for review in reviews:
                territory = review.get('attributes', {}).get('territory', 'Unknown')
                languages[territory] = languages.get(territory, 0) + 1
            
            print(f"\n🌍 Review Languages/Territories:")
            for territory, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(reviews)) * 100
                print(f"   {territory}: {count} ({percentage:.1f}%)")
        
        print()
        
        # Get version info
        self.get_app_versions()

def main():
    """Main function for TrainerDay analytics."""
    try:
        analytics = TrainerDayAppAnalytics()
        analytics.monitor_reviews()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()