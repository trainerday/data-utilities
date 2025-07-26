#!/usr/bin/env python3
"""
Generate overview article (s00-overview.md) that summarizes all sections
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
import openai

# Import utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.google_sheets_client import get_bad_facts_for_article_generation

load_dotenv()

def generate_overview():
    """Generate overview article summarizing all sections"""
    
    print("\n📝 Generating overview article...")
    
    # Load bad facts
    print("🚫 Loading bad facts from Google Sheets...")
    bad_facts = get_bad_facts_for_article_generation()
    
    # Load sections dynamically from workout-queries.md and existing files
    output_dir = Path(os.getenv('CONTENT_OUTPUT_PATH', 'output')) / "articles-ai"
    
    # Parse workout-queries.md to get expected sections and categories
    queries_file = Path("article-queries/workout-queries.md")
    section_categories = {}
    
    with open(queries_file, 'r') as f:
        lines = f.readlines()
    
    current_category = None
    for line in lines:
        line = line.strip()
        if line == '## Core Features':
            current_category = 'Core'
        elif line == '## Secondary Features':
            current_category = 'Secondary'
        elif line.startswith('### ') and current_category:
            section_name = line[4:]
            section_categories[section_name] = current_category
    
    # Get all generated section files
    sections = []
    section_files = sorted(output_dir.glob("s[0-9][0-9]-*.md"))
    
    for section_file in section_files:
        if section_file.name == "s00-overview.md":
            continue
        
        # Extract title from filename
        # s01-Workout_Editor_Basics.md -> Workout Editor Basics
        clean_name = section_file.stem[4:]  # Remove s01-
        title = clean_name.replace('_', ' ')
        
        # Get category from our parsed data
        category = section_categories.get(title, 'Core')
        
        sections.append((section_file.name, title, category))
    
    # Load all section files to get first paragraphs
    core_sections = []
    secondary_sections = []
    
    # Handle both old format (filename, title) and new format (filename, title, category)
    for section_info in sections:
        if len(section_info) == 3:
            filename, title, category = section_info
        else:
            filename, title = section_info
            category = 'Core'  # Default for backward compatibility
        section_file = output_dir / filename
        if section_file.exists():
            with open(section_file, 'r') as f:
                content = f.read()
                # Get first paragraph after the title
                lines = content.split('\n')
                first_para = ""
                for i, line in enumerate(lines[2:], 2):  # Skip title and blank line
                    if line.strip():
                        first_para = line.strip()
                        break
                
                section_entry = f"**[{title}]({filename})**\nFirst paragraph: {first_para[:200]}..."
                
                if category == 'Core':
                    core_sections.append((title, filename, first_para))
                else:
                    secondary_sections.append((title, filename, first_para))
    
    # Format sections for template with Core/Secondary distinction and engagement types
    sections_text = "CORE FEATURES (quick-post):\n\n"
    for title, filename, first_para in core_sections:
        sections_text += f"**{title}** ({filename}) [quick-post]:\nFirst paragraph: {first_para[:200]}...\n\n"
    
    if secondary_sections:
        sections_text += "\nSECONDARY FEATURES:\n\n"
        for i, (title, filename, first_para) in enumerate(secondary_sections):
            # Alternate between complete-post and geek-post for secondary features
            engagement = "complete-post" if i % 2 == 0 else "geek-post"
            sections_text += f"**{title}** ({filename}) [{engagement}]:\nFirst paragraph: {first_para[:200]}...\n\n"
    
    # Load overview template
    template_file = Path("templates/overview-template.txt")
    with open(template_file, 'r') as f:
        template = f.read()
    
    # Fill template with note about Core vs Secondary features
    template_vars = {
        'sections_content': sections_text,
        'bad_facts_section': bad_facts
    }
    
    # Add feature_distinction if template supports it
    if '{feature_distinction}' in template:
        template_vars['feature_distinction'] = "Note: Features are organized into Core Features (most important functionality) and Secondary Features (additional capabilities)."
    
    prompt = template.format(**template_vars)
    
    print(f"📏 Sending {len(prompt):,} characters to GPT-4 mini...")
    
    # Use OpenAI GPT-4o
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": prompt
        }],
        temperature=0.5
    )
    
    overview = response.choices[0].message.content
    
    # Generate YAML metadata
    from datetime import datetime
    
    yaml_prompt = f"""Generate YAML metadata for this overview article about TrainerDay's workout features.

Article content:
{overview[:1000]}...

Generate YAML metadata with:
1. title: "TrainerDay Workout Creation and Management Features - Overview"
2. tags: Choose 3-5 relevant overview tags
3. engagement: quick-post (this is an overview)
4. excerpt: A 1-2 sentence summary

Return ONLY the YAML front matter in this exact format:
---
title: TrainerDay Workout Creation and Management Features - Overview
date: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')}
blog-group: Features
engagement: quick-post
tags:
  - [tag1]
  - [tag2]
  - [tag3]
excerpt: >-
  [excerpt]
permalink: blog/articles/ai/trainerday-workout-creation-management-overview
author: AI
---"""

    yaml_response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": yaml_prompt
        }],
        temperature=0.3
    )
    
    yaml_metadata = yaml_response.choices[0].message.content
    
    # Save overview with YAML
    overview_file = output_dir / "s00-overview.md"
    with open(overview_file, 'w') as f:
        f.write(yaml_metadata + "\n")
        # Remove duplicate title if it exists at the start
        if overview.startswith("# TrainerDay Workout Creation and Management Features - Overview"):
            f.write(overview)
        else:
            f.write(f"# TrainerDay Workout Creation and Management Features - Overview\n\n{overview}")
    
    word_count = len(overview.split())
    print(f"\n✅ Overview saved to: {overview_file}")
    print(f"📊 Word count: {word_count} words")
    
    print("\n✨ Overview generation complete!")

if __name__ == "__main__":
    generate_overview()