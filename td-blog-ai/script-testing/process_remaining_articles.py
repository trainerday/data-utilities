#!/usr/bin/env python3
"""
Process Remaining Articles Script

Continues processing all remaining articles in the background.
Shows progress and can be interrupted/resumed.
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

class ContinuousFactExtractor:
    def __init__(self):
        # Initialize API clients
        self.anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Embedding configuration
        self.embedding_model = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-large')
        self.embedding_dimensions = int(os.getenv('OPENAI_EMBEDDING_DIMENSIONS', '1536'))
        
        # Rate limiting - more conservative for continuous processing
        self.last_api_call = 0
        self.min_api_interval = 0.2  # 5 requests per second to be safe
        
        self.session_stats = {
            'articles_processed': 0,
            'facts_extracted': 0,
            'facts_stored': 0,
            'duplicates_skipped': 0,
            'errors': 0,
            'start_time': datetime.now()
        }

    def get_remaining_articles(self):
        """Get list of articles not yet processed"""
        # Get articles directory
        content_output_path = os.getenv('CONTENT_OUTPUT_PATH', '.')
        articles_dir = Path(content_output_path) / 'articles-ai'
        
        all_articles = sorted(list(articles_dir.glob('*.md')))
        
        # Get already processed articles
        try:
            conn = get_db_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT DISTINCT source_article FROM facts")
                results = cursor.fetchall()
            conn.close()
            processed = {row['source_article'] for row in results}
        except Exception as e:
            print(f"⚠️  Could not get processed articles: {e}")
            processed = set()
        
        # Filter to remaining articles
        remaining = [f for f in all_articles if f.name not in processed]
        
        return remaining, len(processed)

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
            return response.data[0].embedding
            
        except Exception as e:
            print(f"❌ Error creating embedding: {e}")
            self.session_stats['errors'] += 1
            return None

    def extract_facts_from_article(self, article_content, article_title):
        """Extract facts using OpenAI (Claude likely exhausted)"""
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

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ OpenAI failed: {e}")
            self.session_stats['errors'] += 1
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
            self.session_stats['errors'] += 1
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
            self.session_stats['facts_stored'] += 1
            return fact_id
            
        except Exception as e:
            print(f"❌ Error storing fact: {e}")
            self.session_stats['errors'] += 1
            return None

    def process_all_remaining(self):
        """Process all remaining articles"""
        
        remaining_articles, already_processed = self.get_remaining_articles()
        
        print(f"📊 STATUS:")
        print(f"   - Already processed: {already_processed} articles")
        print(f"   - Remaining to process: {len(remaining_articles)} articles")
        print()
        
        if not remaining_articles:
            print("✅ All articles already processed!")
            return True
        
        print(f"🔄 Starting continuous processing...")
        print(f"💡 Tip: Press Ctrl+C to stop and resume later")
        print()
        
        try:
            for i, article_file in enumerate(remaining_articles, 1):
                print(f"🔄 Processing {i}/{len(remaining_articles)}: {article_file.name}")
                
                # Read article
                try:
                    with open(article_file, 'r', encoding='utf-8') as f:
                        post = frontmatter.load(f)
                    
                    article_title = post.metadata.get('title', article_file.stem)
                    article_content = post.content
                    
                except Exception as e:
                    print(f"   ❌ Error reading article: {e}")
                    self.session_stats['errors'] += 1
                    continue
                
                # Extract facts
                ai_response = self.extract_facts_from_article(article_content, article_title)
                if not ai_response:
                    print(f"   ❌ Failed to extract facts")
                    continue
                
                facts = self.parse_facts(ai_response)
                self.session_stats['facts_extracted'] += len(facts)
                
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
                        self.session_stats['duplicates_skipped'] += 1
                        continue
                    
                    # Store fact
                    fact_id = self.store_fact(fact_text, article_file.name, embedding)
                    if fact_id:
                        article_facts_stored += 1
                
                print(f"   📊 Stored {article_facts_stored}/{len(facts)} unique facts")
                self.session_stats['articles_processed'] += 1
                
                # Show progress every 5 articles
                if i % 5 == 0:
                    elapsed = datetime.now() - self.session_stats['start_time']
                    print(f"\n📈 PROGRESS UPDATE:")
                    print(f"   - Articles completed: {i}/{len(remaining_articles)}")
                    print(f"   - Facts stored this session: {self.session_stats['facts_stored']}")
                    print(f"   - Duplicates skipped: {self.session_stats['duplicates_skipped']}")
                    print(f"   - Errors: {self.session_stats['errors']}")
                    print(f"   - Elapsed time: {elapsed}")
                    print()
                
                print()
        
        except KeyboardInterrupt:
            print(f"\n⏸️  Processing interrupted by user")
            print(f"📊 Session completed {self.session_stats['articles_processed']} articles")
            return False
        
        # Final summary
        elapsed = datetime.now() - self.session_stats['start_time']
        print(f"🎉 ALL ARTICLES PROCESSED!")
        print(f"📊 FINAL SESSION SUMMARY:")
        print(f"   - Articles processed: {self.session_stats['articles_processed']}")
        print(f"   - Facts extracted: {self.session_stats['facts_extracted']}")
        print(f"   - Facts stored: {self.session_stats['facts_stored']}")
        print(f"   - Duplicates skipped: {self.session_stats['duplicates_skipped']}")
        print(f"   - Errors: {self.session_stats['errors']}")
        print(f"   - Total time: {elapsed}")
        
        return True

def main():
    print("🎯 CONTINUOUS FACT EXTRACTION")
    print("=" * 50)
    
    extractor = ContinuousFactExtractor()
    
    try:
        completed = extractor.process_all_remaining()
        
        if completed:
            print(f"\n✅ All remaining articles processed successfully!")
        else:
            print(f"\n⏸️  Processing can be resumed by running this script again")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()