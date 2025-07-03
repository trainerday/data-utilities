#!/usr/bin/env python3
"""
Mautic Campaign Statistics Analyzer
Gets time-based statistics for email campaigns
"""

import requests
import json
from typing import Dict
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

class MauticCampaignStats:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.auth = (username, password)
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    def get_campaigns(self) -> Dict:
        """Get all campaigns"""
        try:
            response = requests.get(
                f"{self.base_url}/api/campaigns",
                auth=self.auth,
                headers=self.headers,
                params={'limit': 100}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching campaigns: {e}")
            return {}
    
    def get_campaign_contacts(self, campaign_id: int, days_back: int = 30) -> Dict:
        """Get contacts added to a campaign in recent days"""
        date_from = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        try:
            response = requests.get(
                f"{self.base_url}/api/campaigns/{campaign_id}/contacts",
                auth=self.auth,
                headers=self.headers,
                params={
                    'dateFrom': date_from,
                    'limit': 1000
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching campaign contacts: {e}")
            return {}
    
    def get_email_message_stats(self, email_id: int) -> Dict:
        """Get message statistics for an email"""
        try:
            # Try the stats endpoint
            response = requests.get(
                f"{self.base_url}/api/stats/email/{email_id}",
                auth=self.auth,
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            
            # Fallback to email endpoint with stats
            response = requests.get(
                f"{self.base_url}/api/emails/{email_id}?includeStat=true",
                auth=self.auth,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching email stats: {e}")
            return {}
    
    def analyze_onboarding_stats(self):
        """Analyze onboarding email statistics"""
        print("\n=== MAUTIC CAMPAIGN & EMAIL STATISTICS ===\n")
        
        # First, let's see what campaigns exist
        print("Fetching campaigns...")
        campaigns = self.get_campaigns()
        
        if campaigns and 'campaigns' in campaigns:
            print(f"\nFound {len(campaigns['campaigns'])} campaigns:")
            for camp_id, camp_data in campaigns['campaigns'].items():
                print(f"  ID: {camp_id} - {camp_data.get('name', 'Unknown')}")
                # Check recent activity
                recent = self.get_campaign_contacts(int(camp_id), days_back=30)
                if recent and 'total' in recent:
                    print(f"    Recent contacts (30 days): {recent['total']}")
        
        # Get detailed stats for onboarding emails
        onboarding_emails = [
            {"id": 11, "name": "Welcome"},
            {"id": 7, "name": "Quick Tour"},
            {"id": 8, "name": "App Settings"},
            {"id": 9, "name": "Checking In"}
        ]
        
        print("\n=== ONBOARDING EMAIL DETAILED STATS ===\n")
        
        for email in onboarding_emails:
            print(f"\n{email['name']} (ID: {email['id']}):")
            stats = self.get_email_message_stats(email['id'])
            
            if stats:
                # Print whatever stats we can find
                if 'email' in stats:
                    email_data = stats['email']
                    print(f"  Total Sent: {email_data.get('sentCount', 'N/A')}")
                    print(f"  Total Read: {email_data.get('readCount', 'N/A')}")
                    print(f"  Read Rate: {email_data.get('readRate', 'N/A')}%")
                    print(f"  Unique Opens: {email_data.get('uniqueReadCount', 'N/A')}")
                    print(f"  Click Rate: {email_data.get('clickRate', 'N/A')}%")
                    
                    # Check for date-based stats
                    if 'stats' in email_data:
                        print("  Recent activity available - would need to parse stats array")
                
                # Save full stats for analysis
                with open(f"email_{email['id']}_full_stats.json", 'w') as f:
                    json.dump(stats, f, indent=2)

def main():
    # Load environment variables
    load_dotenv()
    
    MAUTIC_URL = "https://crm.trainerday.com"
    username = os.getenv('MAUTIC_USERNAME')
    password = os.getenv('MAUTIC_PASSWORD')
    
    if not username or not password:
        print("Error: Missing credentials. Please check your .env file.")
        return
    
    # Initialize client
    client = MauticCampaignStats(MAUTIC_URL, username, password)
    
    # Analyze campaigns and stats
    client.analyze_onboarding_stats()

if __name__ == "__main__":
    main()