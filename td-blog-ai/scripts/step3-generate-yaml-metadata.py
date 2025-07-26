#!/usr/bin/env python3
"""
Step 3: Generate YAML metadata for each article
This script adds YAML front matter to all generated articles using LLM
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
import openai

load_dotenv()


class YAMLMetadataGenerator:
    def __init__(self):
        """Initialize with API client and paths"""
        self.openai_client = openai.OpenAI()
        self.output_path = Path(os.getenv('CONTENT_OUTPUT_PATH', 'output'))
        
    def load_section_info(self) -> list:
        """Load section information from previous step"""
        section_info_file = Path("article-temp-files/generated_sections.json")
        
        if not section_info_file.exists():
            raise FileNotFoundError(f"Section info not found at {section_info_file}")
        
        with open(section_info_file, 'r') as f:
            return json.load(f)
    
    def generate_yaml_metadata(self, section_name: str, content: str, category: str) -> str:
        """Generate YAML metadata for the article using GPT"""
        
        # Load hierarchy rules
        hierarchy_file = Path("/Users/alex/Documents/bm-projects/TD-Business/blog/articles-ai/category-sub-categories/_hierarchy_rules_json.md")
        with open(hierarchy_file, 'r') as f:
            hierarchy_content = f.read()
        
        # Determine engagement based on category
        if category == 'Core':
            engagement = 'quick-post'
        else:
            engagement = None  # Let GPT decide
        
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
            response = self.openai_client.chat.completions.create(
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
    
    def add_yaml_to_articles(self):
        """Add YAML metadata to all generated articles"""
        print("\n🏷️  Step 3: Adding YAML Metadata")
        print("=" * 50)
        
        # Load section info
        section_info = self.load_section_info()
        
        print(f"📝 Adding metadata to {len(section_info)} articles...")
        
        output_dir = self.output_path / "articles-ai"
        
        for section in section_info:
            filename = section['filename']
            section_name = section['section_name']
            category = section['category']
            
            file_path = output_dir / filename
            
            # Read the article content
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check if YAML already exists
            if content.startswith('---'):
                print(f"  ⏭️  {filename} already has metadata, skipping...")
                continue
            
            print(f"  Processing {filename}...")
            
            # Generate YAML metadata
            yaml_metadata = self.generate_yaml_metadata(section_name, content, category)
            
            # Combine YAML and content
            updated_content = yaml_metadata + "\n" + content
            
            # Write back to file
            with open(file_path, 'w') as f:
                f.write(updated_content)
            
            print(f"    ✅ Added metadata")
            time.sleep(1)  # Rate limiting
        
        print("\n✨ YAML metadata generation complete!")


def main():
    generator = YAMLMetadataGenerator()
    generator.add_yaml_to_articles()


if __name__ == "__main__":
    main()