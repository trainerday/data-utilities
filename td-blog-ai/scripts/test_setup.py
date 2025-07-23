#!/usr/bin/env python3
"""
Test setup for TrainerDay AI blog system
"""

import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent / 'utils'))

from db_connection import test_connection as test_db
from claude_client import ClaudeClient

def main():
    print("🧪 Testing TrainerDay AI Blog System Setup")
    print("=" * 50)
    
    # Test database connection
    print("\n1. Testing Database Connection...")
    db_success = test_db()
    
    # Test Claude API
    print("\n2. Testing Claude Sonnet 4 API...")
    claude = ClaudeClient()
    claude_success = claude.test_connection()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Setup Summary:")
    print(f"  Database: {'✅ Connected' if db_success else '❌ Failed'}")
    print(f"  Claude API: {'✅ Connected' if claude_success else '❌ Failed'}")
    
    if db_success and claude_success:
        print("\n🎉 System setup complete! Ready to generate blog articles.")
        return True
    else:
        print("\n⚠️ Setup incomplete. Please check your configuration.")
        return False

if __name__ == "__main__":
    main()