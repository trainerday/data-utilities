#!/usr/bin/env python3
"""
Sentry API client for TrainerDay.
"""

import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

class SentryClient:
    """Client for interacting with Sentry API."""
    
    def __init__(self):
        """Initialize Sentry client with environment variables."""
        load_dotenv()
        
        self.auth_token = os.getenv('SENTRY_AUTH_TOKEN')
        self.base_url = os.getenv('SENTRY_URL')
        self.org = os.getenv('SENTRY_ORG')
        
        if not all([self.auth_token, self.base_url, self.org]):
            raise ValueError("Missing required environment variables: SENTRY_AUTH_TOKEN, SENTRY_URL, SENTRY_ORG")
        
        self.headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json'
        }
        
        # Remove trailing slash from base_url if present
        self.base_url = self.base_url.rstrip('/')
    
    def test_connection(self):
        """Test connection to Sentry API."""
        try:
            url = f"{self.base_url}/api/0/organizations/{self.org}/"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                org_data = response.json()
                print(f"✅ Successfully connected to Sentry!")
                print(f"Organization: {org_data.get('name', 'Unknown')}")
                print(f"Slug: {org_data.get('slug', 'Unknown')}")
                return True
            else:
                print(f"❌ Connection failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def get_projects(self):
        """Get list of projects in the organization."""
        try:
            url = f"{self.base_url}/api/0/organizations/{self.org}/projects/"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                projects = response.json()
                print(f"📁 Found {len(projects)} projects:")
                for project in projects:
                    print(f"  - {project['name']} (ID: {project['id']})")
                return projects
            else:
                print(f"❌ Failed to get projects: {response.status_code}")
                print(f"Response: {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting projects: {e}")
            return []
    
    def get_issues(self, project_id=None, limit=10, days_back=7):
        """Get recent issues from Sentry."""
        try:
            if project_id:
                url = f"{self.base_url}/api/0/projects/{self.org}/{project_id}/issues/"
            else:
                url = f"{self.base_url}/api/0/organizations/{self.org}/issues/"
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            params = {
                'limit': limit,
                'query': f'is:unresolved',
                'statsPeriod': f'{days_back}d'
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                issues = response.json()
                print(f"🐛 Found {len(issues)} recent issues:")
                for issue in issues[:limit]:
                    print(f"  - {issue['title'][:80]}...")
                    print(f"    Count: {issue.get('count', 0)}, Last seen: {issue.get('lastSeen', 'Unknown')}")
                return issues
            else:
                print(f"❌ Failed to get issues: {response.status_code}")
                print(f"Response: {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting issues: {e}")
            return []
    
    def get_stats(self, project_id=None, days_back=7):
        """Get project statistics."""
        try:
            if project_id:
                url = f"{self.base_url}/api/0/projects/{self.org}/{project_id}/stats/"
            else:
                # Get stats for all projects
                projects = self.get_projects()
                if not projects:
                    return {}
                
                stats = {}
                for project in projects:
                    project_stats = self._get_project_stats(project['slug'], days_back)
                    if project_stats:
                        stats[project['name']] = project_stats
                return stats
            
            return self._get_project_stats(project_id, days_back)
                
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {}
    
    def _get_project_stats(self, project_slug, days_back):
        """Get statistics for a specific project."""
        try:
            url = f"{self.base_url}/api/0/projects/{self.org}/{project_slug}/stats/"
            
            params = {
                'stat': 'received',
                'since': (datetime.now() - timedelta(days=days_back)).timestamp(),
                'until': datetime.now().timestamp(),
                'resolution': '1d'
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get stats for {project_slug}: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting project stats: {e}")
            return None

def main():
    """Main function to test Sentry client."""
    print("🔍 Sentry API Connection Test")
    print("=" * 40)
    
    try:
        client = SentryClient()
        
        # Test connection
        if client.test_connection():
            print()
            
            # Get projects
            projects = client.get_projects()
            print()
            
            # Get recent issues
            if projects:
                print("📊 Getting recent issues...")
                client.get_issues(limit=5, days_back=7)
                print()
                
                # Get stats for first project
                if len(projects) > 0:
                    project_slug = projects[0]['slug']
                    print(f"📈 Getting stats for {projects[0]['name']}...")
                    stats = client.get_stats(project_slug, days_back=7)
                    if stats:
                        print(f"Stats data points: {len(stats)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()