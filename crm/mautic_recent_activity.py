#!/usr/bin/env python3
"""
Mautic Recent Activity Analyzer
Pulls recent email campaign data to understand current onboarding activity
"""

import requests
import json
from typing import Dict, List
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

class MauticRecentActivity:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.auth = (username, password)
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    def get_recent_contacts(self, days_back: int = 30) -> Dict:
        """Get contacts created in the last N days"""
        date_from = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        try:
            response = requests.get(
                f"{self.base_url}/api/contacts",
                auth=self.auth,
                headers=self.headers,
                params={
                    'search': f'date_added:>={date_from}',
                    'limit': 1000,
                    'orderBy': 'date_added',
                    'orderByDir': 'DESC'
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching recent contacts: {e}")
            return {}
    
    def get_email_sends_by_date(self, email_id: int, days_back: int = 30) -> Dict:
        """Get email send statistics for a specific time period"""
        date_from = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        date_to = datetime.now().strftime('%Y-%m-%d')
        
        try:
            # Try to get email stats with date filter
            response = requests.get(
                f"{self.base_url}/api/emails/{email_id}/contact",
                auth=self.auth,
                headers=self.headers,
                params={
                    'dateFrom': date_from,
                    'dateTo': date_to,
                    'limit': 1000
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching email sends for ID {email_id}: {e}")
            return {}
    
    def analyze_recent_onboarding(self, days_back: int = 30):
        """Analyze recent onboarding activity"""
        print(f"\n=== RECENT ONBOARDING ACTIVITY (Last {days_back} Days) ===\n")
        
        # Get recent contacts
        print(f"Fetching contacts from last {days_back} days...")
        recent_contacts = self.get_recent_contacts(days_back)
        
        if recent_contacts and 'total' in recent_contacts:
            total_new = int(recent_contacts['total'])
            print(f"New signups: {total_new}")
            if total_new > 0:
                print(f"Average per day: {total_new / days_back:.1f}")
                print(f"Projected monthly: {(total_new / days_back) * 30:.0f}")
            else:
                print("No new signups in this period")
        
        # Analyze onboarding emails
        onboarding_emails = [
            {"id": 11, "name": "Welcome"},
            {"id": 7, "name": "Quick Tour"},
            {"id": 8, "name": "App Settings"},
            {"id": 9, "name": "Checking In"}
        ]
        
        print(f"\n=== RECENT EMAIL ACTIVITY ===\n")
        
        for email in onboarding_emails:
            print(f"\nChecking {email['name']} (ID: {email['id']})...")
            sends = self.get_email_sends_by_date(email['id'], days_back)
            
            if sends and 'total' in sends:
                print(f"  Sent in last {days_back} days: {sends['total']}")
                
                # Try to calculate read rate from the contacts
                if 'contacts' in sends:
                    read_count = sum(1 for c in sends['contacts'].values() 
                                   if c.get('read', 0) == 1)
                    read_rate = (read_count / sends['total'] * 100) if sends['total'] > 0 else 0
                    print(f"  Read: {read_count} ({read_rate:.1f}%)")

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
    client = MauticRecentActivity(MAUTIC_URL, username, password)
    
    # Analyze different time periods
    for days in [7, 30, 90]:
        client.analyze_recent_onboarding(days)
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()