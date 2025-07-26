#!/usr/bin/env python3
"""
Merge the generated sections into a comprehensive article
"""

import os
import sys
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

# Import utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.google_sheets_client import get_bad_facts_for_article_generation

load_dotenv()

def merge_sections():
    """Load sections and merge them"""
    
    # Load all section files
    section_files = sorted(Path("script-testing").glob("section_*.md"))
    sections = []
    
    print("📄 Loading sections...")
    for section_file in section_files:
        with open(section_file, 'r') as f:
            content = f.read()
            # Extract section name from first line
            lines = content.split('\n')
            section_name = lines[0].replace('# ', '')
            section_content = '\n'.join(lines[2:])  # Skip title and blank line
            
            sections.append({
                'name': section_name,
                'content': section_content
            })
            
            word_count = len(section_content.split())
            print(f"  ✅ {section_name}: {word_count} words")
    
    total_words = sum(len(s['content'].split()) for s in sections)
    print(f"\n📊 Total words before merge: {total_words:,}")
    
    # Get bad facts
    print("\n🚫 Loading bad facts from Google Sheets...")
    bad_facts = get_bad_facts_for_article_generation()
    
    # Format sections for merge
    sections_text = "\n\n=== SECTION BREAK ===\n\n".join([
        f"## {s['name']}\n\n{s['content']}"
        for s in sections
    ])
    
    merge_prompt = f"""You are Alex, creating the final comprehensive guide for TrainerDay workout creation and management.

You have been given {len(sections)} independently written sections totaling {total_words:,} words. Your task is to:

1. REMOVE all duplicate information between sections
2. MAINTAIN all unique information from each section  
3. CREATE smooth transitions between sections
4. ENSURE the final article is 5,000-8,000 words
5. PRESERVE your conversational writing style

IMPORTANT INSTRUCTIONS:
- If the same fact appears in multiple sections, keep it in the MOST RELEVANT section only
- Ensure features like W' and W'bal are comprehensively covered
- Create a logical flow from basic to advanced features
- Add brief transitions between sections for readability
- Start with a compelling introduction that sets up the entire guide
- End with a conclusion that ties everything together

DO NOT INCLUDE THESE FACTS:
{bad_facts}

Here are the sections to merge:

{sections_text}

IMPORTANT: Do not ask questions or seek permission. Write the complete, deduplicated, comprehensive article NOW. Start immediately with the article title and introduction."""
    
    print("\n🔀 Merging sections with Claude...")
    
    # Use Claude for merging
    client = Anthropic()
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=8192,
        messages=[{
            "role": "user",
            "content": merge_prompt
        }],
        temperature=0.7
    )
    
    final_article = response.content[0].text
    
    # Save the result
    output_file = Path("output/articles-ai/comprehensive_article.md")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(final_article)
    
    final_words = len(final_article.split())
    print(f"\n✅ Saved to: {output_file}")
    print(f"📊 Final word count: {final_words:,}")
    
    # Save a backup with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = Path(f"script-testing/comprehensive_article_{timestamp}.md")
    with open(backup_file, 'w') as f:
        f.write(final_article)
    print(f"📁 Backup saved to: {backup_file}")

if __name__ == "__main__":
    merge_sections()