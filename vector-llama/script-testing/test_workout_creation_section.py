#!/usr/bin/env python3
"""
Test script to create Workout Creation & Management section using ONLY actual content from LlamaIndex
"""

import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from llama_index.embeddings.openai import OpenAIEmbedding

load_dotenv()

class WorkoutCreationArticle:
    def __init__(self):
        self.embedding_model = OpenAIEmbedding(
            model="text-embedding-3-large",
            dimensions=1536
        )
        
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'trainerday_local',
            'user': os.getenv('USER', 'alex'),
            'password': '',
        }
        
        # Workout creation queries from workouts.md
        self.creation_queries = {
            "Visual Workout Editor": [
                '"workout editor"',
                '"visual workout builder"', 
                '"drag-and-drop"',
                '"drag and drop"'
            ],
            "Fastest Workout Editor": [
                '"fastest workout editor"',
                '"copy paste" AND workout',
                '"keyboard shortcuts" AND workout'
            ],
            "Sets and Reps Editor": [
                '"sets and reps"',
                '"interval structure"',
                '"complex intervals"'
            ],
            "Interval Comments": [
                '"interval comments"',
                '"coaching notes"',
                '"workout instructions"'
            ],
            "Workout Cloning": [
                '"workout cloning"',
                '"duplicate workouts"',
                '"ALT drag"',
                '"clone workout"'
            ]
        }
        
    def query_feature_content(self, feature_name, queries):
        """Query LlamaIndex for actual content about a feature"""
        
        conn = psycopg2.connect(**self.db_config)
        all_results = []
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                for query in queries:
                    # Get embedding
                    query_embedding = self.embedding_model.get_text_embedding(query)
                    
                    # Query with priority thresholds
                    cur.execute("""
                        WITH ranked_results AS (
                            SELECT 
                                text,
                                metadata_->>'title' as title,
                                metadata_->>'source' as source,
                                metadata_->>'priority' as priority,
                                metadata_->>'content_type' as content_type,
                                embedding <=> %s::vector as distance
                            FROM llamaindex_knowledge_base 
                            WHERE embedding IS NOT NULL
                            AND (
                                (metadata_->>'source' = 'facts' AND embedding <=> %s::vector <= 0.2) OR
                                (metadata_->>'source' IN ('blog', 'youtube') AND embedding <=> %s::vector <= 0.3) OR
                                (metadata_->>'source' = 'forum' AND metadata_->>'content_type' LIKE '%%qa%%' AND embedding <=> %s::vector <= 0.4) OR
                                (metadata_->>'source' = 'forum' AND embedding <=> %s::vector <= 0.6)
                            )
                        )
                        SELECT * FROM ranked_results
                        ORDER BY distance
                        LIMIT 5
                    """, (query_embedding, query_embedding, query_embedding, query_embedding, query_embedding))
                    
                    results = cur.fetchall()
                    if results:
                        all_results.extend(results)
                        
        finally:
            conn.close()
            
        # Deduplicate by text similarity
        unique_results = []
        seen_texts = set()
        
        for result in all_results:
            text_key = result['text'][:200]  # First 200 chars as key
            if text_key not in seen_texts:
                seen_texts.add(text_key)
                unique_results.append(result)
        
        return unique_results
    
    def extract_relevant_content(self, results, feature_name):
        """Extract only the relevant parts of the content"""
        
        relevant_content = {
            'facts': [],
            'blog': [],
            'youtube': [],
            'forum_qa': [],
            'forum_discussion': []
        }
        
        for result in results:
            source = result['source']
            content = {
                'text': result['text'],
                'title': result['title'],
                'score': result['distance']
            }
            
            if source == 'facts':
                relevant_content['facts'].append(content)
            elif source == 'blog':
                relevant_content['blog'].append(content)
            elif source == 'youtube':
                relevant_content['youtube'].append(content)
            elif source == 'forum':
                if 'qa' in result['content_type']:
                    relevant_content['forum_qa'].append(content)
                else:
                    relevant_content['forum_discussion'].append(content)
        
        return relevant_content
    
    def generate_section(self):
        """Generate the Workout Creation & Management section using ONLY found content"""
        
        print("🔍 Querying LlamaIndex for actual workout creation content...")
        
        article_content = """# Workout Creation & Management - Test Section

*This section uses ONLY content found in the LlamaIndex knowledge base*

"""
        
        for feature_name, queries in self.creation_queries.items():
            print(f"\n📋 Querying for: {feature_name}")
            
            # Get actual content
            results = self.query_feature_content(feature_name, queries)
            content = self.extract_relevant_content(results, feature_name)
            
            # Only include feature if we found content
            if any(content.values()):
                article_content += f"\n## {feature_name}\n\n"
                
                # Add content from different sources
                if content['facts']:
                    article_content += "**What we know:**\n"
                    for fact in content['facts'][:3]:  # Top 3 facts
                        # Clean up fact text
                        fact_text = fact['text'].replace('Fact: ', '').strip()
                        article_content += f"- {fact_text}\n"
                    article_content += "\n"
                
                if content['blog']:
                    article_content += "**From our blog articles:**\n"
                    for blog in content['blog'][:2]:  # Top 2 blog mentions
                        article_content += f"From '{blog['title']}':\n"
                        # Extract relevant snippet
                        text = blog['text']
                        # Get more content and clean it up
                        if len(text) > 500:
                            article_content += f"> {text[:500]}...\n\n"
                        else:
                            article_content += f"> {text}\n\n"
                
                if content['forum_qa']:
                    article_content += "**From user discussions:**\n"
                    for qa in content['forum_qa'][:3]:  # Top 3 Q&As
                        # Extract key parts
                        text = qa['text']
                        if 'Question:' in text and 'Answer:' in text:
                            # Extract Q&A structure
                            q_start = text.find('Question:') + 9
                            q_end = text.find('\n', q_start)
                            if q_end == -1:
                                q_end = text.find('Context:', q_start)
                            if q_end == -1:
                                q_end = text.find('User Problem:', q_start)
                            if q_end == -1:
                                q_end = q_start + 200
                            
                            question = text[q_start:q_end].strip()
                            article_content += f"- Q: {question}\n"
                            
                            # Try to find answer
                            if 'Answer:' in text:
                                a_start = text.find('Answer:') + 7
                                a_end = text.find('\n', a_start + 50)
                                if a_end == -1:
                                    a_end = a_start + 200
                                answer = text[a_start:a_end].strip()
                                article_content += f"  A: {answer}\n"
                        else:
                            article_content += f"- {text[:300]}...\n"
                    article_content += "\n"
                
                if content['youtube']:
                    article_content += "**From video tutorials:**\n"
                    for video in content['youtube'][:1]:  # Top video
                        article_content += f"In '{video['title']}':\n"
                        article_content += f"> {video['text'][:200]}...\n\n"
            else:
                print(f"  ❌ No content found for {feature_name}")
        
        # Save the test section
        output_dir = Path("./script-testing/workout_query_results")
        output_file = output_dir / f"test_workout_creation_section_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(article_content)
        
        print(f"\n✅ Test section saved to: {output_file}")
        
        # Also save the raw query results for inspection
        results_file = output_dir / f"test_query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        all_query_results = {}
        for feature_name, queries in self.creation_queries.items():
            results = self.query_feature_content(feature_name, queries)
            all_query_results[feature_name] = [
                {
                    'text': r['text'][:500],
                    'title': r['title'],
                    'source': r['source'],
                    'score': r['distance']
                }
                for r in results
            ]
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(all_query_results, f, indent=2)
        
        print(f"📊 Query results saved to: {results_file}")
        
        return article_content

if __name__ == "__main__":
    generator = WorkoutCreationArticle()
    generator.generate_section()