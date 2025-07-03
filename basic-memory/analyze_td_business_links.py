#!/usr/bin/env python3
"""
Comprehensive link analysis for TD-Business project
Identifies various types of link problems in markdown files
"""

import os
import re
from pathlib import Path
from collections import defaultdict
import json
import sys

def check_file_exists(base_path, link_path):
    """Check if a linked file actually exists"""
    # Handle different link formats
    if link_path.startswith('#'):
        return True  # Internal anchor link
    if link_path.startswith('http://') or link_path.startswith('https://'):
        return True  # External URL
    if link_path.startswith('mailto:'):
        return True  # Email link
    
    # Clean up the link path
    link_path = link_path.split('#')[0]  # Remove anchor if present
    link_path = link_path.strip()
    
    if not link_path:
        return True
    
    # Try different path resolutions
    try:
        # Absolute path from project root
        if link_path.startswith('/'):
            full_path = base_path / link_path[1:]
        else:
            # Relative path
            full_path = base_path / link_path
        
        return full_path.exists()
    except:
        return False

def analyze_links(root_dir):
    """
    Comprehensive link analysis for markdown files
    """
    root_path = Path(root_dir)
    if not root_path.exists():
        print(f"Error: Directory {root_dir} does not exist!")
        sys.exit(1)
    
    issues = defaultdict(list)
    stats = defaultdict(int)
    
    # Link patterns
    patterns = {
        'markdown_links': re.compile(r'\[([^\]]+)\]\(([^)]+)\)'),
        'wikilinks': re.compile(r'\[\[([^\]]+)\]\]'),
        'reference_links': re.compile(r'^\[([^\]]+)\]:\s*(.+)$', re.MULTILINE),
        'image_links': re.compile(r'!\[([^\]]*)\]\(([^)]+)\)'),
    }
    
    print(f"Analyzing links in: {root_dir}")
    print("-" * 80)
    
    md_files = list(root_path.rglob('*.md'))
    print(f"Found {len(md_files)} markdown files")
    print("-" * 80)
    
    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            relative_path = str(md_file.relative_to(root_path))
            file_dir = md_file.parent
            
            # Analyze each type of link
            for link_type, pattern in patterns.items():
                matches = pattern.findall(content)
                stats[link_type] += len(matches)
                
                for match in matches:
                    link_info = {'file': relative_path, 'line': None}
                    
                    # Extract URL based on link type
                    if link_type in ['markdown_links', 'image_links']:
                        text, url = match
                        link_info['text'] = text
                        link_info['url'] = url
                    elif link_type == 'wikilinks':
                        link_info['url'] = match
                    else:  # reference_links
                        ref, url = match
                        link_info['ref'] = ref
                        link_info['url'] = url
                    
                    url = link_info['url']
                    
                    # Find line number
                    for i, line in enumerate(content.split('\n'), 1):
                        if url in line:
                            link_info['line'] = i
                            break
                    
                    # Check for various issues
                    
                    # 1. Broken links (file doesn't exist)
                    if not url.startswith(('http://', 'https://', '#', 'mailto:')):
                        if not check_file_exists(file_dir, url):
                            issues['broken_links'].append(link_info)
                    
                    # 2. Double slashes (except in URLs)
                    if '//' in url and not url.startswith(('http://', 'https://')):
                        issues['double_slashes'].append(link_info)
                    
                    # 3. Inconsistent path patterns
                    if 'projects/trainer-day/trainer-day' in url:
                        issues['redundant_trainer_day_path'].append(link_info)
                    elif 'project/trainer-day/trainer-day' in url:
                        issues['singular_project_path'].append(link_info)
                    elif '../projects/' in url:
                        issues['relative_projects_path'].append(link_info)
                    elif '../backlogs/' in url or '../backlog/' in url:
                        issues['relative_backlog_path'].append(link_info)
                    
                    # 4. Mixed path separators
                    if '\\' in url:
                        issues['backslash_in_path'].append(link_info)
                    
                    # 5. Spaces in URLs (should be encoded)
                    if ' ' in url and not url.startswith('mailto:'):
                        if '%20' not in url:
                            issues['unencoded_spaces'].append(link_info)
                    
                    # 6. Empty or malformed links
                    if not url or url.isspace():
                        issues['empty_links'].append(link_info)
                    
                    # 7. Links with query parameters or fragments that might be broken
                    if '?' in url and not url.startswith(('http://', 'https://')):
                        issues['query_in_local_link'].append(link_info)
                    
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
            stats['errors'] += 1
    
    return issues, stats

def generate_report(issues, stats, output_json=False):
    """Generate a detailed report of link issues"""
    
    print("\n" + "=" * 80)
    print("LINK ANALYSIS REPORT")
    print("=" * 80)
    
    # Statistics
    print("\nStatistics:")
    print("-" * 40)
    for link_type, count in stats.items():
        if link_type != 'errors':
            print(f"  {link_type.replace('_', ' ').title()}: {count}")
    if stats.get('errors', 0) > 0:
        print(f"  Files with errors: {stats['errors']}")
    
    # Issues summary
    total_issues = sum(len(issue_list) for issue_list in issues.values())
    print(f"\nTotal issues found: {total_issues}")
    
    if total_issues > 0:
        print("\nIssues by type:")
        print("-" * 40)
        
        # Sort issues by count
        sorted_issues = sorted(issues.items(), key=lambda x: len(x[1]), reverse=True)
        
        for issue_type, issue_list in sorted_issues:
            if issue_list:
                print(f"\n{issue_type.replace('_', ' ').upper()} ({len(issue_list)} found):")
                print("-" * 60)
                
                # Show up to 5 examples
                for i, issue in enumerate(issue_list[:5]):
                    print(f"\nExample {i+1}:")
                    print(f"  File: {issue['file']}")
                    if issue.get('line'):
                        print(f"  Line: {issue['line']}")
                    print(f"  URL: {issue['url']}")
                    if 'text' in issue:
                        print(f"  Text: {issue['text']}")
                    elif 'ref' in issue:
                        print(f"  Reference: {issue['ref']}")
                
                if len(issue_list) > 5:
                    print(f"\n  ... and {len(issue_list) - 5} more")
    else:
        print("\n✅ No link issues found!")
    
    # Export to JSON if requested
    if output_json:
        output_file = 'td_business_link_analysis.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'statistics': dict(stats),
                'issues': {k: v for k, v in issues.items()},
                'summary': {
                    'total_issues': total_issues,
                    'issue_counts': {k: len(v) for k, v in issues.items()}
                }
            }, f, indent=2)
        print(f"\n📄 Detailed report exported to: {output_file}")

def main():
    # Get project path from command line or use default
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = "/Users/alex/Documents/bm-projects/TD-Business"
    
    print(f"TD-Business Link Analysis Tool")
    print("=" * 80)
    
    issues, stats = analyze_links(project_root)
    generate_report(issues, stats, output_json=True)
    
    print("\n" + "=" * 80)
    print("Analysis complete!")

if __name__ == "__main__":
    main()