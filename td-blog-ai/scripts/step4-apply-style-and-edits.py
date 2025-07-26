#!/usr/bin/env python3
"""
Step 4: Apply Alex's writing style and user edits to articles, and reinsert tracked images
This script uses Claude to apply style and edits to all generated articles
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()


class StyleAndEditsApplicator:
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
    
    def load_user_edits(self) -> dict:
        """Load user edits and image data from the edit tracking system"""
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
                "articles": {},
                "images": {}
            }
    
    def get_article_edits(self, article_name: str, user_edits: dict) -> str:
        """Extract edits for a specific article"""
        edits = []
        
        # Global instructions
        if user_edits.get("global_instructions", {}).get("style"):
            edits.extend(user_edits["global_instructions"]["style"])
        
        # Article-specific edits
        if article_name in user_edits.get("articles", {}):
            article_edits = user_edits["articles"][article_name]
            
            if article_edits.get("edit_instructions"):
                for instruction in article_edits["edit_instructions"]:
                    if isinstance(instruction, dict):
                        edits.append(instruction.get("instruction", str(instruction)))
                    else:
                        edits.append(str(instruction))
            
            if article_edits.get("facts_to_add"):
                edits.append(f"Add these facts: {', '.join(article_edits['facts_to_add'])}")
            
            if article_edits.get("facts_to_remove"):
                edits.append(f"Remove these facts: {', '.join(article_edits['facts_to_remove'])}")
        
        return "\n".join(edits) if edits else "No specific edits for this article."
    
    def get_article_images(self, article_name: str, user_edits: dict) -> list:
        """Get tracked images for a specific article"""
        images_data = user_edits.get("images", {})
        if article_name in images_data:
            return images_data[article_name].get("images", [])
        return []
    
    def reinsert_images(self, content: str, images: list) -> str:
        """Reinsert tracked images into the styled content"""
        if not images:
            return content
        
        # Split content into lines
        lines = content.split('\n')
        result_lines = []
        
        # Track if we're in YAML frontmatter
        in_yaml = False
        yaml_ended = False
        article_images_inserted = False
        
        # Group images by type
        article_level_images = [img for img in images if img['type'] == 'article_level']
        inline_images = [img for img in images if img['type'] == 'inline']
        
        for i, line in enumerate(lines):
            # Track YAML frontmatter
            if line.strip() == '---':
                in_yaml = not in_yaml
                if in_yaml == False:
                    yaml_ended = True
                result_lines.append(line)
                continue
            
            # If we've ended YAML and haven't inserted article-level images yet
            if yaml_ended and not article_images_inserted and article_level_images:
                # Insert article-level images before first heading
                for img in article_level_images:
                    result_lines.append(f"![{img['alt_text']}]({img['url']})")
                result_lines.append("")  # Empty line after images
                article_images_inserted = True
            
            # Add the current line
            result_lines.append(line)
            
            # Check if we need to insert inline images based on context
            for img in inline_images:
                if img.get('context') and img['context'] != 'article_header':
                    # Try to match section context
                    if img['context'].startswith('section:'):
                        section_name = img['context'][8:].strip()
                        if line.strip().endswith(section_name):
                            # Insert image after this section heading
                            result_lines.append("")
                            result_lines.append(f"![{img['alt_text']}]({img['url']})")
                    else:
                        # Try to match paragraph context (simplified approach)
                        # In a real implementation, you'd want more sophisticated matching
                        context_preview = img['context'][:50]
                        if context_preview in line:
                            # Insert image after this line
                            result_lines.append("")
                            result_lines.append(f"![{img['alt_text']}]({img['url']})")
        
        return '\n'.join(result_lines)
    
    def apply_style_to_article(self, article_path: Path, style_examples: str, user_edits: str, images: list) -> str:
        """Apply style to a single article using Claude and reinsert images"""
        
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
            full_content = yaml_front_matter + "\n" + styled_content
        else:
            full_content = styled_content
        
        # Reinsert tracked images
        if images:
            full_content = self.reinsert_images(full_content, images)
            print(f"    🖼️  Reinserted {len(images)} tracked images")
        
        return full_content
    
    def create_originals_backup(self):
        """Create backup of articles before applying style"""
        articles_dir = self.output_path / "articles-ai"
        originals_dir = self.output_path / "_originals"
        
        # Create _originals directory
        originals_dir.mkdir(exist_ok=True)
        
        # Copy all articles to _originals
        import shutil
        for article_path in articles_dir.glob("s*.md"):
            shutil.copy2(article_path, originals_dir / article_path.name)
        
        print(f"   ✅ Created backup in {originals_dir}")
    
    def apply_style_to_all_articles(self):
        """Apply style to all generated articles and reinsert images"""
        
        print("\n🎨 Step 4: Applying Style, Edits, and Reinserting Images")
        print("=" * 50)
        
        # Create backup first
        print("\n📁 Creating backup of original articles...")
        self.create_originals_backup()
        
        # Load style examples and user edits
        style_examples = self.load_style_examples()
        user_edits = self.load_user_edits()
        
        # Get all articles
        articles_dir = self.output_path / "articles-ai"
        article_files = sorted(articles_dir.glob("s*.md"))
        
        print(f"\n📝 Found {len(article_files)} articles to style")
        
        for article_path in article_files:
            print(f"\n  Processing: {article_path.name}")
            
            # Get edits and images for this article
            article_name = article_path.stem
            article_edits = self.get_article_edits(article_name, user_edits)
            article_images = self.get_article_images(article_name, user_edits)
            
            # Apply style and reinsert images
            styled_content = self.apply_style_to_article(
                article_path, 
                style_examples, 
                article_edits,
                article_images
            )
            
            # Save styled version
            with open(article_path, 'w') as f:
                f.write(styled_content)
            
            print(f"    ✅ Style applied successfully")
        
        print("\n✨ Style, edits, and image reinsertion complete!")


def main():
    applicator = StyleAndEditsApplicator()
    applicator.apply_style_to_all_articles()


if __name__ == "__main__":
    main()