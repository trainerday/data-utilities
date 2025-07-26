#!/usr/bin/env python3
"""
Finalize edits by:
1. Comparing edited articles with originals
2. Extracting edit instructions
3. Extracting and tracking image URLs
4. Updating workout-edits.json with image data
5. Moving articles to blog system
"""

import os
import sys
import json
import shutil
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import openai
from dotenv import load_dotenv

load_dotenv()

class EditFinalizer:
    def __init__(self, query_set='workout'):
        self.query_set = query_set
        self.output_dir = Path('output/articles-ai')
        self.originals_dir = Path('output/_originals')
        self.edits_dir = Path(f'article-queries/edits')
        self.edits_file = self.edits_dir / f'{query_set}-edits.json'
        self.blog_destination = Path('/Users/alex/Documents/bm-projects/TD-Business/blog/articles-ai/articles-new')
        
        # Create directories if needed
        self.edits_dir.mkdir(exist_ok=True)
        self.blog_destination.mkdir(parents=True, exist_ok=True)
        
        # Setup OpenAI
        self.client = openai.OpenAI()
        
    def load_existing_edits(self) -> Dict:
        """Load existing edits if file exists"""
        if self.edits_file.exists():
            with open(self.edits_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "last_updated": "",
                "global_instructions": {
                    "style": [],
                    "facts_to_avoid": []
                },
                "articles": {},
                "images": {}  # New section for image tracking
            }
    
    def extract_edit_instructions(self, original_content: str, edited_content: str, article_name: str) -> Dict:
        """Use GPT-4o to extract high-level edit instructions"""
        
        # Skip if contents are identical
        if original_content.strip() == edited_content.strip():
            return None
            
        prompt = f"""Compare these two versions of an article and extract high-level editing instructions.

ORIGINAL VERSION:
{original_content}

EDITED VERSION:
{edited_content}

Create instructions that could be applied to a regenerated version of this article.
Focus on:
1. Content additions or enhancements  
2. Content removals
3. Style or tone changes
4. Factual corrections
5. Structural improvements
6. New sections added
7. Specific facts or details that were added

Return a JSON object with this structure:
{{
  "edit_instructions": [
    {{
      "section": "section name or 'global'",
      "instruction": "clear instruction for what to change",
      "type": "enhancement|addition|removal|style|correction"
    }}
  ],
  "facts_to_add": ["specific facts that were added"],
  "facts_to_remove": ["specific facts that were removed"],
  "custom_sections": [
    {{
      "after": "section heading to insert after",
      "title": "new section title",
      "content_summary": "what this section should contain"
    }}
  ]
}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user", 
                    "content": prompt
                }],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Error extracting edits for {article_name}: {e}")
            return None
    
    def extract_images_from_content(self, content: str, article_name: str) -> List[Dict]:
        """Extract image URLs and their context from article content"""
        images = []
        
        # Split content into lines for processing
        lines = content.split('\n')
        
        # Pattern to match markdown images
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        
        # Check for article-level images (before the first heading)
        article_started = False
        in_yaml = False
        
        for i, line in enumerate(lines):
            # Track YAML frontmatter
            if line.strip() == '---':
                in_yaml = not in_yaml
                continue
                
            # Skip YAML content
            if in_yaml:
                continue
                
            # Detect when article content starts (first heading)
            if line.strip().startswith('#') and not article_started:
                article_started = True
            
            # Find images in the line
            matches = re.finditer(image_pattern, line)
            for match in matches:
                alt_text = match.group(1)
                url = match.group(2)
                
                # Determine if this is an article-level image
                is_article_level = not article_started
                
                # Get context - the preceding paragraph or section
                context = self._get_image_context(lines, i, is_article_level)
                
                # Extract metadata from URL and alt text
                metadata = self._extract_image_metadata(url, alt_text, context)
                
                image_info = {
                    "url": url,
                    "alt_text": alt_text,
                    "type": "article_level" if is_article_level else "inline",
                    "line_number": i + 1,
                    "context": context,
                    "metadata": metadata
                }
                
                images.append(image_info)
        
        return images
    
    def _get_image_context(self, lines: List[str], image_line_index: int, is_article_level: bool) -> str:
        """Get context for an image - preceding paragraph or section heading"""
        if is_article_level:
            return "article_header"
        
        # Look backwards for context
        context_lines = []
        for i in range(image_line_index - 1, -1, -1):
            line = lines[i].strip()
            
            # Stop at previous image or empty line after content
            if line.startswith('![') or (not line and context_lines):
                break
                
            # Capture section headings
            if line.startswith('#'):
                return f"section: {line.lstrip('#').strip()}"
                
            # Capture paragraph content
            if line and not line.startswith('---'):
                context_lines.insert(0, line)
        
        # Return first 100 chars of preceding paragraph
        context_text = ' '.join(context_lines)
        return context_text[:100] + '...' if len(context_text) > 100 else context_text
    
    def _extract_image_metadata(self, url: str, alt_text: str, context: str) -> Dict:
        """Extract searchable metadata from image info"""
        metadata = {
            "keywords": [],
            "topics": [],
            "feature": ""
        }
        
        # Extract keywords from alt text
        if alt_text:
            # Simple keyword extraction - could be enhanced with NLP
            words = alt_text.lower().split()
            metadata["keywords"] = [w for w in words if len(w) > 3]
        
        # Try to determine feature from context
        feature_keywords = {
            "workout editor": ["editor", "workout", "interface"],
            "sets and reps": ["sets", "reps", "repetition"],
            "erg mode": ["erg", "power", "resistance"],
            "calendar": ["calendar", "schedule", "planning"],
            "import": ["import", "upload", "file"],
            "export": ["export", "download", "save"]
        }
        
        context_lower = context.lower()
        for feature, keywords in feature_keywords.items():
            if any(kw in context_lower for kw in keywords):
                metadata["feature"] = feature
                break
        
        return metadata
    
    def process_all_articles(self):
        """Process all articles to extract edits and images"""
        
        edits_data = self.load_existing_edits()
        articles_processed = 0
        articles_with_edits = 0
        total_images_found = 0
        
        print(f"\n📝 Processing articles for edits and images...")
        
        # Get all article files
        article_files = sorted(self.output_dir.glob("s*.md"))
        
        for article_file in article_files:
            original_file = self.originals_dir / article_file.name
            
            if not original_file.exists():
                print(f"⚠️  No original found for {article_file.name}, skipping edit extraction...")
                # Still extract images even without original
                with open(article_file, 'r') as f:
                    edited_content = f.read()
                original_content = ""
            else:
                # Read both versions
                with open(article_file, 'r') as f:
                    edited_content = f.read()
                with open(original_file, 'r') as f:
                    original_content = f.read()
            
            # Extract article info
            article_key = article_file.stem  # e.g., "s01-Workout_Editor_Basics"
            
            # Extract title from content
            title_line = edited_content.split('\n')[0]
            if title_line.startswith('# '):
                title = title_line[2:].strip()
            else:
                # Look for title after YAML
                for line in edited_content.split('\n'):
                    if line.startswith('# '):
                        title = line[2:].strip()
                        break
                else:
                    title = article_key
            
            print(f"\n  Processing: {article_file.name}")
            
            # Extract images
            images = self.extract_images_from_content(edited_content, article_file.name)
            if images:
                edits_data["images"][article_key] = {
                    "title": title,
                    "images": images,
                    "count": len(images)
                }
                total_images_found += len(images)
                print(f"    🖼️  Found {len(images)} images")
                for img in images:
                    print(f"       - {img['type']}: {img['url'][:50]}...")
            
            # Extract edit instructions if we have an original
            if original_content:
                edit_info = self.extract_edit_instructions(original_content, edited_content, article_file.name)
                
                if edit_info:
                    # Update or create article entry
                    if article_key not in edits_data["articles"]:
                        edits_data["articles"][article_key] = {}
                        
                    edits_data["articles"][article_key].update({
                        "title": title,
                        "edit_instructions": edit_info.get("edit_instructions", []),
                        "facts_to_add": edit_info.get("facts_to_add", []),
                        "facts_to_remove": edit_info.get("facts_to_remove", []),
                        "custom_sections": edit_info.get("custom_sections", [])
                    })
                    articles_with_edits += 1
                    print(f"    ✅ Found {len(edit_info.get('edit_instructions', []))} edit instructions")
                else:
                    print(f"    ✓ No edits found")
                
            articles_processed += 1
        
        # Update timestamp
        edits_data["last_updated"] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')
        
        # Save edits
        with open(self.edits_file, 'w') as f:
            json.dump(edits_data, f, indent=2)
            
        print(f"\n✅ Processed {articles_processed} articles")
        print(f"📝 Found edits in {articles_with_edits} articles")
        print(f"🖼️  Found {total_images_found} total images")
        print(f"💾 Saved edits and images to: {self.edits_file}")
        
        return articles_processed, articles_with_edits, total_images_found
    
    def copy_to_blog(self):
        """Copy edited articles to blog system"""
        
        print(f"\n📦 Copying articles to blog system...")
        
        # Get all article files
        article_files = sorted(self.output_dir.glob("s*.md"))
        copied_count = 0
        
        for article_file in article_files:
            destination = self.blog_destination / article_file.name
            
            try:
                # Copy to blog system, preserving the working copy
                shutil.copy2(article_file, destination)
                print(f"  ✅ Copied {article_file.name}")
                copied_count += 1
            except Exception as e:
                print(f"  ❌ Error copying {article_file.name}: {e}")
        
        print(f"\n✅ Copied {copied_count} articles to: {self.blog_destination}")
        
        return copied_count
    
    def finalize(self):
        """Main finalization process"""
        
        print(f"\n🚀 Finalizing edits for {self.query_set} articles...")
        
        # Process articles to extract edits and images
        articles_processed, articles_with_edits, total_images = self.process_all_articles()
        
        # Copy to blog system
        copied_count = self.copy_to_blog()
        
        print(f"\n✨ Finalization complete!")
        print(f"   - Processed: {articles_processed} articles")
        print(f"   - Edits found: {articles_with_edits} articles")
        print(f"   - Images found: {total_images} images")
        print(f"   - Copied to blog: {copied_count} articles")
        print(f"   - Data saved to: {self.edits_file}")
        
        # Provide instructions for next regeneration
        print(f"\n📌 Next regeneration will automatically apply these edits and reinsert images")
        print(f"   Run: python run-all-steps-to-generate-articles.py {self.query_set}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Finalize article edits with image tracking')
    parser.add_argument('--query-set', default='workout', help='Query set name (default: workout)')
    
    args = parser.parse_args()
    
    finalizer = EditFinalizer(query_set=args.query_set)
    finalizer.finalize()


if __name__ == "__main__":
    main()