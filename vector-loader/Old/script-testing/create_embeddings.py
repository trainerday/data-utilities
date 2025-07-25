#!/usr/bin/env python3
"""
Forum Analysis Pipeline - Step 3: Create Embeddings
Creates vector embeddings from Q&A pairs for similarity search
"""

import os
import sys
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import openai
from typing import List, Dict, Optional
import argparse

# Load environment variables
load_dotenv()

class ForumEmbeddingsCreator:
    def __init__(self, db_config: Dict, openai_api_key: Optional[str] = None):
        self.db_config = db_config
        self.db_connection = None
        
        # OpenAI setup
        self.openai_client = openai.OpenAI(
            api_key=openai_api_key or os.getenv('OPENAI_API_KEY')
        )
        
        # Rate limiting
        self.last_api_call = 0
        self.min_api_interval = 0.1  # 10 requests per second max
        
        # Statistics
        self.stats = {
            'embeddings_created': 0,
            'embeddings_skipped': 0,
            'errors': 0,
            'total_qa_pairs': 0
        }

    def connect_db(self):
        """Connect to PostgreSQL database"""
        try:
            self.db_connection = psycopg2.connect(**self.db_config)
            print("✓ Connected to database")
            self.setup_embeddings_table()
        except Exception as e:
            raise Exception(f"Failed to connect to database: {e}")

    def setup_embeddings_table(self):
        """Create embeddings table with pgvector support"""
        schema_sql = """
        -- Enable pgvector extension
        CREATE EXTENSION IF NOT EXISTS vector;
        
        -- Create unified content embeddings table
        CREATE TABLE IF NOT EXISTS content_embeddings (
            id SERIAL PRIMARY KEY,
            source VARCHAR(20) NOT NULL,        -- 'forum', 'blog', 'youtube'  
            source_id VARCHAR(100) NOT NULL,    -- topic_id, article_filename, video_id
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            embedding vector(1536) NOT NULL,
            metadata JSONB,                     -- source-specific fields
            chunk_index INTEGER DEFAULT 0,     -- For multi-chunk content
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(source, source_id, chunk_index)
        );
        
        -- Create index for fast similarity search
        CREATE INDEX IF NOT EXISTS idx_content_embeddings_similarity 
        ON content_embeddings USING ivfflat (embedding vector_cosine_ops);
        
        -- Create indexes for lookups
        CREATE INDEX IF NOT EXISTS idx_content_embeddings_source 
        ON content_embeddings(source, source_id);
        
        CREATE INDEX IF NOT EXISTS idx_content_embeddings_source_type 
        ON content_embeddings(source);
        """
        
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute(schema_sql)
                self.db_connection.commit()
                print("✓ Embeddings table and indexes ready")
        except Exception as e:
            self.db_connection.rollback()
            raise Exception(f"Failed to create embeddings table: {e}")

    def get_qa_pairs_needing_embeddings(self) -> List[Dict]:
        """Get Q&A pairs that don't have embeddings yet"""
        if not self.db_connection:
            return []

        try:
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT fa.id, fa.question, fa.answer, fa.category
                    FROM forum_analysis fa
                    LEFT JOIN forum_embeddings fe ON fa.id = fe.analysis_id
                    WHERE fe.analysis_id IS NULL
                      AND fa.question IS NOT NULL 
                      AND fa.answer IS NOT NULL
                      AND LENGTH(TRIM(fa.question)) > 0
                      AND LENGTH(TRIM(fa.answer)) > 0
                    ORDER BY fa.id
                """)
                
                qa_pairs = cursor.fetchall()
                print(f"✓ Found {len(qa_pairs)} Q&A pairs needing embeddings")
                return qa_pairs
                
        except Exception as e:
            print(f"Error fetching Q&A pairs: {e}")
            return []

    def format_qa_text(self, question: str, answer: str) -> str:
        """Format Q&A pair for embedding"""
        # Clean up text
        question = question.strip()
        answer = answer.strip()
        
        # Format for embedding
        qa_text = f"Question: {question}\nAnswer: {answer}"
        return qa_text

    def create_embedding(self, text: str) -> Optional[List[float]]:
        """Create embedding using OpenAI API with rate limiting"""
        # Rate limiting
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        
        if time_since_last_call < self.min_api_interval:
            sleep_time = self.min_api_interval - time_since_last_call
            time.sleep(sleep_time)

        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            
            self.last_api_call = time.time()
            embedding = response.data[0].embedding
            return embedding
            
        except Exception as e:
            print(f"  ❌ OpenAI API error: {e}")
            self.stats['errors'] += 1
            return None

    def store_embedding(self, analysis_id: int, qa_text: str, embedding: List[float]) -> bool:
        """Store embedding in database"""
        if not self.db_connection:
            return False

        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO forum_embeddings (analysis_id, qa_text, embedding)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (analysis_id) DO UPDATE SET
                        qa_text = EXCLUDED.qa_text,
                        embedding = EXCLUDED.embedding,
                        created_at = NOW()
                """, (analysis_id, qa_text, embedding))
                
                self.db_connection.commit()
                return True
                
        except Exception as e:
            self.db_connection.rollback()
            print(f"  ❌ Database error: {e}")
            self.stats['errors'] += 1
            return False

    def process_embeddings(self, max_items: Optional[int] = None):
        """Main processing method"""
        print("🚀 Starting embedding creation process...")
        
        start_time = time.time()
        
        # Get Q&A pairs that need embeddings
        qa_pairs = self.get_qa_pairs_needing_embeddings()
        
        if not qa_pairs:
            print("✅ No Q&A pairs need embeddings - all done!")
            return

        self.stats['total_qa_pairs'] = len(qa_pairs)
        
        # Limit processing if requested
        if max_items and max_items < len(qa_pairs):
            qa_pairs = qa_pairs[:max_items]
            print(f"🎯 Processing first {max_items} items (limited)")

        # Process each Q&A pair
        for i, qa_pair in enumerate(qa_pairs, 1):
            analysis_id = qa_pair['id']
            question = qa_pair['question']
            answer = qa_pair['answer']
            category = qa_pair['category'] or 'general'
            
            print(f"\n[{i}/{len(qa_pairs)}] Processing Q&A {analysis_id} ({category})")
            print(f"  Q: {question[:80]}...")
            
            # Format text for embedding
            qa_text = self.format_qa_text(question, answer)
            
            # Create embedding
            embedding = self.create_embedding(qa_text)
            
            if embedding:
                # Store embedding
                if self.store_embedding(analysis_id, qa_text, embedding):
                    print(f"  ✅ Embedding created and stored")
                    self.stats['embeddings_created'] += 1
                else:
                    print(f"  ❌ Failed to store embedding")
            else:
                print(f"  ❌ Failed to create embedding")
                
            # Progress update every 10 items
            if i % 10 == 0:
                elapsed = time.time() - start_time
                rate = i / elapsed if elapsed > 0 else 0
                print(f"\n📊 Progress: {i}/{len(qa_pairs)} ({(i/len(qa_pairs))*100:.1f}%) - {rate:.1f} embeddings/sec")

        # Final statistics
        elapsed_time = time.time() - start_time
        print(f"\n🎯 EMBEDDING CREATION COMPLETE")
        print(f"=====================================")
        print(f"Total Q&A pairs: {self.stats['total_qa_pairs']}")
        print(f"Embeddings created: {self.stats['embeddings_created']}")
        print(f"Embeddings skipped: {self.stats['embeddings_skipped']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"Time elapsed: {elapsed_time:.1f} seconds")
        
        if self.stats['embeddings_created'] > 0:
            rate = self.stats['embeddings_created'] / elapsed_time
            print(f"Processing rate: {rate:.2f} embeddings/second")
            
            # Estimate OpenAI cost (rough estimate)
            estimated_cost = self.stats['embeddings_created'] * 0.0001  # $0.0001 per 1K tokens
            print(f"Estimated OpenAI cost: ${estimated_cost:.4f}")

        # Close database connection
        if self.db_connection:
            self.db_connection.close()
            print("Database connection closed")

    def similarity_search_example(self, query_text: str, limit: int = 5):
        """Example of how to perform similarity search"""
        print(f"\n🔍 Similarity search example for: '{query_text}'")
        
        # Create embedding for query
        query_embedding = self.create_embedding(query_text)
        if not query_embedding:
            print("❌ Could not create query embedding")
            return

        try:
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        fe.analysis_id,
                        fe.qa_text,
                        fa.category,
                        1 - (fe.embedding <=> %s) AS similarity_score
                    FROM forum_embeddings fe
                    JOIN forum_analysis fa ON fe.analysis_id = fa.id
                    ORDER BY fe.embedding <=> %s
                    LIMIT %s
                """, (query_embedding, query_embedding, limit))
                
                results = cursor.fetchall()
                
                print(f"\n📊 Top {len(results)} similar Q&As:")
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. Similarity: {result['similarity_score']:.3f} | Category: {result['category']}")
                    print(f"   {result['qa_text'][:200]}...")
                    
        except Exception as e:
            print(f"❌ Search error: {e}")


def main():
    parser = argparse.ArgumentParser(description="Create embeddings for forum Q&A pairs")
    parser.add_argument("--max-items", type=int, help="Maximum number of items to process (for testing)")
    parser.add_argument("--test-search", help="Test similarity search with this query")
    
    args = parser.parse_args()
    
    # Database configuration from environment
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('DB_SSLMODE', 'require')
    }
    
    # Validate configuration
    if not all([db_config['host'], db_config['database'], db_config['user'], db_config['password']]):
        print("❌ Database configuration incomplete. Please set environment variables:")
        print("   Required: DB_HOST, DB_DATABASE, DB_USERNAME, DB_PASSWORD")
        sys.exit(1)
        
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key required. Please set OPENAI_API_KEY environment variable.")
        sys.exit(1)

    try:
        creator = ForumEmbeddingsCreator(db_config=db_config)
        creator.connect_db()
        
        if args.test_search:
            # Test similarity search
            creator.similarity_search_example(args.test_search)
        else:
            # Create embeddings
            creator.process_embeddings(max_items=args.max_items)
        
        print("✅ Process completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


# USAGE EXAMPLES:
#
# Create embeddings for all Q&A pairs:
# python scripts/create_embeddings.py
#
# Process only first 10 items (for testing):
# python scripts/create_embeddings.py --max-items 10
#
# Test similarity search:
# python scripts/create_embeddings.py --test-search "How do I sync to Garmin?"
#
# SIMILARITY SEARCH IN OTHER SCRIPTS:
#
# import psycopg2
# from psycopg2.extras import RealDictCursor
# 
# def find_similar_qas(query_text: str, limit: int = 10):
#     # Create query embedding using OpenAI
#     query_embedding = create_embedding(query_text)
#     
#     # Search database
#     with psycopg2.connect(**db_config).cursor(cursor_factory=RealDictCursor) as cursor:
#         cursor.execute("""
#             SELECT 
#                 fe.analysis_id,
#                 fe.qa_text,
#                 fa.category,
#                 1 - (fe.embedding <=> %s) AS similarity_score
#             FROM forum_embeddings fe
#             JOIN forum_analysis fa ON fe.analysis_id = fa.id
#             WHERE 1 - (fe.embedding <=> %s) > 0.7  -- Similarity threshold
#             ORDER BY fe.embedding <=> %s
#             LIMIT %s
#         """, (query_embedding, query_embedding, query_embedding, limit))
#         
#         return cursor.fetchall()