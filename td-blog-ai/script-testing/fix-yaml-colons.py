#!/usr/bin/env python3
"""
Fix YAML titles that contain colons by wrapping them in quotes
"""

import re
from pathlib import Path

def fix_yaml_colons_in_file(file_path: Path) -> bool:
    """Fix YAML titles with colons in a single file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if file has YAML front matter
    if not content.startswith('---'):
        return False
    
    # Split YAML and content
    parts = content.split('---', 2)
    if len(parts) < 3:
        return False
    
    yaml_content = parts[1]
    rest_content = '---' + parts[2]
    
    # Check if title line contains a colon that's not already quoted
    lines = yaml_content.split('\n')
    modified = False
    
    for i, line in enumerate(lines):
        if line.startswith('title: ') and ':' in line[7:]:
            # Check if already quoted
            title_value = line[7:].strip()
            if not (title_value.startswith('"') and title_value.endswith('"')):
                # Quote the title
                lines[i] = f'title: "{title_value}"'
                modified = True
                break
    
    if modified:
        # Reconstruct the file
        fixed_yaml = '\n'.join(lines)
        fixed_content = '---' + fixed_yaml + rest_content
        
        # Write back
        with open(file_path, 'w') as f:
            f.write(fixed_content)
        
        return True
    
    return False

def main():
    output_dir = Path("output/articles-ai")
    
    if not output_dir.exists():
        print(f"Output directory not found: {output_dir}")
        return
    
    print("🔧 Fixing YAML titles with colons...")
    print("=" * 50)
    
    fixed_count = 0
    
    # Process all markdown files
    for md_file in sorted(output_dir.glob("*.md")):
        if fix_yaml_colons_in_file(md_file):
            print(f"  ✅ Fixed: {md_file.name}")
            fixed_count += 1
    
    print(f"\n✨ Fixed {fixed_count} files")

if __name__ == "__main__":
    main()