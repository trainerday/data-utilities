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
            similarity_top_k=30,
            response_mode="no_text"  # Just retrieve, don't synthesize
        )
        
        # Setup AI clients
        self.openai_client = openai.OpenAI()
        self.anthropic_client = Anthropic()
        
        # Paths
        self.priority_lists_path = Path("/Users/alex/Documents/bm-projects/TD-Business/blog/in-progress")
        self.output_path = Path(os.getenv('CONTENT_OUTPUT_PATH', 'output'))
        self.templates_path = Path("templates")
        
    def load_article_config(self, article_number: int, category: str = "features") -> Dict:
        """Load article configuration from priority list"""
        
        # Map category to file
        category_files = {
            "features": "ai-articles-features.md",
            "issues": "ai-articles-issues.md",
            "training": "ai-articles-training.md",
            "other": "ai-articles-other.md"
        }
        
        file_path = self.priority_lists_path / category_files.get(category, "ai-articles-features.md")
        
        # Parse markdown table to find article
        # This is simplified - in production, use proper markdown parsing
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
        # Find the row for this article number
        for line in lines:
            if line.startswith(f"| {article_number} |"):
                parts = [p.strip() for p in line.split('|')]
                return {
                    'number': int(parts[1]),
                    'include': parts[2],
                    'title': parts[3],
                    'category': parts[4],
                    'engagement': parts[5],
                    'tags': parts[6],
                    'user_question': parts[7]
                }
        
        raise ValueError(f"Article {article_number} not found in {category} list")
    
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
    
    def query_knowledge_base(self, queries: List[str]) -> List[Any]:
        """Query LlamaIndex for relevant content"""
        
        all_nodes = []
        seen_ids = set()
        
        for query in queries:
            print(f"🔍 Querying: {query}")
            response = self.query_engine.query(query)
            
            for node in response.source_nodes:
                if node.node_id not in seen_ids:
                    all_nodes.append(node)
                    seen_ids.add(node.node_id)
        
        # Sort by relevance score
        all_nodes.sort(key=lambda x: x.score, reverse=True)
        
        print(f"📊 Found {len(all_nodes)} unique content pieces")
        
        # Group by source
        by_source = {}
        for node in all_nodes:
            source = node.metadata.get('source', 'unknown')
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(node)
        
        for source, nodes in by_source.items():
            print(f"  - {source}: {len(nodes)} pieces")
        
        return all_nodes[:50]  # Return top 50
    
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
        """Generate article using Claude with template"""
        
        # Load template
        template_path = self.templates_path / "individual-article-prompt-template.txt"
        with open(template_path, 'r') as f:
            template = f.read()
        
        # Build context sections
        facts_section = "\n".join([f"- {fact['text']}" for fact in content['facts'][:10]])
        
        blog_section = "\n".join([
            f"From '{q['title']}':\n\"{q['quote']}\""
            for q in content['blog_quotes'][:5]
        ])
        
        forum_section = "\n".join([
            f"Q: {q['question']}\nA: {q['answer']}"
            for q in content['forum_questions'][:5]
        ])
        
        # Fill template
        prompt = template.format(
            article_title=config['title'],
            user_question=config['user_question'],
            facts_content=facts_section or "No specific facts found.",
            blog_content=blog_section or "No relevant blog content found.",
            forum_content=forum_section or "No relevant forum discussions found.",
            key_points="\n".join([f"- {point}" for point in list(content['key_points'])[:10]])
        )
        
        # Generate with Claude
        response = self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        return response.content[0].text
    
    def save_article(self, content: str, config: Dict):
        """Save article with metadata"""
        
        # Create filename
        filename = f"{config['category'][0]}{config['number']:03d}-{config['title'].lower().replace(' ', '-')[:50]}.md"
        
        # Add frontmatter
        frontmatter = f"""---
title: "{config['title']}"
category: {config['category']}
engagement: {config['engagement']}
tags: {config['tags']}
status: new-article
created: {datetime.now().strftime('%Y-%m-%d')}
---

"""
        
        # Save to output directory
        output_dir = self.output_path / "articles-ai"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / filename
        with open(output_file, 'w') as f:
            f.write(frontmatter + content)
        
        print(f"✅ Saved article to: {output_file}")
    
    def generate(self, article_number: int, category: str = "features"):
        """Main generation workflow"""
        
        print(f"\n🚀 Generating article #{article_number} from {category} category")
        
        # Load article config
        config = self.load_article_config(article_number, category)
        print(f"📋 Title: {config['title']}")
        print(f"❓ Question: {config['user_question']}")
        
        # Generate search queries
        queries = self.generate_search_queries(config['title'], config['user_question'])
        print(f"🔎 Generated {len(queries)} search queries")
        
        # Query knowledge base
        nodes = self.query_knowledge_base(queries)
        
        # Extract key content
        content = self.extract_key_content(nodes)
        print(f"📝 Extracted: {len(content['facts'])} facts, {len(content['blog_quotes'])} blog quotes, {len(content['forum_questions'])} forum Q&As")
        
        # Generate article
        print("🤖 Generating article with Claude...")
        article_content = self.generate_article(config, content)
        
        # Save article
        self.save_article(article_content, config)
        
        print("✨ Article generation complete!")


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_article_llamaindex.py <article_number> [category]")
        print("Categories: features (default), issues, training, other")
        sys.exit(1)
    
    article_number = int(sys.argv[1])
    category = sys.argv[2] if len(sys.argv) > 2 else "features"
    
    generator = LlamaIndexArticleGenerator()
    generator.generate(article_number, category)


if __name__ == "__main__":
    main()