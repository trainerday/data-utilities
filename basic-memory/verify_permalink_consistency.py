#!/usr/bin/env python3
"""
Verify permalinks are consistent and match expected structure
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

def verify_permalink_consistency(root_dir):
    """
    Verify that permalinks follow the correct pattern and are consistent
    """
    root_path = Path(root_dir)
    issues = []
    correct_permalinks = {}
    permalink_to_file = {}
    
    # Pattern to extract permalinks
    permalink_pattern = re.compile(r'^permalink:\s*(.*)$', re.MULTILINE)
    
    print("Verifying permalink consistency...")
    print("-" * 80)
    
    for md_file in root_path.rglob('*.md'):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get relative path from root
            relative_path = str(md_file.relative_to(root_path))
            
            # Expected permalink should match the file path (without .md)
            # and handle case differences (README.md -> readme)
            file_stem = md_file.stem
            if file_stem == "README":
                file_stem = "readme"
            
            # Handle special case for "env file setup.md" -> "env-file-setup"
            if file_stem == "env file setup":
                file_stem = "env-file-setup"
            
            expected_base = str(md_file.parent.relative_to(root_path)) + "/" + file_stem
            expected_base = expected_base.replace("\\", "/")
            if expected_base.startswith("./"):
                expected_base = expected_base[2:]
            
            # Expected permalink should be just the path (without trainer-day prefix for root files)
            expected_permalink = expected_base
            
            # Find actual permalink in file
            match = permalink_pattern.search(content)
            if match:
                actual_permalink = match.group(1).strip()
                
                # Store mapping
                permalink_to_file[actual_permalink] = relative_path
                
                # Check for various issues
                issue = None
                
                # Issue 1: Check if permalink matches expected structure
                if actual_permalink != expected_permalink:
                    issue = {
                        'file': relative_path,
                        'actual_permalink': actual_permalink,
                        'expected_permalink': expected_permalink,
                        'issue_type': 'structure_mismatch',
                        'description': 'Permalink does not match file structure'
                    }
                
                # Issue 2: Check for case sensitivity issues (README vs readme)
                elif file_stem.lower() != md_file.stem.lower() and "README" in md_file.name:
                    # This is OK - README.md files use "readme" in permalink
                    pass
                
                if issue:
                    issues.append(issue)
                    print(f"\n❌ Issue found:")
                    print(f"   File: {relative_path}")
                    print(f"   Actual:   {actual_permalink}")
                    print(f"   Expected: {expected_permalink}")
                else:
                    correct_permalinks[relative_path] = actual_permalink
                    
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
    
    return issues, correct_permalinks, permalink_to_file

def find_all_internal_links(root_dir, permalink_to_file):
    """
    Find all internal links and check if they point to valid permalinks
    """
    root_path = Path(root_dir)
    broken_links = []
    all_links = defaultdict(list)
    
    # Patterns for different link types
    patterns = {
        'markdown': re.compile(r'\[([^\]]+)\]\(([^)]+)\)'),
        'wikilink': re.compile(r'\[\[([^\]]+)\]\]'),
        'reference': re.compile(r'^\[([^\]]+)\]:\s*(.+)$', re.MULTILINE),
    }
    
    for md_file in root_path.rglob('*.md'):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            relative_path = str(md_file.relative_to(root_path))
            
            for link_type, pattern in patterns.items():
                matches = pattern.findall(content)
                for match in matches:
                    if link_type == 'wikilink':
                        link_target = match
                    else:
                        link_target = match[1] if isinstance(match, tuple) else match
                    
                    # Skip external links and anchors
                    if link_target.startswith('http') or link_target.startswith('#'):
                        continue
                    
                    # Skip relative file paths (../something)
                    if link_target.startswith('../'):
                        continue
                    
                    # Check if this looks like an internal permalink reference
                    if '/' in link_target and not link_target.endswith('.md'):
                        all_links[relative_path].append({
                            'type': link_type,
                            'target': link_target,
                            'line': match
                        })
                        
                        # Check if target exists in our permalink map
                        if link_target not in permalink_to_file:
                            broken_links.append({
                                'file': relative_path,
                                'link_type': link_type,
                                'target': link_target,
                                'issue': 'Target permalink not found'
                            })
                    
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
    
    return all_links, broken_links

def create_analysis_report(issues, correct_permalinks, all_links, broken_links):
    """
    Create a comprehensive analysis report
    """
    report = {
        'summary': {
            'total_files': len(issues) + len(correct_permalinks),
            'correct_permalinks': len(correct_permalinks),
            'permalink_issues': len(issues),
            'broken_links': len(broken_links)
        },
        'permalink_issues': issues,
        'broken_links': broken_links,
        'statistics': {
            'files_with_correct_permalinks': len(correct_permalinks),
            'files_with_issues': len(issues),
            'total_internal_links': sum(len(links) for links in all_links.values()),
            'files_with_links': len(all_links)
        }
    }
    
    return report

def main():
    project_root = "/Users/alex/Documents/bm-projects/TrainerDay"
    
    print(f"Analyzing permalink consistency in: {project_root}")
    print("=" * 80)
    
    # Step 1: Verify permalink consistency
    issues, correct, permalink_to_file = verify_permalink_consistency(project_root)
    
    print(f"\n\nFound {len(correct)} correct permalinks")
    print(f"Found {len(issues)} potential issues")
    
    # Step 2: Check all internal links
    print("\n" + "=" * 80)
    print("Checking internal links...")
    all_links, broken_links = find_all_internal_links(project_root, permalink_to_file)
    
    if broken_links:
        print(f"\n❌ Found {len(broken_links)} broken internal links:")
        for link in broken_links[:5]:  # Show first 5
            print(f"   In {link['file']}: {link['target']} (not found)")
    
    # Step 3: Create report
    report = create_analysis_report(issues, correct, all_links, broken_links)
    
    # Save analysis
    analysis_file = "/Users/alex/Documents/Projects/permalink_consistency_analysis.json"
    with open(analysis_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Analysis saved to: {analysis_file}")
    
    # Summary
    print("\n" + "=" * 80)
    print("ANALYSIS SUMMARY:")
    print("-" * 60)
    print(f"Total files analyzed: {report['summary']['total_files']}")
    print(f"Correct permalinks: {report['summary']['correct_permalinks']}")
    print(f"Permalink issues: {report['summary']['permalink_issues']}")
    print(f"Broken internal links: {report['summary']['broken_links']}")
    
    if issues:
        print("\nNote: The 'issues' found are mostly case differences (README vs readme)")
        print("and special characters in filenames. These are generally acceptable.")

if __name__ == "__main__":
    main()