#!/usr/bin/env python3
"""
Guide for finding Google Cloud services in Linked services.
"""

def show_more_services_guide():
    """Guide user to find Google Cloud in Linked services."""
    print("🔍 Looking for Google Cloud in Linked Services")
    print("=" * 50)
    print()
    
    print("✅ Great! I can see the Linked services page")
    print("   Current linked services:")
    print("   • Google Ads (linked)")
    print("   • Firebase (linked to TrainerDay app)")
    print("   • Google Analytics (linked to TrainerDay app)")
    print()
    
    print("🔍 Next Steps - Look for Google Cloud:")
    print()
    
    print("1. Click on 'Show more' link (top right of the page)")
    print("   This should show additional Google services you can link")
    print()
    
    print("2. Look for these services in the expanded list:")
    print("   • Google Cloud")
    print("   • Google Cloud Platform")
    print("   • BigQuery")
    print("   • Cloud Console")
    print("   • Developer API")
    print("   • Play Console API")
    print()
    
    print("3. If you see Google Cloud or similar:")
    print("   • Click to link/connect it")
    print("   • Look for project selection (claude-play-store-api-access)")
    print("   • Grant permissions to service account")
    print()
    
    print("📊 Alternative - Check Analytics Integration:")
    print("   Since Google Analytics is already linked:")
    print("   • Click 'Manage in Google Analytics'")
    print("   • This might show API access options")
    print("   • Sometimes Play Console API access is managed through Analytics")
    print()
    
    print("🎯 What We're Looking For:")
    print("   Service that allows:")
    print("   • Connecting Google Cloud projects")
    print("   • Adding service accounts")
    print("   • API access permissions")
    print("   • Developer/Publishing API")

def alternative_approach():
    """Show alternative approach if Google Cloud is not available."""
    print()
    print("🔄 Alternative Approach - BigQuery Export")
    print("-" * 40)
    print()
    
    print("If Google Cloud is not directly available:")
    print()
    
    print("1. Look for 'BigQuery' or 'Data export' options")
    print("   • BigQuery often requires Google Cloud linking")
    print("   • This might be the gateway to Cloud Console integration")
    print()
    
    print("2. Check if any service mentions 'API access'")
    print("   • Some services have API access as a sub-feature")
    print("   • Developer tools might be bundled with other services")
    print()
    
    print("3. Try 'Download reports' from main menu")
    print("   • Go back to main Play Console menu")
    print("   • Click 'Download reports'")
    print("   • Look for 'Export to BigQuery' or 'API access'")
    print()
    
    print("🤔 Organization Account Limitations:")
    print("   If Google Cloud is not available, it might be because:")
    print("   • Organization accounts have restricted access")
    print("   • API features require admin approval")
    print("   • Feature not enabled for your account type")
    print("   • Regional restrictions")

def check_existing_integrations():
    """Check existing integrations for API access."""
    print()
    print("🔗 Check Existing Integrations")
    print("-" * 30)
    print()
    
    print("Since you already have Google Analytics linked:")
    print()
    
    print("1. Click 'Manage in Google Analytics'")
    print("   • This opens Google Analytics dashboard")
    print("   • Look for 'Admin' or 'API' settings")
    print("   • Google Analytics API might provide some Play Console data")
    print()
    
    print("2. Check Firebase integration:")
    print("   • Click 'Manage in Firebase'")
    print("   • Firebase projects are Google Cloud projects")
    print("   • Might have API access or Cloud Console links")
    print()
    
    print("💡 Firebase + Google Cloud Connection:")
    print("   Firebase project 'trainerdaycom' might be the key!")
    print("   • Firebase projects are Google Cloud projects")
    print("   • If Firebase is linked, Cloud Console might be accessible")
    print("   • Check if you can add service accounts to Firebase project")

if __name__ == "__main__":
    show_more_services_guide()
    alternative_approach()
    check_existing_integrations()