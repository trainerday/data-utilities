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
import frontmatter
import yaml

load_dotenv()


class YAMLMetadataGenerator:
    def __init__(self):
        """Initialize with API client and paths"""
        self.openai_client = openai.OpenAI()
        self.output_path = Path(os.getenv('CONTENT_OUTPUT_PATH', 'output'))
        
    def discover_articles(self) -> list:
        """Discover all articles from output directory"""
        output_dir = self.output_path / "articles-ai"
        articles = []
        
        if output_dir.exists():
            # Get ALL markdown files
            article_files = sorted(output_dir.glob("s*.md"))
            
            for article_file in article_files:
                # Extract section name from filename
                if article_file.name == "s00-overview.md":
                    section_name = "TrainerDay Features Overview"
                else:
                    # e.g., s01-Workout_Editor_Basics.md -> Workout Editor Basics
                    filename_parts = article_file.stem.split('-', 1)
                    if len(filename_parts) > 1:
                        section_name = filename_parts[1].replace('_', ' ')
                    else:
                        section_name = article_file.stem
                
                articles.append({
                    "filename": article_file.name,
                    "section_name": section_name,
                    "file_path": article_file
                })
        
        if not articles:
            raise FileNotFoundError("No articles found to add YAML metadata to")
        
        return articles
    
    def generate_yaml_metadata(self, section_name: str, content: str) -> dict:
        """Generate YAML metadata for the article using GPT"""
        
        # Load hierarchy rules
        hierarchy_file = Path("/Users/alex/Documents/bm-projects/TD-Business/blog/articles-ai/category-sub-categories/_hierarchy_rules_json.md")
        with open(hierarchy_file, 'r') as f:
            hierarchy_content = f.read()
        
        prompt = f"""Based on this article content about "{section_name}", generate appropriate YAML metadata.

Article content:
{content[:2000]}...

Available metadata options from our hierarchy:
{hierarchy_content}

Generate YAML metadata with:
1. title: A clear, descriptive title for the article
2. tags: Choose 3-5 relevant tags from the available tags list
3. engagement: Choose one of: quick-post, complete-post, or geek-post based on the article's depth and complexity
4. excerpt: A 1-2 sentence summary of the article

Return the metadata as a JSON object with these fields:
{{
  "title": "...",
  "tags": ["tag1", "tag2", "tag3"],
  "engagement": "...",
  "excerpt": "..."
}}"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            metadata = json.loads(response.choices[0].message.content)
            
            # Add fixed fields
            metadata['date'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')
            metadata['blog-group'] = 'Features'
            metadata['permalink'] = f"blog/articles/ai/{section_name.lower().replace(' ', '-').replace('(', '').replace(')', '').replace(',', '')}"
            metadata['author'] = 'AI'
            
            return metadata
            
        except Exception as e:
            print(f"Error generating YAML metadata: {e}")
            # Fallback metadata
            return {
                'title': section_name,
                'date': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                'blog-group': 'Features',
                'engagement': 'complete-post',
                'tags': ['web-app', 'mobile-app', 'workout-creator'],
                'excerpt': f'A comprehensive guide to {section_name} in TrainerDay.',
                'permalink': f"blog/articles/ai/{section_name.lower().replace(' ', '-').replace('(', '').replace(')', '').replace(',', '')}",
                'author': 'AI'
            }
    
    def add_yaml_to_articles(self):
        """Add YAML metadata to all generated articles"""
        print("\n🏷️  Step 5: Adding YAML Metadata to ALL Articles")
        print("=" * 50)
        
        # Discover all articles in the output folder
        articles = self.discover_articles()
        
        print(f"📝 Found {len(articles)} articles to process...")
        
        for article in articles:
            filename = article['filename']
            section_name = article['section_name']
            file_path = article['file_path']
            
            # Read the article content using frontmatter
            with open(file_path, 'r') as f:
                post = frontmatter.load(f)
            
            # Check if YAML already exists
            if post.metadata:
                print(f"  🔄 {filename} has metadata, removing and regenerating...")
                # Clear existing metadata
                post.metadata = {}
            else:
                print(f"  📝 Processing {filename}...")
            
            # Generate YAML metadata based on content
            metadata = self.generate_yaml_metadata(section_name, post.content)
            
            # Update the post metadata
            post.metadata = metadata
            
            # Write back to file using frontmatter
            with open(file_path, 'w') as f:
                f.write(frontmatter.dumps(post))
            
            print(f"    ✅ Added metadata")
            time.sleep(1)  # Rate limiting
        
        print("\n✨ YAML metadata generation complete!")


def main():
    generator = YAMLMetadataGenerator()
    generator.add_yaml_to_articles()


if __name__ == "__main__":
    main()