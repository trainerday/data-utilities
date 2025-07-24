#!/usr/bin/env python3
"""
Check Article Processing Status

Shows current progress and remaining articles to process.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from utils.db_connection import get_db_connection

def check_status():
    """Check current processing status"""
    
    print("📊 ARTICLE PROCESSING STATUS")
    print("=" * 40)
    
    # Get articles directory
    content_output_path = os.getenv('CONTENT_OUTPUT_PATH', '.')
    articles_dir = Path(content_output_path) / 'articles-ai'
    
    all_articles = sorted(list(articles_dir.glob('*.md')))
    total_articles = len(all_articles)
    
    # Get processed articles from database
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Get total facts
            cursor.execute('SELECT COUNT(*) as count FROM facts')
            total_facts = cursor.fetchone()['count']
            
            # Get processed articles
            cursor.execute('SELECT DISTINCT source_article FROM facts ORDER BY source_article')
            processed_files = [row['source_article'] for row in cursor.fetchall()]
            
            # Get facts per article
            cursor.execute('''
                SELECT source_article, COUNT(*) as fact_count 
                FROM facts 
                GROUP BY source_article 
                ORDER BY source_article
            ''')
            facts_per_article = {row['source_article']: row['fact_count'] for row in cursor.fetchall()}
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error accessing database: {e}")
        return
    
    processed_count = len(processed_files)
    remaining_count = total_articles - processed_count
    
    print(f"📄 Total articles: {total_articles}")
    print(f"✅ Processed: {processed_count}")
    print(f"🔄 Remaining: {remaining_count}")
    print(f"📊 Total facts: {total_facts}")
    print(f"📈 Progress: {processed_count/total_articles*100:.1f}%")
    print()
    
    if remaining_count > 0:
        print("🔄 REMAINING ARTICLES:")
        remaining_files = [f.name for f in all_articles if f.name not in processed_files]
        
        for i, filename in enumerate(remaining_files[:10], 1):  # Show first 10
            print(f"  {i:2d}. {filename}")
        
        if len(remaining_files) > 10:
            print(f"      ... and {len(remaining_files) - 10} more")
        
        print()
        print("💡 TO CONTINUE PROCESSING:")
        print(f"   python script-testing/extract_facts_batch.py --start {processed_count} --batch-size 3")
        print("   (or run smaller batches if timeouts occur)")
    
    else:
        print("🎉 ALL ARTICLES PROCESSED!")
        print()
        print("📝 NEXT STEPS:")
        print("   1. Update Google Sheets with new facts:")
        print("      python script-testing/populate_td_blog_facts.py")
        print("   2. Review facts in Google Sheets and set status")
    
    print()
    print("📊 FACTS PER ARTICLE:")
    for filename in processed_files[-10:]:  # Show last 10 processed
        count = facts_per_article.get(filename, 0)
        print(f"   {filename}: {count} facts")
    
    if len(processed_files) > 10:
        print(f"   ... and {len(processed_files) - 10} more articles")

if __name__ == "__main__":
    check_status()