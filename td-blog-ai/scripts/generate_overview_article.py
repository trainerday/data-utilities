#!/usr/bin/env python3
"""
Overview Hub Article Generator

Creates comprehensive overview articles using vector search across:
- Blog content vectors
- YouTube video vectors  
- Forum Q&A vectors

Prioritizes recent content and uses Claude to generate articles in your style.
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
import openai
from anthropic import Anthropic
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import yaml

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.db_connection import get_db_connection

class OverviewArticleGenerator:
    def __init__(self):
        # Initialize API clients
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        # Article properties template (see templates/obsidian-frontmatter-template.yaml)
        self.properties_template = {
            'category': '',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'engagement': 'Complete',
            'excerpt': '',
            'permalink': '',
            'status': 'new-article',
            'tags': [],
            'title': ''
        }

    def get_embedding(self, text):
        """Generate embedding for text using OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-large",
                input=text,
                dimensions=1536
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None

    def search_vectors(self, query_embedding, source_filter=None, limit=20, recency_boost=True):
        """Search vectors in unified content_embeddings table with optional source filter"""
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            if recency_boost:
                # Boost recent content in scoring
                recency_sql = """
                CASE 
                    WHEN created_at >= CURRENT_DATE - INTERVAL '30 days' THEN 1.3
                    WHEN created_at >= CURRENT_DATE - INTERVAL '90 days' THEN 1.2
                    WHEN created_at >= CURRENT_DATE - INTERVAL '180 days' THEN 1.1
                    WHEN created_at >= CURRENT_DATE - INTERVAL '365 days' THEN 1.0
                    ELSE 0.9
                END
                """
            else:
                recency_sql = "1.0"
            
            source_condition = ""
            params = [query_embedding]
            
            if source_filter:
                source_condition = "AND source = %s"
                params.append(source_filter)
            
            # TODO: Exclude content marked as include = 'no' when column exists  
            # source_condition += " AND (include IS NULL OR include != 'no')"
            
            params.append(limit)
            
            query = f"""
            SELECT *, 
                   (1 - (embedding <=> %s::vector)) * {recency_sql} as similarity_score
            FROM content_embeddings
            WHERE embedding IS NOT NULL {source_condition}
            ORDER BY similarity_score DESC
            LIMIT %s
            """
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return results
            
        except Exception as e:
            print(f"Error searching content_embeddings with source_filter {source_filter}: {e}")
            cursor.close()
            conn.close()
            return []

    def get_user_questions_for_tag(self, tag, limit=50):
        """Get user questions related to specific tag"""
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Search for questions containing tag-related keywords
            tag_keywords = {
                'mobile-app': ['app', 'mobile', 'iphone', 'android', 'ios'],
                'coach-jack': ['coach jack', 'cj', 'coach', 'plan'],
                'garmin': ['garmin', 'connect', 'watch'],
                'sync': ['sync', 'synchronize', 'upload'],
                'ftp': ['ftp', 'ramp test', 'threshold'],
                'heart-rate': ['heart rate', 'hr', 'hrm'],
                'indoor-cycling': ['indoor', 'trainer', 'smart trainer'],
                'web-app': ['web', 'website', 'browser'],
                'my-calendar': ['calendar', 'schedule', 'my calendar'],
                'equipment': ['trainer', 'kickr', 'elite', 'tacx', 'wahoo']
            }
            
            keywords = tag_keywords.get(tag, [tag.replace('-', ' ')])
            keyword_conditions = ' OR '.join([f"LOWER(pain_point || ' ' || question_content) LIKE %s" for _ in keywords])
            keyword_params = [f"%{keyword.lower()}%" for keyword in keywords]
            
            query = f"""
            SELECT qa.*, ftr.title as topic_title,
                   CASE 
                       WHEN qa.date_posted >= CURRENT_DATE - INTERVAL '30 days' THEN 4
                       WHEN qa.date_posted >= CURRENT_DATE - INTERVAL '90 days' THEN 3
                       WHEN qa.date_posted >= CURRENT_DATE - INTERVAL '180 days' THEN 2
                       ELSE 1
                   END as recency_score
            FROM forum_qa_pairs qa
            JOIN forum_topics_raw ftr ON qa.topic_id = ftr.topic_id
            WHERE ({keyword_conditions})
                AND qa.pain_point IS NOT NULL 
                AND qa.pain_point != ''
                AND LENGTH(qa.pain_point) > 10
                AND qa.date_posted >= CURRENT_DATE - INTERVAL '2 years'
                AND NOT (LOWER(qa.pain_point || ' ' || qa.question_content) ~ '(concept2|rowing|erg|swim|run|weight loss|strength)')
            ORDER BY recency_score DESC, qa.date_posted DESC
            LIMIT %s
            """
            
            cursor.execute(query, keyword_params + [limit])
            results = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return results
            
        except Exception as e:
            print(f"Error getting user questions for {tag}: {e}")
            cursor.close()
            conn.close()
            return []

    def load_prompt_template(self, template_name):
        """Load prompt template from file"""
        template_path = Path(__file__).parent.parent / 'templates' / template_name
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading template {template_name}: {e}")
            return None

    def generate_article_with_claude(self, article_info, related_content, user_questions):
        """Generate article content using Claude with your writing style"""
        
        # Load prompt template
        prompt_template = self.load_prompt_template('overview-article-prompt-template.txt')
        if not prompt_template:
            return None
        
        # Prepare content summaries
        blog_summaries = []
        youtube_summaries = []
        forum_summaries = []
        
        for item in related_content['blog']:
            blog_summaries.append(f"- {item.get('title', 'Untitled')}: {item.get('content', '')[:200]}...")
        
        for item in related_content['youtube']:
            youtube_summaries.append(f"- {item.get('title', 'Untitled')}: {item.get('content', '')[:200]}...")
        
        for item in related_content['forum']:
            forum_summaries.append(f"- {item.get('title', 'Untitled')}: {item.get('content', '')[:200]}...")
        
        # Prepare user questions list
        user_questions_text = []
        for i, q in enumerate(user_questions[:20], 1):  # Top 20 questions
            user_questions_text.append(f"{i}. {q.get('pain_point', '')}")
        
        # Format the prompt template
        prompt = prompt_template.format(
            title=article_info['title'],
            tag=article_info['tag'],
            estimated_words=article_info['estimated_words'],
            description=article_info.get('description', ''),
            blog_summaries=chr(10).join(blog_summaries[:10]),
            youtube_summaries=chr(10).join(youtube_summaries[:10]),
            forum_summaries=chr(10).join(forum_summaries[:15]),
            user_questions_text=chr(10).join(user_questions_text)
        )

        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            print(f"Error generating article with Claude: {e}")
            return None

    def create_overview_article(self, article_info):
        """Create complete overview article with vector search"""
        
        print(f"🔍 Generating overview article: {article_info['title']}")
        print(f"   Tag: {article_info['tag']}")
        print(f"   Target words: {article_info['estimated_words']}")
        print()
        
        # Generate query embedding
        query_text = f"{article_info['title']} {article_info['tag']} {article_info.get('description', '')}"
        query_embedding = self.get_embedding(query_text)
        
        if not query_embedding:
            print("❌ Failed to generate query embedding")
            return None
        
        print("🔍 Searching across data sources...")
        
        # Search across unified content_embeddings table by source
        related_content = {
            'blog': [],
            'youtube': [],
            'forum': []
        }
        
        # Search blog content
        try:
            blog_results = self.search_vectors(query_embedding, source_filter='blog', limit=15)
            related_content['blog'] = blog_results
            print(f"   📝 Found {len(blog_results)} related blog articles")
        except Exception as e:
            print(f"   ⚠️  Blog search failed: {e}")
        
        # Search YouTube content
        try:
            youtube_results = self.search_vectors(query_embedding, source_filter='youtube', limit=10)
            related_content['youtube'] = youtube_results
            print(f"   🎥 Found {len(youtube_results)} related YouTube videos")
        except Exception as e:
            print(f"   ⚠️  YouTube search failed: {e}")
        
        # Search forum content
        try:
            forum_results = self.search_vectors(query_embedding, source_filter='forum', limit=20)
            related_content['forum'] = forum_results
            print(f"   💬 Found {len(forum_results)} related forum Q&A pairs")
        except Exception as e:
            print(f"   ⚠️  Forum search failed: {e}")
        
        # Get specific user questions for this tag
        print(f"🙋 Getting user questions for tag: {article_info['tag']}")
        user_questions = self.get_user_questions_for_tag(article_info['tag'], limit=30)
        print(f"   Found {len(user_questions)} user questions")
        
        # Generate article with Claude
        print("🤖 Generating article content with Claude...")
        article_content = self.generate_article_with_claude(article_info, related_content, user_questions)
        
        if not article_content:
            print("❌ Failed to generate article content")
            return None
        
        # Create properties (remove colons from values to prevent YAML parsing issues)
        properties = self.properties_template.copy()
        properties.update({
            'category': article_info['category'].replace(':', ''),
            'title': article_info['title'].replace(':', ''),
            'tags': [],  # Empty like the template
            'excerpt': "",  # Empty like the template  
            'permalink': f"blog/articles-ai/{article_info['tag']}-complete-guide".replace(':', '')
        })
        
        # Create frontmatter to exactly match template format
        # The template shows "excerpt: " and "tags: " (with space but nothing after)
        frontmatter = "---\n"
        frontmatter += f"category: {properties['category']}\n"
        frontmatter += f"date: {properties['date']}\n"
        frontmatter += f"engagement: {properties['engagement']}\n"
        frontmatter += "excerpt: \n"  # Empty with space like template
        frontmatter += f"permalink: {properties['permalink']}\n"
        frontmatter += f"status: {properties['status']}\n"
        frontmatter += "tags: \n"  # Empty with space like template
        frontmatter += f"title: {properties['title']}\n"
        frontmatter += "---\n\n"
        
        # Combine frontmatter and content
        full_article = frontmatter + article_content
        
        # Save article to blog/articles-ai directory
        output_base = Path(os.getenv('CONTENT_OUTPUT_PATH', '.'))
        output_dir = output_base / 'articles-ai'  # Go to TD-Business/blog/articles-ai
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{article_info['tag']}-complete-guide.md"
        output_file = output_dir / filename
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_article)
        
        print(f"✅ Article created: {output_file}")
        print(f"   📊 Content length: {len(article_content)} characters")
        print(f"   🎯 Target was: {article_info['estimated_words']} words")
        
        return {
            'file_path': str(output_file),
            'properties': properties,
            'content_length': len(article_content),
            'related_sources': {
                'blog_count': len(related_content['blog']),
                'youtube_count': len(related_content['youtube']),
                'forum_count': len(related_content['forum']),
                'user_questions_count': len(user_questions)
            }
        }

