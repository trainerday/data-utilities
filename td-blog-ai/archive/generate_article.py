#!/usr/bin/env python3
"""
Simplified article generation using LlamaIndex
Replaces complex manual vector search with intelligent retrieval
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from dotenv import load_dotenv
import openai
from anthropic import Anthropic

# Import utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.google_sheets_client import get_bad_facts_for_article_generation

# LlamaIndex imports
from llama_index.core import VectorStoreIndex, Settings
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

load_dotenv()

class LlamaIndexArticleGenerator:
    def __init__(self):
        """Initialize LlamaIndex and API clients"""
        
        # Configure LlamaIndex
        Settings.embed_model = OpenAIEmbedding(
            model="text-embedding-3-large",
            dimensions=1536
        )
        Settings.llm = OpenAI(model="gpt-4-turbo-preview")
        
        # Setup vector store
        self.vector_store = PGVectorStore.from_params(
            database=os.getenv('DB_DATABASE', 'trainerday_local'),
            host=os.getenv('DB_HOST', 'localhost'),
            password=os.getenv('DB_PASSWORD', ''),
            port=5432,
            user=os.getenv('DB_USERNAME', os.getenv('USER')),
            table_name="llamaindex_knowledge_base",
            embed_dim=1536,
        )
        
        # Create index and query engine
        self.index = VectorStoreIndex.from_vector_store(self.vector_store)
        self.query_engine = self.index.as_query_engine(
            similarity_top_k=50,  # Increased from 30 for more comprehensive results
            response_mode="no_text"  # Just retrieve, don't synthesize
        )
        
        # Setup AI clients
        self.openai_client = openai.OpenAI()
        self.anthropic_client = Anthropic()
        
        # Paths
        self.priority_lists_path = Path("/Users/alex/Documents/bm-projects/TD-Business/blog/in-progress")
        self.output_path = Path(os.getenv('CONTENT_OUTPUT_PATH', 'output'))
        self.templates_path = Path("templates")
        
    def load_query_results(self) -> Dict:
        """Load query results from article_features.json"""
        
        results_file = Path("article-temp-files/article_features.json")
        
        if not results_file.exists():
            raise FileNotFoundError(
                f"Query results not found at {results_file}. "
                "Please run: python scripts/query_all_article_features.py workout-queries"
            )
        
        with open(results_file, 'r') as f:
            return json.load(f)
    
    def generate_search_queries(self, title: str, user_question: str) -> List[str]:
        """Generate multiple search queries for comprehensive retrieval"""
        
        queries = [
            title,  # Exact title
            user_question,  # Original question
            title.lower(),  # Lowercase variation
        ]
        
        # Add key terms from title
        key_terms = [term for term in title.split() if len(term) > 3]
        if len(key_terms) > 2:
            queries.append(" ".join(key_terms[:3]))
        
        # Add question variations
        if "how" in user_question.lower():
            queries.append(user_question.replace("How do I", "").strip())
        
        return list(set(queries))  # Remove duplicates
    
    def extract_content_from_results(self, query_results: Dict) -> Dict[str, Any]:
        """Extract and organize content from query results"""
        
        content = {
            'facts': [],
            'blog_quotes': [],
            'forum_questions': [],
            'video_references': [],
            'all_features': []
        }
        
        # Process each category and feature
        for category, features in query_results.items():
            for feature_name, results in features.items():
                content['all_features'].append({
                    'category': category,
                    'feature': feature_name,
                    'results': results
                })
                
                # Process individual results
                for result in results:
                    source = result.get('source', '')
                    text = result.get('text', '')
                    
                    if source == 'facts':
                        content['facts'].append({
                            'text': text,
                            'feature': feature_name,
                            'score': result.get('distance', 0)
                        })
                    
                    elif source == 'blog':
                        content['blog_quotes'].append({
                            'quote': text[:500] + '...' if len(text) > 500 else text,
                            'title': result.get('title', 'Blog Article'),
                            'feature': feature_name,
                            'score': result.get('distance', 0)
                        })
                    
                    elif source == 'forum':
                        content['forum_questions'].append({
                            'question': text[:200] + '...' if len(text) > 200 else text,
                            'answer': text[200:500] + '...' if len(text) > 200 else '',
                            'feature': feature_name,
                            'score': result.get('distance', 0)
                        })
                    
                    elif source == 'youtube':
                        content['video_references'].append({
                            'title': result.get('title', 'Video'),
                            'excerpt': text[:300] + '...' if len(text) > 300 else text,
                            'feature': feature_name,
                            'score': result.get('distance', 0)
                        })
        
        # Sort by relevance (lower distance = more relevant)
        for key in ['facts', 'blog_quotes', 'forum_questions', 'video_references']:
            content[key].sort(key=lambda x: x.get('score', 1))
        
        return content
    
    def extract_key_content(self, nodes: List[Any]) -> Dict[str, Any]:
        """Extract key content from retrieved nodes"""
        
        content = {
            'facts': [],
            'blog_quotes': [],
            'forum_questions': [],
            'video_references': [],
            'key_points': set()
        }
        
        for node in nodes:
            source = node.metadata.get('source')
            text = node.text
            
            if source == 'facts':
                # Skip wrong facts
                if not text.startswith("DO NOT USE"):
                    content['facts'].append({
                        'text': text,
                        'score': node.score
                    })
            
            elif source == 'blog':
                # Extract key sentences
                sentences = text.split('. ')
                for sent in sentences[:3]:  # First 3 sentences
                    if len(sent) > 50:
                        content['blog_quotes'].append({
                            'quote': sent,
                            'title': node.metadata.get('title', 'Blog Article'),
                            'score': node.score
                        })
            
            elif source == 'forum':
                # Extract questions and solutions
                if 'Question:' in text:
                    parts = text.split('Answer:')
                    if len(parts) == 2:
                        content['forum_questions'].append({
                            'question': parts[0].replace('Question:', '').strip(),
                            'answer': parts[1].strip()[:200] + '...',
                            'score': node.score
                        })
            
            elif source == 'youtube':
                content['video_references'].append({
                    'title': node.metadata.get('title', 'Video'),
                    'excerpt': text[:150] + '...',
                    'score': node.score
                })
        
        # Extract key points from all content
        for node in nodes[:10]:  # Top 10 nodes
            words = node.text.lower().split()
            for i in range(len(words) - 2):
                if words[i] in ['click', 'tap', 'select', 'go', 'open']:
                    content['key_points'].add(' '.join(words[i:i+3]))
        
        return content
    
    def generate_article(self, config: Dict, content: Dict) -> str:
        """Generate comprehensive article using Claude with template"""
        
        # Load comprehensive template
        template_path = self.templates_path / "comprehensive-article-template.txt"
        with open(template_path, 'r') as f:
            template = f.read()
        
        # Get bad facts from Google Sheets
        bad_facts_section = get_bad_facts_for_article_generation()
        
        # Organize all content by source type
        content_sections = []
        
        # Facts section - include ALL facts
        if content['facts']:
            facts_text = "\n".join([f"- {fact['text']}" for fact in content['facts']])
            content_sections.append(f"## FACTS FROM KNOWLEDGE BASE ({len(content['facts'])} total facts)\n{facts_text}")
        
        # Blog content - include ALL blog quotes
        if content['blog_quotes']:
            blog_text = "\n\n".join([
                f"From '{q['title']}':\n\"{q['quote']}\""
                for q in content['blog_quotes']  # ALL quotes, no limit
            ])
            content_sections.append(f"## BLOG CONTENT ({len(content['blog_quotes'])} total quotes)\n{blog_text}")
        
        # Forum discussions - include most relevant Q&As
        if content['forum_questions']:
            # Limit answer length to avoid repetition
            forum_entries = []
            for q in content['forum_questions'][:100]:  # Top 100 most relevant
                answer = q['answer']
                if len(answer) > 300:
                    answer = answer[:300] + "..."
                forum_entries.append(f"Q: {q['question']}\nA: {answer}")
            
            forum_text = "\n\n".join(forum_entries)
            content_sections.append(f"## FORUM DISCUSSIONS ({len(content['forum_questions'])} total Q&As, showing top 100)\n{forum_text}")
        
        # Video content - include most relevant videos
        if content['video_references']:
            video_entries = []
            for v in content['video_references'][:50]:  # Top 50 most relevant
                excerpt = v['excerpt']
                if len(excerpt) > 200:
                    excerpt = excerpt[:200] + "..."
                video_entries.append(f"Video: {v['title']}\n{excerpt}")
            
            video_text = "\n\n".join(video_entries)
            content_sections.append(f"## VIDEO CONTENT ({len(content['video_references'])} total videos, showing top 50)\n{video_text}")
        
        # Fill comprehensive template
        prompt = template.format(
            title=config['title'],
            content_sections="\n\n".join(content_sections),
            bad_facts_section=bad_facts_section
        )
        
        # Debug: Show prompt size
        print(f"📊 Prompt size: {len(prompt):,} characters")
        
        # Try with OpenAI GPT-4 for longer output
        try:
            print("🤖 Using OpenAI GPT-4 Turbo...")
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",  # GPT-4 Turbo for better long-form content
                max_tokens=4096,  # GPT-4 Turbo max tokens
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ OpenAI error: {e}")
            print("🔄 Falling back to Claude...")
            
            # Fallback to Claude
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=8192,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return response.content[0].text
    
    def save_article(self, content: str, config: Dict):
        """Save article without metadata"""
        
        # Simple filename
        filename = "article.md"
        
        # Save to output directory
        output_dir = self.output_path / "articles-ai"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / filename
        with open(output_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Saved article to: {output_file}")
    
    def determine_article_title(self, query_results: Dict) -> str:
        """Determine article title based on query results"""
        
        # Check if there's a stored query filename to determine the topic
        results_file = Path("article-temp-files/article_features.json")
        
        # Default title for workout queries
        title = "TrainerDay Workout Creation and Management Features - Complete Guide"
        
        # Could expand this logic to handle different query types
        # For now, focusing on workout features as that's the current query
        
        return title
    
    def generate(self):
        """Main generation workflow using query results"""
        
        # Load query results
        print("📄 Loading query results from article_features.json...")
        query_results = self.load_query_results()
        
        # Determine title from query results
        title = self.determine_article_title(query_results)
        print(f"\n🚀 Generating comprehensive article: {title}")
        
        # Extract content from results
        content = self.extract_content_from_results(query_results)
        print(f"📝 Extracted: {len(content['facts'])} facts, {len(content['blog_quotes'])} blog quotes, {len(content['forum_questions'])} forum Q&As, {len(content['video_references'])} video references")
        
        # Create config for the article
        config = {
            'title': title,
            'category': 'features',
            'engagement': 'high',
            'tags': 'workouts, training, features',
            'number': 1
        }
        
        # Generate article
        print("🤖 Generating article...")
        article_content = self.generate_article(config, content)
        
        # Save article
        self.save_article(article_content, config)
        
        print("✨ Article generation complete!")


def main():
    generator = LlamaIndexArticleGenerator()
    generator.generate()


if __name__ == "__main__":
    main()