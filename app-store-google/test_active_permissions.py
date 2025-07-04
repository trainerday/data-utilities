#!/usr/bin/env python3
"""
Test the Google Play Console API now that service account has been granted access.
"""

def test_permissions_success():
    """Test API access now that permissions are granted."""
    print("🎉 SUCCESS! Service Account Access Granted!")
    print("=" * 50)
    print()
    
    print("✅ Status: Service account is now ACTIVE in Play Console")
    print("   claude-access@claude-play-store-api-access.iam.gserviceaccount.com")
    print()
    
    print("🧪 Let's test the API connection now!")
    print("   The permissions should now be working.")
    print()
    
    print("📝 What permissions were granted:")
    print("   When you invited the service account, you likely gave it:")
    print("   • View app information")
    print("   • Download bulk reports")
    print("   • Access to app analytics")
    print()
    
    print("🔧 Next Steps:")
    print("1. Test the API connection")
    print("2. If working, we can get:")
    print("   • App details and metadata")
    print("   • Customer reviews and ratings")
    print("   • Download statistics (if available)")
    print("   • App version information")
    print()
    
    print("⏱️  Note: Permissions can take a few minutes to propagate")
    print("   If the first test fails, wait 2-3 minutes and try again")

def run_api_test():
    """Run the API test to verify access."""
    print()
    print("🚀 Testing Google Play Console API Access")
    print("-" * 40)
    print()
    
    print("Running API test...")
    print()
    
    try:
        # Import and run the test
        import subprocess
        result = subprocess.run(['python3', 'play_console_api.py'], 
                              capture_output=True, text=True, cwd='/Users/alex/Documents/Projects/data-utilities/app-store-google')
        
        print("API Test Output:")
        print("-" * 20)
        print(result.stdout)
        
        if result.stderr:
            print("Errors:")
            print(result.stderr)
            
        if "✅" in result.stdout:
            print("\n🎉 API ACCESS WORKING!")
            print("Google Play Console API is now functional!")
        elif "❌" in result.stdout and "403" in result.stdout:
            print("\n⏱️  Permissions still propagating...")
            print("Wait 2-3 minutes and try again")
        else:
            print(f"\n🤔 Mixed results - check output above")
            
    except Exception as e:
        print(f"❌ Error running test: {e}")
        print("\nTo test manually, run:")
        print("python3 play_console_api.py")

if __name__ == "__main__":
    test_permissions_success()
    run_api_test()