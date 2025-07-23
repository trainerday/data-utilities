#!/usr/bin/env python3
"""
Fix blog articles to conform to the specification:
1. Remove 'difficulty' field
2. Add missing 'engagement' field (mapped from difficulty)
3. Fix tags formatting
"""

import os
import re
from pathlib import Path
import yaml

TD_BUSINESS_PATH = "/Users/alex/Documents/bm-projects/TD-Business"

# Mapping from old difficulty to new engagement
DIFFICULTY_TO_ENGAGEMENT = {
    "Beginner": "Quick",
    "Everyone": "Complete", 
    "Intermediate": "Complete",
    "Advanced": "Geek-Out"
}

def extract_and_fix_frontmatter(content):
    """Extract, fix, and replace frontmatter in content."""
    if not content.startswith('---'):
        return content, False
    
    # Find the end of frontmatter
    end_match = re.search(r'\n---\n', content)
    if not end_match:
        return content, False
    
    frontmatter_raw = content[3:end_match.start()]
    body = content[end_match.end():]
    
    try:
        frontmatter = yaml.safe_load(frontmatter_raw)
    except yaml.YAMLError:
        return content, False
    
    if not frontmatter:
        return content, False
    
    changed = False
    
    # Fix missing engagement field
    if 'engagement' not in frontmatter and 'difficulty' in frontmatter:
        difficulty = frontmatter['difficulty']
        if difficulty in DIFFICULTY_TO_ENGAGEMENT:
            frontmatter['engagement'] = DIFFICULTY_TO_ENGAGEMENT[difficulty]
            changed = True
            print(f"      Added engagement: {frontmatter['engagement']}")
    
    # Remove difficulty field
    if 'difficulty' in frontmatter:
        del frontmatter['difficulty']
        changed = True
        print(f"      Removed difficulty field")
    
    # Fix tags formatting - ensure it's a list
    if 'tags' in frontmatter:
        tags = frontmatter['tags']
        if isinstance(tags, str):
            # Convert single string to list
            frontmatter['tags'] = [tags.strip()]
            changed = True
            print(f"      Fixed tags formatting: {frontmatter['tags']}")
        elif not isinstance(tags, list):
            # Convert to list if it's some other type
            frontmatter['tags'] = []
            changed = True
            print(f"      Reset invalid tags to empty list")
    
    if changed:
        # Rebuild the content
        new_frontmatter = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
        new_content = f"---\n{new_frontmatter}---\n{body}"
        return new_content, True
    
    return content, False

def fix_article(file_path):
    """Fix a single article."""
    print(f"\n📝 {file_path.name}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    new_content, changed = extract_and_fix_frontmatter(original_content)
    
    if changed:
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"   ✅ Fixed and saved")
        return True
    else:
        print(f"   ➖ No changes needed")
        return False

def main():
    """Main fix function."""
    print("🔧 Fixing blog articles...")
    print("="*50)
    
    # Find all blog articles
    blog_articles_path = Path(TD_BUSINESS_PATH) / "blog" / "articles"
    
    if not blog_articles_path.exists():
        print(f"❌ Blog articles directory not found: {blog_articles_path}")
        return
    
    # Get all markdown files
    article_files = list(blog_articles_path.glob("*.md"))
    print(f"📝 Found {len(article_files)} articles to check")
    
    # Fix each article
    fixed_count = 0
    
    for article_file in sorted(article_files):
        if fix_article(article_file):
            fixed_count += 1
    
    # Print results
    print(f"\n{'='*50}")
    print(f"🎉 Fixed {fixed_count} articles")
    print(f"📊 {len(article_files) - fixed_count} articles were already correct")
    print(f"\n💡 Run validate_blog_articles.py again to verify all fixes")

if __name__ == "__main__":
    main()