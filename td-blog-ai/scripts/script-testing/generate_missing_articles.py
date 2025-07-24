#!/usr/bin/env python3
"""
Generate the missing articles F069 and F070 that couldn't be parsed from the features file
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import the generator
sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.generate_individual_article import IndividualArticleGenerator

def generate_missing_articles():
    """Generate the missing articles F069 and F070 manually"""
    
    generator = IndividualArticleGenerator()
    
    # Article data for F069 and F070 from the features list
    missing_articles = {
        69: {
            'title': 'How to Upgrade to Premium Subscription',
            'slug': 'how-to-upgrade-to-premium-subscription',
            'category': 'Features',
            'engagement': 'Quick',
            'user_pain_point': 'How do I unlock all TrainerDay features?',
            'keywords': ['premium', 'subscription', 'upgrade', 'features'],
            'tags': '`premium`'
        },
        70: {
            'title': 'Guide to Free Tier Limitations',
            'slug': 'guide-to-free-tier-limitations',
            'category': 'Features', 
            'engagement': 'Quick',
            'user_pain_point': 'What can I do with the free version of TrainerDay?',
            'keywords': ['free', 'tier', 'limitations', 'features'],
            'tags': '`free-features`'
        }
    }
    
    print("🎯 GENERATING MISSING ARTICLES F069-F070")
    print("=" * 50)
    
    for article_num, article_info in missing_articles.items():
        f_code = f"F{article_num:03d}"
        print(f"\n🔄 Generating {f_code}: {article_info['title']}")
        
        try:
            result = generator.create_individual_article(article_info)
            
            if result:
                print(f"✅ Successfully generated {f_code}")
                print(f"   File: {result['file_path']}")
                print(f"   Length: {result['content_length']:,} characters")
            else:
                print(f"❌ Failed to generate {f_code}")
                
        except Exception as e:
            print(f"💥 Exception generating {f_code}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    generate_missing_articles()