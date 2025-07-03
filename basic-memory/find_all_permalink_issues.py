#!/usr/bin/env python3
"""
Find all potential permalink issues in markdown files
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def analyze_permalinks(root_dir):
    """
    Analyze all permalinks in markdown files to find patterns
    """
    root_path = Path(root_dir)
    permalink_patterns = defaultdict(list)
    
    # Pattern to match any permalink line
    permalink_pattern = re.compile(r'^permalink:\s*(.*)$', re.MULTILINE)
    
    for md_file in root_path.rglob('*.md'):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all permalinks in the file
            for match in permalink_pattern.finditer(content):
                permalink = match.group(1).strip()
                relative_path = str(md_file.relative_to(root_path))
                
                # Categorize permalinks by their prefix
                if permalink.startswith('projects/'):
                    permalink_patterns['projects/'].append((relative_path, permalink))
                elif permalink.startswith('project/'):
                    permalink_patterns['project/'].append((relative_path, permalink))
                elif permalink.startswith('trainer-day/'):
                    permalink_patterns['trainer-day/'].append((relative_path, permalink))
                elif permalink:
                    permalink_patterns['other'].append((relative_path, permalink))
        
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
    
    return permalink_patterns

def main():
    # Path to the TrainerDay project
    project_root = "/Users/alex/MyGoogleDrive/notes-basic-memory/Projects/TrainerDay"
    
    print(f"Analyzing permalinks in: {project_root}")
    print("=" * 80)
    
    patterns = analyze_permalinks(project_root)
    
    # Report findings
    for prefix, files in patterns.items():
        if prefix in ['projects/', 'project/', 'other']:
            print(f"\n⚠️  Potential issues with prefix '{prefix}':")
            print("-" * 60)
            for file_path, permalink in files[:10]:  # Show first 10
                print(f"  File: {file_path}")
                print(f"  Permalink: {permalink}")
                print()
            if len(files) > 10:
                print(f"  ... and {len(files) - 10} more files")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("-" * 60)
    for prefix, files in patterns.items():
        print(f"{prefix:<20} {len(files)} files")
    
    # Look for specific problematic patterns
    print("\n" + "=" * 80)
    print("SPECIFIC ISSUES TO FIX:")
    print("-" * 60)
    
    issues_found = False
    for prefix, files in patterns.items():
        if prefix == 'projects/':
            for file_path, permalink in files:
                if permalink.startswith('projects/trainer-day/trainer-day/'):
                    print(f"❌ Fix needed: {file_path}")
                    print(f"   Current: {permalink}")
                    print(f"   Should be: {permalink.replace('projects/trainer-day/trainer-day/', 'trainer-day/')}")
                    print()
                    issues_found = True
    
    if not issues_found:
        print("✅ No more 'projects/trainer-day/trainer-day/' issues found!")

if __name__ == "__main__":
    main()