#!/usr/bin/env python3
"""
Forum Topic Analysis v2 with Raw Content Storage
Stores complete raw forum data in database, then analyzes for insights.
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from openai import OpenAI
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded environment variables from: {env_path}")
    else:
        print("No .env file found, using system environment variables")
except ImportError:
    print("python-dotenv not installed, using system environment variables")

class ForumTopicAnalyzerV2:
    def __init__(self, openai_api_key: str = None, db_config: dict = None):
        """Initialize the analyzer with OpenAI API key and database config."""
        if openai_api_key:
            self.openai_client = OpenAI(api_key=openai_api_key)
        elif os.getenv('OPENAI_API_KEY'):
            self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        else:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable or pass as parameter.")
        
        self.db_config = db_config
        self.db_connection = None
    
    def connect_to_database(self):
        """Connect to PostgreSQL database."""
        if not self.db_config:
            raise ValueError("Database configuration required for PostgreSQL storage.")
        
        try:
            print("Connecting to PostgreSQL database...")
            print(f"Host: {self.db_config['host']}")
            print(f"Database: {self.db_config['database']}")
            print(f"SSL mode: {self.db_config.get('sslmode', 'none')}")
            self.db_connection = psycopg2.connect(**self.db_config)
            print("✓ Connected to PostgreSQL database")
        except Exception as e:
            raise Exception(f"Failed to connect to database: {e}")
    
    def create_database_schema(self):
        """Create database tables for storing raw content and forum analysis."""
        if not self.db_connection:
            raise ValueError("Database connection required. Call connect_to_database() first.")
        
        schema_sql = """
        -- Raw Forum Content Storage
        CREATE TABLE IF NOT EXISTS forum_topics_raw (
            topic_id INTEGER PRIMARY KEY,
            raw_content JSONB NOT NULL,
            checksum VARCHAR(32) NOT NULL,
            scraped_at TIMESTAMP,
            last_updated TIMESTAMP DEFAULT NOW(),
            title TEXT,
            posts_count INTEGER,
            created_at_original TIMESTAMP
        );
        
        -- Forum Topics Analysis Tables (existing schema)
        CREATE TABLE IF NOT EXISTS forum_topics (
            id SERIAL PRIMARY KEY,
            topic_id INTEGER UNIQUE NOT NULL,
            title TEXT NOT NULL,
            category TEXT,
            analysis_category TEXT,
            date_created DATE,
            total_posts INTEGER,
            is_announcement BOOLEAN,
            views INTEGER,
            like_count INTEGER,
            analyzed_at TIMESTAMP DEFAULT NOW(),
            CONSTRAINT fk_raw_topic FOREIGN KEY (topic_id) REFERENCES forum_topics_raw(topic_id)
        );
        
        CREATE TABLE IF NOT EXISTS forum_qa_pairs (
            id SERIAL PRIMARY KEY,
            topic_id INTEGER REFERENCES forum_topics_raw(topic_id),
            sequence INTEGER NOT NULL,
            date_posted DATE,
            
            -- Question data
            question_username TEXT,
            question_content TEXT NOT NULL,
            question_context TEXT,
            pain_point TEXT,
            user_language TEXT,
            
            -- Response data  
            response_username TEXT,
            response_content TEXT NOT NULL,
            response_type TEXT,
            solution_offered TEXT,
            platform_language TEXT,
            
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        CREATE TABLE IF NOT EXISTS forum_voice_patterns (
            id SERIAL PRIMARY KEY,
            topic_id INTEGER REFERENCES forum_topics_raw(topic_id),
            pattern_type TEXT NOT NULL, -- 'user_voice' or 'platform_voice'
            
            -- User voice patterns
            main_pain_points JSONB,
            common_language JSONB,
            expectations_vs_reality JSONB,
            user_workarounds JSONB,
            praise_points JSONB,
            confusion_areas JSONB,
            
            -- Platform voice patterns
            explanation_style TEXT,
            common_solutions JSONB,
            feature_positioning JSONB,
            development_transparency JSONB,
            methodology_mentions JSONB,
            
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        CREATE TABLE IF NOT EXISTS forum_insights (
            id SERIAL PRIMARY KEY,
            topic_id INTEGER REFERENCES forum_topics_raw(topic_id),
            
            content_opportunities JSONB,
            messaging_gaps JSONB,
            success_indicators JSONB,
            recurring_issues JSONB,
            feature_demand JSONB,
            
            -- Priority scoring
            recency_score TEXT,
            frequency_score TEXT,
            impact_score TEXT,
            
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        -- Indexes for better query performance
        CREATE INDEX IF NOT EXISTS idx_forum_topics_raw_checksum ON forum_topics_raw(checksum);
        CREATE INDEX IF NOT EXISTS idx_forum_topics_raw_updated ON forum_topics_raw(last_updated);
        CREATE INDEX IF NOT EXISTS idx_forum_topics_category ON forum_topics(analysis_category);
        CREATE INDEX IF NOT EXISTS idx_forum_topics_date ON forum_topics(date_created);
        CREATE INDEX IF NOT EXISTS idx_qa_pairs_topic ON forum_qa_pairs(topic_id);
        CREATE INDEX IF NOT EXISTS idx_qa_pairs_date ON forum_qa_pairs(date_posted);
        """
        
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute(schema_sql)
                self.db_connection.commit()
                print("✓ Database schema created successfully")
        except Exception as e:
            self.db_connection.rollback()
            raise Exception(f"Failed to create database schema: {e}")
    
    def get_topic_checksum(self, raw_content: dict) -> str:
        """Generate checksum for raw topic content to detect changes."""
        # Create a normalized version for checksumming
        checksum_data = {
            'topic_id': raw_content.get('topic', {}).get('id'),
            'title': raw_content.get('topic', {}).get('title', ''),
            'posts_count': raw_content.get('topic', {}).get('posts_count', 0),
            'last_posted_at': raw_content.get('topic', {}).get('last_posted_at', ''),
            'posts_preview': []
        }
        
        # Include first few characters of each post for change detection
        for post in raw_content.get('posts', []):
            post_preview = {
                'id': post.get('id'),
                'username': post.get('username'),
                'created_at': post.get('created_at'),
                'content_preview': post.get('cooked', '')[:100]  # First 100 chars
            }
            checksum_data['posts_preview'].append(post_preview)
        
        content_str = json.dumps(checksum_data, sort_keys=True)
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def store_raw_topic(self, raw_content: dict) -> bool:
        """Store raw topic content in database."""
        if not self.db_connection:
            raise ValueError("Database connection required.")
        
        try:
            topic_data = raw_content.get('topic', {})
            topic_id = topic_data.get('id')
            if not topic_id:
                raise ValueError("Topic ID not found in raw content")
            
            # Generate checksum
            checksum = self.get_topic_checksum(raw_content)
            
            # Extract key metadata for easier querying
            title = topic_data.get('title', '')
            posts_count = topic_data.get('posts_count', 0)
            created_at_str = topic_data.get('created_at', '')
            scraped_at_str = raw_content.get('downloaded_at', datetime.now().isoformat())
            
            # Parse timestamps
            created_at = None
            scraped_at = None
            try:
                if created_at_str:
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                if scraped_at_str:
                    scraped_at = datetime.fromisoformat(scraped_at_str.replace('Z', '+00:00'))
            except ValueError:
                pass  # Use None if parsing fails
            
            with self.db_connection.cursor() as cursor:
                # Check if topic exists and if checksum has changed
                cursor.execute("""
                    SELECT checksum FROM forum_topics_raw WHERE topic_id = %s
                """, (topic_id,))
                
                result = cursor.fetchone()
                if result and result[0] == checksum:
                    print(f"  Topic {topic_id} unchanged (checksum match)")
                    return False  # No changes
                
                # Store or update raw content
                cursor.execute("""
                    INSERT INTO forum_topics_raw (
                        topic_id, raw_content, checksum, scraped_at, 
                        title, posts_count, created_at_original
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (topic_id) DO UPDATE SET
                        raw_content = EXCLUDED.raw_content,
                        checksum = EXCLUDED.checksum,
                        last_updated = NOW(),
                        title = EXCLUDED.title,
                        posts_count = EXCLUDED.posts_count,
                        scraped_at = EXCLUDED.scraped_at,
                        created_at_original = EXCLUDED.created_at_original
                """, (
                    topic_id, 
                    json.dumps(raw_content),
                    checksum,
                    scraped_at,
                    title,
                    posts_count,
                    created_at
                ))
                
                self.db_connection.commit()
                
                action = "Updated" if result else "Stored"
                print(f"  ✓ {action} raw content for topic {topic_id}")
                return True  # Changes detected
                
        except Exception as e:
            self.db_connection.rollback()
            raise Exception(f"Failed to store raw topic content: {e}")
    
    def delete_existing_analysis(self, topic_id: int):
        """Delete existing analysis for a topic before re-analyzing."""
        try:
            with self.db_connection.cursor() as cursor:
                # Delete in reverse dependency order
                cursor.execute("DELETE FROM forum_insights WHERE topic_id = %s", (topic_id,))
                cursor.execute("DELETE FROM forum_voice_patterns WHERE topic_id = %s", (topic_id,))
                cursor.execute("DELETE FROM forum_qa_pairs WHERE topic_id = %s", (topic_id,))
                cursor.execute("DELETE FROM forum_topics WHERE topic_id = %s", (topic_id,))
                
                self.db_connection.commit()
                print(f"  Cleared existing analysis for topic {topic_id}")
        except Exception as e:
            print(f"Error deleting existing analysis for topic {topic_id}: {e}")
            self.db_connection.rollback()
    
    def get_analysis_prompt(self) -> str:
        """Return the LLM prompt for analyzing forum topics."""
        return """You are analyzing TrainerDay forum topics to extract insights for content strategy and messaging improvements.

Analyze this entire forum topic and return a JSON response with the following structure:

{
  "topic_summary": {
    "topic_id": <number>,
    "title": "<topic title>",
    "category": "<forum category name>",
    "analysis_category": "<one of: Getting Started, Integrations & Export, Training Execution, Technical Issues, Feature Requests, Advanced Features, Success Stories, Training Theory>",
    "date_created": "<YYYY-MM-DD>",
    "total_posts": <number>,
    "is_announcement": <boolean - true if Alex posted first with feature/news announcement>
  },
  "qa_pairs": [
    {
      "sequence": <number - order in conversation>,
      "date": "<YYYY-MM-DD of question>",
      "question": {
        "username": "<user who asked>",
        "content": "<EXACT original user question text - do not paraphrase>",
        "context": "<any relevant context user provided>",
        "pain_point": "<specific problem user is experiencing>",
        "user_language": "<key terms/phrases user uses to describe issue>"
      },
      "response": {
        "username": "Alex",
        "content": "<EXACT original text of Alex's response - do not paraphrase or summarize>",
        "response_type": "<explanation|troubleshooting|announcement|limitation_admission|roadmap_hint|question_back>",
        "solution_offered": "<what solution Alex provided, if any>",
        "platform_language": "<key terms Alex uses to explain>"
      }
    }
  ],
  "user_voice_patterns": {
    "main_pain_points": ["<list of primary user struggles>"],
    "common_language": ["<terms users commonly use>"],
    "expectations_vs_reality": ["<where user expectations didn't match experience>"],
    "user_workarounds": ["<creative solutions users found>"],
    "praise_points": ["<what users specifically praised>"],
    "confusion_areas": ["<what confused users most>"]
  },
  "platform_voice_patterns": {
    "explanation_style": "<how Alex typically explains things>",
    "common_solutions": ["<Alex's go-to fixes/responses>"],
    "feature_positioning": ["<how Alex frames TrainerDay value>"],
    "development_transparency": ["<what Alex reveals about roadmap/challenges>"],
    "methodology_mentions": ["<training philosophy Alex shares>"]
  },
  "key_insights": {
    "content_opportunities": ["<videos/blogs needed based on questions>"],
    "messaging_gaps": ["<where user/platform language differs>"],
    "success_indicators": ["<signs of user satisfaction>"],
    "recurring_issues": ["<problems that come up repeatedly>"],
    "feature_demand": ["<features users are asking for>"]
  },
  "priority_score": {
    "recency": "<high|medium|low based on date>",
    "frequency": "<high|medium|low based on common issues>",
    "impact": "<high|medium|low based on user frustration/excitement>"
  }
}

Focus on extracting genuine Q&A pairs where users ask questions and Alex responds. Skip purely social interactions. For announcements where Alex posts first, capture how users respond and what questions emerge.

Preserve the actual language users and Alex use - don't paraphrase, use their exact key terms and phrases.

Here is the forum topic data:

"""

    def clean_html_content(self, html_text: str) -> str:
        """Clean HTML tags and convert to readable text."""
        import re
        
        # Remove HTML tags
        text = re.sub('<[^<]+?>', '', html_text)
        
        # Convert HTML entities
        text = text.replace('&quot;', '"')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&nbsp;', ' ')
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text

    def prepare_topic_for_analysis(self, topic_data: dict) -> dict:
        """Prepare topic data for LLM analysis by cleaning and structuring it."""
        
        # Clean topic info - handle both raw API format and stored format
        if 'topic' in topic_data:
            topic_info = topic_data.get('topic', {})
        else:
            topic_info = topic_data  # Direct topic data
            
        # Get posts from the correct location - handle both formats
        posts = []
        if 'posts' in topic_data:
            posts = topic_data.get('posts', [])
        elif 'post_stream' in topic_data and 'posts' in topic_data['post_stream']:
            posts = topic_data['post_stream']['posts']
        
        # Clean posts - only include essential fields
        cleaned_posts = []
        for post in posts:
            cleaned_post = {
                'id': post.get('id'),
                'username': post.get('username'),
                'created_at': post.get('created_at'),
                'content': self.clean_html_content(post.get('cooked', '')),
                'post_number': post.get('post_number'),
                'reply_to_post_number': post.get('reply_to_post_number')
            }
            cleaned_posts.append(cleaned_post)
        
        return {
            'topic': {
                'id': topic_info.get('id'),
                'title': topic_info.get('title'),
                'created_at': topic_info.get('created_at'),
                'category_id': topic_info.get('category_id'),
                'posts_count': topic_info.get('posts_count'),
                'views': topic_info.get('views'),
                'like_count': topic_info.get('like_count')
            },
            'posts': cleaned_posts
        }

    def analyze_stored_topic(self, topic_id: int, model: str = "gpt-4o-mini") -> Optional[dict]:
        """Analyze a topic from stored raw content."""
        
        if not self.db_connection:
            raise ValueError("Database connection required.")
        
        try:
            # Get raw content from database
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT raw_content FROM forum_topics_raw WHERE topic_id = %s
                """, (topic_id,))
                
                result = cursor.fetchone()
                if not result:
                    print(f"  ❌ FAILURE: Topic {topic_id} not found in raw content table")
                    return None
                
                raw_content = result['raw_content']
            
            # Prepare cleaned data for analysis
            cleaned_data = self.prepare_topic_for_analysis(raw_content)
            
            # Create the full prompt
            prompt = self.get_analysis_prompt()
            topic_json = json.dumps(cleaned_data, indent=2)
            
            # Check if topic is too large (rough estimate)
            if len(topic_json) > 15000:  # Roughly 3-4k tokens
                print(f"  ⚠️  WARNING: Topic {topic_id} is large ({len(topic_json)} chars) - may hit token limits")
            
            print(f"  → Making OpenAI API call for topic {topic_id}...")
            
            # Make API call
            try:
                response = self.openai_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are an expert at analyzing forum discussions for content strategy insights."},
                        {"role": "user", "content": prompt + topic_json}
                    ],
                    temperature=0.1  # Low temperature for consistent analysis
                )
            except Exception as api_error:
                print(f"  ❌ FAILURE: OpenAI API error for topic {topic_id}: {api_error}")
                return None
            
            # Parse response
            analysis_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON from response
            try:
                # Look for JSON block
                if "```json" in analysis_text:
                    json_start = analysis_text.find("```json") + 7
                    json_end = analysis_text.find("```", json_start)
                    json_text = analysis_text[json_start:json_end].strip()
                else:
                    json_text = analysis_text
                
                analysis = json.loads(json_text)
                print(f"  ✓ OpenAI analysis successful for topic {topic_id}")
                return analysis
                
            except json.JSONDecodeError as e:
                print(f"  ❌ FAILURE: JSON parsing error for topic {topic_id}")
                print(f"     Error: {e}")
                print(f"     Raw response preview: {analysis_text[:300]}...")
                return None
                
        except Exception as e:
            print(f"  ❌ FAILURE: Unexpected error analyzing topic {topic_id}: {e}")
            return None

    def save_analysis_to_database(self, analysis: dict):
        """Save analysis results to PostgreSQL database."""
        if not self.db_connection:
            raise ValueError("Database connection required.")
        
        try:
            with self.db_connection.cursor() as cursor:
                topic_summary = analysis['topic_summary']
                
                # Insert topic summary
                topic_sql = """
                INSERT INTO forum_topics (
                    topic_id, title, category, analysis_category, date_created, 
                    total_posts, is_announcement, views, like_count
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (topic_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    category = EXCLUDED.category,
                    analysis_category = EXCLUDED.analysis_category,
                    date_created = EXCLUDED.date_created,
                    total_posts = EXCLUDED.total_posts,
                    is_announcement = EXCLUDED.is_announcement,
                    views = EXCLUDED.views,
                    like_count = EXCLUDED.like_count,
                    analyzed_at = NOW()
                """
                
                cursor.execute(topic_sql, (
                    topic_summary['topic_id'],
                    topic_summary['title'],
                    topic_summary.get('category', ''),
                    topic_summary.get('analysis_category', ''),
                    topic_summary.get('date_created'),
                    topic_summary.get('total_posts', 0),
                    topic_summary.get('is_announcement', False),
                    topic_summary.get('views', 0),
                    topic_summary.get('like_count', 0)
                ))
                
                # Insert Q&A pairs
                for qa_pair in analysis.get('qa_pairs', []):
                    qa_sql = """
                    INSERT INTO forum_qa_pairs (
                        topic_id, sequence, date_posted,
                        question_username, question_content, question_context, pain_point, user_language,
                        response_username, response_content, response_type, solution_offered, platform_language
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    question = qa_pair.get('question', {})
                    response = qa_pair.get('response', {})
                    
                    cursor.execute(qa_sql, (
                        topic_summary['topic_id'],
                        qa_pair.get('sequence'),
                        qa_pair.get('date'),
                        question.get('username'),
                        question.get('content'),
                        question.get('context'),
                        question.get('pain_point'),
                        question.get('user_language'),
                        response.get('username'),
                        response.get('content'),
                        response.get('response_type'),
                        response.get('solution_offered'),
                        response.get('platform_language')
                    ))
                
                # Insert voice patterns
                user_patterns = analysis.get('user_voice_patterns', {})
                platform_patterns = analysis.get('platform_voice_patterns', {})
                
                # User voice patterns
                voice_sql = """
                INSERT INTO forum_voice_patterns (
                    topic_id, pattern_type, main_pain_points, common_language, 
                    expectations_vs_reality, user_workarounds, praise_points, confusion_areas
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(voice_sql, (
                    topic_summary['topic_id'],
                    'user_voice',
                    json.dumps(user_patterns.get('main_pain_points', [])),
                    json.dumps(user_patterns.get('common_language', [])),
                    json.dumps(user_patterns.get('expectations_vs_reality', [])),
                    json.dumps(user_patterns.get('user_workarounds', [])),
                    json.dumps(user_patterns.get('praise_points', [])),
                    json.dumps(user_patterns.get('confusion_areas', []))
                ))
                
                # Platform voice patterns
                platform_sql = """
                INSERT INTO forum_voice_patterns (
                    topic_id, pattern_type, explanation_style, common_solutions,
                    feature_positioning, development_transparency, methodology_mentions
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(platform_sql, (
                    topic_summary['topic_id'],
                    'platform_voice',
                    platform_patterns.get('explanation_style'),
                    json.dumps(platform_patterns.get('common_solutions', [])),
                    json.dumps(platform_patterns.get('feature_positioning', [])),
                    json.dumps(platform_patterns.get('development_transparency', [])),
                    json.dumps(platform_patterns.get('methodology_mentions', []))
                ))
                
                # Insert insights
                insights = analysis.get('key_insights', {})
                priority = analysis.get('priority_score', {})
                
                insights_sql = """
                INSERT INTO forum_insights (
                    topic_id, content_opportunities, messaging_gaps, success_indicators,
                    recurring_issues, feature_demand, recency_score, frequency_score, impact_score
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(insights_sql, (
                    topic_summary['topic_id'],
                    json.dumps(insights.get('content_opportunities', [])),
                    json.dumps(insights.get('messaging_gaps', [])),
                    json.dumps(insights.get('success_indicators', [])),
                    json.dumps(insights.get('recurring_issues', [])),
                    json.dumps(insights.get('feature_demand', [])),
                    priority.get('recency'),
                    priority.get('frequency'),
                    priority.get('impact')
                ))
                
                self.db_connection.commit()
                print(f"  ✓ Saved analysis for topic {topic_summary['topic_id']} to database")
                
        except Exception as e:
            self.db_connection.rollback()
            raise Exception(f"Failed to save analysis to database: {e}")
    
    def close_database_connection(self):
        """Close database connection."""
        if self.db_connection:
            self.db_connection.close()
            print("Database connection closed")
    
    def process_topics_with_raw_storage(self, forum_data_dir: str = None, max_topics: int = None, 
                                      start_from: int = 0, force_reanalyze: bool = False) -> Dict:
        """Process forum topics from database raw content storage."""
        
        # Setup database
        self.connect_to_database()
        self.create_database_schema()
        
        # Get topics from database instead of files
        print("Getting topics from database raw storage...")
        
        with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
            if max_topics:
                cursor.execute("""
                    SELECT topic_id, title, posts_count 
                    FROM forum_topics_raw 
                    WHERE (jsonb_array_length(COALESCE(raw_content -> 'posts', '[]'::jsonb)) > 0
                           OR jsonb_array_length(COALESCE(raw_content -> 'post_stream' -> 'posts', '[]'::jsonb)) > 0)
                    AND topic_id NOT IN (SELECT topic_id FROM forum_topics)
                    ORDER BY topic_id
                    LIMIT %s OFFSET %s
                """, (max_topics, start_from))
            else:
                cursor.execute("""
                    SELECT topic_id, title, posts_count 
                    FROM forum_topics_raw 
                    WHERE (jsonb_array_length(COALESCE(raw_content -> 'posts', '[]'::jsonb)) > 0
                           OR jsonb_array_length(COALESCE(raw_content -> 'post_stream' -> 'posts', '[]'::jsonb)) > 0)
                    AND topic_id NOT IN (SELECT topic_id FROM forum_topics)
                    ORDER BY topic_id
                """)
            
            db_topics = cursor.fetchall()
        
        topic_list = [(row['topic_id'], row['title'], row['posts_count']) for row in db_topics]
        
        print(f"Found {len(topic_list)} topics in database")
        
        if start_from > 0:
            print(f"Starting from offset {start_from}")
        
        if max_topics:
            print(f"Limited to {max_topics} topics")
        
        results = {
            "analysis_metadata": {
                "analyzed_at": datetime.now().isoformat(),
                "total_topics_processed": 0,
                "topics_stored_raw": 0,
                "topics_analyzed": 0,
                "successful_analyses": 0,
                "failed_analyses": 0,
                "unchanged_topics": 0,
                "topics_by_category": {},
                "storage_method": "database_with_raw_content",
                "failed_topics": []  # Track specific failures
            }
        }
        
        print(f"\n🔄 PROCESSING TOPICS FROM DATABASE")
        print("-" * 45)
        
        for i, (topic_id, title, posts_count) in enumerate(topic_list):
            print(f"\n[{i+1}/{len(topic_list)}] Processing Topic {topic_id}: {title[:50]}...")
            
            try:
                # Raw content is already stored, just analyze it
                # Step 1: Check if analysis already exists (for force_reanalyze logic)
                content_changed = True  # Always analyze since we're processing from raw storage
                results["analysis_metadata"]["topics_stored_raw"] += 1
                
                # Step 2: Decide if analysis is needed
                should_analyze = force_reanalyze or content_changed
                
                if not should_analyze:
                    print(f"  → Skipping analysis (no changes detected)")
                    results["analysis_metadata"]["unchanged_topics"] += 1
                else:
                    print(f"  → Running analysis (content {'changed' if content_changed else 'forced reanalysis'})")
                    
                    # Clear existing analysis if this is an update
                    if content_changed:
                        self.delete_existing_analysis(topic_id)
                    
                    # Step 3: Analyze from stored raw content
                    analysis = self.analyze_stored_topic(topic_id)
                    
                    if analysis:
                        # Step 4: Save analysis results
                        try:
                            self.save_analysis_to_database(analysis)
                            results["analysis_metadata"]["successful_analyses"] += 1
                            
                            # Track categories
                            category = analysis.get("topic_summary", {}).get("analysis_category", "Unknown")
                            results["analysis_metadata"]["topics_by_category"][category] = \
                                results["analysis_metadata"]["topics_by_category"].get(category, 0) + 1
                            
                            print(f"  ✅ SUCCESS: Complete analysis for {title[:50]}...")
                        except Exception as save_error:
                            print(f"  ❌ FAILURE: Database save error for topic {topic_id}: {save_error}")
                            results["analysis_metadata"]["failed_analyses"] += 1
                            results["analysis_metadata"]["failed_topics"].append({
                                "topic_id": topic_id,
                                "title": title,
                                "failure_reason": f"Database save error: {save_error}",
                                "failure_stage": "save_analysis"
                            })
                    else:
                        results["analysis_metadata"]["failed_analyses"] += 1
                        results["analysis_metadata"]["failed_topics"].append({
                            "topic_id": topic_id,
                            "title": title,
                            "failure_reason": "OpenAI analysis returned None - check logs above for details",
                            "failure_stage": "openai_analysis"
                        })
                        print(f"  ❌ FAILURE: Analysis failed for {title[:50]}...")
                    
                    results["analysis_metadata"]["topics_analyzed"] += 1
                
                results["analysis_metadata"]["total_topics_processed"] += 1
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"  Error processing topic {topic_id}: {e}")
                results["analysis_metadata"]["failed_analyses"] += 1
                results["analysis_metadata"]["failed_topics"].append({
                    "topic_id": topic_id,
                    "title": title,
                    "failure_reason": f"Processing error: {e}",
                    "failure_stage": "topic_processing"
                })
                continue
        
        # Close database connection
        self.close_database_connection()
        
        print(f"\n🏁 PROCESSING COMPLETE!")
        print("=" * 50)
        print(f"📊 SUMMARY:")
        print(f"  Topics processed: {results['analysis_metadata']['total_topics_processed']}")
        print(f"  Raw content stored: {results['analysis_metadata']['topics_stored_raw']}")
        print(f"  Topics analyzed: {results['analysis_metadata']['topics_analyzed']}")
        print(f"  ✅ Successful analyses: {results['analysis_metadata']['successful_analyses']}")
        print(f"  ❌ Failed analyses: {results['analysis_metadata']['failed_analyses']}")
        print(f"  ⏭️  Unchanged (skipped): {results['analysis_metadata']['unchanged_topics']}")
        print(f"  📁 Categories found: {results['analysis_metadata']['topics_by_category']}")
        
        # Show detailed failure information
        if results['analysis_metadata']['failed_analyses'] > 0:
            print(f"\n🚨 FAILURE DETAILS:")
            print("=" * 30)
            for failure in results['analysis_metadata']['failed_topics']:
                print(f"❌ Topic {failure['topic_id']}: {failure['title']}")
                print(f"   Stage: {failure['failure_stage']}")
                print(f"   Reason: {failure['failure_reason']}")
                print()
        else:
            print(f"\n🎉 ALL TOPICS PROCESSED SUCCESSFULLY - NO FAILURES!")
        
        print("=" * 50)
        
        return results

def main():
    """Main function to run the analysis."""
    
    # Configuration
    FORUM_DATA_DIR = "../forum_data"
    MAX_TOPICS = None  # Process ALL remaining topics 
    START_FROM = 0  # Will skip already analyzed ones automatically
    FORCE_REANALYZE = False  # Set to True to reanalyze all topics regardless of changes
    
    print("TrainerDay Forum Analysis Tool v2 - With Raw Content Storage")
    print("=" * 70)
    
    # Check if OpenAI API key is available
    if not os.getenv('OPENAI_API_KEY'):
        print("Please set your OpenAI API key in the .env file")
        return
    else:
        print("Using OpenAI API key from environment variable.")
    
    # Database configuration from environment variables
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('DB_SSLMODE', 'require')
    }
    
    # Add SSL certificate if specified
    if os.getenv('DB_SSLROOTCERT'):
        ssl_cert_filename = os.getenv('DB_SSLROOTCERT')
        ssl_cert_path = Path(__file__).parent.parent / ssl_cert_filename
        if ssl_cert_path.exists():
            db_config['sslrootcert'] = str(ssl_cert_path)
            print(f"Using SSL certificate: {ssl_cert_path}")
        else:
            print(f"Warning: SSL certificate file not found: {ssl_cert_path}")
    
    if not all([db_config['host'], db_config['database'], db_config['user'], db_config['password']]):
        print("Database configuration incomplete. Please check environment variables:")
        print("Required: DB_HOST, DB_DATABASE, DB_USERNAME, DB_PASSWORD")
        return
    
    try:
        # Initialize analyzer
        analyzer = ForumTopicAnalyzerV2(db_config=db_config)
        
        # Run analysis with raw content storage
        results = analyzer.process_topics_with_raw_storage(
            forum_data_dir=FORUM_DATA_DIR,
            max_topics=MAX_TOPICS,
            start_from=START_FROM,
            force_reanalyze=FORCE_REANALYZE
        )
        
        print(f"\n🎯 Results saved to PostgreSQL database!")
        print("Raw content is now stored and can be re-analyzed with different strategies!")
        
    except Exception as e:
        print(f"Error: {e}")
        return

if __name__ == "__main__":
    main()