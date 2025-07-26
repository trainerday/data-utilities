#!/usr/bin/env python3
"""
Step 5: Generate overview article
This script generates the overview article that links to all section articles
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
import openai
from anthropic import Anthropic

# Import utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.google_sheets_client import get_bad_facts_for_article_generation

load_dotenv()


class OverviewGenerator:
    def __init__(self):
        """Initialize with API clients and paths"""
        self.openai_client = openai.OpenAI()
        self.anthropic_client = Anthropic()
        
        self.output_path = Path(os.getenv('CONTENT_OUTPUT_PATH', 'output'))
        self.templates_path = Path("templates")
    
    def load_section_info(self) -> list:
        """Load section information from step 2"""
        section_info_file = Path("article-temp-files/generated_sections.json")
        
        if not section_info_file.exists():
            raise FileNotFoundError(f"Section info not found at {section_info_file}")
        
        with open(section_info_file, 'r') as f:
            return json.load(f)
    
    def load_overview_template(self) -> str:
        """Load the overview template"""
        template_file = self.templates_path / "overview-template.txt"
        with open(template_file, 'r') as f:
            return f.read()
    
    def extract_section_summary(self, article_path: Path) -> str:
        """Extract the first paragraph after the title as summary"""
        with open(article_path, 'r') as f:
            content = f.read()
        
        # Skip YAML front matter if present
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2].strip()
        
        # Split into lines and find content
        lines = content.split('\n')
        
        # Find the title and first paragraph
        title_found = False
        for i, line in enumerate(lines):
            if line.startswith('# ') and not title_found:
                title_found = True
                continue
            
            if title_found and line.strip() and not line.startswith('#'):
                # This is the first paragraph
                return line.strip()
        
        return "Comprehensive guide to this TrainerDay feature."
    
    def format_sections_content(self, section_info: list) -> tuple:
        """Format sections for the overview template"""
        core_sections = []
        secondary_sections = []
        
        articles_dir = self.output_path / "articles-ai"
        
        for section in section_info:
            filename = section['filename']
            section_name = section['section_name']
            category = section['category']
            
            # Get summary from the actual article
            article_path = articles_dir / filename
            if article_path.exists():
                summary = self.extract_section_summary(article_path)
            else:
                summary = f"Guide to {section_name} in TrainerDay."
            
            section_content = f"### {section_name}\n{summary}\n[Read more →]({filename})"
            
            if category == 'Core':
                core_sections.append(section_content)
            else:
                secondary_sections.append(section_content)
        
        # Combine sections
        sections_content = ""
        if core_sections:
            sections_content = "## Core Features\n\n" + "\n\n".join(core_sections)
        
        if secondary_sections:
            if sections_content:
                sections_content += "\n\n"
            sections_content += "## Additional Features\n\n" + "\n\n".join(secondary_sections)
        
        # Feature distinction
        feature_distinction = """
Core Features are the most commonly used features that most users will need.
Additional Features are more specialized features for specific use cases.
"""
        
        return sections_content, feature_distinction
    
    def generate_overview(self, sections_content: str, feature_distinction: str, bad_facts: str) -> str:
        """Generate the overview article"""
        template = self.load_overview_template()
        
        prompt = template.format(
            sections_content=sections_content,
            feature_distinction=feature_distinction,
            bad_facts_section=bad_facts
        )
        
        # Use OpenAI for overview generation
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI error: {e}, falling back to Claude")
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.3
            )
            return response.content[0].text
    
    def generate_overview_yaml(self) -> str:
        """Generate YAML metadata for the overview"""
        return f"""---
title: TrainerDay Workout Creation and Management Features - Overview
date: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')}
blog-group: Features
engagement: quick-post
tags:
  - web-app
  - mobile-app
  - workout-creator
  - features
  - overview
excerpt: >-
  A comprehensive overview of TrainerDay's workout creation and management features, with links to detailed guides for each feature.
permalink: blog/articles/ai/trainerday-features-overview
author: AI
---"""
    
    def generate(self):
        """Main generation workflow for overview"""
        print("\n📋 Step 5: Generating Overview Article")
        print("=" * 50)
        
        # Load section info
        section_info = self.load_section_info()
        print(f"📝 Creating overview for {len(section_info)} sections")
        
        # Format sections content
        sections_content, feature_distinction = self.format_sections_content(section_info)
        
        # Get bad facts
        print("\n🚫 Loading bad facts from Google Sheets...")
        bad_facts = get_bad_facts_for_article_generation()
        
        # Generate overview
        print("\n📝 Generating overview content...")
        overview_content = self.generate_overview(sections_content, feature_distinction, bad_facts)
        
        # Add YAML metadata
        yaml_metadata = self.generate_overview_yaml()
        final_content = yaml_metadata + "\n" + overview_content
        
        # Save overview
        output_dir = self.output_path / "articles-ai"
        overview_file = output_dir / "s00-overview.md"
        
        with open(overview_file, 'w') as f:
            f.write(final_content)
        
        print(f"\n✅ Overview saved to: {overview_file}")
        print("✨ Overview generation complete!")


def main():
    generator = OverviewGenerator()
    generator.generate()


if __name__ == "__main__":
    main()