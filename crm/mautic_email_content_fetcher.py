#!/usr/bin/env python3
"""
Mautic Email Content Fetcher
Downloads email subject and body content for all emails
"""

import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import html
import re
from typing import Dict

class MauticEmailContentFetcher:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.auth = (username, password)
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    def clean_html(self, html_content: str) -> str:
        """Convert HTML to readable text"""
        if not html_content:
            return ""
        
        # Remove style tags and their content
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL)
        
        # Remove script tags and their content
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
        
        # Replace line breaks with newlines
        html_content = html_content.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
        html_content = html_content.replace('</p>', '\n\n').replace('</div>', '\n')
        
        # Remove remaining HTML tags
        html_content = re.sub(r'<[^>]+>', '', html_content)
        
        # Decode HTML entities
        html_content = html.unescape(html_content)
        
        # Clean up excessive whitespace
        html_content = re.sub(r'\n\s*\n', '\n\n', html_content)
        html_content = re.sub(r' +', ' ', html_content)
        
        return html_content.strip()
    
    def get_email_content(self, email_id: int) -> Dict:
        """Get full email details including content"""
        try:
            response = requests.get(
                f"{self.base_url}/api/emails/{email_id}",
                auth=self.auth,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching email {email_id}: {e}")
            return {}
    
    def fetch_all_email_content(self):
        """Fetch content for all emails"""
        print("Fetching all email content...")
        
        # First get list of all emails
        try:
            response = requests.get(
                f"{self.base_url}/api/emails?limit=100",
                auth=self.auth,
                headers=self.headers
            )
            response.raise_for_status()
            emails_data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching email list: {e}")
            return
        
        if not emails_data or 'emails' not in emails_data:
            print("No emails found")
            return
        
        # Collect content for each email
        email_contents = {}
        
        for email_id, email_summary in emails_data['emails'].items():
            print(f"\nFetching content for: {email_summary.get('name', 'Unknown')}")
            
            # Get full email details
            full_email = self.get_email_content(int(email_id))
            
            if full_email and 'email' in full_email:
                email_data = full_email['email']
                
                # Extract and clean content
                content = {
                    'id': email_id,
                    'name': email_data.get('name', ''),
                    'subject': email_data.get('subject', ''),
                    'type': email_data.get('emailType', ''),
                    'sent_count': email_data.get('sentCount', 0),
                    'read_count': email_data.get('readCount', 0),
                    'read_rate': round(email_data.get('readCount', 0) / email_data.get('sentCount', 1) * 100, 1) if email_data.get('sentCount', 0) > 0 else 0,
                    'date_added': email_data.get('dateAdded', ''),
                    'date_modified': email_data.get('dateModified', ''),
                    'html_content': email_data.get('customHtml', ''),
                    'plain_text': email_data.get('plainText', ''),
                    'cleaned_content': self.clean_html(email_data.get('customHtml', ''))
                }
                
                # For onboarding emails, add order
                if int(email_id) == 11:
                    content['sequence_order'] = 1
                    content['sequence_name'] = 'Welcome'
                elif int(email_id) == 7:
                    content['sequence_order'] = 2
                    content['sequence_name'] = 'Quick Tour'
                elif int(email_id) == 8:
                    content['sequence_order'] = 3
                    content['sequence_name'] = 'App Settings'
                elif int(email_id) == 9:
                    content['sequence_order'] = 4
                    content['sequence_name'] = 'Checking In'
                
                email_contents[email_id] = content
                
                # Show preview
                print(f"  Subject: {content['subject']}")
                print(f"  Read Rate: {content['read_rate']}%")
                preview = content['cleaned_content'][:200] + '...' if len(content['cleaned_content']) > 200 else content['cleaned_content']
                print(f"  Preview: {preview}")
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mautic_email_content_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(email_contents, f, indent=2, ensure_ascii=False)
        
        print(f"\n\nEmail content saved to: {filename}")
        
        # Create a simplified onboarding-only file
        onboarding_emails = {k: v for k, v in email_contents.items() 
                           if 'sequence_order' in v}
        
        if onboarding_emails:
            onboarding_filename = f"onboarding_email_content_{timestamp}.json"
            
            # Sort by sequence order
            sorted_onboarding = dict(sorted(onboarding_emails.items(), 
                                          key=lambda x: x[1].get('sequence_order', 999)))
            
            with open(onboarding_filename, 'w', encoding='utf-8') as f:
                json.dump(sorted_onboarding, f, indent=2, ensure_ascii=False)
            
            print(f"Onboarding emails saved to: {onboarding_filename}")
        
        return email_contents

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
    client = MauticEmailContentFetcher(MAUTIC_URL, username, password)
    
    # Fetch all email content
    client.fetch_all_email_content()

if __name__ == "__main__":
    main()