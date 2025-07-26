#!/usr/bin/env python3
"""
Apply Alex's writing style to generated articles using Claude.
This script reads the original generated articles and applies both:
1. Any user edits from the edit tracking system
2. Alex's writing style
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()


class StyleApplicator:
    def __init__(self):
        """Initialize with API client and paths"""
        self.anthropic_client = Anthropic()
        
        # Paths
        self.output_path = Path(os.getenv('CONTENT_OUTPUT_PATH', 'output'))
        self.templates_path = Path("templates")
        self.edits_path = Path("article-queries/edits")
        
    def load_style_template(self) -> str:
        """Load the style application template"""
        template_file = self.templates_path / "apply-style-template.txt"
        with open(template_file, 'r') as f:
            return f.read()
    
    def load_style_examples(self) -> str:
        """Load Alex's writing style examples"""
        # For now, we'll define some style examples inline
        # Later this could be loaded from a file
        return """
Alex's writing style characteristics:
- Direct and instructional tone - "Here's how to..." rather than "You can..."
- No marketing fluff or excessive enthusiasm
- Clear, step-by-step instructions
- Specific values and examples (e.g., "enter 120% FTP")
- Practical focus on what users need to do
- Brief introductions that explain the purpose
- Avoids phrases like "powerful", "robust", "enhance your experience"
- Uses simple language - "fast" instead of "efficient", "easy" instead of "intuitive"

Example of Alex's style:
"To create a workout, open the Workout Editor and enter your intervals in the grid. Use copy and paste to duplicate similar intervals. The editor works like Excel - arrow keys move between cells."

NOT Alex's style:
"The powerful Workout Editor enhances your training experience with its robust features. This intuitive tool empowers users to craft personalized workouts that optimize their fitness journey."
"""
    
    def load_user_edits(self) -> Dict:
        """Load user edits from the edit tracking system"""
        edits_file = self.edits_path / "workout-edits.json"
        
        if edits_file.exists():
            with open(edits_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "global_instructions": {
                    "style": [],
                    "facts_to_avoid": []
                },
                "articles": {}
            }
    
    def get_article_edits(self, article_name: str, user_edits: Dict) -> str:
        """Extract edits for a specific article"""
        edits = []
        
        # Global instructions
        if user_edits.get("global_instructions", {}).get("style"):
            edits.extend(user_edits["global_instructions"]["style"])
        
        # Article-specific edits
        if article_name in user_edits.get("articles", {}):
            article_edits = user_edits["articles"][article_name]
            
            if article_edits.get("edit_instructions"):
                edits.extend(article_edits["edit_instructions"])
            
            if article_edits.get("facts_to_add"):
                edits.append(f"Add these facts: {', '.join(article_edits['facts_to_add'])}")
            
            if article_edits.get("facts_to_remove"):
                edits.append(f"Remove these facts: {', '.join(article_edits['facts_to_remove'])}")
        
        return "\n".join(edits) if edits else "No specific edits for this article."
    
    def apply_style_to_article(self, article_path: Path, style_examples: str, user_edits: str) -> str:
        """Apply style to a single article using Claude"""
        
        # Read the original article
        with open(article_path, 'r') as f:
            original_content = f.read()
        
        # Check if article has YAML front matter
        has_yaml = original_content.startswith('---')
        
        if has_yaml:
            # Split YAML and content
            parts = original_content.split('---', 2)
            if len(parts) >= 3:
                yaml_front_matter = f"---{parts[1]}---"
                article_content = parts[2].strip()
            else:
                yaml_front_matter = ""
                article_content = original_content
        else:
            yaml_front_matter = ""
            article_content = original_content
        
        # Load and format the template
        template = self.load_style_template()
        prompt = template.format(
            style_examples=style_examples,
            user_edits=user_edits,
            original_article=article_content
        )
        
        # Apply style using Claude
        response = self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8192,
            messages=[{
                "role": "user",
                "content": prompt
            }],
            temperature=0.3
        )
        
        styled_content = response.content[0].text
        
        # Recombine with YAML if present
        if yaml_front_matter:
            return yaml_front_matter + "\n" + styled_content
        else:
            return styled_content
    
    def apply_style_to_all_articles(self):
        """Apply style to all generated articles"""
        
        print("\n🎨 Applying Alex's writing style to articles...")
        
        # Load style examples and user edits
        style_examples = self.load_style_examples()
        user_edits = self.load_user_edits()
        
        # Get all articles
        articles_dir = self.output_path / "articles-ai"
        article_files = sorted(articles_dir.glob("s*.md"))
        
        print(f"📝 Found {len(article_files)} articles to style")
        
        for article_path in article_files:
            print(f"\n  Processing: {article_path.name}")
            
            # Get edits for this article
            article_name = article_path.stem
            article_edits = self.get_article_edits(article_name, user_edits)
            
            # Apply style
            styled_content = self.apply_style_to_article(
                article_path, 
                style_examples, 
                article_edits
            )
            
            # Save styled version
            with open(article_path, 'w') as f:
                f.write(styled_content)
            
            print(f"    ✅ Style applied successfully")
        
        print("\n✨ Style application complete!")


def main():
    applicator = StyleApplicator()
    applicator.apply_style_to_all_articles()


if __name__ == "__main__":
    main()