#!/usr/bin/env python3
"""
Helper script to find the correct Google Play package name.
"""

def find_package_name():
    """Help user find the correct package name."""
    print("🔍 Finding Your Google Play Package Name")
    print("=" * 50)
    print()
    
    print("📱 You provided: 4973346410933177334")
    print("   ↳ This is a Google Play Console App ID (numeric)")
    print("   ↳ We need the Package Name (text format)")
    print()
    
    print("🎯 How to Find Package Name:")
    print()
    
    print("Method 1 - Google Play Console:")
    print("1. Go to https://play.google.com/console/")
    print("2. Select your TrainerDay app")
    print("3. Go to 'App information' → 'App details'")
    print("4. Look for 'Package name' field")
    print("   Example: com.trainerday.app")
    print()
    
    print("Method 2 - Google Play Store:")
    print("1. Go to your app's Play Store page")
    print("2. Look at the URL:")
    print("   https://play.google.com/store/apps/details?id=PACKAGE_NAME")
    print("3. The 'id=' part is your package name")
    print()
    
    print("Method 3 - From APK (if you have it):")
    print("1. The package name is in the AndroidManifest.xml")
    print("2. Same as 'applicationId' in build.gradle")
    print()
    
    print("📋 Common Package Name Formats:")
    print("   • com.trainerday.app")
    print("   • com.trainerday.cycling")
    print("   • com.trainerday.trainer")
    print("   • trainerday.turbo (if same as iOS)")
    print("   • com.yourcompany.trainerday")
    print()
    
    print("🔧 Once you have it:")
    print("1. Update .env file:")
    print("   PACKAGE_NAME=your.actual.package.name")
    print("2. Run: python3 play_console_api.py")
    print()
    
    # Try some common variations
    print("🤔 Want to try some common guesses?")
    guesses = [
        "com.trainerday.app",
        "com.trainerday.cycling", 
        "com.trainerday.trainer",
        "trainerday.turbo",
        "com.trainerday.trainerday"
    ]
    
    print("   We could test these common patterns:")
    for guess in guesses:
        print(f"   • {guess}")
    
    print()
    print("📞 Need help? Check your Google Play Console or app store listing!")

if __name__ == "__main__":
    find_package_name()