#!/usr/bin/env python3
"""
Generate remaining instructional sections
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv
import openai
from anthropic import Anthropic

# Import utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.google_sheets_client import get_bad_facts_for_article_generation

load_dotenv()

# Define remaining sections
REMAINING_SECTIONS = [
    ("6-Second Warmup", ["6-second", "warmup", "immediate", "pedaling"]),
    ("Broadcast Feature", ["broadcast", "screen", "display", "tv", "browser"]),
    ("Workout Library Organization", ["library", "search", "filter", "tags", "lists", "favorites"]),
    ("Common Issues and Solutions", ["issue", "problem", "solution", "troubleshoot", "error"])
]

class RemainingGenerator:
    def __init__(self):
        """Initialize with API clients and paths"""
        
        # Setup AI clients
        self.openai_client = openai.OpenAI()
        self.anthropic_client = Anthropic()
        
        # Paths
        self.templates_path = Path("templates")
        self.script_testing_path = Path("script-testing")
        
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
            
            # Check if any keyword matches
            if any(keyword.lower() in text_lower for keyword in keywords):
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
            facts_text = "\n".join([f"- {fact['text']}" for fact in content['facts'][:20]])
            sections.append(f"FACTS ({len(content['facts'])} total, showing top 20):\n{facts_text}")
        
        if content['blog_quotes']:
            # Limit blog quotes and truncate
            blog_entries = []
            for q in content['blog_quotes'][:5]:
                quote = q['quote']
                if len(quote) > 400:
                    quote = quote[:400] + "..."
                blog_entries.append(f"From '{q['title']}':\n{quote}")
            
            blog_text = "\n\n".join(blog_entries)
            sections.append(f"BLOG CONTENT ({len(content['blog_quotes'])} total, showing top 5):\n{blog_text}")
        
        if content['forum_questions']:
            # Limit forum content
            forum_entries = []
            for q in content['forum_questions'][:10]:
                text = q['text']
                if len(text) > 300:
                    text = text[:300] + "..."
                forum_entries.append(f"Forum discussion:\n{text}")
            
            forum_text = "\n\n".join(forum_entries)
            sections.append(f"FORUM DISCUSSIONS ({len(content['forum_questions'])} total, showing top 10):\n{forum_text}")
        
        if content['video_references']:
            # Limit video content
            video_entries = []
            for v in content['video_references'][:3]:
                text = v['text']
                if len(text) > 200:
                    text = text[:200] + "..."
                video_entries.append(f"Video '{v['title']}':\n{text}")
            
            video_text = "\n\n".join(video_entries)
            sections.append(f"VIDEO CONTENT ({len(content['video_references'])} total, showing top 3):\n{video_text}")
        
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
        
        # Use Claude with lower temperature for instructional content
        try:
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
        except Exception as e:
            print(f"Claude error: {e}, trying OpenAI")
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.3
            )
            return response.choices[0].message.content
    
    def generate(self):
        """Generate remaining sections"""
        
        print("\n🚀 Generating remaining instructional sections...")
        
        # Load query results
        print("📄 Loading query results...")
        query_results = self.load_query_results()
        
        # Extract all content
        all_content = self.extract_content_from_results(query_results)
        print(f"📝 Extracted: {len(all_content['facts'])} facts, {len(all_content['blog_quotes'])} blog quotes, "
              f"{len(all_content['forum_questions'])} forum Q&As, {len(all_content['video_references'])} video references")
        
        # Get bad facts early
        print("\n🚫 Loading bad facts from Google Sheets...")
        bad_facts = get_bad_facts_for_article_generation()
        
        # Generate remaining sections
        print("\n📑 Generating remaining sections...")
        
        # Start numbering from 8 (after the 7 existing sections)
        start_number = 8
        
        for i, (section_name, keywords) in enumerate(REMAINING_SECTIONS, start_number):
            section_file = self.script_testing_path / f"instructional_{i:02d}_{section_name.replace(' ', '_').replace('(', '').replace(')', '').replace(',', '')}.md"
            
            if section_file.exists():
                print(f"  [{i-start_number+1}/{len(REMAINING_SECTIONS)}] Already exists: {section_name}")
                continue
            
            print(f"  [{i-start_number+1}/{len(REMAINING_SECTIONS)}] Generating: {section_name}")
            
            # Extract content for this section
            section_content = self.extract_section_content(keywords, all_content)
            
            # Skip if no content found
            if not any(section_content.values()):
                print(f"    ⚠️  No content found for this section, skipping...")
                continue
            
            # Generate section
            section_text = self.generate_section(section_name, section_content, bad_facts)
            
            # Save individual section
            with open(section_file, 'w') as f:
                f.write(f"# {section_name}\n\n{section_text}")
            
            print(f"    ✅ Generated {len(section_text.split())} words")
            
            # Add delay to avoid rate limits
            time.sleep(3)
        
        print("\n✨ Remaining sections generation complete!")


def main():
    generator = RemainingGenerator()
    generator.generate()


if __name__ == "__main__":
    main()