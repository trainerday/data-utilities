#!/usr/bin/env python3
"""
Sentry API client for TrainerDay with proper authentication handling.
"""

import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

class SentryAPI:
    """Simplified Sentry API client."""
    
    def __init__(self):
        """Initialize Sentry API client."""
        load_dotenv()
        
        self.auth_token = os.getenv('SENTRY_AUTH_TOKEN')
        self.base_url = os.getenv('SENTRY_URL', 'https://sentry.trainerday.com:9443')
        self.org = os.getenv('SENTRY_ORG', 'trainerday')
        
        if not self.auth_token:
            raise ValueError("SENTRY_AUTH_TOKEN environment variable is required")
        
        self.headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json'
        }
        
        self.base_url = self.base_url.rstrip('/')
    
    def get_api_info(self):
        """Get basic API information."""
        try:
            url = f"{self.base_url}/api/0/"
            response = requests.get(url, headers=self.headers, timeout=30, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Sentry API Connection Successful!")
                print(f"Version: {data.get('version', 'Unknown')}")
                print(f"User: {data.get('user', {}).get('email', 'Unknown')}")
                print(f"Auth: {data.get('auth', {})}")
                return data
            else:
                print(f"❌ API call failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error connecting to Sentry API: {e}")
            return None
    
    def test_permissions(self):
        """Test what endpoints are accessible with current token."""
        test_endpoints = [
            ('/api/0/', 'Basic API info'),
            ('/api/0/organizations/', 'Organizations list'),
            (f'/api/0/organizations/{self.org}/', 'Organization details'),
            (f'/api/0/organizations/{self.org}/projects/', 'Projects list'),
            ('/api/0/projects/', 'Global projects'),
            ('/api/0/issues/', 'Global issues'),
        ]
        
        print("🔍 Testing endpoint permissions:")
        print("=" * 50)
        
        accessible_endpoints = []
        
        for endpoint, description in test_endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = requests.get(url, headers=self.headers, timeout=10, verify=False)
                
                if response.status_code == 200:
                    print(f"✅ {description}: Accessible")
                    accessible_endpoints.append(endpoint)
                elif response.status_code == 403:
                    print(f"🔒 {description}: Permission denied")
                elif response.status_code == 404:
                    print(f"❓ {description}: Not found")
                else:
                    print(f"❌ {description}: Error {response.status_code}")
                    
            except Exception as e:
                print(f"💥 {description}: Exception - {e}")
        
        return accessible_endpoints
    
    def get_user_info(self):
        """Get current user information."""
        try:
            url = f"{self.base_url}/api/0/"
            response = requests.get(url, headers=self.headers, timeout=30, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                user_info = data.get('user', {})
                return {
                    'id': user_info.get('id'),
                    'email': user_info.get('email'),
                    'name': user_info.get('name'),
                    'username': user_info.get('username'),
                    'isActive': user_info.get('isActive'),
                    'dateJoined': user_info.get('dateJoined')
                }
            return None
            
        except Exception as e:
            print(f"❌ Error getting user info: {e}")
            return None
    
    def search_issues(self, query="", limit=10):
        """Search for issues if accessible."""
        try:
            # Try different issue endpoints
            endpoints = [
                f"/api/0/organizations/{self.org}/issues/",
                "/api/0/issues/"
            ]
            
            for endpoint in endpoints:
                try:
                    url = f"{self.base_url}{endpoint}"
                    params = {
                        'limit': limit,
                        'query': query
                    }
                    
                    response = requests.get(url, headers=self.headers, params=params, timeout=30, verify=False)
                    
                    if response.status_code == 200:
                        issues = response.json()
                        print(f"📋 Found {len(issues)} issues via {endpoint}")
                        for issue in issues:
                            print(f"  - {issue.get('title', 'No title')[:80]}")
                        return issues
                    elif response.status_code != 403:
                        print(f"⚠️  Endpoint {endpoint}: {response.status_code}")
                        
                except Exception as e:
                    print(f"💥 Error with {endpoint}: {e}")
                    continue
            
            print("🔒 No accessible issue endpoints found")
            return []
            
        except Exception as e:
            print(f"❌ Error searching issues: {e}")
            return []

def main():
    """Main function to test Sentry API."""
    print("🎯 Sentry API Test - TrainerDay")
    print("=" * 40)
    
    try:
        api = SentryAPI()
        
        # Get basic API info
        api_info = api.get_api_info()
        print()
        
        # Test permissions
        accessible = api.test_permissions()
        print()
        
        # Get user info
        user_info = api.get_user_info()
        if user_info:
            print("👤 Current User Info:")
            for key, value in user_info.items():
                if value is not None:
                    print(f"  {key}: {value}")
        print()
        
        # Try to search issues
        print("🐛 Attempting to search issues...")
        api.search_issues(limit=5)
        
        print("\n✅ Sentry API setup complete!")
        print("Available functionality depends on token permissions.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()