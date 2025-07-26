#!/usr/bin/env python3
"""
Two-stage article generation with instructional focus:
1. Generate instructional sections without fluff
2. Merge into comprehensive guide
"""

import os
import sys
import json
import time
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

# Define article sections with keywords for content extraction
ARTICLE_SECTIONS = [
    ("Workout Editor Basics", ["editor", "grid", "excel", "speed", "copy", "paste", "row"]),
    ("Sets and Reps Editor", ["sets", "reps", "intervals", "repetitions", "complex"]),
    ("W' and W'bal Features", ["W'", "W'bal", "anaerobic", "capacity", "matches"]),
    ("Control Modes (ERG, Slope, Resistance, HR)", ["ERG", "slope", "resistance", "HR", "mode", "heart rate"]),
    ("Interval Comments and Instructions", ["comment", "interval comment", "offset", "guidance"]),
    ("Calendar Integration", ["calendar", "sync", "garmin", "trainingpeaks", "google"]),
    ("Import and Export", ["import", "export", "zwift", "MRC", "ZWO", "download", "route"]),
    ("6-Second Warmup", ["6-second", "warmup", "immediate", "pedaling"]),
    ("Broadcast Feature", ["broadcast", "screen", "display", "tv", "browser"]),
    ("Workout Library Organization", ["library", "search", "filter", "tags", "lists", "favorites"]),
    ("Common Issues and Solutions", ["issue", "problem", "solution", "troubleshoot", "error"])
]

class InstructionalArticleGenerator:
    def __init__(self):
        """Initialize with API clients and paths"""
        
        # Setup AI clients
        self.openai_client = openai.OpenAI()
        self.anthropic_client = Anthropic()
        
        # Paths
        self.output_path = Path(os.getenv('CONTENT_OUTPUT_PATH', 'output'))
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
            facts_text = "\n".join([f"- {fact['text']}" for fact in content['facts'][:30]])
            sections.append(f"FACTS ({len(content['facts'])} total, showing top 30):\n{facts_text}")
        
        if content['blog_quotes']:
            # Limit blog quotes and truncate
            blog_entries = []
            for q in content['blog_quotes'][:10]:
                quote = q['quote']
                if len(quote) > 500:
                    quote = quote[:500] + "..."
                blog_entries.append(f"From '{q['title']}':\n{quote}")
            
            blog_text = "\n\n".join(blog_entries)
            sections.append(f"BLOG CONTENT ({len(content['blog_quotes'])} total, showing top 10):\n{blog_text}")
        
        if content['forum_questions']:
            # Limit forum content
            forum_entries = []
            for q in content['forum_questions'][:15]:
                text = q['text']
                if len(text) > 400:
                    text = text[:400] + "..."
                forum_entries.append(f"Forum discussion:\n{text}")
            
            forum_text = "\n\n".join(forum_entries)
            sections.append(f"FORUM DISCUSSIONS ({len(content['forum_questions'])} total, showing top 15):\n{forum_text}")
        
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
                model="gpt-4-turbo-preview",
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
    
    def merge_sections(self, sections: List[Dict[str, str]], bad_facts: str) -> str:
        """Merge sections using comprehensive template"""
        
        # Load comprehensive template
        template_file = self.templates_path / "comprehensive-article-template.txt"
        with open(template_file, 'r') as f:
            template = f.read()
        
        # Format sections for merge
        sections_text = "\n\n".join([
            f"## {s['name']}\n\n{s['content']}"
            for s in sections
        ])
        
        # Fill template
        prompt = template.format(
            title="TrainerDay Workout Creation and Management Features - Complete Guide",
            content_sections=sections_text,
            bad_facts_section=bad_facts
        )
        
        # Use Claude for merging
        response = self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8192,
            messages=[{
                "role": "user",
                "content": prompt
            }],
            temperature=0.7
        )
        
        return response.content[0].text
    
    def generate(self):
        """Main two-stage generation workflow"""
        
        print("\n🚀 Starting instructional article generation...")
        
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
        
        # Stage 1: Generate instructional sections
        print("\n📑 Stage 1: Generating instructional sections...")
        sections = []
        
        for i, (section_name, keywords) in enumerate(ARTICLE_SECTIONS, 1):
            # Check if section already exists
            section_file = self.script_testing_path / f"instructional_{i:02d}_{section_name.replace(' ', '_').replace('(', '').replace(')', '').replace(',', '')}.md"
            
            if section_file.exists():
                print(f"  [{i}/{len(ARTICLE_SECTIONS)}] Loading existing: {section_name}")
                with open(section_file, 'r') as f:
                    section_text = f.read().replace(f"# {section_name}\n\n", "")
                sections.append({
                    'name': section_name,
                    'content': section_text
                })
                print(f"    ✅ Loaded {len(section_text.split())} words")
                continue
            
            print(f"  [{i}/{len(ARTICLE_SECTIONS)}] Generating: {section_name}")
            
            # Extract content for this section
            section_content = self.extract_section_content(keywords, all_content)
            
            # Skip if no content found
            if not any(section_content.values()):
                print(f"    ⚠️  No content found for this section, skipping...")
                continue
            
            # Generate section
            section_text = self.generate_section(section_name, section_content, bad_facts)
            sections.append({
                'name': section_name,
                'content': section_text
            })
            
            # Save individual section
            with open(section_file, 'w') as f:
                f.write(f"# {section_name}\n\n{section_text}")
            
            print(f"    ✅ Generated {len(section_text.split())} words")
            
            # Add delay to avoid rate limits
            time.sleep(2)
        
        # Save raw combined version
        print("\n📝 Saving raw combined version...")
        combined = ["# TrainerDay Workout Creation and Management - Complete Guide\n"]
        
        for section in sections:
            combined.append(f"\n## {section['name']}\n")
            combined.append(section['content'])
        
        raw_file = self.output_path / "articles-ai" / "instructional_raw.md"
        raw_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(raw_file, 'w') as f:
            f.write('\n'.join(combined))
        
        word_count = len(' '.join(combined).split())
        print(f"✅ Raw version saved to: {raw_file}")
        print(f"📊 Total words: {word_count:,}")
        
        # Stage 2: Merge and refine
        print("\n🔀 Stage 2: Merging sections with comprehensive template...")
        final_article = self.merge_sections(sections, bad_facts)
        
        # Save final article
        output_file = self.output_path / "articles-ai" / "instructional_comprehensive.md"
        
        with open(output_file, 'w') as f:
            f.write(final_article)
        
        final_word_count = len(final_article.split())
        print(f"\n✅ Final article saved to: {output_file}")
        print(f"📊 Final word count: {final_word_count:,} words")
        
        print("\n✨ Instructional article generation complete!")


def main():
    generator = InstructionalArticleGenerator()
    generator.generate()


if __name__ == "__main__":
    main()