#!/usr/bin/env python3
"""
Enhanced Fact Extraction Script with Database Storage

Extracts factual statements from articles using Claude Sonnet 4,
generates embeddings using OpenAI text-embedding-3-large,
and stores them in PostgreSQL facts table.
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

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from utils.db_connection import get_db_connection

class FactExtractorWithDatabase:
    def __init__(self):
        # Initialize API clients
        self.anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Embedding configuration (matches vector-processor)
        self.embedding_model = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-large')
        self.embedding_dimensions = int(os.getenv('OPENAI_EMBEDDING_DIMENSIONS', '1536'))
        
        # Rate limiting for API calls
        self.last_api_call = 0
        self.min_api_interval = 0.1  # 10 requests per second max
        
        self.stats = {
            'facts_extracted': 0,
            'facts_stored': 0,
            'embeddings_created': 0,
            'errors': 0
        }
        
    def setup_facts_table(self):
        """Create facts table if it doesn't exist"""
        schema_sql = """
        -- Enable pgvector extension
        CREATE EXTENSION IF NOT EXISTS vector;
        
        -- Create facts table
        CREATE TABLE IF NOT EXISTS facts (
            id SERIAL PRIMARY KEY,
            fact_text TEXT NOT NULL,
            source_article VARCHAR(200) NOT NULL,
            embedding vector(1536) NOT NULL,
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        -- Create index for similarity search
        CREATE INDEX IF NOT EXISTS idx_facts_embedding_similarity 
        ON facts USING ivfflat (embedding vector_cosine_ops);
        
        -- Create index for source article lookups
        CREATE INDEX IF NOT EXISTS idx_facts_source_article 
        ON facts(source_article);
        """
        
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(schema_sql)
                conn.commit()
            conn.close()
            print("✅ Facts table and indexes ready")
        except Exception as e:
            print(f"❌ Failed to create facts table: {e}")
            raise

    def create_embedding(self, text: str):
        """Create embedding using OpenAI API with rate limiting"""
        # Rate limiting
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
        """Extract factual statements from article using Claude Sonnet 4 with OpenAI fallback"""
        
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

