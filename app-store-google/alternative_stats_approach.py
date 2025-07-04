#!/usr/bin/env python3
"""
Alternative approaches to get Google Play download statistics.
"""

def show_alternative_approaches():
    """Show alternative ways to get download statistics."""
    print("📊 Alternative Approaches for Download Statistics")
    print("=" * 55)
    print()
    
    print("❌ Current Status:")
    print("   Google Play Console API doesn't provide download statistics")
    print("   with basic 'View app information' permissions")
    print()
    
    print("🔍 Alternative Approaches:")
    print()
    
    print("1. 📊 Google Play Console Web Interface")
    print("   • Go to play.google.com/console")
    print("   • Click on TrainerDay app")
    print("   • Look for 'Statistics' or 'Dashboard' section")
    print("   • This shows download numbers, active users, etc.")
    print("   • Manual export available")
    print()
    
    print("2. 📈 BigQuery Export (Advanced)")
    print("   • Go to Play Console > Download reports")
    print("   • Look for 'Export to BigQuery' option")
    print("   • Links Google Cloud BigQuery to Play Console")
    print("   • Provides detailed analytics via SQL queries")
    print("   • Requires additional Google Cloud setup")
    print()
    
    print("3. 🔗 Google Analytics Integration")
    print("   • You already have Google Analytics linked")
    print("   • GA can track app installations and usage")
    print("   • Might provide download/install data")
    print("   • Check Google Analytics dashboard")
    print()
    
    print("4. 📱 Firebase Analytics")
    print("   • If TrainerDay uses Firebase SDK")
    print("   • Provides detailed user analytics")
    print("   • Can track app installs and user behavior")
    print("   • Accessible via Firebase Console")
    print()
    
    print("5. 🎯 Request Enhanced Permissions")
    print("   • Go back to Play Console > Users and permissions")
    print("   • Edit the service account permissions")
    print("   • Look for additional permission options:")
    print("     - 'View financial data'")
    print("     - 'Download bulk reports'")
    print("     - 'Access to app statistics'")
    print()
    
    print("🎯 Quick Manual Check:")
    print("   1. Go to Google Play Console")
    print("   2. Click on TrainerDay app")
    print("   3. Look for 'Statistics' or 'Dashboard'")
    print("   4. This will show last month's downloads manually")

def check_current_permissions():
    """Check what permissions the service account currently has."""
    print()
    print("🔧 Current Service Account Permissions")
    print("-" * 35)
    print()
    
    print("📧 Service Account: claude-access@claude-play-store-api-access.iam.gserviceaccount.com")
    print("📦 Package Access: trainerday.turbo")
    print()
    
    print("✅ Current Permissions (Working):")
    print("   • View app information")
    print("   • Download bulk reports")
    print("   • App metadata access")
    print("   • Basic app management")
    print()
    
    print("❌ Missing for Statistics:")
    print("   • Advanced analytics access")
    print("   • Financial data access")
    print("   • Statistics API permissions")
    print("   • BigQuery export permissions")
    print()
    
    print("🔧 To Add More Permissions:")
    print("   1. Go to Play Console > Users and permissions")
    print("   2. Find: claude-access@claude-play-store-api-access.iam.gserviceaccount.com")
    print("   3. Click 'Edit' or manage permissions")
    print("   4. Add additional permission categories")

def bigquery_setup_guide():
    """Guide for setting up BigQuery export."""
    print()
    print("📊 BigQuery Export Setup (Advanced)")
    print("-" * 35)
    print()
    
    print("BigQuery provides the most comprehensive statistics:")
    print()
    
    print("Setup Steps:")
    print("1. Go to Play Console > Download reports")
    print("2. Look for 'Export to BigQuery' option")
    print("3. If available, it will ask for:")
    print("   • Google Cloud project (use: claude-play-store-api-access)")
    print("   • Dataset name")
    print("   • Export frequency")
    print()
    
    print("📊 BigQuery Data Includes:")
    print("   • App downloads by date")
    print("   • User acquisition metrics")
    print("   • Revenue data")
    print("   • User retention")
    print("   • Geographic distribution")
    print("   • Device and OS statistics")
    print()
    
    print("💡 Benefits:")
    print("   • Historical data")
    print("   • Custom SQL queries")
    print("   • Automated reporting")
    print("   • API access to statistics")

if __name__ == "__main__":
    show_alternative_approaches()
    check_current_permissions()
    bigquery_setup_guide()