#!/usr/bin/env python3
"""
Batch Feature Article Generator

Generates feature articles F010 through F070 from the features list.
"""

import subprocess
import sys
import time
from pathlib import Path

def generate_article_batch(start_num, end_num):
    """Generate a batch of articles"""
    
    print(f"🎯 BATCH FEATURE ARTICLE GENERATOR")
    print(f"Generating articles {start_num}-{end_num} as F{start_num:03d}-F{end_num:03d}")
    print("=" * 60)
    
    success_count = 0
    failed_articles = []
    
    for article_num in range(start_num, end_num + 1):
        f_code = f"F{article_num:03d}"
        
        # Let the individual generator create the filename based on the article title
        # We'll pass a placeholder and let it generate the proper title-based filename
        filename = f"{f_code}-placeholder.md"
        
        print(f"\n🔄 Generating article #{article_num} as {f_code}...")
        
        try:
            # Run the individual article generator
            result = subprocess.run([
                'python', 'generate_numbered_article.py', 
                str(article_num), filename
            ], capture_output=True, text=True, timeout=180)  # 3 minute timeout
            
            if result.returncode == 0:
                print(f"✅ Successfully generated {f_code}")
                success_count += 1
            else:
                print(f"❌ Failed to generate {f_code}")
                print(f"   Error: {result.stderr}")
                failed_articles.append((article_num, f_code))
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout generating {f_code}")
            failed_articles.append((article_num, f_code))
        except Exception as e:
            print(f"💥 Exception generating {f_code}: {e}")
            failed_articles.append((article_num, f_code))
        
        # Small delay between articles to avoid rate limiting
        time.sleep(2)
    
    print(f"\n🎉 BATCH COMPLETE!")
    print(f"✅ Successfully generated: {success_count}")
    print(f"❌ Failed: {len(failed_articles)}")
    
    if failed_articles:
        print(f"\nFailed articles:")
        for article_num, f_code in failed_articles:
            print(f"  - Article #{article_num} ({f_code})")

def main():
    # Generate articles 11-70 (F010-F069)
    # We'll do this in smaller batches to manage API limits
    
    if len(sys.argv) > 2:
        start = int(sys.argv[1])
        end = int(sys.argv[2])
    else:
        start = 11  # Start from article #11 since we have F001-F009
        end = 70    # Go through article #70
    
    generate_article_batch(start, end)

if __name__ == "__main__":
    main()