#!/usr/bin/env python3
"""Add YAML metadata to the first 5 articles that are missing it"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime
import openai
from dotenv import load_dotenv

load_dotenv()

def generate_yaml_metadata(section_name: str, content: str, category: str) -> str:
    """Generate YAML metadata for the article using GPT-4o"""
    
    # Load hierarchy rules
    hierarchy_file = Path("/Users/alex/Documents/bm-projects/TD-Business/blog/articles-ai/category-sub-categories/_hierarchy_rules_json.md")
    with open(hierarchy_file, 'r') as f:
        hierarchy_content = f.read()
    
    # Determine engagement based on category
    if category == 'Core':
        engagement = 'quick-post'
    else:
        engagement = None
    
    prompt = f"""Based on this article content about "{section_name}", generate appropriate YAML metadata.

Article content:
{content[:2000]}...

Available metadata options from our hierarchy:
{hierarchy_content}

Generate YAML metadata with:
1. title: A clear, descriptive title for the article
2. tags: Choose 3-5 relevant tags from the available tags list
3. engagement: {f'Must be: {engagement}' if engagement else 'Choose one of: quick-post, complete-post, or geek-post based on the article\'s depth'}
4. excerpt: A 1-2 sentence summary of the article

Return ONLY the YAML front matter in this exact format:
---
title: [title]
date: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')}
blog-group: Features
engagement: [engagement]
tags:
  - [tag1]
  - [tag2]
  - [tag3]
excerpt: >-
  [excerpt]
permalink: blog/articles/ai/{section_name.lower().replace(' ', '-').replace('(', '').replace(')', '').replace(',', '')}
author: AI
---"""
    
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": prompt
            }],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating YAML metadata: {e}")
        # Fallback YAML
        return f"""---
title: {section_name}
date: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')}
blog-group: Features
engagement: complete-post
tags:
  - web-app
  - mobile-app
  - workout-creator
excerpt: >-
  A comprehensive guide to {section_name} in TrainerDay.
permalink: blog/articles/ai/{section_name.lower().replace(' ', '-').replace('(', '').replace(')', '').replace(',', '')}
author: AI
---"""

def main():
    output_dir = Path("output/articles-ai")
    
    # Map of files to section names and categories (Core features)
    files_to_process = {
        "s01-Workout_Editor_Basics.md": ("Workout Editor Basics", "Core"),
        "s02-Control_Modes_ERG_Slope_Resistance_HR.md": ("Control Modes (ERG, Slope, Resistance, HR)", "Core"),
        "s03-Mixed-Mode_Workouts.md": ("Mixed-Mode Workouts", "Core"),
        "s04-Workout_Library_Organization.md": ("Workout Library Organization", "Core"),
        "s05-Import_Export_and_Sharing.md": ("Import, Export and Sharing", "Core")
    }
    
    print("📝 Adding YAML metadata to first 5 articles...")
    
    for filename, (section_name, category) in files_to_process.items():
        file_path = output_dir / filename
        
        if not file_path.exists():
            print(f"    ⚠️  {filename} not found, skipping...")
            continue
        
        # Read the article content
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check if it already has YAML (starts with ---)
        if content.strip().startswith('---'):
            print(f"    ✓ {filename} already has YAML metadata, skipping...")
            continue
        
        # Generate YAML metadata
        yaml_metadata = generate_yaml_metadata(section_name, content, category)
        
        # Combine YAML and content
        updated_content = yaml_metadata + "\n" + content
        
        # Write back to file
        with open(file_path, 'w') as f:
            f.write(updated_content)
        
        print(f"    ✅ Added metadata to {filename}")
        time.sleep(1)  # Rate limiting
    
    print("\n✨ YAML metadata addition complete!")

if __name__ == "__main__":
    main()