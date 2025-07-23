#!/usr/bin/env python3
"""
Test search functionality directly with proper embedding format
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import openai

load_dotenv()

def test_search():
    """Test search functionality"""
    
    # Database configuration
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('DB_SSLMODE', 'require')
    }
    
    # Create embedding for search query
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    query = "how to use power zones in training"
    print(f"🔍 Searching for: '{query}'")
    
    try:
        # Create query embedding
        response = client.embeddings.create(
            model=os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-large'),
            input=query,
            dimensions=int(os.getenv('OPENAI_EMBEDDING_DIMENSIONS', '1536'))
        )
        
        query_embedding = response.data[0].embedding
        print(f"✅ Query embedding created: {len(query_embedding)} dimensions")
        
        # Connect to database and search
        conn = psycopg2.connect(**db_config)
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            
            # Properly format the embedding as a vector
            cursor.execute("""
                SELECT 
                    source, source_id, title, content, metadata, chunk_index,
                    1 - (embedding <=> %s::vector) AS similarity_score
                FROM content_embeddings
                WHERE source = 'youtube'
                ORDER BY embedding <=> %s::vector
                LIMIT 5
            """, (query_embedding, query_embedding))
            
            results = cursor.fetchall()
            
            print(f"\n📊 Found {len(results)} similar results:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. [{result['source'].upper()}] {result['title']}")
                print(f"   Similarity: {result['similarity_score']:.3f}")
                print(f"   Content: {result['content'][:150]}...")
                
                # Show video metadata if available
                if result['metadata']:
                    metadata = result['metadata']
                    if 'start_time' in metadata:
                        print(f"   🎥 Timestamp: {metadata.get('start_time', 'N/A')}s")
                    if 'video_id' in metadata:
                        print(f"   🔗 Video: https://www.youtube.com/watch?v={metadata['video_id']}")
                
        conn.close()
        print("\n✅ Search completed successfully!")
        
    except Exception as e:
        print(f"❌ Search error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search()