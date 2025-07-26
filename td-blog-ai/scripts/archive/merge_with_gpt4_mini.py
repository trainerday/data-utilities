#!/usr/bin/env python3
"""
Comprehensive merge using GPT-4 mini
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import openai

# Import utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.google_sheets_client import get_bad_facts_for_article_generation

load_dotenv()

def run_gpt4_mini_merge():
    """Merge all sections using GPT-4 mini"""
    
    print("\n🔀 Running comprehensive merge with GPT-4 mini...")
    
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
    
    print(f"📏 Sending {len(prompt):,} characters to GPT-4 mini...")
    
    # Use OpenAI GPT-4 mini with higher token limit
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=16384,  # GPT-4o-mini supports up to 16k output tokens
        messages=[{
            "role": "user",
            "content": prompt
        }],
        temperature=0.7
    )
    
    final_article = response.choices[0].message.content
    
    # Save final article
    output_file = Path("output/articles-ai/gpt4_mini_final.md")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(final_article)
    
    word_count = len(final_article.split())
    print(f"\n✅ Final article saved to: {output_file}")
    print(f"📊 Final word count: {word_count:,} words")
    
    # Check if we hit the token limit
    if response.choices[0].finish_reason == "length":
        print("⚠️  Hit token limit - article may be truncated")
    
    print("\n✨ GPT-4 mini merge complete!")

if __name__ == "__main__":
    run_gpt4_mini_merge()