Example format:
FACT: TrainerDay workout creator supports ERG mode, slope mode, and heart rate mode
FACT: W'bal integration requires entering FTP and W' values
FACT: Workouts can be duplicated by holding ALT key and dragging
"""

        # Try Claude first
        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=3000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            print("✅ Used Claude Sonnet 4")
            return response.content[0].text
            
        except Exception as e:
            print(f"⚠️  Claude failed ({str(e)[:100]}...), trying OpenAI GPT-4 as fallback...")
            
            # Fallback to OpenAI GPT-4
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=3000,
                    temperature=0.3
                )
                
                print("✅ Used OpenAI GPT-4 (fallback)")
                return response.choices[0].message.content
                
            except Exception as e2:
                print(f"❌ Both Claude and OpenAI failed. OpenAI: {e2}")
                self.stats['errors'] += 1
                return None

    def parse_facts_from_response(self, ai_response):
        """Parse individual facts from AI response"""
        facts = []
        
        if not ai_response:
            return facts
            
        lines = ai_response.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('FACT:'):
                fact_text = line[5:].strip()  # Remove 'FACT:' prefix
                if fact_text:
                    facts.append(fact_text)
        
        return facts

    def check_fact_similarity(self, fact_embedding, similarity_threshold=0.90):
        """Check if similar fact already exists in database"""
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
            print(f"❌ Error checking fact similarity: {e}")
            self.stats['errors'] += 1
            return None

    def store_fact_in_database(self, fact_text, source_article, embedding):
        """Store fact with embedding in database"""
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                # Create metadata
                metadata = {
                    'extraction_date': datetime.now().isoformat(),
                    'embedding_model': self.embedding_model,
                    'embedding_dimensions': self.embedding_dimensions
                }
                
                query = """
                INSERT INTO facts (fact_text, source_article, embedding, metadata)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """
                
                cursor.execute(query, [
                    fact_text,
                    source_article,
                    embedding,
                    json.dumps(metadata)
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

    def process_all_articles(self):
        """Process all articles and store facts in database"""
        
        # Setup database table
        self.setup_facts_table()
        
        # Get the output path from environment
        content_output_path = os.getenv('CONTENT_OUTPUT_PATH', '.')
        articles_dir = Path(content_output_path) / 'articles-ai'
        
        if not articles_dir.exists():
            print(f"❌ Articles directory not found: {articles_dir}")
            return None
        
        # Find all articles (sorted)
        article_files = sorted(list(articles_dir.glob('*.md')))
        
        if not article_files:
            print(f"❌ No articles found in {articles_dir}")
            return None
        
        print(f"📄 Found {len(article_files)} articles to process")
        print()
        
        # Initialize totals
        total_articles_processed = 0
        total_facts_extracted = 0
        total_facts_stored = 0
        all_processed_facts = []
        
        # Process each article
        for article_idx, article_file in enumerate(article_files, 1):
            print(f"🔄 Processing article {article_idx}/{len(article_files)}: {article_file.name}")
            
            # Read and parse the article
            try:
                with open(article_file, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)
                
                article_title = post.metadata.get('title', article_file.stem)
                article_content = post.content
                
                print(f"   📖 Title: {article_title}")
                print(f"   📊 Content length: {len(article_content)} characters")
                
            except Exception as e:
                print(f"   ❌ Error reading article: {e}")
                self.stats['errors'] += 1
                continue
            
            # Extract facts
            print(f"   🤖 Extracting facts...")
            ai_response = self.extract_facts_from_article(article_content, article_title)
            
            if not ai_response:
                print(f"   ❌ Failed to extract facts")
                continue
            
            facts = self.parse_facts_from_response(ai_response)
            article_facts_extracted = len(facts)
            total_facts_extracted += article_facts_extracted
            
            print(f"   ✅ Extracted {article_facts_extracted} facts")
            
            # Process each fact for this article
            print(f"   🔄 Processing facts (embedding + database storage)...")
            
            article_facts_stored = 0
            for i, fact_text in enumerate(facts, 1):
                print(f"      Processing fact {i}/{len(facts)}: {fact_text[:40]}...")
                
                # Create embedding
                embedding = self.create_embedding(fact_text)
                if not embedding:
                    print(f"      ❌ Failed to create embedding for fact {i}")
                    continue
                
                # Check for similar facts
                similar_fact = self.check_fact_similarity(embedding)
                if similar_fact:
                    print(f"      ⚠️  Similar fact exists (similarity: {similar_fact['similarity_score']:.3f})")
                    print(f"          Existing: {similar_fact['fact_text'][:40]}...")
                    print(f"          Skipping duplicate")
                    continue
                
                # Store fact in database
                fact_id = self.store_fact_in_database(fact_text, article_file.name, embedding)
                if fact_id:
                    print(f"      ✅ Stored fact #{fact_id}")
                    article_facts_stored += 1
                    all_processed_facts.append({
                        'id': fact_id,
                        'text': fact_text,
                        'article': article_file.name,
                        'embedding_created': True
                    })
            
            total_facts_stored += article_facts_stored
            total_articles_processed += 1
            
            print(f"   📊 Article Summary: {article_facts_extracted} extracted, {article_facts_stored} stored")
            print()
        
        print(f"🎉 FINAL PROCESSING SUMMARY:")
        print(f"=" * 40)
        print(f"   - Articles processed: {total_articles_processed}/{len(article_files)}")
        print(f"   - Total facts extracted: {total_facts_extracted}")
        print(f"   - Total facts stored: {total_facts_stored}")
        print(f"   - Total embeddings created: {self.stats['embeddings_created']}")
        print(f"   - Total errors: {self.stats['errors']}")
        print(f"   - Duplicate facts skipped: {total_facts_extracted - total_facts_stored}")
        
        return {
            'articles_processed': total_articles_processed,
            'total_articles': len(article_files),
            'total_facts_extracted': total_facts_extracted,
            'total_facts_stored': total_facts_stored,
            'facts': all_processed_facts,
            'stats': self.stats
        }

def main():
    """Main function"""
    print("🎯 FACT EXTRACTION WITH DATABASE STORAGE")
    print("=" * 50)
    
    extractor = FactExtractorWithDatabase()
    
    try:
        result = extractor.process_all_articles()
        
        if result:
            print("\n✅ All articles processed successfully!")
            print(f"🗄️  Database: {result['total_facts_stored']} facts stored with embeddings")
            print(f"📈 Efficiency: {result['total_facts_stored']}/{result['total_facts_extracted']} facts were unique")
        else:
            print("\n❌ Article processing failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()