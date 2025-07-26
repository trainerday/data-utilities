#!/usr/bin/env python3
"""
Fix YAML code blocks in existing articles
Removes markdown code block wrappers around YAML front matter
"""

import sys
from pathlib import Path

def fix_yaml_in_file(file_path: Path) -> bool:
    """Fix YAML code blocks in a single file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if file starts with ```yaml
    if content.startswith('```yaml\n---'):
        # Find the ending ```
        lines = content.split('\n')
        yaml_end_idx = None
        
        for i, line in enumerate(lines):
            if i > 0 and line.strip() == '```':
                yaml_end_idx = i
                break
        
        if yaml_end_idx:
            # Reconstruct without the code block markers
            yaml_lines = lines[1:yaml_end_idx]  # Skip ```yaml, keep until ```
            rest_lines = lines[yaml_end_idx+1:]  # Skip the closing ```
            
            fixed_content = '\n'.join(yaml_lines) + '\n' + '\n'.join(rest_lines)
            
            # Write back
            with open(file_path, 'w') as f:
                f.write(fixed_content)
            
            return True
    
    return False

def main():
    output_dir = Path("output/articles-ai")
    
    if not output_dir.exists():
        print(f"Output directory not found: {output_dir}")
        sys.exit(1)
    
    print("🔧 Fixing YAML code blocks in articles...")
    print("=" * 50)
    
    fixed_count = 0
    
    # Process all markdown files
    for md_file in sorted(output_dir.glob("*.md")):
        if fix_yaml_in_file(md_file):
            print(f"  ✅ Fixed: {md_file.name}")
            fixed_count += 1
        else:
            print(f"  ⏭️  Skipped: {md_file.name} (no code blocks found)")
    
    print(f"\n✨ Fixed {fixed_count} files")

if __name__ == "__main__":
    main()