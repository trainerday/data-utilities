#!/usr/bin/env python3
"""
Batch Fact Extraction Script

Processes articles in smaller batches with progress tracking.
Allows resuming from where it left off.
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic
import openai
import frontmatter
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import argparse

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from utils.db_connection import get_db_connection

class BatchFactExtractor:
    def __init__(self):
        # Initialize API clients
        self.anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Embedding configuration
        self.embedding_model = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-large')
        self.embedding_dimensions = int(os.getenv('OPENAI_EMBEDDING_DIMENSIONS', '1536'))
        
        # Rate limiting
        self.last_api_call = 0
        self.min_api_interval = 0.1
        
        self.stats = {
            'articles_processed': 0,
            'facts_extracted': 0,
            'facts_stored': 0,
            'embeddings_created': 0,
            'duplicates_skipped': 0,
            'errors': 0
        }

    def setup_facts_table(self):
        """Create facts table if it doesn't exist"""
        schema_sql = """
        CREATE EXTENSION IF NOT EXISTS vector;
        
        CREATE TABLE IF NOT EXISTS facts (
            id SERIAL PRIMARY KEY,
            fact_text TEXT NOT NULL,
            source_article VARCHAR(200) NOT NULL,
            embedding vector(1536) NOT NULL,
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_facts_embedding_similarity 
        ON facts USING ivfflat (embedding vector_cosine_ops);
        
        CREATE INDEX IF NOT EXISTS idx_facts_source_article 
        ON facts(source_article);
        """
        
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(schema_sql)
                conn.commit()
            conn.close()
            print("✅ Facts table ready")
        except Exception as e:
            print(f"❌ Failed to create facts table: {e}")
            raise

    def get_processed_articles(self):
        """Get list of articles already processed"""
        try:
            conn = get_db_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT DISTINCT source_article FROM facts")
                results = cursor.fetchall()
            conn.close()
            return [row['source_article'] for row in results]
        except Exception as e:
            print(f"⚠️  Could not get processed articles: {e}")
            return []

    def create_embedding(self, text: str):
        """Create embedding with rate limiting"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        
        if time_since_last_call < self.min_api_interval:
            sleep_time = self.min_api_interval - time_since_last_call
            time.sleep(sleep_time)

        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text,
                dimensions=self.embedding_dimensions
            )
            
            self.last_api_call = time.time()
            self.stats['embeddings_created'] += 1
            
            return response.data[0].embedding
            
        except Exception as e:
            print(f"❌ Error creating embedding: {e}")
            self.stats['errors'] += 1
            return None

    def extract_facts_from_article(self, article_content, article_title):
        """Extract facts using Claude/OpenAI"""
        prompt = f"""
Extract factual statements from this TrainerDay article. Focus on concrete, verifiable facts about features, functionality, and technical specifications.

Article Title: {article_title}

Article Content:
{article_content}

Please extract factual statements and return them in this format:
FACT: [Clear, standalone factual statement]

