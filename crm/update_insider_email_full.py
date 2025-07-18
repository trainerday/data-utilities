#!/usr/bin/env python3
"""
Full Update for Insider Welcome Email Template
Get existing email data first, then update with all required fields
"""

import requests
import json
import os
from dotenv import load_dotenv

def get_full_email_data(email_id):
    """Get complete email data to see what fields are required"""
    
    load_dotenv()
    
    MAUTIC_URL = "https://crm.trainerday.com"
    username = os.getenv('MAUTIC_USERNAME')
    password = os.getenv('MAUTIC_PASSWORD')
    
    auth = (username, password)
    headers = {'Accept': 'application/json'}
    
    try:
        response = requests.get(
            f"{MAUTIC_URL}/api/emails/{email_id}",
            auth=auth,
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get email data: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

def update_email_with_full_data(email_id, new_subject, new_html):
    """Update email using existing data as base"""
    
    load_dotenv()
    
    MAUTIC_URL = "https://crm.trainerday.com"
    username = os.getenv('MAUTIC_USERNAME')
    password = os.getenv('MAUTIC_PASSWORD')
    
    auth = (username, password)
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    # Get existing email data
    print(f"📋 Getting existing email data for ID {email_id}...")
    email_data = get_full_email_data(email_id)
    
    if not email_data or 'email' not in email_data:
        print("❌ Could not get existing email data")
        return None
    
    existing_email = email_data['email']
    print(f"✅ Got existing email: {existing_email.get('name', 'N/A')}")
    
    # Create update payload with all existing data plus our changes
    update_data = {
        "name": existing_email.get('name', 'Insider Welcome'),
        "subject": new_subject,
        "customHtml": new_html,
        "emailType": existing_email.get('emailType', 'template'),
        "language": existing_email.get('language', 'en'),
        "isPublished": existing_email.get('isPublished', True)
    }
    
    print(f"🔄 Updating email {email_id} with full data...")
    print(f"   Name: {update_data['name']}")
    print(f"   Subject: {update_data['subject']}")
    print(f"   Type: {update_data['emailType']}")
    
    # Try PUT method with /api/emails/{id}/edit
    try:
        response = requests.put(
            f"{MAUTIC_URL}/api/emails/{email_id}/edit",
            auth=auth,
            headers=headers,
            json=update_data
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Successfully updated email!")
            result = response.json()
            print(f"Result: {json.dumps(result, indent=2)}")
            return result
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

def main():
    email_id = 16
    new_subject = "🌟 Welcome to the Insider Club! You're in the know now 😉"
    
    # Load new HTML content
    html_file = "data/insider_welcome_updated_content.html"
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            new_html = f.read()
    except FileNotFoundError:
        print(f"❌ HTML file not found: {html_file}")
        return
    
    print(f"📄 Loaded HTML content from {html_file}")
    
    # Update the email
    result = update_email_with_full_data(email_id, new_subject, new_html)
    
    if result:
        print("\n✅ Email update completed successfully!")
        
        # Save log
        os.makedirs('data', exist_ok=True)
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        with open(f"data/email_update_success_{timestamp}.json", 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"📋 Log saved to: data/email_update_success_{timestamp}.json")
    else:
        print("\n❌ Email update failed.")

if __name__ == "__main__":
    main()