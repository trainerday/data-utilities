#!/usr/bin/env python3
"""
Simple Sentry API connection test to debug authentication.
"""

import os
import requests
from dotenv import load_dotenv

def test_sentry_connection():
    """Test basic Sentry API connectivity."""
    load_dotenv()
    
    auth_token = os.getenv('SENTRY_AUTH_TOKEN')
    base_url = os.getenv('SENTRY_URL')
    org = os.getenv('SENTRY_ORG')
    
    print(f"🔗 Testing connection to: {base_url}")
    print(f"🏢 Organization: {org}")
    print(f"🔑 Token: {auth_token[:20]}...")
    print("=" * 50)
    
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    
    # Test different endpoints
    endpoints = [
        f"{base_url}/api/0/",
        f"{base_url}/api/0/organizations/",
        f"{base_url}/api/0/organizations/{org}/",
        f"{base_url}/api/0/projects/"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\n📡 Testing: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=10, verify=False)
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"✅ Success - Found {len(data)} items")
                    else:
                        print(f"✅ Success - Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                except:
                    print(f"✅ Success - Response length: {len(response.text)}")
            else:
                print(f"❌ Error: {response.text[:200]}")
                
        except requests.exceptions.SSLError as e:
            print(f"🔒 SSL Error: {e}")
        except requests.exceptions.RequestException as e:
            print(f"🌐 Request Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    test_sentry_connection()