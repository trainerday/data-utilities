#!/usr/bin/env python3
"""
Generate Article from User Question

Simple function to generate an article from a user question using existing infrastructure.
Combines the vector search and Claude generation logic into a single, easy-to-use interface.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import openai
from anthropic import Anthropic
import psycopg2
from psycopg2.extras import RealDictCursor
import re

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from utils.db_connection import get_db_connection

class QuestionToArticleGenerator:
    def __init__(self):
        # Initialize API clients
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        # Article properties template
        self.properties_template = {
            'category': 'User Questions',
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

    def search_vectors(self, query_embedding, source_filter=None, limit=15):
        """Search vectors in unified content_embeddings table with optional source filter"""
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
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
            
            source_condition = ""
            params = [query_embedding]
            
            if source_filter:
                source_condition = "AND source = %s"
                params.append(source_filter)
            
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

    def search_related_forum_topics(self, user_question, limit=15):
        """Search for forum topics related to the user question"""
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Extract keywords from question for search
            keywords = re.findall(r'\b\w+\b', user_question.lower())
            important_keywords = [k for k in keywords if len(k) > 3 and k not in ['what', 'how', 'when', 'where', 'why', 'does', 'can', 'will', 'should', 'would', 'could', 'the', 'and', 'but', 'for', 'with']][:5]
            
            if not important_keywords:
                return []
            
            # Build search conditions
            keyword_conditions = ' OR '.join([f"LOWER(qa.pain_point || ' ' || qa.question_content || ' ' || ftr.title) LIKE %s" for _ in important_keywords])
            keyword_params = [f"%{keyword.lower()}%" for keyword in important_keywords]
            
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
            LIMIT %s
            """
            
            cursor.execute(query, keyword_params + [limit])
            results = cursor.fetchall()
            
            cursor.close()
            conn.close()
            return results
            
        except Exception as e:
            print(f"Error searching forum topics: {e}")
            cursor.close()
            conn.close()
            return []

    def load_prompt_template(self):
        """Load the individual article prompt template"""
        template_path = Path(__file__).parent.parent / 'templates' / 'individual-article-prompt-template.txt'
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading template: {e}")
            return None

    def generate_title_and_slug(self, user_question):
        """Generate appropriate title and slug from user question"""
        # Clean up question to make it title-like
        title = user_question.strip()
        if not title.endswith('?'):
            title += '?'
        
        # Capitalize first letter
        title = title[0].upper() + title[1:]
        
        # Generate slug from title
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
        slug = re.sub(r'\s+', '-', slug)
        slug = slug[:50]  # Limit length
        
        return title, slug

    def generate_article_with_claude(self, user_question, title, related_content, forum_topics):
        """Generate article content using Claude with existing writing style"""
        
        # Load prompt template
        prompt_template = self.load_prompt_template()
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
        
        # Prepare specific forum topics
        specific_topics_text = []
        for i, topic in enumerate(forum_topics[:10], 1):
            specific_topics_text.append(f"{i}. **Topic**: {topic.get('topic_title', '')} (ID: {topic.get('topic_id', '')}) - Posts: {topic.get('posts_count', 0)}")
            specific_topics_text.append(f"   **Problem**: {topic.get('pain_point', '')}")
            specific_topics_text.append(f"   **Details**: {topic.get('question_content', '')[:150]}...")
            specific_topics_text.append("")
        
        # Add user question context
        specific_topics_text.insert(0, f"**Original User Question**: {user_question}")
        specific_topics_text.insert(1, "")
        specific_topics_text.insert(2, "**Related User Problems from Forum**:")
        specific_topics_text.insert(3, "")
        
        # Format the prompt template
        prompt = prompt_template.format(
            title=title,
            category='User Questions',
            problem_type='User Question',
            estimated_words=650,
            user_impact=f"Medium - User seeking guidance: {user_question[:100]}...",
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

    def generate_article_from_question(self, user_question, save_to_file=True):
        """
        Main function to generate an article from a user question
        
        Args:
            user_question (str): The user's question
            save_to_file (bool): Whether to save the article to a file
            
        Returns:
            dict: Article data including content, file path, and metadata
        """
        
        print(f"🔍 Generating article from question: {user_question[:60]}...")
        print()
        
        # Generate title and slug
        title, slug = self.generate_title_and_slug(user_question)
        print(f"📝 Article title: {title}")
        print()
        
        # Generate query embedding
        query_embedding = self.get_embedding(user_question)
        
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
        
        # Get specific forum topics related to the question
        print(f"🎯 Getting related forum discussions...")
        specific_topics = self.search_related_forum_topics(user_question, limit=15)
        print(f"   Found {len(specific_topics)} related discussions")
        
        # Generate article with Claude
        print("🤖 Generating article content with Claude...")
        article_content = self.generate_article_with_claude(user_question, title, related_content, specific_topics)
        
        if not article_content:
            print("❌ Failed to generate article content")
            return None
        
        # Create properties
        properties = self.properties_template.copy()
        properties.update({
            'title': title.replace(':', ''),
            'permalink': f"blog/articles-ai/{slug}".replace(':', '')
        })
        
        result = {
            'title': title,
            'slug': slug,
            'content': article_content,
            'properties': properties,
            'content_length': len(article_content),
            'related_sources': {
                'blog_count': len(related_content['blog']),
                'youtube_count': len(related_content['youtube']),
                'forum_count': len(related_content['forum']),
                'specific_topics_count': len(specific_topics)
            }
        }
        
        if save_to_file:
            # Create frontmatter
            frontmatter = "---\n"
            frontmatter += f"category: {properties['category']}\n"
            frontmatter += f"date: {properties['date']}\n"
            frontmatter += f"engagement: {properties['engagement']}\n"
            frontmatter += "excerpt: \n"
            frontmatter += f"permalink: {properties['permalink']}\n"
            frontmatter += f"status: {properties['status']}\n"
            frontmatter += "tags: \n"
            frontmatter += f"title: {properties['title']}\n"
            frontmatter += "---\n\n"
            
            # Combine frontmatter and content
            full_article = frontmatter + article_content
            
            # Save article to script-testing directory as requested
            output_dir = Path(__file__).parent
            filename = f"{slug}.md"
            output_file = output_dir / filename
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(full_article)
            
            result['file_path'] = str(output_file)
            print(f"✅ Article saved: {output_file}")
        
        print(f"   📊 Content length: {len(article_content)} characters")
        print(f"   🎯 Target was: 500-800 words")
        
        return result

def main():
    """Command line interface for generating articles from questions"""
    
    if len(sys.argv) < 2:
        print("Usage: python generate_article_from_question.py \"Your question here\"")
        print("Example: python generate_article_from_question.py \"How do I sync my Garmin watch with TrainerDay?\"")
        sys.exit(1)
    
    user_question = sys.argv[1]
    
    print("🎯 ARTICLE GENERATOR FROM USER QUESTION")
    print("=" * 50)
    
    generator = QuestionToArticleGenerator()
    
    try:
        result = generator.generate_article_from_question(user_question)
        
        if result:
            print()
            print("🎉 SUCCESS! Article generated from user question")
            print(f"📄 File: {result.get('file_path', 'Not saved')}")
            print(f"📊 Stats:")
            print(f"   - Content length: {result['content_length']:,} characters")
            print(f"   - Blog sources: {result['related_sources']['blog_count']}")
            print(f"   - YouTube sources: {result['related_sources']['youtube_count']}")
            print(f"   - Forum sources: {result['related_sources']['forum_count']}")
            print(f"   - Related topics: {result['related_sources']['specific_topics_count']}")
            
        else:
            print("❌ Failed to generate article")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()