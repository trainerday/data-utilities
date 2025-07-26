#!/usr/bin/env python3
"""
Extract comprehensive workout content from LlamaIndex for article generation
"""

import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from llama_index.embeddings.openai import OpenAIEmbedding
from openai import OpenAI

load_dotenv()

class ComprehensiveContentExtractor:
    def __init__(self):
        self.embedding_model = OpenAIEmbedding(
            model="text-embedding-3-large",
            dimensions=1536
        )
        
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'trainerday_local',
            'user': os.getenv('USER', 'alex'),
            'password': '',
        }
        
    def get_blog_articles(self):
        """Get all blog articles about workouts"""
        conn = psycopg2.connect(**self.db_config)
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        text,
                        metadata_->>'title' as title,
                        metadata_->>'url' as url
                    FROM llamaindex_knowledge_base
                    WHERE metadata_->>'source' = 'blog'
                    AND (
                        text ILIKE '%workout editor%' OR
                        text ILIKE '%fastest workout%' OR
                        text ILIKE '%sets and reps%' OR
                        text ILIKE '%interval%' OR
                        text ILIKE '%create workout%' OR
                        text ILIKE '%edit workout%'
                    )
                    ORDER BY LENGTH(text) DESC
                """)
                
                return cur.fetchall()
                
        finally:
            conn.close()
    
    def get_youtube_transcripts(self):
        """Get YouTube video transcripts about workouts"""
        conn = psycopg2.connect(**self.db_config)
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        text,
                        metadata_->>'title' as title,
                        metadata_->>'video_id' as video_id
                    FROM llamaindex_knowledge_base
                    WHERE metadata_->>'source' = 'youtube'
                    AND (
                        text ILIKE '%workout%' OR
                        metadata_->>'title' ILIKE '%workout%'
                    )
                    ORDER BY LENGTH(text) DESC
                    LIMIT 20
                """)
                
                return cur.fetchall()
                
        finally:
            conn.close()
    
    def get_forum_discussions(self):
        """Get rich forum discussions about workouts"""
        conn = psycopg2.connect(**self.db_config)
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get Q&A format discussions
                cur.execute("""
                    SELECT 
                        text,
                        metadata_->>'title' as title,
                        metadata_->>'content_type' as content_type
                    FROM llamaindex_knowledge_base
                    WHERE metadata_->>'source' = 'forum'
                    AND metadata_->>'content_type' LIKE '%qa%'
                    AND (
                        text ILIKE '%workout editor%' OR
                        text ILIKE '%create workout%' OR
                        text ILIKE '%sets and reps%' OR
                        text ILIKE '%interval comment%' OR
                        text ILIKE '%clone workout%' OR
                        text ILIKE '%copy workout%' OR
                        text ILIKE '%edit workout%'
                    )
                    ORDER BY LENGTH(text) DESC
                    LIMIT 50
                """)
                
                return cur.fetchall()
                
        finally:
            conn.close()
    
    def get_all_facts(self):
        """Get all workout-related facts"""
        conn = psycopg2.connect(**self.db_config)
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT DISTINCT text
                    FROM llamaindex_knowledge_base
                    WHERE metadata_->>'source' = 'facts'
                    AND metadata_->>'content_type' = 'valid_fact'
                    AND (
                        text ILIKE '%workout%' OR
                        text ILIKE '%interval%' OR
                        text ILIKE '%sets%' OR
                        text ILIKE '%reps%'
                    )
                    ORDER BY text
                """)
                
                return cur.fetchall()
                
        finally:
            conn.close()
    
    def extract_and_organize_content(self):
        """Extract and organize all content"""
        
        print("📚 Extracting comprehensive workout content...")
        
        # Get all content types
        blog_articles = self.get_blog_articles()
        youtube_videos = self.get_youtube_transcripts()
        forum_discussions = self.get_forum_discussions()
        facts = self.get_all_facts()
        
        print(f"\nFound:")
        print(f"  📝 {len(blog_articles)} blog articles")
        print(f"  🎥 {len(youtube_videos)} YouTube videos")
        print(f"  💬 {len(forum_discussions)} forum discussions")
        print(f"  ✓ {len(facts)} facts")
        
        # Organize content by topic
        organized_content = {
            'blog_articles': {},
            'youtube_videos': {},
            'forum_qa': {},
            'facts': {},
            'raw_content': {
                'blog': blog_articles,
                'youtube': youtube_videos,
                'forum': forum_discussions,
                'facts': facts
            }
        }
        
        # Categorize blog articles
        for article in blog_articles:
            title = article['title'] or 'Untitled'
            if 'fastest workout' in title.lower():
                organized_content['blog_articles']['fastest_editor'] = article
            elif 'sets' in title.lower() and 'reps' in title.lower():
                organized_content['blog_articles']['sets_reps'] = article
            elif 'interval' in title.lower():
                organized_content['blog_articles']['intervals'] = article
                
        # Save all content
        output_file = Path("./script-testing/workout_query_results/comprehensive_workout_content.json")
        
        # Make serializable
        def make_serializable(obj):
            if isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_serializable(item) for item in obj]
            elif hasattr(obj, '__dict__'):
                return make_serializable(obj.__dict__)
            else:
                return obj
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(make_serializable(organized_content), f, indent=2)
            
        print(f"\n✅ Comprehensive content saved to: {output_file}")
        
        # Generate article using the prompt template
        self.generate_article_with_template(organized_content)
        
    def generate_article_with_template(self, content):
        """Generate article using the prompt template and actual content"""
        
        # Load prompt template
        template_path = Path("/Users/alex/Documents/Projects/data-utilities/vector-llama/templates/individual-article-prompt-template.txt")
        with open(template_path, 'r') as f:
            prompt_template = f.read()
        
        # Prepare content summaries
        blog_summaries = ""
        for article in content['raw_content']['blog'][:5]:  # Top 5 blog articles
            blog_summaries += f"\n\n**{article['title']}**\n{article['text'][:1000]}..."
        
        youtube_summaries = ""
        for video in content['raw_content']['youtube'][:5]:  # Top 5 videos
            youtube_summaries += f"\n\n**{video['title']}**\n{video['text'][:500]}..."
        
        forum_summaries = ""
        for discussion in content['raw_content']['forum'][:10]:  # Top 10 discussions
            forum_summaries += f"\n\n**{discussion['title']}**\n{discussion['text'][:500]}..."
        
        # Build the prompt
        prompt = prompt_template.format(
            title="TrainerDay Workout Creation and Management: A Comprehensive Guide",
            category="Workout Features",
            problem_type="Feature Documentation",
            user_impact="Users need to understand how to create, edit, and manage workouts effectively",
            specific_topics_text="""
- How to use the visual workout editor
- Understanding the fastest workout editor (Excel-like interface)
- Creating complex workouts with sets and reps
- Adding interval comments and coaching notes
- Cloning and modifying existing workouts
- Keyboard shortcuts and efficiency tips
""",
            blog_summaries=blog_summaries,
            youtube_summaries=youtube_summaries,
            forum_summaries=forum_summaries
        )
        
        # Generate article
        print("\n🤖 Generating article with OpenAI...")
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are Alex, the founder of TrainerDay, writing helpful articles for users."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        article_content = response.choices[0].message.content
        
        # Save article
        output_file = Path("./script-testing/workout_articles/comprehensive_workout_article_from_template.md")
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(article_content)
            
        print(f"✅ Article generated and saved to: {output_file}")
        print(f"📄 Article length: {len(article_content)} characters")

if __name__ == "__main__":
    extractor = ComprehensiveContentExtractor()
    extractor.extract_and_organize_content()