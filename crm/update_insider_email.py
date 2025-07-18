#!/usr/bin/env python3
"""
Update Insider Welcome Email Template in Mautic CRM
"""

import requests
import json
import os
from dotenv import load_dotenv

class MauticEmailUpdater:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.auth = (username, password)
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    def update_email_template(self, email_id: int, subject: str, html_content: str):
        """Update email template with new subject and content"""
        
        # Data payload for updating the email
        data = {
            "name": "Insider Welcome",  # Required field
            "subject": subject,
            "customHtml": html_content
        }
        
        print(f"🔍 Attempting to update email at: {self.base_url}/api/emails/{email_id}")
        
        # Try different methods and endpoint variations
        methods_to_try = [
            ("PUT", f"{self.base_url}/api/emails/{email_id}"),
            ("PATCH", f"{self.base_url}/api/emails/{email_id}"),
            ("PUT", f"{self.base_url}/api/emails/{email_id}/edit"),
            ("POST", f"{self.base_url}/api/emails/{email_id}/edit")
        ]
        
        for method, url in methods_to_try:
            try:
                print(f"🔄 Trying {method} to {url}")
                
                if method == "PUT":
                    response = requests.put(url, auth=self.auth, headers=self.headers, json=data)
                elif method == "PATCH":
                    response = requests.patch(url, auth=self.auth, headers=self.headers, json=data)
                elif method == "POST":
                    response = requests.post(url, auth=self.auth, headers=self.headers, json=data)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Successfully updated email template {email_id} using {method}")
                    print(f"   Subject: {subject}")
                    print(f"   Response: {result.get('message', 'Updated successfully')}")
                    return result
                else:
                    print(f"   Status: {response.status_code} - {response.reason}")
                    try:
                        error_data = response.json()
                        print(f"   Error: {error_data}")
                    except:
                        print(f"   Response: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                print(f"   Request error: {e}")
                continue
        
        print(f"❌ All methods failed to update email template {email_id}")
        return None
    
    def get_email_details(self, email_id: int):
        """Get current email details before updating"""
        try:
            response = requests.get(
                f"{self.base_url}/api/emails/{email_id}",
                auth=self.auth,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching email {email_id}: {e}")
            return None

def main():
    # Load environment variables
    load_dotenv()
    
    MAUTIC_URL = "https://crm.trainerday.com"
    username = os.getenv('MAUTIC_USERNAME')
    password = os.getenv('MAUTIC_PASSWORD')
    
    if not username or not password:
        print("❌ Error: Missing credentials. Please check your .env file.")
        return
    
    # Initialize updater
    updater = MauticEmailUpdater(MAUTIC_URL, username, password)
    
    # Insider Welcome email ID (from the JSON data we fetched)
    INSIDER_EMAIL_ID = 16
    
    # New subject line
    new_subject = "🌟 Welcome to the Insider Club! You're in the know now 😉"
    
    # Load the updated HTML content
    html_file_path = "data/insider_welcome_updated_content.html"
    
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            new_html_content = f.read()
    except FileNotFoundError:
        print(f"❌ Error: HTML file not found at {html_file_path}")
        return
    
    # Show current email details
    print("📧 Current email details:")
    current_email = updater.get_email_details(INSIDER_EMAIL_ID)
    if current_email and 'email' in current_email:
        email_data = current_email['email']
        print(f"   Name: {email_data.get('name', 'N/A')}")
        print(f"   Current Subject: {email_data.get('subject', 'N/A')}")
        print(f"   Last Modified: {email_data.get('dateModified', 'N/A')}")
    
    # Confirm update
    print(f"\n🔄 About to update email template {INSIDER_EMAIL_ID}")
    print(f"   New Subject: {new_subject}")
    print(f"   Using HTML content from: {html_file_path}")
    
    # Auto-proceed in non-interactive environment
    try:
        confirm = input("\n❓ Proceed with update? (y/N): ").lower().strip()
        if confirm != 'y':
            print("❌ Update cancelled.")
            return
    except EOFError:
        # Non-interactive environment - auto-proceed
        print("\n✅ Non-interactive mode - proceeding with update...")
        pass
    
    # Update the email template
    print("\n📝 Updating email template...")
    result = updater.update_email_template(INSIDER_EMAIL_ID, new_subject, new_html_content)
    
    if result:
        print("\n✅ Email template updated successfully!")
        print("   You can now test the email in your Mautic CRM interface.")
        
        # Save update log
        os.makedirs('data', exist_ok=True)
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        update_log = {
            "timestamp": timestamp,
            "email_id": INSIDER_EMAIL_ID,
            "new_subject": new_subject,
            "update_status": "success",
            "api_response": result
        }
        
        with open(f"data/insider_email_update_log_{timestamp}.json", 'w') as f:
            json.dump(update_log, f, indent=2)
        
        print(f"📋 Update log saved to: data/insider_email_update_log_{timestamp}.json")
    else:
        print("\n❌ Failed to update email template.")

if __name__ == "__main__":
    main()