#!/usr/bin/env python3
"""
Fix all link issues in TD-Business project
- Convert file-based links to permalink-based links
- Fix broken links by mapping to correct permalinks
- URL encode spaces in image links
"""

import os
import re
from pathlib import Path
import json
from urllib.parse import quote

def load_permalink_map(root_dir):
    """Build a map of all files and their permalinks"""
    root_path = Path(root_dir)
    permalink_map = {}
    file_map = {}
    
    # First pass - collect all permalinks
    for md_file in root_path.rglob('*.md'):
        relative_path = str(md_file.relative_to(root_path))
        
        # Expected permalink (what it should be)
        expected_permalink = str(md_file.relative_to(root_path).with_suffix(''))
        expected_permalink = expected_permalink.replace('\\', '/')
        
        # Store mapping
        filename = md_file.name
        file_map[filename] = expected_permalink
        
        # Also store without .md extension
        filename_no_ext = md_file.stem
        file_map[filename_no_ext] = expected_permalink
        
        # Store the full relative path mapping
        file_map[relative_path] = expected_permalink
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract actual permalink if it exists
            permalink_pattern = re.compile(r'^permalink:\s*(.+)$', re.MULTILINE | re.IGNORECASE)
            match = permalink_pattern.search(content)
            if match:
                actual_permalink = match.group(1).strip()
                permalink_map[actual_permalink] = expected_permalink
        except:
            pass
    
    return permalink_map, file_map

def fix_link(url, file_map, current_file_dir, root_path):
    """Fix a single link"""
    # Skip external links and anchors
    if url.startswith(('http://', 'https://', '#', 'mailto:')):
        return url, False
    
    # Handle image links with spaces
    if ' ' in url and (url.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg'))):
        return quote(url, safe='/'), True
    
    # Remove .md extension if present
    url_no_md = url
    if url.endswith('.md'):
        url_no_md = url[:-3]
    
    # Try to find the target file
    # 1. Direct filename match
    if url in file_map:
        return file_map[url], True
    if url_no_md in file_map:
        return file_map[url_no_md], True
    
    # 2. Try as relative path from current file
    if url.startswith('../') or url.startswith('./'):
        try:
            # Resolve relative path
            resolved = (current_file_dir / url).resolve()
            relative_to_root = resolved.relative_to(root_path)
            relative_str = str(relative_to_root).replace('\\', '/')
            
            if relative_str in file_map:
                return file_map[relative_str], True
            
            # Try without .md
            relative_no_md = relative_str
            if relative_str.endswith('.md'):
                relative_no_md = relative_str[:-3]
            if relative_no_md in file_map:
                return file_map[relative_no_md], True
        except:
            pass
    
    # 3. Try common broken patterns
    # Fix "company-structure/priority-board-tasks/..." pattern
    if url.startswith('company-structure/priority-board-tasks/'):
        # These files might actually be in priority-board-tasks/
        alternative = url.replace('company-structure/priority-board-tasks/', 'priority-board-tasks/')
        if alternative in file_map:
            return file_map[alternative], True
    
    # 4. Last resort - search for filename only
    parts = url.split('/')
    if parts:
        filename = parts[-1]
        if filename in file_map:
            return file_map[filename], True
        if filename.endswith('.md'):
            filename_no_md = filename[:-3]
            if filename_no_md in file_map:
                return file_map[filename_no_md], True
    
    # Couldn't fix - return original
    return url, False

def fix_links_in_file(file_path, permalink_map, file_map, root_path, dry_run=True):
    """Fix all links in a single file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    content = original_content
    fixes = []
    file_dir = file_path.parent
    
    # Pattern for markdown links
    md_link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    
    def replace_link(match):
        text = match.group(1)
        url = match.group(2)
        
        fixed_url, was_fixed = fix_link(url, file_map, file_dir, root_path)
        
        if was_fixed:
            fixes.append({
                'original': url,
                'fixed': fixed_url,
                'text': text
            })
            return f'[{text}]({fixed_url})'
        
        return match.group(0)
    
    # Fix markdown links
    content = md_link_pattern.sub(replace_link, content)
    
    # Pattern for wikilinks
    wiki_pattern = re.compile(r'\[\[([^\]]+)\]\]')
    
    def replace_wikilink(match):
        url = match.group(1)
        
        fixed_url, was_fixed = fix_link(url, file_map, file_dir, root_path)
        
        if was_fixed:
            fixes.append({
                'original': url,
                'fixed': fixed_url,
                'type': 'wikilink'
            })
            return f'[[{fixed_url}]]'
        
        return match.group(0)
    
    # Fix wikilinks
    content = wiki_pattern.sub(replace_wikilink, content)
    
    # Save if changed
    if content != original_content and not dry_run:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return fixes, content != original_content

def fix_all_links(root_dir, dry_run=True):
    """Fix all links in the project"""
    root_path = Path(root_dir)
    if not root_path.exists():
        print(f"Error: Directory {root_dir} does not exist!")
        return
    
    print(f"{'DRY RUN: ' if dry_run else ''}Building permalink map...")
    permalink_map, file_map = load_permalink_map(root_dir)
    print(f"Found {len(file_map)} files/permalinks")
    
    all_fixes = []
    files_fixed = []
    
    print(f"\n{'DRY RUN: ' if dry_run else ''}Fixing links...")
    print("-" * 80)
    
    for md_file in root_path.rglob('*.md'):
        try:
            relative_path = str(md_file.relative_to(root_path))
            fixes, changed = fix_links_in_file(md_file, permalink_map, file_map, root_path, dry_run)
            
            if fixes:
                all_fixes.extend([{**fix, 'file': relative_path} for fix in fixes])
                files_fixed.append(relative_path)
                
                print(f"\n{'Would fix' if dry_run else 'Fixed'} {len(fixes)} links in: {relative_path}")
                for fix in fixes[:3]:  # Show first 3
                    print(f"  {fix['original']} → {fix['fixed']}")
                if len(fixes) > 3:
                    print(f"  ... and {len(fixes) - 3} more")
        
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
    
    return all_fixes, files_fixed

def main():
    project_root = "/Users/alex/Documents/bm-projects/TD-Business"
    
    print("TD-Business Link Fix Tool")
    print("=" * 80)
    
    # First do a dry run
    fixes, files = fix_all_links(project_root, dry_run=True)
    
    print("\n" + "=" * 80)
    print("SUMMARY (Dry Run):")
    print(f"Files with broken links: {len(files)}")
    print(f"Total links to fix: {len(fixes)}")
    
    if fixes:
        print("\n" + "=" * 80)
        response = input("Do you want to apply these fixes? (yes/no): ")
        
        if response.lower() == 'yes':
            print("\nApplying fixes...")
            print("-" * 80)
            fixes, files = fix_all_links(project_root, dry_run=False)
            
            # Save summary
            summary = {
                'fixed_files': files,
                'total_fixes': len(fixes),
                'fixes': fixes
            }
            
            with open('td_business_link_fixes.json', 'w') as f:
                json.dump(summary, f, indent=2)
            
            print("\n✅ All links have been fixed!")
            print(f"📄 Fix summary saved to: td_business_link_fixes.json")
        else:
            print("\n❌ No changes made.")
    else:
        print("\n✅ No broken links found!")

if __name__ == "__main__":
    main()