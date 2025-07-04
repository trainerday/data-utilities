#!/usr/bin/env python3
"""
Analyze permalinks in TD-Business project
Ensures all MD files have permalinks and they follow correct relative folder paths
"""

import os
import re
from pathlib import Path
from collections import defaultdict
import json
import sys

def extract_permalink(content):
    """Extract permalink from markdown content"""
    # Look for permalink in frontmatter or as a property
    # Common patterns:
    # permalink: path/to/file
    # Permalink: path/to/file
    # permalink:: path/to/file
    
    patterns = [
        re.compile(r'^permalink:\s*(.+)$', re.MULTILINE | re.IGNORECASE),
        re.compile(r'^permalink::\s*(.+)$', re.MULTILINE | re.IGNORECASE),
    ]
    
    for pattern in patterns:
        match = pattern.search(content)
        if match:
            return match.group(1).strip()
    
    return None

def get_expected_permalink(file_path, root_path):
    """Generate the expected permalink based on file path"""
    relative_path = file_path.relative_to(root_path)
    # Remove .md extension and convert to permalink format
    permalink = str(relative_path.with_suffix(''))
    # Ensure forward slashes
    permalink = permalink.replace('\\', '/')
    return permalink

def analyze_permalinks(root_dir):
    """Analyze all markdown files for permalink issues"""
    root_path = Path(root_dir)
    if not root_path.exists():
        print(f"Error: Directory {root_dir} does not exist!")
        sys.exit(1)
    
    issues = defaultdict(list)
    stats = defaultdict(int)
    all_permalinks = {}  # Track all permalinks for duplicate detection
    
    print(f"Analyzing permalinks in: {root_dir}")
    print("-" * 80)
    
    md_files = list(root_path.rglob('*.md'))
    stats['total_files'] = len(md_files)
    print(f"Found {len(md_files)} markdown files")
    print("-" * 80)
    
    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            relative_path = str(md_file.relative_to(root_path))
            expected_permalink = get_expected_permalink(md_file, root_path)
            
            # Extract actual permalink
            actual_permalink = extract_permalink(content)
            
            file_info = {
                'file': relative_path,
                'expected_permalink': expected_permalink,
                'actual_permalink': actual_permalink
            }
            
            # Check for various issues
            
            # 1. Missing permalink
            if not actual_permalink:
                issues['missing_permalink'].append(file_info)
                stats['missing_permalinks'] += 1
            else:
                stats['has_permalink'] += 1
                
                # 2. Incorrect permalink (doesn't match file path)
                if actual_permalink != expected_permalink:
                    issues['incorrect_permalink'].append(file_info)
                
                # 3. Check if permalink starts with correct folder structure
                # For TD-Business, common top-level folders might be:
                # company-structure/, research-findings/, strategic-insights/, etc.
                top_level_folders = []
                for item in root_path.iterdir():
                    if item.is_dir() and not item.name.startswith('.'):
                        top_level_folders.append(item.name)
                
                # Check if permalink starts with a valid top-level folder
                permalink_parts = actual_permalink.split('/')
                if permalink_parts and permalink_parts[0] not in top_level_folders:
                    if not actual_permalink.startswith(tuple(f"{folder}/" for folder in top_level_folders)):
                        file_info['top_level_folders'] = top_level_folders
                        issues['invalid_folder_structure'].append(file_info)
                
                # 4. Duplicate permalinks
                if actual_permalink in all_permalinks:
                    issues['duplicate_permalink'].append({
                        'file1': all_permalinks[actual_permalink],
                        'file2': relative_path,
                        'permalink': actual_permalink
                    })
                else:
                    all_permalinks[actual_permalink] = relative_path
                
                # 5. Permalink with spaces or special characters
                if ' ' in actual_permalink or any(char in actual_permalink for char in ['?', '#', '&', '%']):
                    issues['invalid_characters'].append(file_info)
                
                # 6. Permalink with file extension (shouldn't have .md)
                if actual_permalink.endswith('.md'):
                    issues['has_extension'].append(file_info)
            
            # Check all links in the file to see if they use permalinks correctly
            link_patterns = [
                re.compile(r'\[([^\]]+)\]\(([^)]+)\)'),  # Markdown links
                re.compile(r'\[\[([^\]]+)\]\]'),  # Wikilinks
            ]
            
            for pattern in link_patterns:
                matches = pattern.findall(content)
                for match in matches:
                    if len(match) == 2:  # Markdown link
                        link_text, link_url = match
                    else:  # Wikilink
                        link_url = match
                    
                    # Skip external links and anchors
                    if link_url.startswith(('http://', 'https://', '#', 'mailto:')):
                        continue
                    
                    # Check if internal link uses correct permalink format
                    # Should start with a top-level folder
                    if link_url and not any(link_url.startswith(f"{folder}/") for folder in top_level_folders):
                        # Check if it's a relative path that should be a permalink
                        if '../' in link_url or './' in link_url or link_url.endswith('.md'):
                            issues['non_permalink_link'].append({
                                'file': relative_path,
                                'link': link_url,
                                'link_text': link_text if len(match) == 2 else link_url
                            })
                    
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
            stats['errors'] += 1
    
    return issues, stats, top_level_folders

