#!/usr/bin/env python3
"""
Two-stage article generation:
1. Generate sections independently 
2. Merge and deduplicate into comprehensive article
"""

import os
import sys
import json
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
    ("Introduction to TrainerDay Workout Creation", ["trainerday", "workout creation", "philosophy"]),
    ("The Workout Editor - Core Features", ["editor", "grid", "excel", "speed", "copy", "paste"]),
    ("Sets and Reps Editor", ["sets", "reps", "intervals", "repetitions", "complex"]),
    ("W' and W'bal Integration", ["W'", "W'bal", "anaerobic", "capacity", "matches"]),
    ("Training Control Modes", ["ERG", "slope", "resistance", "HR", "mode", "heart rate"]),
    ("Calendar and Planning Features", ["calendar", "sync", "garmin", "trainingpeaks", "google"]),
    ("Import and Export Capabilities", ["import", "export", "zwift", "MRC", "ZWO", "download"]),
    ("Advanced Features", ["broadcast", "6-second", "comments", "tags", "lists", "favorites"]),
    ("Integration with Other Platforms", ["integration", "trainingpeaks", "garmin", "zwift", "rouvy"]),
    ("Common Issues and Solutions", ["issue", "problem", "solution", "troubleshoot", "error"]),
    ("Tips and Best Practices", ["tip", "best practice", "workflow", "organization", "advice"])
]

class TwoStageArticleGenerator:
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
        """Load the section generation template"""
        
        # For now, use a simple template. Can be expanded later
        template = """You are Alex, writing a section about {section_name} for a comprehensive TrainerDay guide.

Write in your natural, conversational style:
- Direct and conversational ("If you love hard intervals then sure jump right in")
- Uses "we believe" when sharing TrainerDay's philosophy
- Practical and instructional without being overly formal
- Acknowledges user preferences ("If you want to make it harder you surely can")

SECTION: {section_name}
TARGET LENGTH: 600-1000 words

Use the following content to write a comprehensive section:

{content_sections}

IMPORTANT:
- Be thorough and include ALL relevant facts provided
- Explain features in detail with practical examples
- Include user experiences and tips where available
- Don't worry about repetition with other sections - we'll handle that later
- Focus on being complete rather than concise
"""
        
        return template
    
    def format_section_content(self, content: Dict) -> str:
        """Format content for section generation"""
        
        sections = []
        
        if content['facts']:
            facts_text = "\n".join([f"- {fact['text']}" for fact in content['facts']])
            sections.append(f"FACTS:\n{facts_text}")
        
        if content['blog_quotes']:
            blog_text = "\n\n".join([
                f"From '{q['title']}':\n{q['quote'][:400]}..."
                for q in content['blog_quotes'][:10]
            ])
            sections.append(f"BLOG CONTENT:\n{blog_text}")
        
        if content['forum_questions']:
            forum_text = "\n\n".join([
                f"Forum discussion:\n{q['text'][:300]}..."
                for q in content['forum_questions'][:10]
            ])
            sections.append(f"FORUM DISCUSSIONS:\n{forum_text}")
        
        if content['video_references']:
            video_text = "\n\n".join([
                f"Video '{v['title']}':\n{v['text'][:200]}..."
                for v in content['video_references'][:5]
            ])
            sections.append(f"VIDEO CONTENT:\n{video_text}")
        
        return "\n\n".join(sections)
    
    def generate_section(self, section_name: str, content: Dict) -> str:
        """Generate a single section"""
        
        template = self.load_section_template()
        content_formatted = self.format_section_content(content)
        
        prompt = template.format(
            section_name=section_name,
            content_sections=content_formatted
        )
        
        # Try OpenAI first, fall back to Claude
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                max_tokens=2000,  # Enough for a good section
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7
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
                }]
            )
            return response.content[0].text
    
    def merge_sections(self, sections: List[Dict[str, str]], bad_facts: str) -> str:
        """Merge sections and remove duplication"""
        
        # Format sections for the merge prompt
        sections_text = "\n\n=== SECTION BREAK ===\n\n".join([
            f"## {s['name']}\n\n{s['content']}"
            for s in sections
        ])
        
        merge_prompt = f"""You are Alex, creating the final comprehensive guide for TrainerDay workout creation and management.

You have been given {len(sections)} independently written sections. Your task is to:

1. REMOVE all duplicate information between sections
2. MAINTAIN all unique information from each section
3. CREATE smooth transitions between sections
4. ENSURE the final article is 5,000-8,000 words
5. PRESERVE your conversational writing style

IMPORTANT INSTRUCTIONS:
- If the same fact appears in multiple sections, keep it in the MOST RELEVANT section only
- Ensure features like W' and W'bal are comprehensively covered (dedicate significant space to these)
- Create a logical flow from basic to advanced features
- Add brief transitions between sections for readability
- Start with a compelling introduction that sets up the entire guide
- End with a conclusion that ties everything together

DO NOT INCLUDE THESE FACTS:
{bad_facts}

Here are the sections to merge:

{sections_text}

Write the complete, deduplicated, comprehensive article:"""
        
        # Use Claude for the merge (better at long-form synthesis)
        response = self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8192,  # Maximum for comprehensive output
            messages=[{
                "role": "user",
                "content": merge_prompt
            }],
            temperature=0.7
        )
        
        return response.content[0].text
    
    def generate(self):
        """Main two-stage generation workflow"""
        
        print("\n🚀 Starting two-stage article generation...")
        
        # Load query results
        print("📄 Loading query results...")
        query_results = self.load_query_results()
        
        # Extract all content
        all_content = self.extract_content_from_results(query_results)
        print(f"📝 Extracted: {len(all_content['facts'])} facts, {len(all_content['blog_quotes'])} blog quotes, "
              f"{len(all_content['forum_questions'])} forum Q&As, {len(all_content['video_references'])} video references")
        
        # Stage 1: Generate sections
        print("\n📑 Stage 1: Generating individual sections...")
        sections = []
        
        for i, (section_name, keywords) in enumerate(ARTICLE_SECTIONS, 1):
            # Check if section already exists
            section_file = self.script_testing_path / f"section_{i:02d}_{section_name.replace(' ', '_')}.md"
            
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
            section_text = self.generate_section(section_name, section_content)
            sections.append({
                'name': section_name,
                'content': section_text
            })
            
            # Save individual section for debugging
            with open(section_file, 'w') as f:
                f.write(f"# {section_name}\n\n{section_text}")
            
            print(f"    ✅ Generated {len(section_text.split())} words")
        
        # Get bad facts
        print("\n🚫 Loading bad facts from Google Sheets...")
        bad_facts = get_bad_facts_for_article_generation()
        
        # Stage 2: Merge and deduplicate
        print("\n🔀 Stage 2: Merging and deduplicating sections...")
        final_article = self.merge_sections(sections, bad_facts)
        
        # Save final article
        output_file = self.output_path / "articles-ai" / "comprehensive_article.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(final_article)
        
        word_count = len(final_article.split())
        print(f"\n✅ Final article saved to: {output_file}")
        print(f"📊 Final word count: {word_count:,} words")
        
        # Also save sections summary
        summary_file = self.script_testing_path / "sections_summary.json"
        with open(summary_file, 'w') as f:
            json.dump({
                'sections': [{'name': s['name'], 'words': len(s['content'].split())} for s in sections],
                'total_sections': len(sections),
                'final_words': word_count
            }, f, indent=2)
        
        print("✨ Two-stage article generation complete!")


def main():
    generator = TwoStageArticleGenerator()
    generator.generate()


if __name__ == "__main__":
    main()