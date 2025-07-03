#!/usr/bin/env python3
"""
Fix permalink format in TD-Business project
Convert from simple "permalink: path" to proper YAML frontmatter format
"""

import os
import re
from pathlib import Path
import json

def extract_title_from_filename(file_path):
    """Extract a proper title from the filename"""
    # Get the filename without extension
    filename = file_path.stem
    
    # Handle special cases
    if filename.upper() == 'README':
        return 'readme'
    elif filename.upper() == 'TOP PRIORITIES':
        return 'Top Priorities'
    
    # For most files, use the filename as title
    # but with proper capitalization for certain words
    title = filename
    
    # Don't change case for files that already have mixed case
    if not (title.islower() or title.isupper()):
        return title
    
    # For all lowercase or all uppercase, apply title case
    # but keep certain words lowercase
    words_to_lower = {'and', 'or', 'the', 'of', 'in', 'on', 'at', 'to', 'for', 'with', 'a', 'an'}
    words = title.split('-')
    
    titled_words = []
    for i, word in enumerate(words):
        if i == 0 or word.lower() not in words_to_lower:
            titled_words.append(word.capitalize())
        else:
            titled_words.append(word.lower())
    
    return ' '.join(titled_words)

def has_yaml_frontmatter(content):
    """Check if content already has YAML frontmatter"""
    return content.strip().startswith('---')

def extract_existing_frontmatter(content):
    """Extract existing frontmatter if present"""
    if not has_yaml_frontmatter(content):
        return {}, content
    
    # Find the end of frontmatter
    lines = content.split('\n')
    end_index = -1
    
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end_index = i
            break
    
    if end_index == -1:
        return {}, content
    
    # Parse frontmatter
    frontmatter_text = '\n'.join(lines[1:end_index])
    frontmatter = {}
    
    # Simple YAML parsing for our needs
    for line in frontmatter_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()
    
    # Return frontmatter and content without frontmatter
    remaining_content = '\n'.join(lines[end_index + 1:])
    return frontmatter, remaining_content

def create_frontmatter(title, permalink, existing_fm=None):
    """Create proper YAML frontmatter"""
    # Start with existing frontmatter if available
    fm = existing_fm or {}
    
    # Set required fields
    fm['title'] = title
    fm['type'] = fm.get('type', 'note')  # Default to 'note' if not specified
    fm['permalink'] = permalink
    
    # Build YAML string
    yaml_lines = ['---']
    
    # Maintain order: title, type, permalink, then others
    for key in ['title', 'type', 'permalink']:
        if key in fm:
            yaml_lines.append(f'{key}: {fm[key]}')
    
    # Add any other existing fields
    for key, value in fm.items():
        if key not in ['title', 'type', 'permalink']:
            yaml_lines.append(f'{key}: {value}')
    
    yaml_lines.append('---')
    
    return '\n'.join(yaml_lines)

