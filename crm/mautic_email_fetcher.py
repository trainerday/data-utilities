#!/usr/bin/env python3
"""
Mautic Email Campaign Fetcher
Pulls email campaign data from Mautic CRM using Basic Authentication
"""

import requests
import json
from typing import Dict, List, Optional
import os
from datetime import datetime
from dotenv import load_dotenv

class MauticEmailFetcher:
    def __init__(self, base_url: str, username: str, password: str):
        """
        Initialize Mautic API client with Basic Authentication
        
        Args:
            base_url: Your Mautic instance URL (e.g., https://crm.trainerday.com)
            username: Mautic username
            password: Mautic password
        """
        self.base_url = base_url.rstrip('/')
        self.auth = (username, password)
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    def test_connection(self) -> bool:
        """Test if we can connect to Mautic API"""
        try:
            response = requests.get(
                f"{self.base_url}/api/contacts?limit=1",
                auth=self.auth,
                headers=self.headers
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def get_emails(self, limit: int = 100) -> Dict:
        """
        Get email campaigns from Mautic
        
        Args:
            limit: Number of emails to fetch
            
        Returns:
            Dict containing email campaign data
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/emails?limit={limit}",
                auth=self.auth,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching emails: {e}")
            return {}
    
    def get_email_stats(self, email_id: int) -> Dict:
        """
        Get statistics for a specific email campaign
        
        Args:
            email_id: The ID of the email campaign
            
        Returns:
            Dict containing email statistics
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/emails/{email_id}",
                auth=self.auth,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching email stats for ID {email_id}: {e}")
            return {}
    
    def get_email_stats_by_date(self, email_id: int, date_from: str = None, date_to: str = None) -> Dict:
        """
        Get email statistics within a date range
        
        Args:
            email_id: The ID of the email campaign
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            Dict containing email statistics
        """
        params = {}
        if date_from:
            params['dateFrom'] = date_from
        if date_to:
            params['dateTo'] = date_to
            
        try:
            response = requests.get(
                f"{self.base_url}/api/emails/{email_id}/stats",
                auth=self.auth,
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching email stats by date: {e}")
            return {}
    
    def save_to_file(self, data: Dict, filename: str):
        """Save data to JSON file"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Data saved to {filename}")


def main():
    # Load environment variables
    load_dotenv()
    
    # Configuration
    MAUTIC_URL = "https://crm.trainerday.com"
    
    # Get credentials from environment variables or prompt
    username = os.getenv('MAUTIC_USERNAME')
    password = os.getenv('MAUTIC_PASSWORD')
    
    if not username or not password:
        print("Error: Missing credentials. Please check your .env file.")
        return
    
    # Initialize client
    client = MauticEmailFetcher(MAUTIC_URL, username, password)
    
    # Test connection
    print("Testing connection to Mautic...")
    if not client.test_connection():
        print("Failed to connect to Mautic. Please check your credentials and API settings.")
        return
    
    print("Successfully connected to Mautic!")
    
    # Fetch emails
    print("\nFetching email campaigns...")
    emails = client.get_emails(limit=50)
    
    if emails and 'emails' in emails:
        email_list = emails['emails']
        print(f"\nFound {len(email_list)} email campaigns:")
        
        # Display email campaigns
        for email_id, email_data in email_list.items():
            print(f"\nID: {email_id}")
            print(f"Name: {email_data.get('name', 'N/A')}")
            print(f"Subject: {email_data.get('subject', 'N/A')}")
            print(f"Sent Count: {email_data.get('sentCount', 0)}")
            print(f"Read Count: {email_data.get('readCount', 0)}")
            print(f"Read Rate: {email_data.get('readRate', 0)}%")
            
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mautic_emails_{timestamp}.json"
        client.save_to_file(emails, filename)
        
        # Get detailed stats for onboarding emails
        onboarding_ids = [11, 7, 8, 9]  # IDs of the 4 onboarding emails
        print("\nFetching detailed stats for onboarding emails...")
        
        for email_id in onboarding_ids:
            stats = client.get_email_stats(email_id)
            if stats:
                client.save_to_file(stats, f"email_{email_id}_stats_{timestamp}.json")
    else:
        print("No emails found or error occurred.")


if __name__ == "__main__":
    main()