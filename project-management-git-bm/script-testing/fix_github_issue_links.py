#!/usr/bin/env python3
"""
Fix broken links in GitHub issue #2 after trainer-day → product-development rename
"""

import subprocess
import sys

def update_github_issue():
    """Update GitHub issue #2 with corrected links"""
    
    # New issue body with corrected links
    new_body = """As these items become highest priority they will move to this github project.

Mobile App Backlog
https://github.com/trainerday/Development-Process/blob/master/product-development/os-projects/td-mobile/kanban-board.md

Web App Backlog
https://github.com/trainerday/Development-Process/blob/master/product-development/os-projects/td-web/kanban-board.md

Coach Jack Backlog
https://github.com/trainerday/Development-Process/blob/master/product-development/os-projects/coach-jack/kanban-board.md"""
    
    # Use gh command to update the issue
    cmd = [
        'gh', 'issue', 'edit', '2',
        '--repo', 'trainerday/Development-Process',
        '--body', new_body
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ Successfully updated GitHub issue #2!")
        print(f"Updated links from 'trainer-day' to 'product-development'")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error updating issue: {e}")
        print(f"Command output: {e.stdout}")
        print(f"Command error: {e.stderr}")
        return False

def main():
    print("GitHub Issue Link Fix Tool")
    print("Updating broken links in issue #2 after trainer-day → product-development rename")
    print("=" * 80)
    
    # Check if --apply flag is present
    if '--apply' in sys.argv:
        print("APPLYING FIXES (--apply flag detected)")
        print("-" * 80)
        success = update_github_issue()
        if success:
            print("\n✅ GitHub issue has been updated with corrected links!")
        else:
            print("\n❌ Failed to update GitHub issue.")
    else:
        print("DRY RUN: The following links will be updated:")
        print("\nOld links (broken):")
        print("- https://github.com/trainerday/Development-Process/blob/master/trainer-day/os-projects/td-mobile/kanban-board.md")
        print("- https://github.com/trainerday/Development-Process/blob/master/trainer-day/os-projects/td-web/kanban-board.md")
        print("- https://github.com/trainerday/Development-Process/blob/master/trainer-day/os-projects/coach-jack/kanban-board.md")
        
        print("\nNew links (corrected):")
        print("- https://github.com/trainerday/Development-Process/blob/master/product-development/os-projects/td-mobile/kanban-board.md")
        print("- https://github.com/trainerday/Development-Process/blob/master/product-development/os-projects/td-web/kanban-board.md")
        print("- https://github.com/trainerday/Development-Process/blob/master/product-development/os-projects/coach-jack/kanban-board.md")
        
        print("\nRun with --apply flag to update the GitHub issue.")

if __name__ == "__main__":
    main()