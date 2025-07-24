#!/usr/bin/env python3
"""
Individual Article Generator

Creates specific solution articles targeting individual user problems using vector search across:
- Blog content vectors
- YouTube video vectors  
- Forum Q&A vectors

Focuses on recent high-priority issues identified from forum analysis.
"""

import os
import json
import sys
import re
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
import openai
from anthropic import Anthropic
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

from utils.db_connection import get_db_connection

class IndividualArticleGenerator:
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

    def search_vectors(self, query_embedding, source_filter=None, limit=15, recency_boost=True):
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

    def get_specific_forum_topics(self, topic_ids, keywords=None):
        """Get specific forum topics by ID or keyword search"""
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            if topic_ids:
                # Search by specific topic IDs
                topic_id_list = ', '.join([str(tid) for tid in topic_ids])
                query = f"""
                SELECT qa.*, ftr.title as topic_title,
                       ftr.topic_id, ftr.posts_count
                FROM forum_qa_pairs qa
                JOIN forum_topics_raw ftr ON qa.topic_id = ftr.topic_id
                WHERE qa.topic_id IN ({topic_id_list})
                    AND qa.pain_point IS NOT NULL 
                    AND qa.pain_point != ''
                    AND LENGTH(qa.pain_point) > 10
                ORDER BY qa.date_posted DESC
                LIMIT 50
                """
                cursor.execute(query)
            elif keywords:
                # Search by keywords
                keyword_conditions = ' OR '.join([f"LOWER(qa.pain_point || ' ' || qa.question_content || ' ' || ftr.title) LIKE %s" for _ in keywords])
                keyword_params = [f"%{keyword.lower()}%" for keyword in keywords]
                
                query = f"""
                SELECT qa.*, ftr.title as topic_title,
                       ftr.topic_id, ftr.posts_count,
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
                    AND qa.date_posted >= CURRENT_DATE - INTERVAL '1 year'
                ORDER BY recency_score DESC, qa.date_posted DESC
                LIMIT 30
                """
                cursor.execute(query, keyword_params)
            else:
                return []
            
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            return results
            
        except Exception as e:
            print(f"Error getting specific forum topics: {e}")
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

    def generate_article_with_claude(self, article_info, related_content, forum_topics):
        """Generate individual article content using Claude with your writing style"""
        
        # Load prompt template
        prompt_template = self.load_prompt_template('individual-article-prompt-template.txt')
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
        
        # Prepare specific forum topics and user problems
        specific_topics_text = []
        for i, topic in enumerate(forum_topics[:10], 1):  # Top 10 most relevant
            specific_topics_text.append(f"{i}. **Topic**: {topic.get('topic_title', '')} (ID: {topic.get('topic_id', '')}) - Posts: {topic.get('posts_count', 0)}")
            specific_topics_text.append(f"   **Problem**: {topic.get('pain_point', '')}")
            specific_topics_text.append(f"   **Details**: {topic.get('question_content', '')[:150]}...")
            specific_topics_text.append("")
        
        # Format the prompt template (just for article content, no tags yet)
        prompt = prompt_template.format(
            title=article_info['title'],
            category=article_info['category'],
            problem_type='Feature Usage',  # Since we're focusing on features
            estimated_words=650,  # Target 500-800 words
            user_impact=f"High - {article_info.get('user_pain_point', 'affecting multiple users')}",
            specific_topics_text=chr(10).join(specific_topics_text),
            blog_summaries=chr(10).join(blog_summaries[:8]),
            youtube_summaries=chr(10).join(youtube_summaries[:8]),
            forum_summaries=chr(10).join(forum_summaries[:10])
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

    def get_tags_for_article(self, title, article_content):
        """Get appropriate tags for the article using a separate Claude API call"""
        
        tag_prompt = f"""
Based on this article title and content, suggest 2-4 most relevant tags from the approved list below.

ARTICLE TITLE: {title}

ARTICLE CONTENT: {article_content[:1000]}...

APPROVED TAGS (only use these exact tag names):
App & Platform: web-app, mobile-app, about-trainerday
Training Concepts: time-crunched, polarized, zone-2, heart-rate, recovery, w-prime, ftp
Features & Tools: coach-jack, workout-creator, plan-creator, my-workouts, my-plans, my-calendar, WOD, plans, organization, sharing, export, dynamic-training
Equipment & Tech: equipment, technology, speed-distance
Integrations: garmin, zwift, training-peaks, intervals-icu, wahoo
Activities: vasa-swim, rowing
Content: reviews, health, integrations, web-trainer

Return only the most relevant 2-4 tag names separated by commas, nothing else.
"""

        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=100,
                temperature=0.3,
                messages=[{"role": "user", "content": tag_prompt}]
            )
            
            tag_response = response.content[0].text.strip()
            # Parse the comma-separated tags
            tags = [tag.strip() for tag in tag_response.split(',') if tag.strip()]
            return tags
            
        except Exception as e:
            print(f"Error getting tags from Claude: {e}")
            return []

    def create_individual_article(self, article_info, custom_filename=None):
        """Create complete individual solution article with vector search"""
        
        print(f"🔍 Generating individual article: {article_info['title']}")
        print(f"   Category: {article_info['category']}")
        print(f"   Engagement Level: {article_info.get('engagement', 'Complete')}")
        print(f"   Target words: 500-800")
        if custom_filename:
            print(f"   Custom filename: {custom_filename}")
        print()
        
        # Generate query embedding
        query_text = f"{article_info['title']} {article_info.get('keywords', [])} {article_info.get('description', '')}"
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
            blog_results = self.search_vectors(query_embedding, source_filter='blog', limit=8)
            related_content['blog'] = blog_results
            print(f"   📝 Found {len(blog_results)} related blog articles")
        except Exception as e:
            print(f"   ⚠️  Blog search failed: {e}")
        
        # Search YouTube content
        try:
            youtube_results = self.search_vectors(query_embedding, source_filter='youtube', limit=6)
            related_content['youtube'] = youtube_results
            print(f"   🎥 Found {len(youtube_results)} related YouTube videos")
        except Exception as e:
            print(f"   ⚠️  YouTube search failed: {e}")
        
        # Search forum content
        try:
            forum_results = self.search_vectors(query_embedding, source_filter='forum', limit=10)
            related_content['forum'] = forum_results
            print(f"   💬 Found {len(forum_results)} related forum Q&A pairs")
        except Exception as e:
            print(f"   ⚠️  Forum search failed: {e}")
        
        # Get specific forum topics for this issue
        print(f"🎯 Getting specific forum topics...")
        specific_topics = []
        
        if 'keywords' in article_info and article_info['keywords']:
            specific_topics = self.get_specific_forum_topics(None, article_info['keywords'])
            print(f"   Found {len(specific_topics)} keyword-matched discussions")
        
        # Generate article with Claude
        print("🤖 Generating article content with Claude...")
        article_content = self.generate_article_with_claude(article_info, related_content, specific_topics)
        
        if not article_content:
            print("❌ Failed to generate article content")
            return None
        
        # Get tags using separate API call
        print("🏷️  Getting appropriate tags for the article...")
        tags_list = self.get_tags_for_article(article_info['title'], article_content)
        print(f"   Suggested tags: {', '.join(tags_list)}")
        
        # Clean up any tag lines that might be in the content
        if "**Tags:**" in article_content:
            lines = article_content.split('\n')
            cleaned_lines = [line for line in lines if not line.startswith('**Tags:**')]
            article_content = '\n'.join(cleaned_lines)
        
        # Create properties (remove colons from values to prevent YAML parsing issues)
        properties = self.properties_template.copy()
        properties.update({
            'category': article_info['category'].replace(':', ''),
            'title': article_info['title'].replace(':', ''),
            'tags': tags_list,
            'excerpt': "",  # Empty like the template  
            'permalink': f"blog/articles-ai/{article_info['slug']}".replace(':', '')
        })
        
        # Create frontmatter to exactly match template format
        frontmatter = "---\n"
        frontmatter += f"category: {properties['category']}\n"
        frontmatter += f"date: {properties['date']}\n"
        frontmatter += f"engagement: {properties['engagement']}\n"
        frontmatter += "excerpt: \n"  # Empty with space like template
        frontmatter += f"permalink: {properties['permalink']}\n"
        frontmatter += f"status: {properties['status']}\n"
        
        # Add tags as YAML array if they exist
        if tags_list:
            frontmatter += "tags: \n"
            for tag in tags_list:
                frontmatter += f"  - {tag}\n"
        else:
            frontmatter += "tags: \n"  # Empty with space like template
            
        frontmatter += f"title: {properties['title']}\n"
        frontmatter += "---\n\n"
        
        # Combine frontmatter and content
        full_article = frontmatter + article_content
        
        # Save article to blog/articles-ai directory
        output_base = Path(os.getenv('CONTENT_OUTPUT_PATH', '.'))
        output_dir = output_base / 'articles-ai'  # Go to TD-Business/blog/articles-ai
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if custom_filename:
            # If custom filename provided, use it but also create a title-based version
            if custom_filename.startswith('F') and 'placeholder' in custom_filename:
                # Extract F number and create proper filename
                f_number = custom_filename.split('-')[0]  # Get F001, F002, etc.
                filename = f"{f_number}-{article_info['slug']}.md"
            else:
                filename = custom_filename
        else:
            filename = f"{article_info['slug']}.md"
            
        output_file = output_dir / filename
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_article)
        
        print(f"✅ Article created: {output_file}")
        print(f"   📊 Content length: {len(article_content)} characters")
        print(f"   🎯 Target was: 500-800 words")
        
        return {
            'file_path': str(output_file),
            'properties': properties,
            'content_length': len(article_content),
            'related_sources': {
                'blog_count': len(related_content['blog']),
                'youtube_count': len(related_content['youtube']),
                'forum_count': len(related_content['forum']),
                'specific_topics_count': len(specific_topics)
            }
        }

