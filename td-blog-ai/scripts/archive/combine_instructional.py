#!/usr/bin/env python3
"""
Combine instructional sections
"""

from pathlib import Path

def combine_instructional():
    """Combine all instructional sections"""
    
    # Load all instructional section files
    section_files = sorted(Path("script-testing").glob("instructional_*.md"))
    
    combined = []
    combined.append("# TrainerDay Workout Creation and Management - Instructional Guide\n")
    
    total_words = 0
    
    for section_file in section_files:
        with open(section_file, 'r') as f:
            content = f.read()
            # Remove the individual section title (first line)
            lines = content.split('\n')
            section_name = lines[0].replace('# ', '')
            section_content = '\n'.join(lines[2:])  # Skip title and blank line
            
            # Add as a level 2 heading
            combined.append(f"\n## {section_name}\n")
            combined.append(section_content)
            
            words = len(section_content.split())
            total_words += words
            print(f"✅ {section_name}: {words} words")
    
    # Save combined version
    output_file = Path("output/articles-ai/instructional_combined.md")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write('\n'.join(combined))
    
    print(f"\n📊 Total words: {total_words:,}")
    print(f"✅ Combined article saved to: {output_file}")

if __name__ == "__main__":
    combine_instructional()