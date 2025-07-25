#!/usr/bin/env python3
"""
Enhanced Forum Data Loader for LlamaIndex
Loads rich forum discussions from forum_topics_raw table instead of simple Q&A pairs
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from dotenv import load_dotenv

# LlamaIndex imports
from llama_index.core import Document

import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedForumLoader:
    def __init__(self):
        # Database config
        self.db_config = {
            'host': os.getenv('DB_HOST'),
            'port': int(os.getenv('DB_PORT', 25060)),
            'database': os.getenv('DB_DATABASE'),
            'user': os.getenv('DB_USERNAME'),
            'password': os.getenv('DB_PASSWORD'),
            'sslmode': os.getenv('DB_SSLMODE', 'require')
        }
        
        self.conn = None
    
    def connect_database(self):
        """Connect to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            logger.info("✅ Connected to forum database")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def clean_html_content(self, html_text: str) -> str:
        """Clean HTML tags and convert to readable text"""
        if not html_text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^<]+?>', '', html_text)
        
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
    
    def get_category_name(self, category_id: int) -> str:
        """Get category name from category_id"""
        category_map = {
            1: "General Discussion",
            35: "Technical Issues", 
            3: "Feature Requests",
            4: "Integrations & Export",
            5: "Training Theory",
            6: "Success Stories",
            7: "Getting Started",
            8: "Advanced Features"
        }
        return category_map.get(category_id, f"Category {category_id}")
    
    def determine_discussion_type(self, posts: List[Dict]) -> str:
        """Determine the type of discussion based on post patterns"""
        if not posts:
            return "empty"
        
        if len(posts) == 1:
            return "single_post"
        
        if len(posts) == 2:
            # Check if it's Alex responding to a user question
            usernames = [post.get('username', '') for post in posts]
            if 'Alex' in usernames and len(set(usernames)) == 2:
                return "simple_qa"
        
        # Multiple posts or complex interaction
        if len(posts) >= 3:
            return "multi_turn_discussion"
        
        return "general_discussion"
    
    def extract_pain_points(self, posts: List[Dict]) -> List[str]:
        """Extract user pain points from forum posts"""
        pain_indicators = [
            'problem', 'issue', 'error', 'bug', 'not working', 'failed',
            'confused', 'stuck', 'help', 'trouble', 'difficulty',
            'frustrated', 'annoying', 'broken'
        ]
        
        pain_points = []
        
        for post in posts:
            content = self.clean_html_content(post.get('cooked', '')).lower()
            username = post.get('username', '')
            
            # Skip Alex's posts when looking for pain points
            if username == 'Alex':
                continue
            
            # Look for pain indicators
            for indicator in pain_indicators:
                if indicator in content:
                    # Extract sentence containing the pain indicator
                    sentences = content.split('.')
                    for sentence in sentences:
                        if indicator in sentence:
                            pain_points.append(sentence.strip()[:100])
                            break
                    break
        
        return list(set(pain_points))  # Remove duplicates
    
    def format_discussion_content(self, topic: Dict, posts: List[Dict], 
                                 analysis_category: str) -> str:
        """Format forum discussion as readable content"""
        
        title = topic.get('title', 'Forum Discussion')
        category = self.get_category_name(topic.get('category_id', 0))
        
        content = f"Forum Discussion: {title}\n"
        content += f"Category: {category}\n"
        if analysis_category and analysis_category != category:
            content += f"Topic Type: {analysis_category}\n"
        content += f"Posts: {len(posts)}\n\n"
        
        # Add each post with username and clean content
        for i, post in enumerate(posts):
            username = post.get('username', 'Unknown')
            post_content = self.clean_html_content(post.get('cooked', ''))
            post_number = post.get('post_number', i + 1)
            
            if post_content.strip():
                content += f"Post {post_number} by {username}:\n{post_content}\n\n"
        
        return content.strip()
    
    def create_structured_qa_content(self, qa_pairs: List[Dict]) -> str:
        """Create structured Q&A content from processed pairs"""
        if not qa_pairs:
            return ""
        
        content = ""
        for i, qa in enumerate(qa_pairs):
            content += f"Q&A {i+1}:\n"
            content += f"Question: {qa.get('question_content', '')}\n"
            
            if qa.get('question_context'):
                content += f"Context: {qa.get('question_context')}\n"
            
            if qa.get('pain_point'):
                content += f"User Problem: {qa.get('pain_point')}\n"
            
            content += f"Answer: {qa.get('response_content', '')}\n"
            
            if qa.get('solution_offered'):
                content += f"Solution: {qa.get('solution_offered')}\n"
            
            content += "\n"
        
        return content.strip()
    
    def load_raw_forum_discussions(self, limit: Optional[int] = None) -> List[Document]:
        """Load forum discussions from raw topic data"""
        logger.info("Loading raw forum discussions...")
        
        if not self.conn:
            if not self.connect_database():
                return []
        
        documents = []
        
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get raw topics with their analysis categories
                query = """
                    SELECT 
                        r.topic_id,
                        r.raw_content,
                        r.title,
                        r.posts_count,
                        r.created_at_original,
                        t.analysis_category,
                        t.category
                    FROM forum_topics_raw r
                    LEFT JOIN forum_topics t ON r.topic_id = t.topic_id
                    WHERE jsonb_array_length(COALESCE(r.raw_content->'post_stream'->'posts', '[]'::jsonb)) > 0
                    ORDER BY r.created_at_original DESC
                """
                
                if limit:
                    query += f" LIMIT {limit}"
                
                cur.execute(query)
                topics = cur.fetchall()
                
                logger.info(f"Found {len(topics)} topics with post content")
                
                for topic_row in topics:
                    try:
                        topic_id = topic_row['topic_id']
                        raw_content = topic_row['raw_content']
                        analysis_category = topic_row['analysis_category'] or 'General'
                        
                        # Extract topic and posts from raw JSON
                        topic_info = raw_content
                        posts = raw_content.get('post_stream', {}).get('posts', [])
                        
                        if not posts:
                            continue
                        
                        # Create discussion content
                        content = self.format_discussion_content(
                            topic_info, posts, analysis_category
                        )
                        
                        # Extract metadata
                        participants = list(set(
                            post.get('username', '') for post in posts
                            if post.get('username', '').strip()
                        ))
                        
                        discussion_type = self.determine_discussion_type(posts)
                        pain_points = self.extract_pain_points(posts)
                        
                        # Estimate content tokens for cost tracking
                        content_tokens = len(content) // 4
                        
                        # Create document
                        doc = Document(
                            text=content,
                            metadata={
                                "source": "forum",
                                "source_id": str(topic_id),
                                "content_type": "forum_discussion",
                                "title": topic_info.get('title', ''),
                                "category": topic_row['category'] or 'General',
                                "analysis_category": analysis_category,
                                "discussion_type": discussion_type,
                                "participants": participants,
                                "participant_count": len(participants),
                                "posts_count": len(posts),
                                "has_alex_response": 'Alex' in participants,
                                "pain_points": pain_points,
                                "views": topic_info.get('views', 0),
                                "like_count": topic_info.get('like_count', 0),
                                "created_at": str(topic_row['created_at_original']) if topic_row['created_at_original'] else None,
                                "estimated_tokens": content_tokens
                            }
                        )
                        
                        documents.append(doc)
                        
                        if len(documents) % 100 == 0:
                            logger.info(f"Processed {len(documents)} forum discussions...")
                            
                    except Exception as e:
                        logger.error(f"Error processing topic {topic_row['topic_id']}: {e}")
                        continue
                
        except Exception as e:
            logger.error(f"Database error loading forum discussions: {e}")
            return []
        
        logger.info(f"✅ Loaded {len(documents)} forum discussions")
        return documents
    
    def load_structured_qa_pairs(self, limit: Optional[int] = None) -> List[Document]:
        """Load structured Q&A pairs as alternative approach"""
        logger.info("Loading structured Q&A pairs...")
        
        if not self.conn:
            if not self.connect_database():
                return []
        
        documents = []
        
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Group Q&A pairs by topic for better context
                query = """
                    SELECT 
                        qa.topic_id,
                        t.title,
                        t.analysis_category,
                        t.category,
                        array_agg(
                            json_build_object(
                                'sequence', qa.sequence,
                                'question_content', qa.question_content,
                                'question_context', qa.question_context,
                                'pain_point', qa.pain_point,
                                'user_language', qa.user_language,
                                'response_content', qa.response_content,
                                'response_type', qa.response_type,
                                'solution_offered', qa.solution_offered,
                                'platform_language', qa.platform_language
                            ) ORDER BY qa.sequence
                        ) as qa_pairs
                    FROM forum_qa_pairs qa
                    JOIN forum_topics t ON qa.topic_id = t.topic_id
                    GROUP BY qa.topic_id, t.title, t.analysis_category, t.category
                    ORDER BY qa.topic_id DESC
                """
                
                if limit:
                    query += f" LIMIT {limit}"
                
                cur.execute(query)
                topics = cur.fetchall()
                
                logger.info(f"Found {len(topics)} topics with Q&A pairs")
                
                for topic_row in topics:
                    try:
                        topic_id = topic_row['topic_id']
                        qa_pairs = topic_row['qa_pairs']
                        
                        # Create structured Q&A content
                        content = f"Forum Q&A: {topic_row['title']}\n"
                        content += f"Category: {topic_row['category'] or 'General'}\n"
                        content += f"Topic Type: {topic_row['analysis_category'] or 'General'}\n\n"
                        content += self.create_structured_qa_content(qa_pairs)
                        
                        # Extract metadata
                        pain_points = [qa.get('pain_point') for qa in qa_pairs if qa.get('pain_point')]
                        response_types = [qa.get('response_type') for qa in qa_pairs if qa.get('response_type')]
                        
                        content_tokens = len(content) // 4
                        
                        # Create document
                        doc = Document(
                            text=content,
                            metadata={
                                "source": "forum",
                                "source_id": str(topic_id),
                                "content_type": "forum_qa_structured",
                                "title": topic_row['title'],
                                "category": topic_row['category'] or 'General',
                                "analysis_category": topic_row['analysis_category'] or 'General',
                                "qa_pairs_count": len(qa_pairs),
                                "pain_points": pain_points,
                                "response_types": response_types,
                                "has_solutions": any(qa.get('solution_offered') for qa in qa_pairs),
                                "estimated_tokens": content_tokens
                            }
                        )
                        
                        documents.append(doc)
                        
                        if len(documents) % 100 == 0:
                            logger.info(f"Processed {len(documents)} Q&A topics...")
                            
                    except Exception as e:
                        logger.error(f"Error processing Q&A topic {topic_row['topic_id']}: {e}")
                        continue
                
        except Exception as e:
            logger.error(f"Database error loading Q&A pairs: {e}")
            return []
        
        logger.info(f"✅ Loaded {len(documents)} structured Q&A topics")
        return documents
    
    def get_forum_statistics(self) -> Dict[str, Any]:
        """Get statistics about available forum data"""
        if not self.conn:
            if not self.connect_database():
                return {}
        
        stats = {}
        
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Raw topics stats
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_topics,
                        AVG(posts_count) as avg_posts_per_topic,
                        SUM(posts_count) as total_posts,
                        COUNT(CASE WHEN posts_count >= 3 THEN 1 END) as rich_discussions
                    FROM forum_topics_raw
                """)
                raw_stats = cur.fetchone()
                stats['raw_topics'] = dict(raw_stats)
                
                # Q&A pairs stats
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_qa_pairs,
                        COUNT(DISTINCT topic_id) as topics_with_qa
                    FROM forum_qa_pairs
                """)
                qa_stats = cur.fetchone()
                stats['qa_pairs'] = dict(qa_stats)
                
                # Category distribution
                cur.execute("""
                    SELECT 
                        analysis_category,
                        COUNT(*) as count
                    FROM forum_topics
                    GROUP BY analysis_category
                    ORDER BY count DESC
                """)
                categories = cur.fetchall()
                stats['categories'] = {row['analysis_category']: row['count'] for row in categories}
                
        except Exception as e:
            logger.error(f"Error getting forum statistics: {e}")
        
        return stats
    
    def close_connection(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

def compare_loading_approaches():
    """Compare different forum loading approaches"""
    print("🔍 COMPARING FORUM LOADING APPROACHES")
    print("=" * 50)
    
    loader = EnhancedForumLoader()
    
    # Get statistics
    stats = loader.get_forum_statistics()
    print(f"📊 FORUM DATA STATISTICS:")
    print(f"  Raw topics: {stats.get('raw_topics', {}).get('total_topics', 0):,}")
    print(f"  Total posts: {stats.get('raw_topics', {}).get('total_posts', 0):,}")
    print(f"  Rich discussions (3+ posts): {stats.get('raw_topics', {}).get('rich_discussions', 0):,}")
    print(f"  Structured Q&A pairs: {stats.get('qa_pairs', {}).get('total_qa_pairs', 0):,}")
    print(f"  Topics with Q&A: {stats.get('qa_pairs', {}).get('topics_with_qa', 0):,}")
    
    print(f"\n📈 CATEGORY DISTRIBUTION:")
    categories = stats.get('categories', {})
    for category, count in categories.items():
        print(f"  {category}: {count}")
    
    # Load sample data with both approaches
    print(f"\n🔄 LOADING SAMPLE DATA (10 topics each approach)...")
    
    # Approach 1: Raw discussions
    raw_docs = loader.load_raw_forum_discussions(limit=10)
    print(f"\n📖 RAW DISCUSSIONS APPROACH:")
    print(f"  Documents created: {len(raw_docs)}")
    
    if raw_docs:
        sample_doc = raw_docs[0]
        print(f"  Sample title: {sample_doc.metadata.get('title', 'N/A')}")
        print(f"  Content length: {len(sample_doc.text)} chars")
        print(f"  Participants: {sample_doc.metadata.get('participants', [])}")
        print(f"  Discussion type: {sample_doc.metadata.get('discussion_type', 'N/A')}")
        print(f"  Content preview: {sample_doc.text[:200]}...")
    
    # Approach 2: Structured Q&A
    qa_docs = loader.load_structured_qa_pairs(limit=10)
    print(f"\n❓ STRUCTURED Q&A APPROACH:")
    print(f"  Documents created: {len(qa_docs)}")
    
    if qa_docs:
        sample_doc = qa_docs[0]
        print(f"  Sample title: {sample_doc.metadata.get('title', 'N/A')}")
        print(f"  Content length: {len(sample_doc.text)} chars")
        print(f"  Q&A pairs: {sample_doc.metadata.get('qa_pairs_count', 0)}")
        print(f"  Has solutions: {sample_doc.metadata.get('has_solutions', False)}")
        print(f"  Content preview: {sample_doc.text[:200]}...")
    
    loader.close_connection()
    
    print(f"\n💡 RECOMMENDATIONS:")
    print(f"  1. Use RAW DISCUSSIONS for richer context and natural conversations")
    print(f"  2. Use STRUCTURED Q&A for more focused, solution-oriented content")
    print(f"  3. Consider hybrid approach: structured for simple Q&A, raw for complex discussions")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "compare":
        compare_loading_approaches()
    else:
        # Demo loading
        loader = EnhancedForumLoader()
        
        print("Loading forum discussions...")
        docs = loader.load_raw_forum_discussions(limit=5)
        
        print(f"\nLoaded {len(docs)} documents")
        for doc in docs[:2]:
            print(f"\n--- {doc.metadata.get('title', 'Untitled')} ---")
            print(f"Category: {doc.metadata.get('analysis_category', 'N/A')}")
            print(f"Participants: {doc.metadata.get('participants', [])}")
            print(f"Content preview: {doc.text[:300]}...")
        
        loader.close_connection()