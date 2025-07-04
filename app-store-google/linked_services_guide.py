#!/usr/bin/env python3
"""
Guide for using Linked services section in Google Play Console.
"""

def linked_services_guide():
    """Guide user through Linked services section."""
    print("🎯 Found It! Linked Services Section")
    print("=" * 50)
    print()
    
    print("✅ Perfect! I can see the Settings page")
    print("   The API access is likely in 'Linked services'")
    print()
    
    print("🔗 Next Steps:")
    print("1. Click on 'Linked services' (in Developer account section)")
    print("   Description: 'Link your developer account to other Google services, like Google Ads and Firebase, to do more with your data'")
    print()
    
    print("2. Look for:")
    print("   • Google Cloud")
    print("   • API access")
    print("   • Service accounts")
    print("   • Developer API")
    print("   • External integrations")
    print()
    
    print("3. You might see:")
    print("   • 'Link Google Cloud project' button")
    print("   • List of connected services")
    print("   • Option to add/manage service accounts")
    print()
    
    print("📧 Service Account to Link:")
    print("   claude-access@claude-play-store-api-access.iam.gserviceaccount.com")
    print("   Project: claude-play-store-api-access")
    print()
    
    print("🎯 What We're Looking For:")
    print("   • Google Cloud integration options")
    print("   • Ability to grant API access to service accounts")
    print("   • Connection between Play Console and Cloud Console")
    print()
    
    print("⚠️  If Linked Services Doesn't Have API Options:")
    print("   Sometimes the API access is called:")
    print("   • 'Developer API'")
    print("   • 'Play Console API'")
    print("   • 'Publishing API'")
    print("   • Hidden under Google Cloud integration")
    print()
    
    print("🔍 What to Report:")
    print("   Please click on 'Linked services' and tell me:")
    print("   1. What services are already linked (if any)?")
    print("   2. What options do you see to add new services?")
    print("   3. Any mention of Google Cloud, API, or service accounts?")

def alternative_locations():
    """Show alternative locations if Linked services doesn't work."""
    print()
    print("🔄 Alternative Locations")
    print("-" * 25)
    print()
    
    print("If 'Linked services' doesn't have API options, try:")
    print()
    
    print("1. 'Developer account' (left sidebar)")
    print("   • Might have API settings separate from other settings")
    print()
    
    print("2. 'Download reports' (left sidebar)")
    print("   • Sometimes contains API access for analytics")
    print("   • May have 'Export to BigQuery' or 'API access' options")
    print()
    
    print("3. Back to main app view:")
    print("   • Click on your TrainerDay app")
    print("   • Look for 'Statistics' or 'Analytics' sections")
    print("   • Sometimes API access is app-specific")
    print()
    
    print("4. 'Users and permissions' (left sidebar)")
    print("   • Might allow adding service accounts as 'users'")
    print("   • Check if you can invite the service account email")

def organization_account_considerations():
    """Address organization account specific considerations."""
    print()
    print("🏢 Organization Account Considerations")
    print("-" * 35)
    print()
    
    print("Since this is a TrainerDay Inc organization account:")
    print()
    
    print("Possible scenarios:")
    print("1. ✅ API access available - just need to link Google Cloud")
    print("2. 🔒 API access restricted - need organization admin")
    print("3. 🏢 API access centralized - managed at organization level")
    print("4. ❌ API access not enabled - need Google support")
    print()
    
    print("If you don't see API options:")
    print("• You might not have sufficient permissions")
    print("• Organization admin might need to enable it first")
    print("• Feature might not be available for your account type")
    print("• Google Workspace integration might be required")

if __name__ == "__main__":
    linked_services_guide()
    alternative_locations()
    organization_account_considerations()