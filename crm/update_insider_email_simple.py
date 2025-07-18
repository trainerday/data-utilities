#!/usr/bin/env python3
"""
Simple Update for Insider Welcome Email Template
"""

import requests
import json
import os
from dotenv import load_dotenv

def update_email_subject_only():
    """Update just the subject line first to test API"""
    
    load_dotenv()
    
    MAUTIC_URL = "https://crm.trainerday.com"
    username = os.getenv('MAUTIC_USERNAME')
    password = os.getenv('MAUTIC_PASSWORD')
    
    if not username or not password:
        print("❌ Missing credentials")
        return
    
    auth = (username, password)
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    # Email ID and new subject
    email_id = 16
    new_subject = "🌟 Welcome to the Insider Club! You're in the know now 😉"
    
    # Simple data payload - subject and required name
    data = {
        "name": "Insider Welcome",
        "subject": new_subject
    }
    
    print(f"🔄 Updating email {email_id} subject only...")
    print(f"   New subject: {new_subject}")
    
    # Try PUT method with /api/emails/{id}/edit endpoint
    try:
        response = requests.put(
            f"{MAUTIC_URL}/api/emails/{email_id}/edit",
            auth=auth,
            headers=headers,
            json=data
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Successfully updated subject!")
            result = response.json()
            return result
        else:
            print(f"❌ Failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

def get_all_emails():
    """Get all emails to see the structure"""
    
    load_dotenv()
    
    MAUTIC_URL = "https://crm.trainerday.com"
    username = os.getenv('MAUTIC_USERNAME')
    password = os.getenv('MAUTIC_PASSWORD')
    
    auth = (username, password)
    headers = {'Accept': 'application/json'}
    
    try:
        response = requests.get(
            f"{MAUTIC_URL}/api/emails",
            auth=auth,
            headers=headers
        )
        
        if response.status_code == 200:
            emails = response.json()
            print("📧 Available emails:")
            for email_id, email_data in emails.get('emails', {}).items():
                print(f"   ID: {email_id} - Name: {email_data.get('name', 'N/A')}")
            return emails
        else:
            print(f"❌ Failed to get emails: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    print("📋 Getting all emails first...")
    get_all_emails()
    
    print("\n" + "="*50)
    print("🔄 Attempting to update email subject...")
    update_email_subject_only()