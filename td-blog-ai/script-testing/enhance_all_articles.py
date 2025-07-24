#!/usr/bin/env python3
"""
Enhance ALL Articles - Process Every Article File

This script processes ALL article files (F001-F068) through Claude for enhancement,
not just those with specific fact corrections marked in Google Sheets.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic
import re
import glob
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))


def load_all_articles():
    """Find and load all F###-*.md articles"""
    
    content_output_path = os.getenv('CONTENT_OUTPUT_PATH', '')
    articles_base_dir = Path(content_output_path) / "articles-ai"
    articles_dir = articles_base_dir / "ai-created"
    
    print(f"🔍 Searching for articles in: {articles_dir}")
    
    # Find all F###-*.md files
    pattern = str(articles_dir / "F[0-9][0-9][0-9]-*.md")
    article_files = glob.glob(pattern)
    article_files.sort()
    
    print(f"✅ Found {len(article_files)} articles to process")
    
    articles = []
    for file_path in article_files:
        path_obj = Path(file_path)
        # Extract article number from filename
        match = re.match(r'F(\d+)-', path_obj.name)
        if match:
            article_num = int(match.group(1))
            articles.append({
                'number': article_num,
                'filename': path_obj.name,
                'path': path_obj
            })
    
    # Sort by article number
    articles.sort(key=lambda x: x['number'])
    
    return articles

def load_article_content(article_path):
    """Load the content of an article file"""
    
    try:
        with open(article_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"❌ Could not read {article_path}: {e}")
        return None

def load_prompt_template():
    """Load the article enhancement prompt template"""
    
    template_path = Path(__file__).parent.parent / "templates" / "article-enhancement-prompt-template.txt"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        return template
    except Exception as e:
        print(f"❌ Could not load prompt template: {e}")
        return None

def enhance_article_with_claude(article_content, prompt_template):
    """Send article to Claude for general enhancement"""
    
    # Initialize Anthropic client
    client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    # Extract article title from content
    title_match = re.search(r'^title:\s*["\']?([^"\'\n]+)["\']?', article_content, re.MULTILINE)
    article_title = title_match.group(1) if title_match else "Unknown Article"
    
    # Create a general enhancement prompt (no specific fact corrections)
    prompt = f"""You are Alex, the founder of TrainerDay, an endurance training platform. Please review this blog article and enhance it if needed.

## Article to Review

**Title:** {article_title}
**Current Content:**
{article_content}

## Enhancement Instructions

Review the article for:
1. **Accuracy** - Remove any incorrect claims or outdated information
2. **Clarity** - Improve explanations that might be confusing
3. **Completeness** - Add important information that might be missing
4. **Voice** - Ensure it maintains my personal voice as Alex, the founder

## Writing Guidelines

- **Maintain my personal voice** as Alex, the founder who helps users directly
- **Keep the conversational tone** - avoid formulaic business language
- **Don't make problems sound overly common** - use calm, matter-of-fact language
- **Only use factual information** - don't invent new details, procedures, or features
- **Preserve the article structure** but enhance the content quality

## Output Format

**CRITICAL INSTRUCTION**: You must respond in one of exactly two ways:

**Option 1 - If NO CHANGES are needed**: Respond with exactly and only this:
```
NO_CHANGES_NEEDED
```

**Option 2 - If changes ARE needed**: Return the complete enhanced article starting with the YAML frontmatter (---). Do NOT include any explanatory text before or after the article. The response should be:

1. **YAML frontmatter** (update status to "edit-complete" if it was "new-article")
2. **Enhanced article content** with improvements
3. **Preserved conversational tone** and personal perspective
4. **Improved accuracy and clarity**

**DO NOT** provide explanations, analyses, or commentary. Only return either "NO_CHANGES_NEEDED" or the complete enhanced article.
"""
    
    try:
        # Send to Claude
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            temperature=0.3,
            messages=[
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
        )
        
        enhanced_content = response.content[0].text
        return enhanced_content
        
    except Exception as e:
        print(f"❌ Error calling Claude API: {e}")
        return None

