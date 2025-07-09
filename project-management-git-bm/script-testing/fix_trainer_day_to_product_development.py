#!/usr/bin/env python3
"""
Fix all permalinks after renaming trainer-day folder to product-development
- Update all permalinks that start with "trainer-day/" to "product-development/"
- Handle both actual permalinks in frontmatter and wikilinks/markdown links
"""

import os
import re
import sys
from pathlib import Path
import json

def extract_permalink(content):
    """Extract existing permalink from markdown content"""
    patterns = [
        re.compile(r'^permalink:\s*(.+)$', re.MULTILINE | re.IGNORECASE),
        re.compile(r'^permalink::\s*(.+)$', re.MULTILINE | re.IGNORECASE),
    ]
    
    for pattern in patterns:
        match = pattern.search(content)
        if match:
            return match.group(1).strip(), pattern
    
    return None, None

def update_permalink_in_content(content, old_permalink, new_permalink, pattern):
    """Update existing permalink in content"""
    return pattern.sub(f"permalink: {new_permalink}", content)

def fix_permalink_references(content):
    """Fix all references to trainer-day paths in content"""
    fixes = []
    
    # Fix markdown links [text](trainer-day/...)
    md_link_pattern = re.compile(r'\[([^\]]+)\]\(trainer-day/([^)]+)\)')
    def replace_md_link(match):
        text = match.group(1)
        path = match.group(2)
        old_url = f"trainer-day/{path}"
        new_url = f"product-development/{path}"
        fixes.append({'type': 'markdown_link', 'old': old_url, 'new': new_url})
        return f'[{text}](product-development/{path})'
    
    content = md_link_pattern.sub(replace_md_link, content)
    
    # Fix wikilinks [[trainer-day/...]]
    wiki_pattern = re.compile(r'\[\[trainer-day/([^\]]+)\]\]')
    def replace_wiki_link(match):
        path = match.group(1)
        old_url = f"trainer-day/{path}"
        new_url = f"product-development/{path}"
        fixes.append({'type': 'wikilink', 'old': old_url, 'new': new_url})
        return f'[[product-development/{path}]]'
    
    content = wiki_pattern.sub(replace_wiki_link, content)
    
    return content, fixes

def fix_file_permalinks(root_dir, dry_run=True):
    """Fix all permalinks and references in the project"""
    root_path = Path(root_dir)
    if not root_path.exists():
        print(f"Error: Directory {root_dir} does not exist!")
        return
    
    permalink_updates = []
    reference_fixes = []
    files_modified = []
    
    print(f"{'DRY RUN: ' if dry_run else ''}Updating permalinks from trainer-day to product-development")
    print("-" * 80)
    
    md_files = list(root_path.rglob('*.md'))
    
    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            content = original_content
            relative_path = str(md_file.relative_to(root_path))
            file_changed = False
            
            # 1. Check and update permalink in frontmatter
            current_permalink, pattern = extract_permalink(content)
            if current_permalink and current_permalink.startswith('trainer-day/'):
                new_permalink = current_permalink.replace('trainer-day/', 'product-development/', 1)
                content = update_permalink_in_content(content, current_permalink, new_permalink, pattern)
                permalink_updates.append({
                    'file': relative_path,
                    'old': current_permalink,
                    'new': new_permalink
                })
                file_changed = True
                print(f"{'Would update' if dry_run else 'Updated'} permalink in: {relative_path}")
                print(f"  Old: {current_permalink}")
                print(f"  New: {new_permalink}")
            
            # 2. Fix all references to trainer-day paths in content
            updated_content, fixes = fix_permalink_references(content)
            if fixes:
                content = updated_content
                reference_fixes.extend([{**fix, 'file': relative_path} for fix in fixes])
                file_changed = True
                print(f"{'Would fix' if dry_run else 'Fixed'} {len(fixes)} references in: {relative_path}")
                for fix in fixes[:3]:  # Show first 3
                    print(f"  {fix['old']} → {fix['new']}")
                if len(fixes) > 3:
                    print(f"  ... and {len(fixes) - 3} more")
            
            # Save if content changed
            if file_changed:
                files_modified.append(relative_path)
                if not dry_run:
                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(content)
        
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
    
    return permalink_updates, reference_fixes, files_modified

def main():
    project_root = "/Users/alex/Documents/bm-projects/TrainerDay"
    
    # Check for --apply flag
    apply_fixes = '--apply' in sys.argv
    
    print("TrainerDay Folder Rename Fix Tool")
    print("Updating trainer-day → product-development")
    print("=" * 80)
    
    if apply_fixes:
        print("APPLYING FIXES (--apply flag detected)")
        print("-" * 80)
        permalink_updates, reference_fixes, files_modified = fix_file_permalinks(project_root, dry_run=False)
        
        # Save summary
        summary = {
            'files_modified': files_modified,
            'permalink_updates': permalink_updates,
            'reference_fixes': reference_fixes,
            'total_changes': len(permalink_updates) + len(reference_fixes)
        }
        
        with open('trainer_day_to_product_development_fixes.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print("\n✅ All permalinks and references have been updated!")
        print(f"📄 Fix summary saved to: trainer_day_to_product_development_fixes.json")
        return
    
    # First do a dry run
    permalink_updates, reference_fixes, files_modified = fix_file_permalinks(project_root, dry_run=True)
    
    print("\n" + "=" * 80)
    print("SUMMARY (Dry Run):")
    print(f"Files to modify: {len(files_modified)}")
    print(f"Permalinks to update: {len(permalink_updates)}")
    print(f"References to fix: {len(reference_fixes)}")
    
    if files_modified:
        print("\n" + "=" * 80)
        try:
            response = input("Do you want to apply these fixes? (yes/no): ")
        except EOFError:
            print("Running in non-interactive mode. Use --apply flag to apply fixes.")
            return
        
        if response.lower() == 'yes':
            print("\nApplying fixes...")
            print("-" * 80)
            permalink_updates, reference_fixes, files_modified = fix_file_permalinks(project_root, dry_run=False)
            
            # Save summary
            summary = {
                'files_modified': files_modified,
                'permalink_updates': permalink_updates,
                'reference_fixes': reference_fixes,
                'total_changes': len(permalink_updates) + len(reference_fixes)
            }
            
            with open('trainer_day_to_product_development_fixes.json', 'w') as f:
                json.dump(summary, f, indent=2)
            
            print("\n✅ All permalinks and references have been updated!")
            print(f"📄 Fix summary saved to: trainer_day_to_product_development_fixes.json")
        else:
            print("\n❌ No changes made.")
    else:
        print("\n✅ No trainer-day references found!")

if __name__ == "__main__":
    main()