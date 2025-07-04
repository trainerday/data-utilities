#!/usr/bin/env python3
"""
Comprehensive check for any permalink issues in all markdown files
"""

import os
import re
from pathlib import Path

def check_all_permalinks(root_dir):
    """
    Recursively check ALL markdown files for permalink issues
    """
    root_path = Path(root_dir)
    total_files = 0
    files_with_permalinks = 0
    problematic_files = []
    
    # Patterns to check for
    problems = [
        (re.compile(r'^permalink:\s*projects/trainer-day/trainer-day/.*$', re.MULTILINE), 
         'projects/trainer-day/trainer-day/'),
        (re.compile(r'^permalink:\s*project/trainer-day/trainer-day/.*$', re.MULTILINE), 
         'project/trainer-day/trainer-day/'),
        (re.compile(r'^permalink:\s*projects/trainer-day/.*$', re.MULTILINE), 
         'projects/trainer-day/'),
        (re.compile(r'^permalink:\s*project/trainer-day/.*$', re.MULTILINE), 
         'project/trainer-day/'),
    ]
    
    print("Recursively checking all .md files...")
    print("-" * 80)
    
    for md_file in root_path.rglob('*.md'):
        total_files += 1
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if file has a permalink
            if re.search(r'^permalink:', content, re.MULTILINE):
                files_with_permalinks += 1
            
            # Check for problematic patterns
            for pattern, problem_desc in problems:
                if pattern.search(content):
                    match = pattern.search(content)
                    problematic_files.append({
                        'file': str(md_file.relative_to(root_path)),
                        'issue': problem_desc,
                        'line': match.group(0)
                    })
                    
        except Exception as e:
            print(f"Error reading {md_file}: {e}")
    
    return total_files, files_with_permalinks, problematic_files

def main():
    project_root = "/Users/alex/Documents/bm-projects/TrainerDay"
    
    print(f"Comprehensive permalink check in: {project_root}")
    print("=" * 80)
    
    total, with_permalinks, problems = check_all_permalinks(project_root)
    
    print(f"\nScan complete!")
    print(f"Total .md files scanned: {total}")
    print(f"Files with permalinks: {with_permalinks}")
    print(f"Files with issues: {len(problems)}")
    
    if problems:
        print("\n" + "=" * 80)
        print("❌ PROBLEMS FOUND:")
        print("-" * 80)
        for problem in problems:
            print(f"\nFile: {problem['file']}")
            print(f"Issue: Contains '{problem['issue']}'")
            print(f"Line: {problem['line']}")
    else:
        print("\n" + "=" * 80)
        print("✅ ALL PERMALINKS ARE CORRECT!")
        print("No files found with problematic permalink patterns.")

if __name__ == "__main__":
    main()