Guidelines:
- Focus on features, capabilities, technical specifications
- Include facts about how things work, what's supported, what's available
- Make each fact a complete, standalone statement  
- Avoid subjective opinions or user preferences
- Include specific details like modes, integrations, file formats, etc.
"""

        # Try Claude first
        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=3000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            # Fallback to OpenAI
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=3000,
                    temperature=0.3
                )
                
                return response.choices[0].message.content
                
            except Exception as e2:
                print(f"❌ Both Claude and OpenAI failed")
                self.stats['errors'] += 1
                return None

    def parse_facts(self, ai_response):
        """Parse facts from AI response"""
        facts = []
        if not ai_response:
            return facts
            
        lines = ai_response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('FACT:'):
                fact_text = line[5:].strip()
                if fact_text:
                    facts.append(fact_text)
        
        return facts

    def check_fact_similarity(self, fact_embedding, similarity_threshold=0.90):
        """Check if similar fact exists"""
        try:
            conn = get_db_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                SELECT id, fact_text, source_article,
                       (1 - (embedding <=> %s::vector)) as similarity_score
                FROM facts
                WHERE (1 - (embedding <=> %s::vector)) > %s
                ORDER BY similarity_score DESC
                LIMIT 1
                """
                
                cursor.execute(query, [fact_embedding, fact_embedding, similarity_threshold])
                result = cursor.fetchone()
            
            conn.close()
            return result
            
        except Exception as e:
            print(f"❌ Error checking similarity: {e}")
            self.stats['errors'] += 1
            return None

    def store_fact(self, fact_text, source_article, embedding):
        """Store fact in database"""
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                metadata = {
                    'extraction_date': datetime.now().isoformat(),
                    'embedding_model': self.embedding_model
                }
                
                query = """
                INSERT INTO facts (fact_text, source_article, embedding, metadata)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """
                
                cursor.execute(query, [
                    fact_text, source_article, embedding, json.dumps(metadata)
                ])
                
                fact_id = cursor.fetchone()[0]
                conn.commit()
            
            conn.close()
            self.stats['facts_stored'] += 1
            return fact_id
            
        except Exception as e:
            print(f"❌ Error storing fact: {e}")
            self.stats['errors'] += 1
            return None

    def process_batch(self, start_idx=0, batch_size=5):
        """Process a batch of articles"""
        
        # Setup database table
        self.setup_facts_table()
        
        # Get articles directory
        content_output_path = os.getenv('CONTENT_OUTPUT_PATH', '.')
        articles_dir = Path(content_output_path) / 'articles-ai'
        
        if not articles_dir.exists():
            print(f"❌ Articles directory not found: {articles_dir}")
            return None
        
        article_files = sorted(list(articles_dir.glob('*.md')))
        
        if not article_files:
            print(f"❌ No articles found")
            return None
        
        # Get already processed articles
        processed_articles = self.get_processed_articles()
        
        print(f"📄 Total articles: {len(article_files)}")
        print(f"✅ Already processed: {len(processed_articles)}")
        
        # Process batch
        end_idx = min(start_idx + batch_size, len(article_files))
        batch_files = article_files[start_idx:end_idx]
        
        print(f"🔄 Processing batch: articles {start_idx+1}-{end_idx} ({len(batch_files)} articles)")
        print()
        
        for i, article_file in enumerate(batch_files):
            article_idx = start_idx + i + 1
            
            # Skip if already processed
            if article_file.name in processed_articles:
                print(f"⏭️  Skipping {article_idx}/{len(article_files)}: {article_file.name} (already processed)")
                continue
            
            print(f"🔄 Processing {article_idx}/{len(article_files)}: {article_file.name}")
            
            # Read article
            try:
                with open(article_file, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)
                
                article_title = post.metadata.get('title', article_file.stem)
                article_content = post.content
                
            except Exception as e:
                print(f"   ❌ Error reading article: {e}")
                self.stats['errors'] += 1
                continue
            
            # Extract facts
            ai_response = self.extract_facts_from_article(article_content, article_title)
            if not ai_response:
                print(f"   ❌ Failed to extract facts")
                continue
            
            facts = self.parse_facts(ai_response)
            self.stats['facts_extracted'] += len(facts)
            
            print(f"   ✅ Extracted {len(facts)} facts")
            
            # Process each fact
            article_facts_stored = 0
            for fact_text in facts:
                # Create embedding
                embedding = self.create_embedding(fact_text)
                if not embedding:
                    continue
                
                # Check similarity
                similar_fact = self.check_fact_similarity(embedding)
                if similar_fact:
                    self.stats['duplicates_skipped'] += 1
                    continue
                
                # Store fact
                fact_id = self.store_fact(fact_text, article_file.name, embedding)
                if fact_id:
                    article_facts_stored += 1
            
            print(f"   📊 Stored {article_facts_stored}/{len(facts)} unique facts")
            self.stats['articles_processed'] += 1
            print()
        
        # Print batch summary
        print(f"📊 BATCH SUMMARY:")
        print(f"   - Articles processed: {self.stats['articles_processed']}")
        print(f"   - Facts extracted: {self.stats['facts_extracted']}")
        print(f"   - Facts stored: {self.stats['facts_stored']}")
        print(f"   - Duplicates skipped: {self.stats['duplicates_skipped']}")
        print(f"   - Embeddings created: {self.stats['embeddings_created']}")
        print(f"   - Errors: {self.stats['errors']}")
        
        return self.stats

def main():
    parser = argparse.ArgumentParser(description='Extract facts from articles in batches')
    parser.add_argument('--start', type=int, default=0, help='Starting article index (0-based)')
    parser.add_argument('--batch-size', type=int, default=5, help='Number of articles per batch')
    
    args = parser.parse_args()
    
    print("🎯 BATCH FACT EXTRACTION")
    print("=" * 40)
    
    extractor = BatchFactExtractor()
    
    try:
        result = extractor.process_batch(start_idx=args.start, batch_size=args.batch_size)
        
        if result:
            print(f"\n✅ Batch processing completed!")
        else:
            print(f"\n❌ Batch processing failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()