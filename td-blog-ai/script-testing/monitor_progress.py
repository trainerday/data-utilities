#!/usr/bin/env python3
"""Monitor the progress of article enhancement"""

import os
from pathlib import Path
import glob
import re
from datetime import datetime

def monitor_progress():
    # Get all possible articles
    content_output_path = os.getenv('CONTENT_OUTPUT_PATH', '/Users/alex/Documents/bm-projects/TD-Business/blog')
    articles_base_dir = Path(content_output_path) / "articles-ai"
    articles_dir = articles_base_dir / "ai-created"
    updated_dir = articles_base_dir / "ai-updated"
    
    # Find all original articles
    pattern = str(articles_dir / "F[0-9][0-9][0-9]-*.md")
    all_articles = glob.glob(pattern)
    all_articles.sort()
    
    # Find enhanced articles
    if updated_dir.exists():
        updated_articles = list(updated_dir.glob("F[0-9][0-9][0-9]-*.md"))
        updated_articles.sort()
    else:
        updated_articles = []
    
    print(f"📊 ENHANCEMENT PROGRESS REPORT")
    print(f"=" * 50)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print(f"📄 Total articles found: {len(all_articles)}")
    print(f"✅ Articles enhanced: {len(updated_articles)}")
    print(f"⏳ Remaining: {len(all_articles) - len(updated_articles)}")
    print(f"📈 Progress: {len(updated_articles)}/{len(all_articles)} ({len(updated_articles)/len(all_articles)*100:.1f}%)")
    
    if updated_articles:
        print()
        print(f"🎯 ENHANCED ARTICLES:")
        for article in updated_articles:
            # Get article number
            match = re.match(r'F(\d+)-', article.name)
            if match:
                num = int(match.group(1))
                print(f"   ✅ F{num:03d}: {article.name}")
        
        # Show latest enhanced
        latest = max(updated_articles, key=lambda x: x.stat().st_mtime)
        latest_time = datetime.fromtimestamp(latest.stat().st_mtime)
        print()
        print(f"🕐 Latest enhancement: {latest.name} at {latest_time.strftime('%H:%M:%S')}")
    
    # Show which articles are missing (not enhanced yet)
    enhanced_numbers = set()
    for article in updated_articles:
        match = re.match(r'F(\d+)-', article.name)
        if match:
            enhanced_numbers.add(int(match.group(1)))
    
    all_numbers = set()
    for article_path in all_articles:
        article = Path(article_path)
        match = re.match(r'F(\d+)-', article.name)
        if match:
            all_numbers.add(int(match.group(1)))
    
    remaining_numbers = sorted(all_numbers - enhanced_numbers)
    if remaining_numbers:
        print()
        print(f"⏳ REMAINING ARTICLES:")
        print(f"   {remaining_numbers}")

if __name__ == "__main__":
    monitor_progress()