#!/usr/bin/env python3
"""
Verify permalinks match folder structure and fix all mismatches
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

def analyze_permalink_structure(root_dir):
    """
    Check if permalinks match their actual file paths
    """
    root_path = Path(root_dir)
    mismatches = []
    correct_mappings = {}
    all_permalinks = {}
    
    # Pattern to extract permalinks
    permalink_pattern = re.compile(r'^permalink:\s*(.*)$', re.MULTILINE)
    
    print("Analyzing permalink structure...")
    print("-" * 80)
    
    for md_file in root_path.rglob('*.md'):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get relative path from root
            relative_path = str(md_file.relative_to(root_path))
            
            # Expected permalink should be: trainer-day/[path without .md extension]
            expected_permalink = "trainer-day/" + relative_path.replace('.md', '')
            
            # Find actual permalink in file
            match = permalink_pattern.search(content)
            if match:
                actual_permalink = match.group(1).strip()
                all_permalinks[relative_path] = actual_permalink
                
                # Check if they match
                if actual_permalink != expected_permalink:
                    mismatches.append({
                        'file': relative_path,
                        'actual_permalink': actual_permalink,
                        'expected_permalink': expected_permalink,
                        'needs_update': True
                    })
                    print(f"\n❌ Mismatch found:")
                    print(f"   File: {relative_path}")
                    print(f"   Actual:   {actual_permalink}")
                    print(f"   Expected: {expected_permalink}")
                else:
                    correct_mappings[relative_path] = actual_permalink
                    
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
    
    return mismatches, correct_mappings, all_permalinks

def find_all_links(root_dir):
    """
    Find all links in markdown files
    """
    root_path = Path(root_dir)
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
                    
                    # Store link info
                    all_links[relative_path].append({
                        'type': link_type,
                        'target': link_target,
                        'full_match': match
                    })
                    
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
    
    return all_links

def create_fix_plan(mismatches, all_links):
    """
    Create a plan for fixing permalinks and updating links
    """
    fix_plan = {
        'permalink_fixes': [],
        'link_updates': defaultdict(list)
    }
    
    # Plan permalink fixes
    for mismatch in mismatches:
        fix_plan['permalink_fixes'].append({
            'file': mismatch['file'],
            'old_permalink': mismatch['actual_permalink'],
            'new_permalink': mismatch['expected_permalink']
        })
        
        # Find all links that need to be updated
        old_permalink = mismatch['actual_permalink']
        new_permalink = mismatch['expected_permalink']
        
        # Check all files for links to the old permalink
        for file_path, links in all_links.items():
            for link in links:
                target = link['target']
                
                # Check if this link references the old permalink
                if old_permalink in target or old_permalink.replace('trainer-day/', '') in target:
                    fix_plan['link_updates'][file_path].append({
                        'old_target': target,
                        'new_target': target.replace(old_permalink, new_permalink).replace(
                            old_permalink.replace('trainer-day/', ''), 
                            new_permalink.replace('trainer-day/', '')
                        ),
                        'link_type': link['type']
                    })
    
    return fix_plan

def apply_fixes(root_dir, fix_plan):
    """
    Apply all the fixes according to the plan
    """
    root_path = Path(root_dir)
    fixed_count = 0
    
    print("\n" + "=" * 80)
    print("APPLYING FIXES...")
    print("-" * 80)
    
    # Fix permalinks first
    for fix in fix_plan['permalink_fixes']:
        file_path = root_path / fix['file']
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace old permalink with new
            old_line = f"permalink: {fix['old_permalink']}"
            new_line = f"permalink: {fix['new_permalink']}"
            
            if old_line in content:
                content = content.replace(old_line, new_line)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Fixed permalink in: {fix['file']}")
                fixed_count += 1
                
        except Exception as e:
            print(f"❌ Error fixing {fix['file']}: {e}")
    
    # Update links
    for file_path, updates in fix_plan['link_updates'].items():
        if updates:
            full_path = root_path / file_path
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                for update in updates:
                    # Update based on link type
                    if update['link_type'] == 'wikilink':
                        old_link = f"[[{update['old_target']}]]"
                        new_link = f"[[{update['new_target']}]]"
                    else:
                        # For markdown and reference links, preserve the text part
                        old_link = update['old_target']
                        new_link = update['new_target']
                    
                    content = content.replace(old_link, new_link)
                
                if content != original_content:
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✅ Updated links in: {file_path}")
                    
            except Exception as e:
                print(f"❌ Error updating links in {file_path}: {e}")
    
    return fixed_count

def main():
    project_root = "/Users/alex/Documents/bm-projects/TrainerDay"
    
    print(f"Verifying permalink structure in: {project_root}")
    print("=" * 80)
    
    # Step 1: Analyze permalink structure
    mismatches, correct, all_permalinks = analyze_permalink_structure(project_root)
    
    print(f"\n\nFound {len(mismatches)} permalinks that don't match folder structure")
    print(f"Found {len(correct)} permalinks that are correct")
    
    # Step 2: Find all links
    print("\n" + "=" * 80)
    print("Finding all links in files...")
    all_links = find_all_links(project_root)
    
    # Step 3: Create fix plan
    fix_plan = create_fix_plan(mismatches, all_links)
    
    # Save analysis to JSON
    analysis_file = "/Users/alex/Documents/Projects/permalink_analysis.json"
    with open(analysis_file, 'w') as f:
        json.dump({
            'mismatches': mismatches,
            'correct_count': len(correct),
            'total_files': len(all_permalinks),
            'fix_plan': {
                'permalink_fixes': fix_plan['permalink_fixes'],
                'link_updates': {k: v for k, v in fix_plan['link_updates'].items()}
            }
        }, f, indent=2)
    
    print(f"\n✅ Analysis saved to: {analysis_file}")
    
    if mismatches:
        print("\n" + "=" * 80)
        print("FIX PLAN SUMMARY:")
        print("-" * 80)
        print(f"Permalinks to fix: {len(fix_plan['permalink_fixes'])}")
        print(f"Files with links to update: {len(fix_plan['link_updates'])}")
        
        # Apply fixes
        response = input("\nDo you want to apply these fixes? (yes/no): ")
        if response.lower() == 'yes':
            fixed = apply_fixes(project_root, fix_plan)
            print(f"\n✅ Fixed {fixed} permalinks!")
            print("All links have been updated accordingly.")
        else:
            print("\n❌ No changes made.")
    else:
        print("\n✅ All permalinks correctly match their folder structure!")

if __name__ == "__main__":
    main()