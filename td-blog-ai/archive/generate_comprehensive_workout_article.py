#!/usr/bin/env python3
"""
Generate comprehensive workout article from all queried content
"""

import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

class ComprehensiveWorkoutArticleGenerator:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'trainerday_local',
            'user': os.getenv('USER', 'alex'),
            'password': '',
        }
        
        # Load the comprehensive query results
        results_file = Path("./script-testing/workout_comprehensive_results/all_workout_features_20250725_200223.json")
        with open(results_file, 'r', encoding='utf-8') as f:
            self.all_results = json.load(f)
    
    def get_full_content(self, text_snippet, source_type):
        """Get full content from database for blog articles"""
        if source_type != 'blog' or len(text_snippet) < 100:
            return text_snippet
            
        conn = psycopg2.connect(**self.db_config)
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Try to find the full blog article
                cur.execute("""
                    SELECT text
                    FROM llamaindex_knowledge_base
                    WHERE metadata_->>'source' = 'blog'
                    AND text LIKE %s
                    ORDER BY LENGTH(text) DESC
                    LIMIT 1
                """, (f"{text_snippet[:100]}%",))
                
                result = cur.fetchone()
                if result:
                    return result['text']
        finally:
            conn.close()
        
        return text_snippet
    
    def organize_content_by_category(self):
        """Organize all content by category and feature"""
        organized = {}
        
        for category, features in self.all_results.items():
            organized[category] = {}
            
            for feature_name, results in features.items():
                # Group by source type
                by_source = {
                    'blog': [],
                    'youtube': [],
                    'facts': [],
                    'forum': []
                }
                
                for result in results:
                    source = result['source']
                    if source in by_source:
                        # Get full content for blog articles
                        if source == 'blog':
                            full_text = self.get_full_content(result['text'], source)
                            result['full_text'] = full_text
                        by_source[source].append(result)
                
                organized[category][feature_name] = by_source
        
        return organized
    
    def extract_key_content(self, organized_content):
        """Extract the most important content for the article"""
        key_content = {}
        
        # Priority features to highlight
        priority_features = [
            "Fastest Workout Editor",
            "Visual Workout Editor", 
            "Sets and Reps Editor",
            "Interval Comments",
            "W'bal Integration",
            "Training Modes",
            "Garmin Connect",
            "TrainingPeaks",
            "Community Workout Library"
        ]
        
        for category, features in organized_content.items():
            for feature_name, sources in features.items():
                if any(pf in feature_name for pf in priority_features):
                    key_content[feature_name] = {
                        'blog': sources.get('blog', [])[:2],  # Top 2 blog articles
                        'facts': sources.get('facts', [])[:5],  # Top 5 facts
                        'forum': sources.get('forum', [])[:3],  # Top 3 forum discussions
                        'youtube': sources.get('youtube', [])[:2]  # Top 2 videos
                    }
        
        return key_content
    
    def generate_article_sections(self, organized_content):
        """Generate article sections from organized content"""
        
        sections = []
        
        # Introduction section
        sections.append({
            'title': 'Introduction',
            'content': """TrainerDay offers one of the most comprehensive workout creation and management systems in the indoor cycling world. With over 30,000 open-source workouts and a feature-rich editor designed for speed, our platform empowers cyclists to create, customize, and execute training plans with unprecedented flexibility."""
        })
        
        # Generate sections for each category
        for category, features in organized_content.items():
            category_content = f"\n## {category}\n\n"
            
            for feature_name, sources in features.items():
                feature_content = f"\n### {feature_name}\n\n"
                
                # Add blog content if available
                if sources['blog']:
                    for blog in sources['blog'][:1]:  # First blog article
                        if 'full_text' in blog:
                            # Extract key parts from blog
                            text = blog['full_text']
                            if "Designed for one thing. Speed." in text:
                                feature_content += "**Designed for one thing. Speed.** That's the philosophy behind our workout editor. "
                                feature_content += "It works just like Excel with copy and paste and arrow keys for moving. "
                                feature_content += "This Excel-like functionality makes creating workouts incredibly fast and intuitive.\n\n"
                            elif "Sets and Reps" in text and "hard workout" in text:
                                feature_content += "The Sets and Reps editor transforms complex interval workouts into manageable structures. "
                                feature_content += "What would be an endless scrolling list in a standard editor becomes a concise, easy-to-visualize format.\n\n"
                
                # Add facts
                if sources['facts']:
                    facts_text = "**Key Features:**\n"
                    for fact in sources['facts'][:3]:
                        fact_text = fact['text'].replace('Fact: ', '').strip()
                        facts_text += f"- {fact_text}\n"
                    feature_content += facts_text + "\n"
                
                # Add user insights from forums
                if sources['forum']:
                    user_insights = self.extract_user_insights(sources['forum'][:2])
                    if user_insights:
                        feature_content += f"**User Insights:** {user_insights}\n\n"
                
                category_content += feature_content
            
            sections.append({
                'title': category,
                'content': category_content
            })
        
        return sections
    
    def extract_user_insights(self, forum_posts):
        """Extract key insights from forum discussions"""
        insights = []
        
        for post in forum_posts:
            text = post['text']
            if "Question:" in text and "Answer:" in text:
                # Extract Q&A insights
                q_start = text.find("Question:") + 9
                q_end = text.find("\n", q_start)
                if q_end > q_start:
                    question = text[q_start:q_end].strip()
                    if len(question) < 200:
                        insights.append(f"Users ask: \"{question}\"")
        
        return " ".join(insights[:1]) if insights else ""
    
    def generate_comprehensive_article(self):
        """Generate the complete article using all content"""
        
        print("📚 Organizing content by category...")
        organized_content = self.organize_content_by_category()
        
        print("🔍 Extracting key content...")
        key_content = self.extract_key_content(organized_content)
        
        # Build the article prompt
        prompt = self.build_article_prompt(organized_content, key_content)
        
        print("🤖 Generating comprehensive article...")
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are Alex, founder of TrainerDay, writing a comprehensive guide about workout features. Use the provided content to create a detailed, informative article. Be thorough and comprehensive, using specific examples and quotes from the content provided."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4096
        )
        
        article = response.choices[0].message.content
        
        # Save the article
        output_dir = Path("./script-testing/workout_articles")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f"comprehensive_workout_features_{timestamp}.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(article)
        
        print(f"\n✅ Article saved to: {output_file}")
        print(f"📄 Article length: {len(article)} characters")
        print(f"📝 Word count: {len(article.split())} words")
        
        return output_file
    
    def build_article_prompt(self, organized_content, key_content):
        """Build the comprehensive prompt for article generation"""
        
        # Collect specific content examples
        content_examples = []
        
        # Get the Fastest Workout Editor blog content
        for feature, sources in key_content.items():
            if "Fastest Workout Editor" in feature and sources['blog']:
                for blog in sources['blog']:
                    if 'full_text' in blog:
                        content_examples.append(f"FASTEST WORKOUT EDITOR BLOG:\n{blog['full_text'][:2000]}")
                        break
        
        # Get Sets and Reps content
        for feature, sources in key_content.items():
            if "Sets and Reps" in feature and sources['blog']:
                for blog in sources['blog']:
                    if 'full_text' in blog:
                        content_examples.append(f"\nSETS AND REPS BLOG:\n{blog['full_text'][:1500]}")
                        break
        
        # Get W'bal content
        for feature, sources in key_content.items():
            if "W'bal" in feature and sources['blog']:
                for blog in sources['blog']:
                    if 'full_text' in blog:
                        content_examples.append(f"\nW'BAL BLOG:\n{blog['full_text'][:1500]}")
                        break
        
        # Get Forum insights
        forum_examples = []
        for category, features in organized_content.items():
            for feature, sources in features.items():
                for forum in sources['forum'][:3]:
                    if "Question:" in forum['text'] and "Answer:" in forum['text']:
                        forum_examples.append(f"FORUM Q&A - {feature}:\n{forum['text'][:500]}")
        
        if forum_examples:
            content_examples.append(f"\nUSER QUESTIONS FROM FORUMS:\n{chr(10).join(forum_examples[:5])}")
        
        # Collect all facts
        all_facts = []
        for category, features in organized_content.items():
            for feature, sources in features.items():
                for fact in sources['facts']:
                    all_facts.append(fact['text'])
        
        # Build stats summary
        total_features = sum(len(features) for features in organized_content.values())
        
        prompt = f"""Write a comprehensive guide about TrainerDay's workout creation and management features.

CONTENT STATISTICS:
- {total_features} total features documented
- 854 content pieces from our knowledge base
- Content includes blog articles, video transcripts, user discussions, and verified facts

KEY CONTENT TO INCLUDE:

{chr(10).join(content_examples[:3])}

ALL FACTS ABOUT FEATURES ({len(all_facts)} total):
{chr(10).join(all_facts[:50])}

ARTICLE REQUIREMENTS:
1. Write as Alex (first person) in a conversational but informative tone
2. Target length: 4000-5000 words (be comprehensive and thorough)
3. Include specific quotes from the blog content provided
4. Organize by major categories: Workout Creation & Management, Training Modes, Training Execution, Display & Monitoring, Workout Library, Export & Integration
5. For each feature, explain what it does and why it matters
6. Include practical examples and use cases
7. Reference actual user questions and experiences from the forum content
8. Highlight the "Designed for one thing. Speed." philosophy
9. Explain technical features in accessible terms

STRUCTURE:
1. Introduction (200 words) - Philosophy and overview
2. Workout Creation & Management (800 words) - Core editor features
3. Training Modes (600 words) - ERG, Slope, HR+, Resistance
4. Real-time Training Features (600 words) - Dynamic adjustments and execution
5. Workout Library & Discovery (500 words) - 30,000+ workouts
6. Export & Platform Integration (600 words) - Multi-platform support
7. Advanced Features (500 words) - W'bal, route importing, etc.
8. Conclusion (200 words) - Getting started and support

Use direct quotes and specific examples from the content provided. Make this the definitive guide to TrainerDay workout features."""
        
        return prompt

if __name__ == "__main__":
    generator = ComprehensiveWorkoutArticleGenerator()
    generator.generate_comprehensive_article()