def fix_permalink_format(file_path, root_path, dry_run=True):
    """Fix permalink format in a single file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    content = original_content
    
    # Get expected permalink
    relative_path = file_path.relative_to(root_path)
    expected_permalink = str(relative_path.with_suffix(''))
    expected_permalink = expected_permalink.replace('\\', '/')
    
    # Extract title
    title = extract_title_from_filename(file_path)
    
    # Check for existing frontmatter
    existing_fm, remaining_content = extract_existing_frontmatter(content)
    
    # Check for simple permalink format (permalink: path)
    simple_permalink_pattern = re.compile(r'^permalink:\s*(.+)$', re.MULTILINE | re.IGNORECASE)
    simple_match = simple_permalink_pattern.search(content)
    
    needs_fix = False
    
    if existing_fm and 'permalink' in existing_fm:
        # Has frontmatter with permalink - check if format is complete
        if 'title' not in existing_fm or 'type' not in existing_fm:
            needs_fix = True
        # Also check if permalink is correct
        if existing_fm['permalink'] != expected_permalink:
            needs_fix = True
    elif simple_match:
        # Has simple permalink - needs conversion to frontmatter
        needs_fix = True
        # Remove the simple permalink line
        content = simple_permalink_pattern.sub('', content).strip()
        remaining_content = content
    elif not existing_fm:
        # No frontmatter at all - needs to be added
        needs_fix = True
        remaining_content = content
    
    if needs_fix:
        # Create proper frontmatter
        if existing_fm:
            # Update existing frontmatter
            existing_fm['title'] = existing_fm.get('title', title)
            existing_fm['permalink'] = expected_permalink
            new_frontmatter = create_frontmatter(
                existing_fm['title'],
                expected_permalink,
                existing_fm
            )
        else:
            # Create new frontmatter
            new_frontmatter = create_frontmatter(title, expected_permalink)
        
        # Combine frontmatter with content
        if remaining_content.strip():
            new_content = new_frontmatter + '\n\n' + remaining_content.strip() + '\n'
        else:
            new_content = new_frontmatter + '\n'
        
        if not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
        
        return True, {
            'file': str(file_path.relative_to(root_path)),
            'title': title,
            'permalink': expected_permalink,
            'had_frontmatter': bool(existing_fm),
            'had_simple_permalink': bool(simple_match)
        }
    
    return False, None

def fix_all_permalink_formats(root_dir, dry_run=True):
    """Fix permalink formats in all files"""
    root_path = Path(root_dir)
    if not root_path.exists():
        print(f"Error: Directory {root_dir} does not exist!")
        return
    
    fixed_files = []
    
    print(f"{'DRY RUN: ' if dry_run else ''}Fixing permalink formats...")
    print("-" * 80)
    
    for md_file in root_path.rglob('*.md'):
        try:
            fixed, info = fix_permalink_format(md_file, root_path, dry_run)
            
            if fixed:
                fixed_files.append(info)
                
                status = 'Would fix' if dry_run else 'Fixed'
                print(f"\n{status}: {info['file']}")
                print(f"  Title: {info['title']}")
                print(f"  Permalink: {info['permalink']}")
                
                if info['had_simple_permalink']:
                    print("  Converting from simple permalink format")
                elif info['had_frontmatter']:
                    print("  Updating incomplete frontmatter")
                else:
                    print("  Adding new frontmatter")
        
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
    
    return fixed_files

def main():
    project_root = "/Users/alex/Documents/bm-projects/TD-Business"
    
    print("TD-Business Permalink Format Fix Tool")
    print("=" * 80)
    
    # First do a dry run
    fixed = fix_all_permalink_formats(project_root, dry_run=True)
    
    print("\n" + "=" * 80)
    print("SUMMARY (Dry Run):")
    print(f"Files to fix: {len(fixed)}")
    
    if fixed:
        print("\nBreakdown:")
        simple = sum(1 for f in fixed if f['had_simple_permalink'])
        incomplete = sum(1 for f in fixed if f['had_frontmatter'] and not f['had_simple_permalink'])
        new = sum(1 for f in fixed if not f['had_frontmatter'] and not f['had_simple_permalink'])
        
        print(f"  Simple permalink conversions: {simple}")
        print(f"  Incomplete frontmatter updates: {incomplete}")
        print(f"  New frontmatter additions: {new}")
        
        print("\n" + "=" * 80)
        response = input("Do you want to apply these fixes? (yes/no): ")
        
        if response.lower() == 'yes':
            print("\nApplying fixes...")
            print("-" * 80)
            fixed = fix_all_permalink_formats(project_root, dry_run=False)
            
            # Save summary
            summary = {
                'fixed_files': fixed,
                'total_fixes': len(fixed),
                'breakdown': {
                    'simple_conversions': simple,
                    'incomplete_updates': incomplete,
                    'new_additions': new
                }
            }
            
            with open('td_business_permalink_format_fixes.json', 'w') as f:
                json.dump(summary, f, indent=2)
            
            print("\n✅ All permalink formats have been fixed!")
            print(f"📄 Fix summary saved to: td_business_permalink_format_fixes.json")
        else:
            print("\n❌ No changes made.")
    else:
        print("\n✅ All files already have correct permalink format!")

if __name__ == "__main__":
    main()