def compare_and_save_article(original_content, enhanced_content, original_path, article_num):
    """Compare original and enhanced content, save only if changed"""
    
    # Check if Claude said no changes needed (exact token or within response)
    if enhanced_content.strip() == "NO_CHANGES_NEEDED" or "NO_CHANGES_NEEDED" in enhanced_content:
        print(f"✅ F{article_num:03d}: No changes needed - keeping original in ai-created")
        return False, None
    
    # Also check if Claude returned explanation instead of actual article
    # Real articles should start with YAML frontmatter (---)
    if not enhanced_content.strip().startswith('---'):
        print(f"✅ F{article_num:03d}: Claude returned explanation instead of article - keeping original")
        return False, None
    
    # Additional check: look for explanatory phrases that indicate no real enhancement
    explanation_indicators = [
        "After reviewing",  
        "I notice that",
        "Since this is the only",
        "[Note:",
        "The only change made was"
    ]
    
    if any(indicator in enhanced_content for indicator in explanation_indicators):
        print(f"✅ F{article_num:03d}: Claude returned explanation instead of enhanced article - keeping original")
        return False, None
    
    # Compare content (ignore minor whitespace differences)
    original_normalized = ' '.join(original_content.split())
    enhanced_normalized = ' '.join(enhanced_content.split())
    
    if original_normalized == enhanced_normalized:
        print(f"✅ F{article_num:03d}: No actual changes detected")
        return False, None
    
    print(f"📊 F{article_num:03d}: Changes detected!")
    print(f"   Original length: {len(original_content)} chars")
    print(f"   Enhanced length: {len(enhanced_content)} chars")
    
    # Create ai-updated directory in the articles-ai parent directory
    updated_dir = original_path.parent.parent / "ai-updated"
    updated_dir.mkdir(exist_ok=True)
    
    # Save with same filename in ai-updated directory
    updated_path = updated_dir / original_path.name
    
    try:
        with open(updated_path, 'w', encoding='utf-8') as f:
            f.write(enhanced_content)
        
        print(f"✅ F{article_num:03d}: Enhanced article saved to ai-updated/{original_path.name}")
        
        # Delete original file from ai-created since we saved enhanced version
        try:
            original_path.unlink()
            print(f"🗑️  F{article_num:03d}: Deleted original from ai-created (enhanced version saved)")
        except Exception as e:
            print(f"⚠️  F{article_num:03d}: Could not delete original from ai-created: {e}")
        
        return True, updated_path
        
    except Exception as e:
        print(f"❌ F{article_num:03d}: Error saving enhanced article: {e}")
        return False, None

def main():
    """Main function"""
    
    start_time = datetime.now()
    print("🚀 PROCESSING ALL ARTICLES FOR ENHANCEMENT")
    print("=" * 60)
    print(f"⏰ Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Find all articles
    articles = load_all_articles()
    
    if not articles:
        print("❌ No articles found")
        return
    
    # Load prompt template
    prompt_template = load_prompt_template()
    if not prompt_template:
        print("❌ Could not load prompt template")
        return
    
    print(f"📊 Processing {len(articles)} articles...")
    print()
    
    # Track statistics
    processed_count = 0
    enhanced_count = 0
    no_changes_count = 0
    error_count = 0
    
    # Process each article
    for i, article in enumerate(articles, 1):
        article_num = article['number']
        filename = article['filename']
        path = article['path']
        
        print(f"📄 [{i}/{len(articles)}] Processing F{article_num:03d}: {filename}")
        
        # Load article content
        article_content = load_article_content(path)
        if not article_content:
            print(f"⚠️  F{article_num:03d}: Could not load content - SKIPPING")
            error_count += 1
            continue
        
        # Enhance with Claude
        print(f"🤖 F{article_num:03d}: Sending to Claude for enhancement...")
        enhanced_content = enhance_article_with_claude(article_content, prompt_template)
        if not enhanced_content:
            print(f"⚠️  F{article_num:03d}: Failed to enhance - SKIPPING")
            error_count += 1
            continue
        
        # Compare and save if changed
        was_changed, saved_path = compare_and_save_article(article_content, enhanced_content, path, article_num)
        if was_changed:
            enhanced_count += 1
        else:
            no_changes_count += 1
        
        processed_count += 1
        
        # Show progress
        elapsed = datetime.now() - start_time
        avg_time_per_article = elapsed.total_seconds() / processed_count
        remaining_articles = len(articles) - processed_count
        eta_seconds = avg_time_per_article * remaining_articles
        eta = datetime.now() + timedelta(seconds=eta_seconds)
        
        print(f"⏱️  F{article_num:03d}: Completed | Elapsed: {elapsed} | ETA: {eta.strftime('%H:%M:%S')}")
        print("-" * 60)
    
    # Final summary
    end_time = datetime.now()
    total_time = end_time - start_time
    
    print()
    print("🎉 ALL ARTICLES PROCESSING COMPLETE!")
    print("=" * 60)
    print(f"⏰ Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏰ Ended:   {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️  Total time: {total_time}")
    print()
    print(f"📊 STATISTICS:")
    print(f"   - Total articles found: {len(articles)}")
    print(f"   - Successfully processed: {processed_count}")
    print(f"   - Enhanced and saved: {enhanced_count}")
    print(f"   - No changes needed: {no_changes_count}")
    print(f"   - Errors/skipped: {error_count}")
    
    # Show enhanced articles
    if enhanced_count > 0:
        print()
        print(f"✅ {enhanced_count} ARTICLES ENHANCED:")
        updated_dir = Path(os.getenv('CONTENT_OUTPUT_PATH', '')) / "articles-ai" / "UPDATED"
        if updated_dir.exists():
            updated_files = sorted(updated_dir.glob("F[0-9][0-9][0-9]-*.md"))
            for file in updated_files:
                print(f"   📄 {file.name}")

if __name__ == "__main__":
    main()