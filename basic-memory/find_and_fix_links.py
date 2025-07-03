#!/usr/bin/env python3
"""
Find and fix all links in markdown files that point to old incorrect paths
"""

import os
import re
from pathlib import Path

def find_and_fix_links(root_dir, dry_run=True):
    """
    Find all markdown links and wikilinks that point to old paths and fix them
    """
    root_path = Path(root_dir)
    files_to_fix = []
    total_fixes = 0
    
    # Patterns to find links with old paths
    # 1. Markdown links: [text](path)
    # 2. Wikilinks: [[path]]
    # 3. Reference links: [text]: path
    
    patterns_to_fix = [
        # Markdown links with projects/trainer-day/trainer-day
        (re.compile(r'\[([^\]]+)\]\(projects/trainer-day/trainer-day/([^)]+)\)'),
         lambda m: f'[{m.group(1)}](trainer-day/{m.group(2)})'),
        
        # Wikilinks with projects/trainer-day/trainer-day
        (re.compile(r'\[\[projects/trainer-day/trainer-day/([^\]]+)\]\]'),
         lambda m: f'[[trainer-day/{m.group(1)}]]'),
        
        # Reference links with projects/trainer-day/trainer-day
        (re.compile(r'^(\[.+\]:\s*)projects/trainer-day/trainer-day/(.*)$', re.MULTILINE),
         lambda m: f'{m.group(1)}trainer-day/{m.group(2)}'),
        
        # Also check for project (singular) variants
        (re.compile(r'\[([^\]]+)\]\(project/trainer-day/trainer-day/([^)]+)\)'),
         lambda m: f'[{m.group(1)}](trainer-day/{m.group(2)})'),
        
        (re.compile(r'\[\[project/trainer-day/trainer-day/([^\]]+)\]\]'),
         lambda m: f'[[trainer-day/{m.group(1)}]]'),
        
        # Check for projects/trainer-day (without second trainer-day)
        (re.compile(r'\[([^\]]+)\]\(projects/trainer-day/([^)]+)\)'),
         lambda m: f'[{m.group(1)}](trainer-day/{m.group(2)})'),
        
        (re.compile(r'\[\[projects/trainer-day/([^\]]+)\]\]'),
         lambda m: f'[[trainer-day/{m.group(1)}]]'),
    ]
    
    print(f"{'DRY RUN: ' if dry_run else ''}Searching for links with old paths...")
    print("-" * 80)
    
    for md_file in root_path.rglob('*.md'):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            content = original_content
            file_fixes = 0
            
            # Apply all pattern fixes
            for pattern, replacement in patterns_to_fix:
                matches = pattern.findall(content)
                if matches:
                    content = pattern.sub(replacement, content)
                    file_fixes += len(matches)
            
            # If content changed, save or report
            if content != original_content:
                files_to_fix.append(str(md_file.relative_to(root_path)))
                total_fixes += file_fixes
                
                if not dry_run:
                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Fixed {file_fixes} links in: {md_file.relative_to(root_path)}")
                else:
                    print(f"Would fix {file_fixes} links in: {md_file.relative_to(root_path)}")
                    
                    # Show examples of what would be fixed
                    for pattern, _ in patterns_to_fix:
                        matches = pattern.findall(original_content)
                        for match in matches[:2]:  # Show first 2 examples
                            print(f"  Example: {match}")
                    
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
    
    return files_to_fix, total_fixes

def main():
    project_root = "/Users/alex/Documents/bm-projects/TrainerDay"
    
    print(f"Checking for old path links in: {project_root}")
    print("=" * 80)
    
    # First do a dry run
    files, fixes = find_and_fix_links(project_root, dry_run=True)
    
    print("\n" + "=" * 80)
    print(f"SUMMARY (Dry Run):")
    print(f"Files with old links: {len(files)}")
    print(f"Total links to fix: {fixes}")
    
    if files:
        print("\nFiles that would be fixed:")
        for f in sorted(files):
            print(f"  - {f}")
        
        print("\n" + "=" * 80)
        response = input("Do you want to apply these fixes? (yes/no): ")
        
        if response.lower() == 'yes':
            print("\nApplying fixes...")
            print("-" * 80)
            files, fixes = find_and_fix_links(project_root, dry_run=False)
            print("\n✅ All links have been fixed!")
        else:
            print("\n❌ No changes made.")
    else:
        print("\n✅ No old path links found! All links are already correct.")

if __name__ == "__main__":
    main()