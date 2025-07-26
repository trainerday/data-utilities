#!/usr/bin/env python3
"""
Final merge of instructional sections using comprehensive template
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

def run_final_merge():
    """Merge all instructional sections using comprehensive template"""
    
    print("\n🔀 Running final merge with comprehensive template...")
    
    # Load bad facts
    print("🚫 Loading bad facts from Google Sheets...")
    bad_facts = get_bad_facts_for_article_generation()
    
    # Load the combined instructional content
    combined_file = Path("output/articles-ai/instructional_combined.md")
    with open(combined_file, 'r') as f:
        combined_content = f.read()
    
    # Load comprehensive template
    template_file = Path("templates/comprehensive-article-template.txt")
    with open(template_file, 'r') as f:
        template = f.read()
    
    # Fill template
    prompt = template.format(
        title="TrainerDay Workout Creation and Management Features - Complete Guide",
        content_sections=combined_content,
        bad_facts_section=bad_facts
    )
    
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
        temperature=0.7
    )
    
    final_article = response.content[0].text
    
    # Save final article
    output_file = Path("output/articles-ai/instructional_final.md")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(final_article)
    
    word_count = len(final_article.split())
    print(f"\n✅ Final article saved to: {output_file}")
    print(f"📊 Final word count: {word_count:,} words")
    
    # Also save a copy with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = Path(f"output/articles-ai/instructional_final_{timestamp}.md")
    
    with open(backup_file, 'w') as f:
        f.write(final_article)
    
    print(f"📋 Backup saved to: {backup_file}")
    print("\n✨ Final merge complete!")

if __name__ == "__main__":
    run_final_merge()