def main():
    """Generate the first overview hub article"""
    
    print("📚 OVERVIEW HUB ARTICLE GENERATOR")
    print("=" * 50)
    print("Creating comprehensive guide using vector search across all data sources")
    print()
    
    generator = OverviewArticleGenerator()
    
    # Get the first overview article from our content strategy
    # Based on our strategy, the first/largest is "TrainerDay Mobile App: Complete Guide"
    first_article = {
        'title': 'TrainerDay Mobile App: Complete Guide',
        'tag': 'mobile-app',
        'article_count': 101,
        'category': 'Features',
        'engagement_level': 'Complete',
        'estimated_words': 1800,
        'description': 'Comprehensive guide to all TrainerDay mobile app features with links to specific solutions and troubleshooting guides.'
    }
    
    try:
        result = generator.create_overview_article(first_article)
        
        if result:
            print()
            print("🎉 SUCCESS! Overview article generated")
            print(f"📄 File: {result['file_path']}")
            print(f"📊 Stats:")
            print(f"   - Content length: {result['content_length']:,} characters")
            print(f"   - Blog sources: {result['related_sources']['blog_count']}")
            print(f"   - YouTube sources: {result['related_sources']['youtube_count']}")
            print(f"   - Forum sources: {result['related_sources']['forum_count']}")
            print(f"   - User questions: {result['related_sources']['user_questions_count']}")
            print()
            print("🔗 The article includes:")
            print("   - Comprehensive feature overview")
            print("   - Solutions to common user issues")
            print("   - Best practices and troubleshooting")
            print("   - Integration details")
            print("   - Links to specific solutions")
            
        else:
            print("❌ Failed to generate overview article")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()