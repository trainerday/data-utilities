#!/usr/bin/env python3
"""
Content Strategy Pipeline: Forum Q&A → Feature Analysis → Strategic Article Generation

This script:
1. Extracts Q&A from forum PostgreSQL database
2. Analyzes existing blog articles 
3. Identifies content gaps using Basic Memory strategy docs
4. Generates prioritized article list
5. Creates minimalistic articles via OpenAI
"""

import os
import json
import psycopg2
from pathlib import Path
import yaml
import openai
from datetime import datetime
import re
from collections import defaultdict, Counter

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Paths
TD_BUSINESS_PATH = "/Users/alex/Documents/bm-projects/TD-Business"
SCRIPT_DIR = Path(__file__).parent

class ContentStrategyPipeline:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.db_config = {
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_DATABASE'),
            'user': os.getenv('DB_USERNAME'),
            'password': os.getenv('DB_PASSWORD'),
            'sslmode': os.getenv('DB_SSLMODE'),
            'sslrootcert': os.getenv('DB_SSLROOTCERT')
        }
        self.spec = self.load_specification()
        
    def load_specification(self):
        """Load categories/engagement/tags specification."""
        spec_path = Path(TD_BUSINESS_PATH) / "blog" / "tags-and-categories.md"
        with open(spec_path, 'r') as f:
            content = f.read()
        
        json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
        return json.loads(json_match.group(1))
    
    def extract_forum_qa(self, limit=500):
        """Extract Q&A pairs from forum database."""
        print("📊 Extracting Q&A from forum database...")
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # First, let's check what tables exist
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE '%forum%'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            print(f"   📋 Available forum tables: {tables}")
            
            # Get raw forum content from forum_topics_raw
            if 'forum_topics_raw' in tables:
                query = """
                SELECT 
                    topic_id,
                    title,
                    raw_content,
                    posts_count,
                    scraped_at
                FROM forum_topics_raw
                WHERE raw_content IS NOT NULL
                ORDER BY topic_id DESC
                LIMIT %s
                """
                
                cursor.execute(query, (limit,))
                results = cursor.fetchall()
                
                qa_pairs = []
                for row in results:
                    # Extract Q&A from raw content
                    topic_data = self.extract_qa_from_raw_content(row[2])  # raw_content is JSON
                    if topic_data:
                        qa_pairs.append({
                            'topic_id': row[0],
                            'title': row[1] or f"Topic {row[0]}",
                            'category': 'forum',
                            'question': topic_data.get('question', ''),
                            'answer': topic_data.get('answer', ''),
                            'user_language': topic_data.get('user_language', ''),
                            'platform_response': topic_data.get('platform_response', ''),
                            'content_opportunity': topic_data.get('content_opportunity', ''),
                            'priority_score': topic_data.get('priority_score', 1.0)
                        })
            else:
                print("   ❌ No forum_topics_raw table found")
                return []
            
            
            cursor.close()
            conn.close()
            
            print(f"   ✅ Extracted {len(qa_pairs)} Q&A pairs")
            return qa_pairs
            
        except Exception as e:
            print(f"   ❌ Database error: {e}")
            return []
    
    def extract_qa_from_raw_content(self, raw_content):
        """Extract Q&A information from raw forum content JSON."""
        try:
            import json
            if isinstance(raw_content, str):
                content_data = json.loads(raw_content)
            else:
                content_data = raw_content
            
            # Extract title and posts
            title = content_data.get('title', '')
            posts = content_data.get('post_stream', {}).get('posts', [])
            
            if not posts:
                return None
            
            # First post is usually the question
            first_post = posts[0]
            question = first_post.get('cooked', '')  # HTML content
            
            # Look for responses (posts by different users or staff)
            answer = ''
            for post in posts[1:]:  # Skip first post
                if post.get('staff', False) or post.get('username', '').lower() == 'alex':
                    answer = post.get('cooked', '')
                    break
            
            if not question:
                return None
            
            # Clean HTML tags for question/answer
            import re
            question_clean = re.sub('<.*?>', '', question).strip()
            answer_clean = re.sub('<.*?>', '', answer).strip() if answer else ''
            
            return {
                'question': question_clean[:500],  # Limit length
                'answer': answer_clean[:500],
                'user_language': question_clean,
                'platform_response': answer_clean,
                'content_opportunity': f"Article needed: {title}",
                'priority_score': min(len(posts), 10) / 10.0  # More posts = higher priority
            }
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            return None
    
    def analyze_existing_articles(self):
        """Analyze existing blog articles to identify coverage."""
        print("📚 Analyzing existing blog articles...")
        
        articles_path = Path(TD_BUSINESS_PATH) / "blog" / "articles"
        article_files = list(articles_path.glob("*.md"))
        
        coverage = {
            'categories': defaultdict(list),
            'engagement': defaultdict(list),
            'tags': defaultdict(list),
            'topics': []
        }
        
        for article_file in article_files:
            with open(article_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract frontmatter
            if content.startswith('---'):
                end_match = re.search(r'\n---\n', content)
                if end_match:
                    frontmatter_raw = content[3:end_match.start()]
                    try:
                        frontmatter = yaml.safe_load(frontmatter_raw)
                        
                        # Categorize existing content
                        if frontmatter:
                            category = frontmatter.get('category')
                            engagement = frontmatter.get('engagement') 
                            tags = frontmatter.get('tags', [])
                            title = frontmatter.get('title', article_file.stem)
                            
                            if category:
                                coverage['categories'][category].append(title)
                            if engagement:
                                coverage['engagement'][engagement].append(title)
                            for tag in tags:
                                coverage['tags'][tag].append(title)
                            
                            coverage['topics'].append({
                                'title': title,
                                'category': category,
                                'engagement': engagement,
                                'tags': tags,
                                'file': article_file.name
                            })
                    
                    except yaml.YAMLError:
                        continue
        
        print(f"   ✅ Analyzed {len(coverage['topics'])} articles")
        return coverage
    
    def identify_content_gaps(self, qa_pairs, existing_coverage):
        """Identify content gaps using forum data and existing coverage."""
        print("🔍 Identifying content gaps...")
        
        # Analyze Q&A topics vs existing articles
        qa_topics = defaultdict(list)
        user_pain_points = Counter()
        requested_features = Counter()
        
        for qa in qa_pairs:
            # Categorize Q&A by inferred topic
            topic_keywords = self.extract_topic_keywords(qa['question'])
            
            for keyword in topic_keywords:
                qa_topics[keyword].append(qa)
            
            # Track pain points
            if any(word in qa['question'].lower() for word in ['problem', 'issue', 'error', 'not working', 'help']):
                user_pain_points[topic_keywords[0] if topic_keywords else 'general'] += 1
            
            # Track feature requests  
            if any(word in qa['question'].lower() for word in ['how to', 'can i', 'is it possible', 'feature']):
                requested_features[topic_keywords[0] if topic_keywords else 'general'] += 1
        
        # Find gaps
        gaps = {
            'missing_topics': [],
            'underserved_engagement': defaultdict(list),
            'high_demand_topics': [],
            'pain_point_topics': []
        }
        
        # Topics with high Q&A volume but no articles
        existing_topics = {article['title'].lower() for article in existing_coverage['topics']}
        
        for topic, qas in qa_topics.items():
            if len(qas) >= 3:  # High volume topics
                # Check if we have articles covering this topic
                topic_covered = any(topic.lower() in existing_title for existing_title in existing_topics)
                
                if not topic_covered:
                    gaps['missing_topics'].append({
                        'topic': topic,
                        'qa_count': len(qas),
                        'sample_questions': [qa['question'] for qa in qas[:3]],
                        'priority_score': sum(qa['priority_score'] for qa in qas) / len(qas)
                    })
        
        # High pain point topics
        for topic, count in user_pain_points.most_common(10):
            gaps['pain_point_topics'].append({
                'topic': topic,
                'pain_point_count': count,
                'sample_qas': qa_topics[topic][:3]
            })
        
        print(f"   ✅ Found {len(gaps['missing_topics'])} missing topics")
        print(f"   ✅ Found {len(gaps['pain_point_topics'])} high pain-point topics")
        
        return gaps
    
    def extract_topic_keywords(self, text):
        """Extract topic keywords from question text."""
        # Common TrainerDay topics
        topic_patterns = {
            'garmin': r'\b(garmin|connect|edge|watch)\b',
            'zwift': r'\b(zwift|virtual|game)\b',
            'coach-jack': r'\b(coach\s*jack|plan|training\s*plan)\b',
            'power-zones': r'\b(power|zone|ftp|threshold)\b',
            'heart-rate': r'\b(heart\s*rate|hr|bpm)\b',
            'mobile-app': r'\b(app|mobile|phone|ios|android)\b',
            'workout-creator': r'\b(workout|create|editor|interval)\b',
            'sync': r'\b(sync|export|send|upload)\b',
            'trainer': r'\b(trainer|smart|erg|resistance)\b',
            'setup': r'\b(setup|install|connect|pairing)\b'
        }
        
        keywords = []
        text_lower = text.lower()
        
        for topic, pattern in topic_patterns.items():
            if re.search(pattern, text_lower):
                keywords.append(topic)
        
        return keywords if keywords else ['general']
    
    def generate_article_plan(self, gaps, qa_pairs, existing_coverage):
        """Generate prioritized list of articles to create."""
        print("📝 Generating article creation plan...")
        
        article_plan = []
        
        # Prioritize missing topics
        for gap in sorted(gaps['missing_topics'], key=lambda x: x['priority_score'], reverse=True):
            topic = gap['topic']
            
            # Get relevant Q&As for this topic
            relevant_qas = [qa for qa in qa_pairs if topic in self.extract_topic_keywords(qa['question'])]
            
            # Determine best category and engagement level
            category = self.infer_category(topic, relevant_qas)
            engagement_levels = self.infer_engagement_levels(topic, relevant_qas)
            
            for engagement in engagement_levels:
                article_plan.append({
                    'priority': len(relevant_qas) * gap['priority_score'],
                    'topic': topic,
                    'title': self.generate_title(topic, engagement),
                    'category': category,
                    'engagement': engagement,
                    'tags': self.infer_tags(topic),
                    'source_qas': relevant_qas[:5],  # Top 5 relevant Q&As
                    'sample_questions': gap['sample_questions'],
                    'content_type': 'gap_fill'
                })
        
        # Sort by priority
        article_plan.sort(key=lambda x: x['priority'], reverse=True)
        
        print(f"   ✅ Generated plan for {len(article_plan)} articles")
        return article_plan[:20]  # Top 20 priorities
    
    def infer_category(self, topic, qas):
        """Infer the best category for a topic."""
        category_keywords = {
            'Training': ['power', 'zone', 'ftp', 'heart-rate', 'training', 'plan'],
            'Features': ['coach-jack', 'workout-creator', 'mobile-app', 'sync', 'export'],
            'Indoor': ['trainer', 'setup', 'connect', 'device', 'pairing'],
            'Other': ['compare', 'review', 'vs']
        }
        
        topic_lower = topic.lower()
        for category, keywords in category_keywords.items():
            if any(keyword in topic_lower for keyword in keywords):
                return category
        
        return 'Features'  # Default
    
    def infer_engagement_levels(self, topic, qas):
        """Determine which engagement levels are needed for this topic."""
        # Simple heuristic: most topics need Complete, complex topics need Geek-Out, simple setup needs Quick
        if topic in ['setup', 'connect', 'pairing']:
            return ['Quick']
        elif topic in ['power-zones', 'ftp', 'training']:
            return ['Complete', 'Geek-Out']
        else:
            return ['Complete']
    
    def infer_tags(self, topic):
        """Infer appropriate tags for a topic."""
        topic_to_tags = {
            'garmin': ['garmin', 'export', 'integrations'],
            'zwift': ['zwift', 'export', 'virtual'],
            'coach-jack': ['coach-jack', 'plan-creator', 'training'],
            'power-zones': ['training', 'ftp', 'power-zones'],
            'heart-rate': ['heart-rate', 'training'],
            'mobile-app': ['mobile-app', 'training'],
            'workout-creator': ['workout-creator', 'my-workouts'],
            'sync': ['export', 'integrations'],
            'trainer': ['equipment', 'indoor-cycling'],
            'setup': ['equipment', 'technology']
        }
        
        return topic_to_tags.get(topic, ['training'])
    
    def generate_title(self, topic, engagement):
        """Generate article title based on topic and engagement level."""
        title_templates = {
            'Quick': {
                'garmin': "Sync TrainerDay to Garmin in 3 Steps",
                'zwift': "Export TrainerDay Workouts to Zwift - Quick Guide",
                'setup': "Smart Trainer Setup - Quick Start",
                'mobile-app': "TrainerDay Mobile App - Getting Started"
            },
            'Complete': {
                'garmin': "Complete Guide to TrainerDay Garmin Integration",
                'zwift': "TrainerDay + Zwift: The Complete Workflow",
                'power-zones': "Master Power Zone Training with TrainerDay",
                'coach-jack': "Coach Jack AI Training Plans - Complete Guide"
            },
            'Geek-Out': {
                'power-zones': "Advanced Power Analysis and Zone Optimization",
                'ftp': "FTP Testing Science and Advanced Protocols", 
                'training': "Training Load Science and Periodization Theory"
            }
        }
        
        if engagement in title_templates and topic in title_templates[engagement]:
            return title_templates[engagement][topic]
        
        # Fallback title generation
        engagement_prefixes = {
            'Quick': "Quick Guide:",
            'Complete': "Complete Guide to",
            'Geek-Out': "Advanced"
        }
        
        return f"{engagement_prefixes[engagement]} {topic.replace('-', ' ').title()}"
    
    def create_minimal_article(self, article_plan_item):
        """Create minimal article using OpenAI."""
        print(f"✍️  Generating article: {article_plan_item['title']}")
        
        # Prepare context from Q&As
        qa_context = "\n\n".join([
            f"Q: {qa['question']}\nA: {qa['answer']}" 
            for qa in article_plan_item['source_qas']
        ])
        
        prompt = f"""Create a {article_plan_item['engagement'].lower()} TrainerDay blog article.

Title: {article_plan_item['title']}
Category: {article_plan_item['category']}
Engagement Level: {article_plan_item['engagement']}

Based on these real user questions and answers from the TrainerDay forum:

{qa_context}

Requirements:
- {article_plan_item['engagement']} engagement level:
  * Quick: 600-800 words, actionable steps, minimal theory
  * Complete: 1000-1200 words, full explanation, practical examples
  * Geek-Out: 1400+ words, technical depth, advanced concepts
- Address the user pain points and questions from the forum
- Use TrainerDay-specific terminology and features
- Include clear step-by-step instructions where appropriate
- Match the tone of existing TrainerDay content (helpful, expert, practical)

Write the article in markdown format with proper frontmatter:
---
title: "{article_plan_item['title']}"
date: {datetime.now().strftime('%Y-%m-%d')}
category: {article_plan_item['category']}
engagement: {article_plan_item['engagement']}
tags:
{chr(10).join(f'  - {tag}' for tag in article_plan_item['tags'])}
excerpt: [Write a compelling 1-sentence excerpt]
---

[Article content here]"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a TrainerDay content expert creating educational blog articles for cyclists and indoor training enthusiasts."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"   ❌ OpenAI error: {e}")
            return None
    
    def save_article_plan(self, article_plan):
        """Save the article creation plan."""
        output_file = SCRIPT_DIR / f"article_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w') as f:
            json.dump(article_plan, f, indent=2, default=str)
        
        print(f"📋 Saved article plan to: {output_file}")
        return output_file
    
    def run_pipeline(self):
        """Run the complete content strategy pipeline."""
        print("🚀 Starting Content Strategy Pipeline")
        print("="*50)
        
        # Step 1: Extract forum data
        qa_pairs = self.extract_forum_qa(limit=500)
        
        # Step 2: Analyze existing articles
        existing_coverage = self.analyze_existing_articles()
        
        # Step 3: Identify gaps
        gaps = self.identify_content_gaps(qa_pairs, existing_coverage)
        
        # Step 4: Generate article plan
        article_plan = self.generate_article_plan(gaps, qa_pairs, existing_coverage)
        
        # Step 5: Save plan
        plan_file = self.save_article_plan(article_plan)
        
        # Step 6: Generate sample articles (first 3)
        print(f"\n✍️  Generating sample articles...")
        sample_articles = []
        
        for i, article in enumerate(article_plan[:3]):
            content = self.create_minimal_article(article)
            if content:
                article_file = SCRIPT_DIR / f"sample_article_{i+1}_{article['topic']}.md"
                with open(article_file, 'w') as f:
                    f.write(content)
                sample_articles.append(article_file)
                print(f"   ✅ Saved: {article_file.name}")
        
        print(f"\n{'='*50}")
        print("🎉 Content Strategy Pipeline Complete!")
        print(f"📊 Generated plan for {len(article_plan)} priority articles")
        print(f"📝 Created {len(sample_articles)} sample articles")
        print(f"📋 Full plan saved to: {plan_file.name}")
        
        return article_plan, sample_articles

if __name__ == "__main__":
    pipeline = ContentStrategyPipeline()
    pipeline.run_pipeline()