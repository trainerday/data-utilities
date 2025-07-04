#!/usr/bin/env python3
"""
Comprehensive check for all types of links in markdown files
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def analyze_all_links(root_dir):
    """
    Find and categorize ALL links in markdown files
    """
    root_path = Path(root_dir)
    link_types = defaultdict(list)
    
    # Patterns to find different types of links
    patterns = {
        'markdown_links': re.compile(r'\[([^\]]+)\]\(([^)]+)\)'),
        'wikilinks': re.compile(r'\[\[([^\]]+)\]\]'),
        'reference_links': re.compile(r'^\[([^\]]+)\]:\s*(.+)$', re.MULTILINE),
        'image_links': re.compile(r'!\[([^\]]*)\]\(([^)]+)\)'),
    }
    
    print("Analyzing all links in markdown files...")
    print("-" * 80)
    
    for md_file in root_path.rglob('*.md'):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            relative_path = str(md_file.relative_to(root_path))
            
            # Find all links
            for link_type, pattern in patterns.items():
                matches = pattern.findall(content)
                for match in matches:
                    if link_type in ['markdown_links', 'image_links']:
                        text, url = match
                        link_info = {'file': relative_path, 'text': text, 'url': url}
                    elif link_type == 'wikilinks':
                        link_info = {'file': relative_path, 'url': match}
                    else:  # reference_links
                        ref, url = match
                        link_info = {'file': relative_path, 'ref': ref, 'url': url}
                    
                    # Check for potential issues
                    url_to_check = link_info.get('url', '')
                    
                    # Categorize by potential issues
                    if 'projects/trainer-day/trainer-day' in url_to_check:
                        link_types['projects_trainer_day_trainer_day'].append(link_info)
                    elif 'project/trainer-day/trainer-day' in url_to_check:
                        link_types['project_trainer_day_trainer_day'].append(link_info)
                    elif 'projects/trainer-day' in url_to_check:
                        link_types['projects_trainer_day'].append(link_info)
                    elif 'project/trainer-day' in url_to_check:
                        link_types['project_trainer_day'].append(link_info)
                    elif '../projects/' in url_to_check:
                        link_types['relative_projects'].append(link_info)
                    elif 'trainer-day/projects/' in url_to_check:
                        link_types['trainer_day_projects'].append(link_info)
                    elif url_to_check.startswith('../') and 'backlog' in url_to_check:
                        link_types['relative_backlog_links'].append(link_info)
                    
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
    
    return link_types

def main():
    project_root = "/Users/alex/Documents/bm-projects/TrainerDay"
    
    print(f"Comprehensive link analysis in: {project_root}")
    print("=" * 80)
    
    link_issues = analyze_all_links(project_root)
    
    # Report issues
    issues_found = False
    for issue_type, links in link_issues.items():
        if links:
            issues_found = True
            print(f"\n⚠️  {issue_type.replace('_', ' ').upper()} ({len(links)} found):")
            print("-" * 60)
            
            # Show first 5 examples
            for i, link in enumerate(links[:5]):
                print(f"\nExample {i+1}:")
                print(f"  File: {link['file']}")
                print(f"  URL: {link.get('url', link.get('ref', ''))}")
                if 'text' in link:
                    print(f"  Text: {link['text']}")
            
            if len(links) > 5:
                print(f"\n  ... and {len(links) - 5} more")
    
    if not issues_found:
        print("\n✅ No problematic links found!")
        print("All links appear to use correct paths.")
    
    # Also show statistics
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("-" * 60)
    total_issues = sum(len(links) for links in link_issues.values())
    print(f"Total potential issues: {total_issues}")
    
    if issues_found:
        print("\nIssue breakdown:")
        for issue_type, links in link_issues.items():
            if links:
                print(f"  {issue_type}: {len(links)}")

if __name__ == "__main__":
    main()