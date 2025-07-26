#!/usr/bin/env python3
"""
Generate instructional article sections based on query results.
Each section is saved as a separate file (s1.md, s2.md, etc.)
Sections are determined from the workout-queries.md file.
"""

import os
import sys
import json
import time
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple

from dotenv import load_dotenv
import openai
from anthropic import Anthropic

# Import utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.google_sheets_client import get_bad_facts_for_article_generation

load_dotenv()

class SectionalArticleGenerator:
    def __init__(self):
        """Initialize with API clients and paths"""
        
        # Setup AI clients
        self.openai_client = openai.OpenAI()
        self.anthropic_client = Anthropic()
        
        # Paths
        self.output_path = Path(os.getenv('CONTENT_OUTPUT_PATH', 'output'))
        self.templates_path = Path("templates")
        
    def parse_workout_queries(self) -> List[Tuple[str, List[str], str]]:
        """Parse workout-queries.md to extract sections and their keywords with category"""
        
        queries_file = Path("article-queries/workout-queries.md")
        if not queries_file.exists():
            raise FileNotFoundError(f"workout-queries.md not found at {queries_file}")
        
        sections = []
        current_section = None
        current_keywords = []
        current_category = None
        
        with open(queries_file, 'r') as f:
            lines = f.readlines()
        
        in_core_features = False
        in_secondary_features = False
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and main headers
            if not line or line.startswith('# ') or line.startswith('This document'):
                continue
            
            # Check for feature category headers
            if line == '## Core Features':
                in_core_features = True
                in_secondary_features = False
                current_category = 'Core'
                continue
            elif line == '## Secondary Features' or line == '## Additional Features':
                in_core_features = False
                in_secondary_features = True
                current_category = 'Secondary'
                continue
            elif line.startswith('## '):
                # Other sections we don't need for articles
                in_core_features = False
                in_secondary_features = False
                continue
            
            # Only process sections in Core or Secondary Features
            if not (in_core_features or in_secondary_features):
                continue
            
            # Check for section headers (### or ##)
            if line.startswith('### '):
                # Save previous section if exists
                if current_section and current_keywords and current_category:
                    sections.append((current_section, current_keywords, current_category))
                
                # Start new section
                current_section = line[4:].strip()
                current_keywords = []
            
            # Extract keywords from query lines (lines starting with -)
            elif line.startswith('- "') and line.endswith('"'):
                keyword = line[3:-1]  # Remove - " and closing "
                # Keep the full query as-is for better matching
                current_keywords.append(keyword)
        
        # Add the last section
        if current_section and current_keywords and current_category:
            sections.append((current_section, current_keywords, current_category))
        
        # Return all sections from Core and Secondary features
        return sections
        
    def load_query_results(self) -> Dict:
        """Load query results from article_features.json"""
        
        results_file = Path("article-temp-files/article_features.json")
        
        if not results_file.exists():
            raise FileNotFoundError(
                f"Query results not found at {results_file}. "
                "Please run: python scripts/query_all_article_features.py workout-queries"
            )
        
        with open(results_file, 'r') as f:
            return json.load(f)
    
    def extract_content_from_results(self, query_results: Dict) -> Dict[str, Any]:
        """Extract and organize content from query results"""
        
        content = {
            'facts': [],
            'blog_quotes': [],
            'forum_questions': [],
            'video_references': [],
            'all_text': []  # For keyword searching
        }
        
        # Process each category and feature
        for category, features in query_results.items():
            for feature_name, results in features.items():
                for result in results:
                    source = result.get('source', '')
                    text = result.get('text', '')
                    
                    # Store all text for keyword searching
                    content['all_text'].append({
                        'text': text,
                        'source': source,
                        'feature': feature_name,
                        'category': category,
                        'title': result.get('title', ''),
                        'distance': result.get('distance', 1.0)
                    })
                    
                    if source == 'facts':
                        content['facts'].append({
                            'text': text,
                            'feature': feature_name,
                            'category': category
                        })
                    elif source == 'blog':
                        content['blog_quotes'].append({
                            'quote': text,
                            'title': result.get('title', 'Blog Article'),
                            'feature': feature_name,
                            'category': category
                        })
                    elif source == 'forum':
                        content['forum_questions'].append({
                            'text': text,
                            'feature': feature_name,
                            'category': category
                        })
                    elif source == 'youtube':
                        content['video_references'].append({
                            'title': result.get('title', 'Video'),
                            'text': text,
                            'feature': feature_name,
                            'category': category
                        })
        
        return content
    
    def extract_section_content(self, keywords: List[str], all_content: Dict) -> Dict:
        """Extract content relevant to specific section keywords"""
        
        section_content = {
            'facts': [],
            'blog_quotes': [],
            'forum_questions': [],
            'video_references': []
        }
        
        # Search through all text for keyword matches
        for item in all_content['all_text']:
            text_lower = item['text'].lower()
            
            # Check if any keyword phrase matches
            matched = False
            for keyword in keywords:
                # Check both the full phrase and individual words
                if keyword.lower() in text_lower:
                    matched = True
                    break
                # Also check individual words for better coverage
                keyword_words = keyword.lower().split()
                if all(word in text_lower for word in keyword_words):
                    matched = True
                    break
            
            if matched:
                source = item['source']
                
                if source == 'facts':
                    section_content['facts'].append({
                        'text': item['text'],
                        'feature': item['feature']
                    })
                elif source == 'blog':
                    section_content['blog_quotes'].append({
                        'quote': item['text'],
                        'title': item['title'],
                        'feature': item['feature']
                    })
                elif source == 'forum':
                    section_content['forum_questions'].append({
                        'text': item['text'],
                        'feature': item['feature']
                    })
                elif source == 'youtube':
                    section_content['video_references'].append({
                        'title': item['title'],
                        'text': item['text'],
                        'feature': item['feature']
                    })
        
        return section_content
    
    def load_section_template(self) -> str:
        """Load the instructional section template"""
        
        template_file = self.templates_path / "section-generation-template.txt"
        with open(template_file, 'r') as f:
            return f.read()
    
    def format_section_content(self, content: Dict) -> str:
        """Format content for section generation with size limits"""
        
        sections = []
        
        if content['facts']:
            # Limit to most relevant facts
            facts_text = "\n".join([f"- {fact['text']}" for fact in content['facts'][:50]])
            sections.append(f"FACTS ({len(content['facts'])} total, showing top 50):\n{facts_text}")
        
        if content['blog_quotes']:
            # Limit blog quotes and truncate
            blog_entries = []
            for q in content['blog_quotes'][:20]:
                quote = q['quote']
                if len(quote) > 1000:
                    quote = quote[:1000] + "..."
                blog_entries.append(f"From '{q['title']}':\n{quote}")
            
            blog_text = "\n\n".join(blog_entries)
            sections.append(f"BLOG CONTENT ({len(content['blog_quotes'])} total, showing top 20):\n{blog_text}")
        
        if content['forum_questions']:
            # Limit forum content
            forum_entries = []
            for q in content['forum_questions'][:25]:
                text = q['text']
                if len(text) > 800:
                    text = text[:800] + "..."
                forum_entries.append(f"Forum discussion:\n{text}")
            
            forum_text = "\n\n".join(forum_entries)
            sections.append(f"FORUM DISCUSSIONS ({len(content['forum_questions'])} total, showing top 25):\n{forum_text}")
        
        if content['video_references']:
            # Limit video content
            video_entries = []
            for v in content['video_references'][:5]:
                text = v['text']
                if len(text) > 300:
                    text = text[:300] + "..."
                video_entries.append(f"Video '{v['title']}':\n{text}")
            
            video_text = "\n\n".join(video_entries)
            sections.append(f"VIDEO CONTENT ({len(content['video_references'])} total, showing top 5):\n{video_text}")
        
        return "\n\n".join(sections)
    
    def generate_section(self, section_name: str, content: Dict, bad_facts: str) -> str:
        """Generate a single instructional section"""
        
        template = self.load_section_template()
        content_formatted = self.format_section_content(content)
        
        prompt = template.format(
            section_name=section_name,
            content_sections=content_formatted,
            bad_facts_section=bad_facts
        )
        
        # Try OpenAI first, fall back to Claude
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.3  # Lower temperature for more focused, instructional content
            )
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"OpenAI error: {e}, falling back to Claude")
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.3
            )
            return response.content[0].text
    
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
            # For secondary features, could alternate or use GPT to decide
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
    
    def add_yaml_to_articles(self, output_dir: Path, generated_sections: List[Tuple[str, str, str]]):
        """Add YAML metadata to all generated articles"""
        
        print("\n📝 Adding YAML metadata to articles...")
        
        for filename, section_name, category in generated_sections:
            file_path = output_dir / filename
            
            # Read the article content
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Generate YAML metadata
            yaml_metadata = self.generate_yaml_metadata(section_name, content, category)
            
            # Combine YAML and content
            updated_content = yaml_metadata + "\n" + content
            
            # Write back to file
            with open(file_path, 'w') as f:
                f.write(updated_content)
            
            print(f"    ✅ Added metadata to {filename}")
            time.sleep(1)  # Rate limiting
    
    def generate(self):
        """Main generation workflow for sectional articles"""
        
        print("\n🚀 Starting sectional article generation...")
        
        # Clean up existing articles first
        output_dir = self.output_path / "articles-ai"
        originals_dir = self.output_path / "_originals"
        
        print("🧹 Cleaning up existing articles...")
        
        # Delete existing articles
        if output_dir.exists():
            import shutil
            shutil.rmtree(output_dir)
            print("   ✅ Removed existing articles-ai directory")
        
        # Delete existing _originals
        if originals_dir.exists():
            import shutil
            shutil.rmtree(originals_dir)
            print("   ✅ Removed existing _originals directory")
        
        # Parse sections from workout-queries.md
        print("\n📄 Parsing workout-queries.md for sections...")
        article_sections = self.parse_workout_queries()
        print(f"📝 Found {len(article_sections)} priority sections to generate")
        
        # Load query results
        print("\n📄 Loading query results...")
        query_results = self.load_query_results()
        
        # Extract all content
        all_content = self.extract_content_from_results(query_results)
        print(f"📝 Extracted: {len(all_content['facts'])} facts, {len(all_content['blog_quotes'])} blog quotes, "
              f"{len(all_content['forum_questions'])} forum Q&As, {len(all_content['video_references'])} video references")
        
        # Get bad facts early
        print("\n🚫 Loading bad facts from Google Sheets...")
        bad_facts = get_bad_facts_for_article_generation()
        
        # Generate sections
        print("\n📑 Generating article sections...")
        
        # Create output directory (already defined above)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        total_words = 0
        generated_sections = []
        
        for i, (section_name, keywords, category) in enumerate(article_sections, 1):
            # Format section name for filename (remove special characters, replace spaces)
            clean_name = section_name.replace(' ', '_').replace('(', '').replace(')', '').replace(',', '').replace("'", '')
            section_file = output_dir / f"s{i:02d}-{clean_name}.md"
            
            print(f"  [{i}/{len(article_sections)}] Generating: {section_name}")
            
            # Extract content for this section
            section_content = self.extract_section_content(keywords, all_content)
            
            # Skip if no content found
            if not any(section_content.values()):
                print(f"    ⚠️  No content found for this section, skipping...")
                continue
            
            # Generate section
            section_text = self.generate_section(section_name, section_content, bad_facts)
            
            # Save section (section_text already includes title)
            with open(section_file, 'w') as f:
                f.write(section_text)
            
            word_count = len(section_text.split())
            total_words += word_count
            print(f"    ✅ Generated {word_count} words -> {section_file.name}")
            
            # Store section info for overview generation
            generated_sections.append((section_file.name, section_name, category))
            
            # Add delay to avoid rate limits
            time.sleep(2)
        
        print(f"\n📊 Total words generated: {total_words:,}")
        print(f"✅ All sections saved to: {output_dir}")
        
        # Add YAML metadata to all articles
        self.add_yaml_to_articles(output_dir, generated_sections)
        
        print("\n✨ Sectional article generation complete!")


def main():
    generator = SectionalArticleGenerator()
    generator.generate()


if __name__ == "__main__":
    main()