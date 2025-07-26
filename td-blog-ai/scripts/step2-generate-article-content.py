#!/usr/bin/env python3
"""
Step 2: Generate article content (without YAML metadata)
This script generates the main content for each article section using LLM
"""

import os
import sys
import json
import time
import shutil
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


class ArticleContentGenerator:
    def __init__(self):
        """Initialize with API clients and paths"""
        self.openai_client = openai.OpenAI()
        self.anthropic_client = Anthropic()
        
        self.output_path = Path(os.getenv('CONTENT_OUTPUT_PATH', 'output'))
        self.templates_path = Path("templates")
        
    def clean_existing_articles(self):
        """Clean up existing articles and _originals directories"""
        output_dir = self.output_path / "articles-ai"
        originals_dir = self.output_path / "_originals"
        
        print("🧹 Cleaning up existing articles...")
        
        # Delete existing articles
        if output_dir.exists():
            shutil.rmtree(output_dir)
            print("   ✅ Removed existing articles-ai directory")
        
        # Delete existing _originals
        if originals_dir.exists():
            shutil.rmtree(originals_dir)
            print("   ✅ Removed existing _originals directory")
    
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
            
            if not line or line.startswith('# ') or line.startswith('This document'):
                continue
            
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
                in_core_features = False
                in_secondary_features = False
                continue
            
            if not (in_core_features or in_secondary_features):
                continue
            
            if line.startswith('### '):
                if current_section and current_keywords and current_category:
                    sections.append((current_section, current_keywords, current_category))
                
                current_section = line[4:].strip()
                current_keywords = []
            
            elif line.startswith('- "') and line.endswith('"'):
                keyword = line[3:-1]
                current_keywords.append(keyword)
        
        if current_section and current_keywords and current_category:
            sections.append((current_section, current_keywords, current_category))
        
        return sections
    
    def load_query_results(self) -> Dict:
        """Load query results from article_features.json"""
        results_file = Path("article-temp-files/article_features.json")
        
        if not results_file.exists():
            raise FileNotFoundError(f"Query results not found at {results_file}")
        
        with open(results_file, 'r') as f:
            return json.load(f)
    
    def extract_content_from_results(self, query_results: Dict) -> Dict[str, Any]:
        """Extract and organize content from query results"""
        content = {
            'facts': [],
            'blog_quotes': [],
            'forum_questions': [],
            'video_references': [],
            'all_text': []
        }
        
        for category, features in query_results.items():
            for feature_name, results in features.items():
                for result in results:
                    source = result.get('source', '')
                    text = result.get('text', '')
                    
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
        
        for item in all_content['all_text']:
            text_lower = item['text'].lower()
            
            matched = False
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    matched = True
                    break
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
            facts_text = "\n".join([f"- {fact['text']}" for fact in content['facts'][:50]])
            sections.append(f"FACTS ({len(content['facts'])} total, showing top 50):\n{facts_text}")
        
        if content['blog_quotes']:
            blog_entries = []
            for q in content['blog_quotes'][:20]:
                quote = q['quote']
                if len(quote) > 1000:
                    quote = quote[:1000] + "..."
                blog_entries.append(f"From '{q['title']}':\n{quote}")
            
            blog_text = "\n\n".join(blog_entries)
            sections.append(f"BLOG CONTENT ({len(content['blog_quotes'])} total, showing top 20):\n{blog_text}")
        
        if content['forum_questions']:
            forum_entries = []
            for q in content['forum_questions'][:25]:
                text = q['text']
                if len(text) > 800:
                    text = text[:800] + "..."
                forum_entries.append(f"Forum discussion:\n{text}")
            
            forum_text = "\n\n".join(forum_entries)
            sections.append(f"FORUM DISCUSSIONS ({len(content['forum_questions'])} total, showing top 25):\n{forum_text}")
        
        if content['video_references']:
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
                temperature=0.3
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
    
    def generate(self):
        """Main generation workflow for article content"""
        print("\n📝 Step 2: Generating Article Content")
        print("=" * 50)
        
        # Clean existing articles
        self.clean_existing_articles()
        
        # Parse sections from workout-queries.md
        print("\n📄 Parsing workout-queries.md for sections...")
        article_sections = self.parse_workout_queries()
        print(f"📝 Found {len(article_sections)} sections to generate")
        
        # Load query results
        print("\n📄 Loading query results...")
        query_results = self.load_query_results()
        
        # Extract all content
        all_content = self.extract_content_from_results(query_results)
        print(f"📊 Extracted: {len(all_content['facts'])} facts, {len(all_content['blog_quotes'])} blog quotes, "
              f"{len(all_content['forum_questions'])} forum Q&As, {len(all_content['video_references'])} video references")
        
        # Get bad facts
        print("\n🚫 Loading bad facts from Google Sheets...")
        bad_facts = get_bad_facts_for_article_generation()
        
        # Create output directory
        output_dir = self.output_path / "articles-ai"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate sections
        print("\n📑 Generating article sections...")
        total_words = 0
        generated_sections = []
        
        for i, (section_name, keywords, category) in enumerate(article_sections, 1):
            # Format section name for filename
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
            
            # Save section
            with open(section_file, 'w') as f:
                f.write(section_text)
            
            word_count = len(section_text.split())
            total_words += word_count
            print(f"    ✅ Generated {word_count} words -> {section_file.name}")
            
            # Store section info for later steps
            generated_sections.append({
                "filename": section_file.name,
                "section_name": section_name,
                "category": category
            })
            
            # Add delay to avoid rate limits
            time.sleep(2)
        
        # Save section info for next steps
        section_info_file = Path("article-temp-files/generated_sections.json")
        section_info_file.parent.mkdir(exist_ok=True)
        with open(section_info_file, 'w') as f:
            json.dump(generated_sections, f, indent=2)
        
        print(f"\n📊 Total words generated: {total_words:,}")
        print(f"✅ All sections saved to: {output_dir}")
        print(f"📋 Section info saved to: {section_info_file}")


def main():
    generator = ArticleContentGenerator()
    generator.generate()


if __name__ == "__main__":
    main()