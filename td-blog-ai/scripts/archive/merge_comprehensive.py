#!/usr/bin/env python3
"""
Comprehensive merge with better content formatting
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic

# Import utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.google_sheets_client import get_bad_facts_for_article_generation

load_dotenv()

def format_sections_for_merge():
    """Format the sections more cleanly for merging"""
    
    sections = []
    
    # Read all instructional section files in order
    section_files = sorted(Path("script-testing").glob("instructional_*.md"))
    
    for section_file in section_files:
        with open(section_file, 'r') as f:
            content = f.read()
            # Extract just the content without duplicate headers
            lines = content.split('\n')
            if lines[0].startswith('# '):
                title = lines[0].replace('# ', '')
                # Skip the title and any duplicate header
                content_lines = []
                skip_next_header = True
                for line in lines[2:]:  # Skip title and blank line
                    if skip_next_header and line.startswith('#'):
                        skip_next_header = False
                        continue
                    content_lines.append(line)
                
                sections.append({
                    'title': title,
                    'content': '\n'.join(content_lines).strip()
                })
    
    return sections

def run_comprehensive_merge():
    """Merge all sections with comprehensive formatting"""
    
    print("\n🔀 Running comprehensive merge...")
    
    # Load bad facts
    print("🚫 Loading bad facts from Google Sheets...")
    bad_facts = get_bad_facts_for_article_generation()
    
    # Format sections
    sections = format_sections_for_merge()
    
    # Create formatted content
    content_parts = []
    for section in sections:
        content_parts.append(f"SECTION: {section['title']}")
        content_parts.append(section['content'])
        content_parts.append("")  # Blank line between sections
    
    formatted_content = '\n'.join(content_parts)
    
    # Create a simpler prompt that focuses on merging
    prompt = f"""You are Alex, creating a comprehensive guide about TrainerDay's workout creation and management features.

TASK: Merge the following instructional sections into a single, well-organized article. Remove any duplication while keeping all unique information. Add smooth transitions between sections and ensure logical flow.

TARGET: Create a 5,000-10,000 word comprehensive guide that includes ALL the information from these sections.

SECTIONS TO MERGE:
{formatted_content}

BAD FACTS TO AVOID:
{bad_facts}

INSTRUCTIONS:
1. Start with a brief introduction explaining what TrainerDay is and what this guide covers
2. Organize the content logically, merging related information
3. Remove duplicate content between sections
4. Add transitions to connect sections smoothly
5. Include ALL specific instructions and features mentioned
6. End with a brief conclusion
7. Write in a conversational but informative tone
8. DO NOT ask for permission or indicate you'll continue later
9. Generate the COMPLETE article now

Write the full comprehensive article now:"""
    
    print(f"📏 Sending {len(prompt):,} characters to Claude...")
    
    # Use Claude for final merge
    client = Anthropic()
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=8192,
        messages=[{
            "role": "user",
            "content": prompt
        }],
        temperature=0.5  # Lower temperature for more focused output
    )
    
    final_article = response.content[0].text
    
    # Save final article
    output_file = Path("output/articles-ai/comprehensive_final.md")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(final_article)
    
    word_count = len(final_article.split())
    print(f"\n✅ Final article saved to: {output_file}")
    print(f"📊 Final word count: {word_count:,} words")
    
    print("\n✨ Comprehensive merge complete!")

if __name__ == "__main__":
    run_comprehensive_merge()