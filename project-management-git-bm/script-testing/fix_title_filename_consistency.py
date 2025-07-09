#!/usr/bin/env python3
"""
Fix title/filename consistency issues in addition to permalinks
- Ensure titles match expected format based on filename
- Fix permalinks to match file paths
- Check for and report inconsistencies
"""

import os
import re
import sys
from pathlib import Path
import json

def extract_title_and_permalink(content):
    """Extract existing title and permalink from markdown content"""
    title_pattern = re.compile(r'^title:\s*(.+)$', re.MULTILINE | re.IGNORECASE)
    permalink_patterns = [
        re.compile(r'^permalink:\s*(.+)$', re.MULTILINE | re.IGNORECASE),
        re.compile(r'^permalink::\s*(.+)$', re.MULTILINE | re.IGNORECASE),
    ]
    
    title_match = title_pattern.search(content)
    title = title_match.group(1).strip() if title_match else None
    
    permalink = None
    permalink_pattern = None
    for pattern in permalink_patterns:
        match = pattern.search(content)
        if match:
            permalink = match.group(1).strip()
            permalink_pattern = pattern
            break
    
    return title, permalink, title_pattern, permalink_pattern

def generate_expected_title(filename):
    """Generate expected title from filename"""
    # Remove .md extension and convert to title case
    base = filename.replace('.md', '')
    
    # Handle special cases
    if base.startswith('CJ ') or base.startswith('CJ-'):
        # Keep CJ prefix
        parts = base.replace('CJ-', 'CJ ').replace('CJ ', '').split('-')
        return 'CJ ' + ' '.join(word.capitalize() for word in parts)
    elif 'README' in base.upper():
        return 'README'
    else:
        # Standard title case conversion
        return ' '.join(word.capitalize() for word in base.split('-'))

def generate_expected_permalink(file_path, root_path):
    """Generate expected permalink from file path"""
    relative_path = file_path.relative_to(root_path)
    permalink = str(relative_path.with_suffix(''))
    return permalink.replace('\\', '/')

def update_frontmatter(content, title, permalink, title_pattern, permalink_pattern):
    """Update title and/or permalink in frontmatter"""
    # Handle title
    if title_pattern and title:
        content = title_pattern.sub(f"title: {title}", content)
    elif title and not title_pattern:
        # Add title to frontmatter
        if content.startswith('---'):
            end_index = content.find('---', 3)
            if end_index != -1:
                content = content[:end_index] + f"title: {title}\n" + content[end_index:]
        else:
            content = f"---\ntitle: {title}\n---\n\n{content}"
    
    # Handle permalink
    if permalink_pattern and permalink:
        content = permalink_pattern.sub(f"permalink: {permalink}", content)
    elif permalink and not permalink_pattern:
        # Add permalink to frontmatter
        if content.startswith('---'):
            end_index = content.find('---', 3)
            if end_index != -1:
                content = content[:end_index] + f"permalink: {permalink}\n" + content[end_index:]
        else:
            content = f"---\npermalink: {permalink}\n---\n\n{content}"
    
    return content

def fix_consistency_issues(root_dir, dry_run=True):
    """Fix title/filename and permalink consistency issues"""
    root_path = Path(root_dir)
    if not root_path.exists():
        print(f"Error: Directory {root_dir} does not exist!")
        return
    
    title_fixes = []
    permalink_fixes = []
    files_modified = []
    
    print(f"{'DRY RUN: ' if dry_run else ''}Fixing title/filename and permalink consistency")
    print("-" * 80)
    
    md_files = list(root_path.rglob('*.md'))
    
    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            content = original_content
            relative_path = str(md_file.relative_to(root_path))
            file_changed = False
            
            # Extract current title and permalink
            current_title, current_permalink, title_pattern, permalink_pattern = extract_title_and_permalink(content)
            
            # Generate expected values
            expected_title = generate_expected_title(md_file.name)
            expected_permalink = generate_expected_permalink(md_file, root_path)
            
            # Check title consistency
            title_needs_fix = False
            if not current_title:
                title_needs_fix = True
                fix_type = "add"
            elif current_title != expected_title:
                title_needs_fix = True
                fix_type = "update"
            
            # Check permalink consistency
            permalink_needs_fix = False
            if not current_permalink:
                permalink_needs_fix = True
                perm_fix_type = "add"
            elif current_permalink != expected_permalink:
                permalink_needs_fix = True
                perm_fix_type = "update"
            
            # Apply fixes
            if title_needs_fix:
                content = update_frontmatter(
                    content, expected_title, None, 
                    title_pattern, None
                )
                title_fixes.append({
                    'file': relative_path,
                    'type': fix_type,
                    'old': current_title,
                    'new': expected_title
                })
                file_changed = True
                print(f"{'Would ' + fix_type if dry_run else fix_type.capitalize() + 'd'} title in: {relative_path}")
                if current_title:
                    print(f"  Old: {current_title}")
                print(f"  New: {expected_title}")
            
            if permalink_needs_fix:
                content = update_frontmatter(
                    content, None, expected_permalink, 
                    None, permalink_pattern
                )
                permalink_fixes.append({
                    'file': relative_path,
                    'type': perm_fix_type,
                    'old': current_permalink,
                    'new': expected_permalink
                })
                file_changed = True
                print(f"{'Would ' + perm_fix_type if dry_run else perm_fix_type.capitalize() + 'd'} permalink in: {relative_path}")
                if current_permalink:
                    print(f"  Old: {current_permalink}")
                print(f"  New: {expected_permalink}")
            
            # Save if content changed
            if file_changed:
                files_modified.append(relative_path)
                if not dry_run:
                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(content)
        
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
    
    return title_fixes, permalink_fixes, files_modified

def main():
    project_root = "/Users/alex/Documents/bm-projects/TrainerDay"
    
    # Check for --apply flag
    apply_fixes = '--apply' in sys.argv
    
    print("TrainerDay Title/Filename and Permalink Consistency Fix Tool")
    print("=" * 80)
    
    if apply_fixes:
        print("APPLYING FIXES (--apply flag detected)")
        print("-" * 80)
        title_fixes, permalink_fixes, files_modified = fix_consistency_issues(project_root, dry_run=False)
        
        # Save summary
        summary = {
            'files_modified': files_modified,
            'title_fixes': title_fixes,
            'permalink_fixes': permalink_fixes,
            'total_changes': len(title_fixes) + len(permalink_fixes)
        }
        
        with open('title_filename_consistency_fixes.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print("\n✅ All title/filename and permalink issues have been fixed!")
        print(f"📄 Fix summary saved to: title_filename_consistency_fixes.json")
        return
    
    # First do a dry run
    title_fixes, permalink_fixes, files_modified = fix_consistency_issues(project_root, dry_run=True)
    
    print("\n" + "=" * 80)
    print("SUMMARY (Dry Run):")
    print(f"Files to modify: {len(files_modified)}")
    print(f"Title fixes needed: {len(title_fixes)}")
    print(f"Permalink fixes needed: {len(permalink_fixes)}")
    
    if files_modified:
        print(f"\nRun with --apply flag to fix these issues.")
        print("After applying fixes, push to GitHub and then fix any broken GitHub issue links.")
    else:
        print("\n✅ No consistency issues found!")

if __name__ == "__main__":
    main()