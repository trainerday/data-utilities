#!/usr/bin/env python3
"""
Simply combine all sections into one article
"""

from pathlib import Path

def combine_sections():
    """Combine all sections into one article"""
    
    # Load all section files
    section_files = sorted(Path("script-testing").glob("section_*.md"))
    
    combined = []
    combined.append("# TrainerDay Workout Creation and Management - Complete Guide\n")
    
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
    
    # Save combined version
    output_file = Path("output/articles-ai/combined_article_raw.md")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write('\n'.join(combined))
    
    word_count = len(' '.join(combined).split())
    print(f"✅ Combined article saved to: {output_file}")
    print(f"📊 Total words: {word_count:,}")

if __name__ == "__main__":
    combine_sections()