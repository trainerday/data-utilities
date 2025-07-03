#!/usr/bin/env python3
"""
Fix all permalink issues in TD-Business project
- Add missing permalinks
- Correct incorrect permalinks to match file paths
"""

import os
import re
from pathlib import Path
import json

def extract_permalink(content):
    """Extract existing permalink from markdown content"""
    patterns = [
        re.compile(r'^permalink:\s*(.+)$', re.MULTILINE | re.IGNORECASE),
        re.compile(r'^permalink::\s*(.+)$', re.MULTILINE | re.IGNORECASE),
    ]
    
    for pattern in patterns:
        match = pattern.search(content)
        if match:
            return match.group(1).strip(), pattern
    
    return None, None

def get_expected_permalink(file_path, root_path):
    """Generate the expected permalink based on file path"""
    relative_path = file_path.relative_to(root_path)
    # Remove .md extension
    permalink = str(relative_path.with_suffix(''))
    # Ensure forward slashes
    permalink = permalink.replace('\\', '/')
    return permalink

def add_permalink(content, permalink):
    """Add permalink to content that doesn't have one"""
    # Check if file has frontmatter
    if content.startswith('---'):
        # Add to existing frontmatter
        end_index = content.find('---', 3)
        if end_index != -1:
            # Insert before closing ---
            return content[:end_index] + f"permalink: {permalink}\n" + content[end_index:]
    
    # No frontmatter, add at the beginning
    return f"permalink: {permalink}\n\n{content}"

def update_permalink(content, old_permalink, new_permalink, pattern):
    """Update existing permalink"""
    return pattern.sub(f"permalink: {new_permalink}", content)

def fix_permalinks(root_dir, dry_run=True):
    """Fix all permalink issues"""
    root_path = Path(root_dir)
    if not root_path.exists():
        print(f"Error: Directory {root_dir} does not exist!")
        return
    
    fixed_files = []
    added_permalinks = []
    updated_permalinks = []
    
    print(f"{'DRY RUN: ' if dry_run else ''}Fixing permalinks in {root_dir}")
    print("-" * 80)
    
    md_files = list(root_path.rglob('*.md'))
    
    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            content = original_content
            relative_path = str(md_file.relative_to(root_path))
            expected_permalink = get_expected_permalink(md_file, root_path)
            
            # Extract current permalink
            current_permalink, pattern = extract_permalink(content)
            
            if not current_permalink:
                # Add missing permalink
                content = add_permalink(content, expected_permalink)
                added_permalinks.append({
                    'file': relative_path,
                    'permalink': expected_permalink
                })
                print(f"{'Would add' if dry_run else 'Added'} permalink to: {relative_path}")
                print(f"  Permalink: {expected_permalink}")
            elif current_permalink != expected_permalink:
                # Fix incorrect permalink
                content = update_permalink(content, current_permalink, expected_permalink, pattern)
                updated_permalinks.append({
                    'file': relative_path,
                    'old': current_permalink,
                    'new': expected_permalink
                })
                print(f"{'Would update' if dry_run else 'Updated'} permalink in: {relative_path}")
                print(f"  Old: {current_permalink}")
                print(f"  New: {expected_permalink}")
            
            # Save if content changed
            if content != original_content:
                fixed_files.append(relative_path)
                if not dry_run:
                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(content)
        
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
    
    return fixed_files, added_permalinks, updated_permalinks

def main():
    project_root = "/Users/alex/Documents/bm-projects/TD-Business"
    
    print("TD-Business Permalink Fix Tool")
    print("=" * 80)
    
    # First do a dry run
    fixed, added, updated = fix_permalinks(project_root, dry_run=True)
    
    print("\n" + "=" * 80)
    print("SUMMARY (Dry Run):")
    print(f"Files to fix: {len(fixed)}")
    print(f"Permalinks to add: {len(added)}")
    print(f"Permalinks to update: {len(updated)}")
    
    if fixed:
        print("\n" + "=" * 80)
        response = input("Do you want to apply these fixes? (yes/no): ")
        
        if response.lower() == 'yes':
            print("\nApplying fixes...")
            print("-" * 80)
            fixed, added, updated = fix_permalinks(project_root, dry_run=False)
            
            # Save summary
            summary = {
                'fixed_files': fixed,
                'added_permalinks': added,
                'updated_permalinks': updated,
                'total_fixes': len(fixed)
            }
            
            with open('td_business_permalink_fixes.json', 'w') as f:
                json.dump(summary, f, indent=2)
            
            print("\n✅ All permalinks have been fixed!")
            print(f"📄 Fix summary saved to: td_business_permalink_fixes.json")
        else:
            print("\n❌ No changes made.")
    else:
        print("\n✅ No permalink issues found!")

if __name__ == "__main__":
    main()