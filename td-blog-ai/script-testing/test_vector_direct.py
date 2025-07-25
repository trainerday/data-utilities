#!/usr/bin/env python3
"""
Test vector similarity directly with PostgreSQL
"""

import os
import psycopg2
from dotenv import load_dotenv
from llama_index.embeddings.openai import OpenAIEmbedding

load_dotenv()

def test_vector_similarity():
    """Test vector similarity search directly"""
    
    print("🔍 DIRECT VECTOR SIMILARITY TEST")
    print("=" * 40)
    
    # Create test embedding
    embedding_model = OpenAIEmbedding(
        model="text-embedding-3-large", 
        dimensions=1536
    )
    
    test_query = "TrainerDay features"
    print(f"Creating embedding for: '{test_query}'")
    
    query_embedding = embedding_model.get_text_embedding(test_query)
    print(f"Embedding created: {len(query_embedding)} dimensions")
    
    # Connect to database
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='trainerday_local',
        user=os.getenv('USER', 'alex'),
        password=''
    )
    
    try:
        with conn.cursor() as cur:
            # Test direct vector similarity
            cur.execute("""
                SELECT 
                    metadata_->>'title' as title,
                    metadata_->>'source' as source,
                    metadata_->>'priority' as priority,
                    embedding <=> %s::vector as distance
                FROM llamaindex_knowledge_base 
                WHERE embedding IS NOT NULL
                ORDER BY distance
                LIMIT 5
            """, (query_embedding,))
            
            results = cur.fetchall()
            
            print(f"\n📊 Found {len(results)} results:")
            for i, (title, source, priority, distance) in enumerate(results):
                print(f"  {i+1}. Distance: {distance:.4f}")
                print(f"     Source: {source} ({priority})")
                print(f"     Title: {title}")
                print()
            
            if results:
                print("✅ Vector similarity search is working!")
                print("❓ Issue might be with LlamaIndex configuration")
            else:
                print("❌ No results found - vector search issue")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_vector_similarity()