#!/usr/bin/env python3
"""
Guide for personal Google Play Console accounts to find API access.
"""

def personal_account_guide():
    """Guide for personal accounts - API access should be available."""
    print("👤 Personal Google Play Console Account - API Access")
    print("=" * 55)
    print()
    
    print("✅ Much better! Personal accounts typically have full API access.")
    print("   API features should be available in your account.")
    print()
    
    print("🔍 Most Likely Locations for Personal Accounts:")
    print()
    
    print("1. 'Download reports' (left sidebar)")
    print("   • This is the #1 most common location")
    print("   • Look for 'Export to BigQuery' or 'API access'")
    print("   • Often has 'Enable API access' button")
    print()
    
    print("2. 'Users and permissions' (left sidebar)")
    print("   • Personal accounts can often add service accounts as 'users'")
    print("   • Try 'Invite new user' with service account email")
    print("   • claude-access@claude-play-store-api-access.iam.gserviceaccount.com")
    print()
    
    print("3. Individual app settings:")
    print("   • Click on TrainerDay app → look for 'Statistics' section")
    print("   • Sometimes API access is app-specific")
    print("   • Check for 'Export data' or 'API settings'")
    print()
    
    print("4. Back in Settings → Look for these sections:")
    print("   • 'Developer API'")
    print("   • 'Data export'")
    print("   • 'External access'")
    print("   • Any section we might have missed")

def download_reports_focus():
    """Focus on Download reports section."""
    print()
    print("📊 Download Reports - Primary Target")
    print("-" * 35)
    print()
    
    print("Since you have a personal account, Download reports should have:")
    print()
    
    print("Expected options:")
    print("✅ 'Export to BigQuery' (requires Google Cloud linking)")
    print("✅ 'API access' or 'Enable API access'")
    print("✅ 'Service account management'")
    print("✅ 'Google Cloud project' selection")
    print()
    
    print("What to do in Download reports:")
    print("1. Look for any 'Enable' buttons")
    print("2. Check for Google Cloud project options")
    print("3. Look for service account email fields")
    print("4. Any mention of 'Publishing API' or 'Reports API'")
    print()
    
    print("💡 If you see 'Export to BigQuery':")
    print("   • This often requires linking Google Cloud")
    print("   • Might be the gateway to API access")
    print("   • Could ask for the claude-play-store-api-access project")

def users_permissions_approach():
    """Guide for trying Users and permissions."""
    print()
    print("👥 Users and Permissions Approach")
    print("-" * 32)
    print()
    
    print("Personal accounts often allow adding service accounts as users:")
    print()
    
    print("Steps:")
    print("1. Click 'Users and permissions' (left sidebar)")
    print("2. Look for 'Invite new user' or 'Add user' button")
    print("3. Enter service account email:")
    print("   claude-access@claude-play-store-api-access.iam.gserviceaccount.com")
    print("4. If it accepts the email, assign permissions:")
    print("   • 'View app information and download bulk reports'")
    print("   • This might be equivalent to API access")
    print()
    
    print("⚠️  What might happen:")
    print("   • Service account email is accepted → Great!")
    print("   • Error: 'Invalid email' → This method doesn't work")
    print("   • Redirects to API setup → Perfect!")

def check_app_specific_settings():
    """Check app-specific API settings."""
    print()
    print("📱 App-Specific API Settings")
    print("-" * 28)
    print()
    
    print("Sometimes API access is configured per app:")
    print()
    
    print("Steps:")
    print("1. Click on 'TrainerDay - Indoor Cycling' app")
    print("2. In the app dashboard, look for:")
    print("   • 'Statistics' section")
    print("   • 'Analytics' or 'Reports' section")
    print("   • Any 'Settings' or 'Advanced' options")
    print("   • 'Data export' or 'API access'")
    print()
    
    print("3. Common locations within app:")
    print("   • Statistics → Export options")
    print("   • Release management → API settings")
    print("   • App information → Advanced settings")
    print()
    
    print("🎯 Personal accounts should definitely have API access!")
    print("   It's just a matter of finding the right menu location.")

if __name__ == "__main__":
    personal_account_guide()
    download_reports_focus()
    users_permissions_approach()
    check_app_specific_settings()