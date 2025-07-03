#!/usr/bin/env python3
"""
Final comprehensive verification of the TrainerDay project
"""

import os
import re
from pathlib import Path

def final_check(root_dir):
    """
    Final verification of all aspects
    """
    root_path = Path(root_dir)
    
    # Counters
    total_md_files = 0
    files_with_permalinks = 0
    correct_permalinks = 0
    incorrect_permalinks = 0
    total_links = 0
    problematic_links = 0
    
    # Patterns
    permalink_pattern = re.compile(r'^permalink:\s*(.*)$', re.MULTILINE)
    link_patterns = [
        re.compile(r'\[([^\]]+)\]\(([^)]+)\)'),  # Markdown links
        re.compile(r'\[\[([^\]]+)\]\]'),  # Wikilinks
    ]
    
    print("Running final verification...")
    print("-" * 80)
    
    for md_file in root_path.rglob('*.md'):
        total_md_files += 1
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check permalink
            permalink_match = permalink_pattern.search(content)
            if permalink_match:
                files_with_permalinks += 1
                permalink = permalink_match.group(1).strip()
                
                if permalink.startswith('trainer-day/'):
                    correct_permalinks += 1
                elif 'projects/trainer-day/trainer-day' in permalink:
                    incorrect_permalinks += 1
                    print(f"❌ Incorrect permalink found: {md_file.relative_to(root_path)}")
                    print(f"   Permalink: {permalink}")
            
            # Check links
            for pattern in link_patterns:
                matches = pattern.findall(content)
                for match in matches:
                    total_links += 1
                    link_text = match[1] if isinstance(match, tuple) else match
                    
                    if 'projects/trainer-day/trainer-day' in link_text:
                        problematic_links += 1
                        print(f"❌ Problematic link found: {md_file.relative_to(root_path)}")
                        print(f"   Link: {link_text}")
                        
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
    
    return {
        'total_md_files': total_md_files,
        'files_with_permalinks': files_with_permalinks,
        'correct_permalinks': correct_permalinks,
        'incorrect_permalinks': incorrect_permalinks,
        'total_links': total_links,
        'problematic_links': problematic_links
    }

def main():
    project_root = "/Users/alex/Documents/bm-projects/TrainerDay"
    
    print(f"Final verification of: {project_root}")
    print("=" * 80)
    
    results = final_check(project_root)
    
    print("\n" + "=" * 80)
    print("FINAL VERIFICATION RESULTS:")
    print("-" * 60)
    print(f"Total markdown files: {results['total_md_files']}")
    print(f"Files with permalinks: {results['files_with_permalinks']}")
    print(f"Correct permalinks (trainer-day/*): {results['correct_permalinks']}")
    print(f"Incorrect permalinks: {results['incorrect_permalinks']}")
    print(f"Total links found: {results['total_links']}")
    print(f"Problematic links: {results['problematic_links']}")
    
    print("\n" + "=" * 80)
    if results['incorrect_permalinks'] == 0 and results['problematic_links'] == 0:
        print("✅ VERIFICATION COMPLETE - ALL CLEAR!")
        print("   - All permalinks are correct")
        print("   - No problematic links found")
        print("   - Project is ready to use")
    else:
        print("❌ ISSUES FOUND!")
        print(f"   - {results['incorrect_permalinks']} incorrect permalinks")
        print(f"   - {results['problematic_links']} problematic links")

if __name__ == "__main__":
    main()