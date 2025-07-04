#!/usr/bin/env python3
"""
Fix permalinks in markdown files that incorrectly start with 'projects/trainer-day/trainer-day'
and update them to start with just 'trainer-day'
"""

import os
import re
from pathlib import Path

def fix_permalinks(root_dir):
    """
    Walk through all markdown files and fix incorrect permalinks
    """
    root_path = Path(root_dir)
    fixed_files = []
    
    # Pattern to match permalinks starting with projects/trainer-day/trainer-day
    permalink_pattern = re.compile(r'^permalink:\s*projects/trainer-day/trainer-day/(.*)$', re.MULTILINE)
    
    for md_file in root_path.rglob('*.md'):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if file contains the incorrect permalink pattern
            if permalink_pattern.search(content):
                # Replace the incorrect pattern
                new_content = permalink_pattern.sub(r'permalink: trainer-day/\1', content)
                
                # Write the fixed content back
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                fixed_files.append(str(md_file.relative_to(root_path)))
                print(f"Fixed: {md_file.relative_to(root_path)}")
        
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
    
    return fixed_files

def main():
    # Path to the TrainerDay project
    project_root = "/Users/alex/Documents/bm-projects/TrainerDay"
    
    print(f"Searching for incorrect permalinks in: {project_root}")
    print("-" * 60)
    
    fixed_files = fix_permalinks(project_root)
    
    print("-" * 60)
    if fixed_files:
        print(f"\nFixed {len(fixed_files)} files:")
        for file in sorted(fixed_files):
            print(f"  - {file}")
    else:
        print("\nNo files with incorrect permalinks found.")

if __name__ == "__main__":
    main()