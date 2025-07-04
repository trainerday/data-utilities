#!/usr/bin/env python3
"""
Google Play Console API client for TrainerDay.
"""

import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

try:
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
except ImportError:
    print("❌ Required packages not installed. Run:")
    print("   pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2")
    exit(1)

class PlayConsoleAPI:
    """Client for Google Play Console API."""
    
    def __init__(self):
        """Initialize Play Console API client."""
        load_dotenv()
        
        self.service_account_file = os.getenv('SERVICE_ACCOUNT_FILE')
        self.package_name = os.getenv('PACKAGE_NAME')
        self.track = os.getenv('TRACK', 'production')
        
        if not self.service_account_file or not self.package_name:
            raise ValueError("SERVICE_ACCOUNT_FILE and PACKAGE_NAME are required in .env file")
        
        # Build the service
        self.service = self._build_service()
    
    def _build_service(self):
        """Build the Google Play Console API service."""
        try:
            # Load service account credentials
            service_account_path = os.path.join(os.path.dirname(__file__), self.service_account_file)
            
            if not os.path.exists(service_account_path):
                raise FileNotFoundError(f"Service account file not found: {service_account_path}")
            
            # Define the scopes
            scopes = ['https://www.googleapis.com/auth/androidpublisher']
            
            # Create credentials
            credentials = service_account.Credentials.from_service_account_file(
                service_account_path, scopes=scopes
            )
            
            # Build the service
            service = build('androidpublisher', 'v3', credentials=credentials)
            return service
            
        except Exception as e:
            raise Exception(f"Failed to build Play Console service: {e}")
    
    def test_connection(self):
        """Test connection to Google Play Console API."""
        print("🔍 Testing Google Play Console API connection...")
        
        try:
            # Try to get app details
            result = self.service.edits().insert(
                packageName=self.package_name,
                body={}
            ).execute()
            
            edit_id = result['id']
            
            # Get app details
            app_details = self.service.edits().details().get(
                packageName=self.package_name,
                editId=edit_id
            ).execute()
            
            # Clean up the edit
            self.service.edits().delete(
                packageName=self.package_name,
                editId=edit_id
            ).execute()
            
            print(f"✅ API connection successful!")
            print(f"📱 Package: {self.package_name}")
            print(f"🏷️  Default Language: {app_details.get('defaultLanguage', 'Unknown')}")
            print(f"📧 Contact Email: {app_details.get('contactEmail', 'Unknown')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def get_app_details(self):
        """Get app details and metadata."""
        print("📱 Getting app details...")
        
        try:
            # Create edit
            edit_result = self.service.edits().insert(
                packageName=self.package_name,
                body={}
            ).execute()
            edit_id = edit_result['id']
            
            try:
                # Get app details
                details = self.service.edits().details().get(
                    packageName=self.package_name,
                    editId=edit_id
                ).execute()
                
                # Get app listings
                listings = self.service.edits().listings().list(
                    packageName=self.package_name,
                    editId=edit_id
                ).execute()
                
                print(f"📦 Package: {self.package_name}")
                print(f"🌐 Default Language: {details.get('defaultLanguage', 'Unknown')}")
                print(f"📧 Contact Email: {details.get('contactEmail', 'Unknown')}")
                print(f"🌍 Available Languages: {len(listings.get('listings', []))}")
                
                # Show listing details for default language
                if listings.get('listings'):
                    for listing in listings['listings']:
                        lang = listing.get('language', 'unknown')
                        title = listing.get('title', 'No title')
                        short_desc = listing.get('shortDescription', 'No description')
                        
                        print(f"\n📝 Listing ({lang}):")
                        print(f"   Title: {title}")
                        print(f"   Short Description: {short_desc[:100]}{'...' if len(short_desc) > 100 else ''}")
                
                return details, listings
                
            finally:
                # Always clean up the edit
                self.service.edits().delete(
                    packageName=self.package_name,
                    editId=edit_id
                ).execute()
                
        except Exception as e:
            print(f"❌ Error getting app details: {e}")
            return None, None
    
    def get_reviews(self, max_results=50):
        """Get user reviews."""
        print(f"📝 Getting reviews (max {max_results})...")
        
        try:
            # Get reviews
            reviews_result = self.service.reviews().list(
                packageName=self.package_name,
                maxResults=max_results
            ).execute()
            
            reviews = reviews_result.get('reviews', [])
            print(f"Found {len(reviews)} reviews")
            
            if reviews:
                # Analyze ratings
                ratings = []
                recent_reviews = []
                
                for review in reviews:
                    user_comment = review.get('comments', [{}])[-1]  # Latest comment
                    user_comment_details = user_comment.get('userComment', {})
                    
                    rating = user_comment_details.get('starRating', 0)
                    text = user_comment_details.get('text', '')
                    last_modified = user_comment_details.get('lastModified', {})
                    
                    ratings.append(rating)
                    recent_reviews.append({
                        'rating': rating,
                        'text': text,
                        'date': last_modified.get('seconds', 0)
                    })
                
                # Calculate statistics
                if ratings:
                    avg_rating = sum(ratings) / len(ratings)
                    print(f"\n📊 Review Analysis:")
                    print(f"⭐ Average Rating: {avg_rating:.1f}/5")
                    print(f"📈 Rating Distribution:")
                    
                    for i in range(1, 6):
                        count = ratings.count(i)
                        percentage = (count / len(ratings)) * 100 if ratings else 0
                        print(f"   {i}⭐: {count} ({percentage:.1f}%)")
                    
                    # Show latest reviews
                    print(f"\n📋 Latest Reviews:")
                    sorted_reviews = sorted(recent_reviews, key=lambda x: x['date'], reverse=True)
                    
                    for review in sorted_reviews[:5]:
                        rating = review['rating']
                        text = review['text']
                        date_ts = review['date']
                        
                        if date_ts:
                            date_str = datetime.fromtimestamp(int(date_ts)).strftime('%Y-%m-%d')
                        else:
                            date_str = 'Unknown date'
                        
                        print(f"\n{rating}⭐ {date_str}")
                        print(f"Review: {text[:150]}{'...' if len(text) > 150 else ''}")
            
            return reviews
            
        except Exception as e:
            print(f"❌ Error getting reviews: {e}")
            return []
    
    def get_statistics(self):
        """Get app statistics if available."""
        print("📊 Getting app statistics...")
        
        try:
            # Note: Statistics API requires special permissions
            # This is a placeholder for when those permissions are granted
            print("⚠️  Statistics API requires additional permissions")
            print("   Contact Google Play Console support to enable statistics API access")
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
    
    def show_config(self):
        """Show current configuration."""
        print("🔧 Google Play Console API Configuration:")
        print(f"  Service Account File: {self.service_account_file}")
        print(f"  Package Name: {self.package_name}")
        print(f"  Track: {self.track}")
        print(f"  Service: {'Initialized' if self.service else 'Not initialized'}")

def main():
    """Main function to test Google Play Console API."""
    print("🤖 Google Play Console API Test")
    print("=" * 50)
    
    try:
        client = PlayConsoleAPI()
        
        # Show configuration
        client.show_config()
        print()
        
        # Test connection
        if client.test_connection():
            print()
            
            # Get app details
            client.get_app_details()
            print()
            
            # Get reviews
            client.get_reviews(max_results=20)
            print()
            
            # Try to get statistics
            client.get_statistics()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Setup Instructions:")
        print("   1. Follow SETUP.md to create service account")
        print("   2. Download service-account.json to this directory")
        print("   3. Update .env with correct package name")
        print("   4. Install required packages:")
        print("      pip install google-api-python-client google-auth")

if __name__ == "__main__":
    main()