def generate_report(issues, stats, top_level_folders, output_json=False):
    """Generate a detailed report of permalink issues"""
    
    print("\n" + "=" * 80)
    print("PERMALINK ANALYSIS REPORT")
    print("=" * 80)
    
    # Statistics
    print("\nStatistics:")
    print("-" * 40)
    print(f"  Total files: {stats['total_files']}")
    print(f"  Files with permalinks: {stats['has_permalink']}")
    print(f"  Files missing permalinks: {stats['missing_permalinks']}")
    if stats.get('errors', 0) > 0:
        print(f"  Files with errors: {stats['errors']}")
    
    print(f"\nTop-level folders detected: {', '.join(sorted(top_level_folders))}")
    
    # Issues summary
    total_issues = sum(len(issue_list) for issue_list in issues.values())
    print(f"\nTotal permalink issues found: {total_issues}")
    
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
                    if issue_type == 'duplicate_permalink':
                        print(f"  Permalink: {issue['permalink']}")
                        print(f"  File 1: {issue['file1']}")
                        print(f"  File 2: {issue['file2']}")
                    elif issue_type == 'non_permalink_link':
                        print(f"  File: {issue['file']}")
                        print(f"  Link: {issue['link']}")
                        print(f"  Link text: {issue['link_text']}")
                    else:
                        print(f"  File: {issue['file']}")
                        if 'expected_permalink' in issue:
                            print(f"  Expected: {issue['expected_permalink']}")
                        if 'actual_permalink' in issue and issue['actual_permalink']:
                            print(f"  Actual: {issue['actual_permalink']}")
                        if 'top_level_folders' in issue:
                            print(f"  Valid folders: {', '.join(issue['top_level_folders'])}")
                
                if len(issue_list) > 5:
                    print(f"\n  ... and {len(issue_list) - 5} more")
        
        # Provide fixes for missing permalinks
        if issues.get('missing_permalink'):
            print("\n" + "=" * 80)
            print("SUGGESTED PERMALINK ADDITIONS")
            print("=" * 80)
            print("\nAdd these permalinks to the respective files:")
            print("-" * 60)
            
            for issue in issues['missing_permalink'][:10]:
                print(f"\nFile: {issue['file']}")
                print(f"Add: permalink: {issue['expected_permalink']}")
            
            if len(issues['missing_permalink']) > 10:
                print(f"\n... and {len(issues['missing_permalink']) - 10} more files need permalinks")
    
    else:
        print("\n✅ No permalink issues found!")
        print("All files have correct permalinks following the folder structure.")
    
    # Export to JSON if requested
    if output_json:
        output_file = 'td_business_permalink_analysis.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'statistics': dict(stats),
                'top_level_folders': sorted(top_level_folders),
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
    
    print(f"TD-Business Permalink Analysis Tool")
    print("=" * 80)
    
    issues, stats, top_level_folders = analyze_permalinks(project_root)
    generate_report(issues, stats, top_level_folders, output_json=True)
    
    print("\n" + "=" * 80)
    print("Analysis complete!")

if __name__ == "__main__":
    main()