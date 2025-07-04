#!/usr/bin/env python3
"""
Check Download reports section for API access options.
"""

def download_reports_guide():
    """Guide user to check Download reports for API access."""
    print("📊 Download Reports - API Access Location")
    print("=" * 50)
    print()
    
    print("You're right - Firebase is unrelated to Play Console API access.")
    print("Let's check the most common location for API settings.")
    print()
    
    print("🔍 Next Steps:")
    print("1. Go back to main Play Console (click back or home)")
    print("2. In the left sidebar, click 'Download reports'")
    print("3. Look for these options:")
    print("   • 'Export to BigQuery'")
    print("   • 'API access'")
    print("   • 'Cloud integration'")
    print("   • 'Reporting API'")
    print("   • 'Enable API access'")
    print()
    
    print("📊 What Download Reports Often Contains:")
    print("   • Export options for analytics data")
    print("   • BigQuery integration (requires Google Cloud)")
    print("   • API access for downloading reports programmatically")
    print("   • Service account management for data export")
    print()
    
    print("🎯 What We're Looking For:")
    print("   • Button to 'Enable API access'")
    print("   • 'Link Google Cloud project' option")
    print("   • Service account email input field")
    print("   • Permission settings for external access")

def alternative_locations():
    """Show other possible locations for API access."""
    print()
    print("🔄 Alternative Locations to Check")
    print("-" * 35)
    print()
    
    print("If Download reports doesn't have API options:")
    print()
    
    print("1. 'Users and permissions' (left sidebar)")
    print("   • Try to 'Invite new user'")
    print("   • Enter service account email:")
    print("     claude-access@claude-play-store-api-access.iam.gserviceaccount.com")
    print("   • See if it accepts service account emails")
    print()
    
    print("2. Individual app settings:")
    print("   • Click on TrainerDay app")
    print("   • Look for 'Statistics' or 'Analytics' section")
    print("   • Check for API or export options")
    print()
    
    print("3. 'Developer account' (left sidebar)")
    print("   • Separate from general Settings")
    print("   • Might have API-specific configurations")

def organization_account_reality():
    """Address the reality of organization account limitations."""
    print()
    print("🏢 Organization Account Reality Check")
    print("-" * 35)
    print()
    
    print("Possible reasons API access isn't visible:")
    print()
    
    print("1. ❌ Feature not enabled for organization accounts")
    print("   • Some Google Play features are restricted")
    print("   • API access might require individual developer accounts")
    print()
    
    print("2. 🔒 Admin permissions required")
    print("   • You might not have sufficient permissions")
    print("   • Organization admin needs to enable API features")
    print()
    
    print("3. 📋 Manual application process")
    print("   • Some accounts need to apply for API access")
    print("   • Google might require verification for organization accounts")
    print()
    
    print("4. 🌍 Regional restrictions")
    print("   • API access might not be available in all regions")
    print("   • Different features for different account types")
    print()
    
    print("💡 What this means:")
    print("   If we can't find API access in the UI, the feature")
    print("   might not be available for your account type.")

def contact_google_approach():
    """Show how to contact Google for API access."""
    print()
    print("📞 Contact Google Approach")
    print("-" * 25)
    print()
    
    print("If UI doesn't have API access options:")
    print()
    
    print("1. Google Play Console Help:")
    print("   • Look for '?' or 'Help' button in Play Console")
    print("   • Search for 'API access' or 'service account'")
    print("   • Contact support directly")
    print()
    
    print("2. Google Cloud Console approach:")
    print("   • Go to console.cloud.google.com")
    print("   • Select claude-play-store-api-access project")
    print("   • Look for Play Console integration in Google Cloud")
    print()
    
    print("3. Google Developer Forums:")
    print("   • Ask on Google Play Console developer forums")
    print("   • Other developers might have solved this")
    print()
    
    print("📝 Information to provide Google:")
    print("   • Account type: Organization account (TrainerDay Inc)")
    print("   • Goal: Grant API access to service account")
    print("   • Service account: claude-access@claude-play-store-api-access.iam.gserviceaccount.com")
    print("   • Package: trainerday.turbo")

if __name__ == "__main__":
    download_reports_guide()
    alternative_locations()
    organization_account_reality()
    contact_google_approach()