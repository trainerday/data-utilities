#!/usr/bin/env python3
"""
Validate all blog articles against the categories/engagement/tags specification.
"""

import os
import json
import re
from pathlib import Path
import yaml

# Path to TD-Business project (from .env)
TD_BUSINESS_PATH = "/Users/alex/Documents/bm-projects/TD-Business"

def load_specification():
    """Load the tags-and-categories.json specification."""
    spec_path = Path(TD_BUSINESS_PATH) / "blog" / "tags-and-categories.md"
    
    if not spec_path.exists():
        print(f"❌ Specification file not found at: {spec_path}")
        return None
    
    with open(spec_path, 'r') as f:
        content = f.read()
    
    # Extract JSON from markdown
    json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
    if not json_match:
        print("❌ No JSON found in specification file")
        return None
    
    try:
        spec = json.loads(json_match.group(1))
        return spec
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in specification: {e}")
        return None

def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown content."""
    if not content.startswith('---'):
        return None
    
    # Find the end of frontmatter
    end_match = re.search(r'\n---\n', content)
    if not end_match:
        return None
    
    frontmatter_content = content[3:end_match.start()]
    
    try:
        return yaml.safe_load(frontmatter_content)
    except yaml.YAMLError:
        return None

def validate_article(file_path, spec):
    """Validate a single article against the specification."""
    errors = []
    warnings = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    frontmatter = extract_frontmatter(content)
    if not frontmatter:
        return ["No valid frontmatter found"], []
    
    # Valid categories
    valid_categories = [cat['name'] for cat in spec.get('categories', [])]
    
    # Valid engagement levels  
    valid_engagement = [eng['name'] for eng in spec.get('engagement', [])]
    
    # Valid tags
    valid_tags = [tag['name'] for tag in spec.get('tags', [])]
    
    # Check category
    category = frontmatter.get('category')
    if not category:
        errors.append("Missing 'category' field")
    elif category not in valid_categories:
        errors.append(f"Invalid category '{category}'. Valid: {valid_categories}")
    
    # Check engagement
    engagement = frontmatter.get('engagement')
    if not engagement:
        errors.append("Missing 'engagement' field")
    elif engagement not in valid_engagement:
        errors.append(f"Invalid engagement '{engagement}'. Valid: {valid_engagement}")
    
    # Check for old 'difficulty' field
    if 'difficulty' in frontmatter:
        warnings.append("Still has 'difficulty' field - should be 'engagement'")
    
    # Check tags
    tags = frontmatter.get('tags', [])
    if not isinstance(tags, list):
        errors.append("Tags must be a list")
    else:
        for tag in tags:
            if tag not in valid_tags:
                errors.append(f"Invalid tag '{tag}'. Valid tags available in spec.")
    
    # Check required fields
    required_fields = ['title', 'date', 'category', 'engagement']
    for field in required_fields:
        if field not in frontmatter:
            errors.append(f"Missing required field: {field}")
    
    return errors, warnings

def main():
    """Main validation function."""
    print("🔍 Validating blog articles...")
    print("="*50)
    
    # Load specification
    spec = load_specification()
    if not spec:
        return
    
    print(f"✅ Loaded specification:")
    print(f"   - {len(spec.get('categories', []))} categories")
    print(f"   - {len(spec.get('engagement', []))} engagement levels") 
    print(f"   - {len(spec.get('tags', []))} tags")
    print()
    
    # Find all blog articles
    blog_articles_path = Path(TD_BUSINESS_PATH) / "blog" / "articles"
    
    if not blog_articles_path.exists():
        print(f"❌ Blog articles directory not found: {blog_articles_path}")
        return
    
    # Get all markdown files
    article_files = list(blog_articles_path.glob("*.md"))
    print(f"📝 Found {len(article_files)} articles to validate")
    print()
    
    # Validate each article
    total_errors = 0
    total_warnings = 0
    articles_with_issues = []
    
    for article_file in sorted(article_files):
        errors, warnings = validate_article(article_file, spec)
        
        if errors or warnings:
            articles_with_issues.append({
                'file': article_file.name,
                'errors': errors,
                'warnings': warnings
            })
            total_errors += len(errors)
            total_warnings += len(warnings)
    
    # Print results
    print("📊 VALIDATION RESULTS")
    print("="*50)
    print(f"Total Articles: {len(article_files)}")
    print(f"Articles with Issues: {len(articles_with_issues)}")
    print(f"Total Errors: {total_errors}")
    print(f"Total Warnings: {total_warnings}")
    print()
    
    if articles_with_issues:
        print("🚨 ARTICLES WITH ISSUES:")
        print("-" * 50)
        
        for article in articles_with_issues:
            print(f"\n📄 {article['file']}")
            
            if article['errors']:
                print("   ❌ ERRORS:")
                for error in article['errors']:
                    print(f"      • {error}")
            
            if article['warnings']:
                print("   ⚠️  WARNINGS:")
                for warning in article['warnings']:
                    print(f"      • {warning}")
    
    else:
        print("✅ ALL ARTICLES VALID!")
    
    print(f"\n{'='*50}")
    if total_errors == 0:
        print("🎉 No errors found - all articles conform to specification!")
    else:
        print(f"⚠️  Found {total_errors} errors that need to be fixed.")

if __name__ == "__main__":
    main()