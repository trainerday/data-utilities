#!/usr/bin/env python3
"""
Instructions to grant Google Play Console permissions to service account.
"""

import os
import json
from dotenv import load_dotenv

def show_permission_steps():
    """Show steps to grant permissions in Google Play Console."""
    load_dotenv()
    
    print("🔑 Grant Google Play Console Permissions")
    print("=" * 50)
    print()
    
    # Get service account email
    service_account_file = os.getenv('SERVICE_ACCOUNT_FILE')
    service_account_path = os.path.join(os.path.dirname(__file__), service_account_file)
    
    try:
        with open(service_account_path, 'r') as f:
            sa_data = json.load(f)
        
        service_email = sa_data.get('client_email', 'Unknown')
        project_id = sa_data.get('project_id', 'Unknown')
        
        print("✅ GOOD NEWS: Package 'trainerday.turbo' found!")
        print("❌ ISSUE: Service account needs permissions")
        print()
        
        print("📧 Service Account Email:")
        print(f"   {service_email}")
        print()
        
        print("🎯 Steps to Grant Access:")
        print()
        
        print("1. Go to Google Play Console:")
        print("   https://play.google.com/console/")
        print()
        
        print("2. Select TrainerDay app")
        print()
        
        print("3. Go to: Setup → API access")
        print()
        
        print("4. If not linked yet:")
        print("   • Click 'Link Google Cloud Project'")
        print(f"   • Select project: {project_id}")
        print("   • Click 'Link'")
        print()
        
        print("5. Grant Service Account Access:")
        print("   • Find in the list:")
        print(f"     {service_email}")
        print("   • Click 'Grant Access'")
        print()
        
        print("6. Select Permissions:")
        print("   ✅ View app information and download bulk reports")
        print("   ✅ View financial data (optional)")
        print("   ❌ Don't give admin access unless needed")
        print()
        
        print("7. Click 'Apply'")
        print()
        
        print("🧪 Test After Setup:")
        print("   python3 play_console_api.py")
        print()
        
        print("⏱️  Note: Permissions can take a few minutes to activate")
        
    except Exception as e:
        print(f"❌ Error reading service account file: {e}")

if __name__ == "__main__":
    show_permission_steps()