def parse_features_markdown():
    """Parse the ai-articles-features.md file to get article data"""
    features_file_path = Path("/Users/alex/Documents/bm-projects/TD-Business/blog/in-progress/ai-articles-features.md")
    
    if not features_file_path.exists():
        print(f"Error: Features file not found at {features_file_path}")
        return {}
    
    articles = {}
    
    try:
        with open(features_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the first table (Generated Feature Articles section)
        lines = content.split('\n')
        table_started = False
        table_count = 0
        
        for i, line in enumerate(lines):
            # Skip until we find the table header separator
            if '|---|' in line or '| ---' in line:
                table_count += 1
                print(f"Debug: Found table {table_count} at line {i+1}")
                if table_count == 1:  # Use the first table only
                    table_started = True
                continue
                
            if not table_started:
                continue
                
            # Stop if we hit a new section header
            if line.startswith('##'):
                print(f"Debug: Stopping at section header at line {i+1}: {line}")
                break
                
            # Parse table row
            if line.startswith('|') and '|' in line[1:]:
                parts = [part.strip() for part in line.split('|')[1:-1]]  # Remove empty first/last elements
                
                if len(parts) >= 5:  # Ensure we have all required columns
                    try:
                        article_num = int(parts[0])
                        include = parts[1] 
                        title = parts[2]
                        engagement = parts[3]
                        tags = parts[4]
                        user_pain_point = parts[5] if len(parts) > 5 else ""
                        
                        # Skip articles not marked as "yes"
                        if include.lower() != 'yes':
                            continue
                            
                        # Generate slug from title
                        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
                        slug = re.sub(r'\s+', '-', slug)
                        slug = slug[:50]  # Limit length
                        
                        # Extract keywords from tags and title
                        keywords = []
                        if tags and tags != '':
                            # Extract words from tags, removing backticks
                            tag_words = re.findall(r'`([^`]+)`', tags)
                            keywords.extend(tag_words)
                        
                        # Add key words from title
                        title_words = re.findall(r'\b\w+\b', title.lower())
                        important_words = [w for w in title_words if len(w) > 3 and w not in ['guide', 'trainerday', 'workout', 'complete', 'quick', 'solve']]
                        keywords.extend(important_words[:5])  # Limit to 5 key words
                        
                        articles[article_num] = {
                            'title': title,
                            'slug': slug,
                            'category': 'Features',
                            'engagement': engagement,
                            'user_pain_point': user_pain_point,
                            'keywords': keywords,
                            'tags': tags
                        }
                        
                    except (ValueError, IndexError) as e:
                        print(f"Warning: Could not parse line: {line[:50]}... ({e})")
                        continue
        
        print(f"Debug: Parsed {len(articles)} articles: {sorted(articles.keys())}")
        return articles
        
    except Exception as e:
        print(f"Error reading features file: {e}")
        return {}

def main():
    """Generate individual solution article based on article number"""
    
    # Get article number and optional custom filename from command line
    article_num = 1  # Default to article 1
    custom_filename = None
    
    if len(sys.argv) > 1:
        try:
            article_num = int(sys.argv[1])
        except ValueError:
            print("Error: Article number must be an integer")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        custom_filename = sys.argv[2]
    
    print("🎯 INDIVIDUAL SOLUTION ARTICLE GENERATOR")
    print("=" * 50)
    
    generator = IndividualArticleGenerator()
    
    # Load articles from the features markdown file
    print("📖 Loading articles from ai-articles-features.md...")
    articles = parse_features_markdown()
    
    if not articles:
        print("❌ No articles found in the features file.")
        sys.exit(1)
    
    # Select the requested article
    if article_num not in articles:
        print(f"Error: Article #{article_num} not found. Available articles: {list(articles.keys())}")
        sys.exit(1)
    
    selected_article = articles[article_num]
    print(f"Creating individual article #{article_num}: {selected_article['title'][:60]}...")
    print()
    
    try:
        result = generator.create_individual_article(selected_article, custom_filename)
        
        if result:
            print()
            print("🎉 SUCCESS! Individual solution article generated")
            print(f"📄 File: {result['file_path']}")
            print(f"📊 Stats:")
            print(f"   - Content length: {result['content_length']:,} characters")
            print(f"   - Blog sources: {result['related_sources']['blog_count']}")
            print(f"   - YouTube sources: {result['related_sources']['youtube_count']}")
            print(f"   - Forum sources: {result['related_sources']['forum_count']}")
            print(f"   - Specific topics: {result['related_sources']['specific_topics_count']}")
            print()
            print("🔗 The article includes:")
            print("   - Specific problem identification")
            print("   - Step-by-step solution procedures")
            print("   - Advanced troubleshooting options")
            print("   - Prevention tips and best practices")
            print("   - When to escalate to support")
            
        else:
            print("❌ Failed to generate individual article")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()