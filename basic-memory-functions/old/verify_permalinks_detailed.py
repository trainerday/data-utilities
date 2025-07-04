#!/usr/bin/env python3
"""
Detailed verification of all permalinks to ensure they're correct
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def verify_all_permalinks(root_dir):
    """
    Show all permalinks and verify they match expected patterns
    """
    root_path = Path(root_dir)
    permalink_stats = defaultdict(int)
    all_permalinks = []
    
    # Pattern to extract permalinks
    permalink_pattern = re.compile(r'^permalink:\s*(.*)$', re.MULTILINE)
    
    print("Analyzing all permalinks...")
    print("-" * 80)
    
    for md_file in root_path.rglob('*.md'):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find permalink in the file
            match = permalink_pattern.search(content)
            if match:
                permalink = match.group(1).strip()
                relative_path = str(md_file.relative_to(root_path))
                
                # Categorize permalink
                if permalink.startswith('trainer-day/'):
                    permalink_stats['correct_trainer_day'] += 1
                elif permalink.startswith('projects/'):
                    permalink_stats['incorrect_projects'] += 1
                elif permalink.startswith('project/'):
                    permalink_stats['incorrect_project'] += 1
                elif '[' in permalink:  # Template placeholders
                    permalink_stats['template_placeholder'] += 1
                else:
                    permalink_stats['other'] += 1
                
                all_permalinks.append({
                    'file': relative_path,
                    'permalink': permalink,
                    'category': 'correct' if permalink.startswith('trainer-day/') else 'check'
                })
                
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
    
    return permalink_stats, all_permalinks

def main():
    project_root = "/Users/alex/Documents/bm-projects/TrainerDay"
    
    print(f"Detailed permalink verification in: {project_root}")
    print("=" * 80)
    
    stats, permalinks = verify_all_permalinks(project_root)
    
    # Show statistics
    print("\nPERMALINK STATISTICS:")
    print("-" * 60)
    for category, count in sorted(stats.items()):
        status = "✅" if "correct" in category else "❌" if "incorrect" in category else "ℹ️"
        print(f"{status} {category}: {count}")
    
    # Show any problematic permalinks
    print("\n" + "=" * 80)
    problems = [p for p in permalinks if p['category'] == 'check']
    
    if problems:
        print("PERMALINKS THAT NEED REVIEW:")
        print("-" * 60)
        for p in problems:
            print(f"\nFile: {p['file']}")
            print(f"Permalink: {p['permalink']}")
    else:
        print("✅ ALL PERMALINKS FOLLOW THE CORRECT PATTERN!")
    
    # Show first 10 correct permalinks as examples
    print("\n" + "=" * 80)
    print("SAMPLE OF CORRECT PERMALINKS:")
    print("-" * 60)
    correct = [p for p in permalinks if p['permalink'].startswith('trainer-day/')][:10]
    for p in correct:
        print(f"{p['file']:<50} → {p['permalink']}")

if __name__ == "__main__":
    main()