#!/usr/bin/env python3
"""
Search blog content using semantic search
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
import argparse

load_dotenv()

def search_blog_content(query: str, limit: int = 5):
    """Search blog content with semantic similarity"""
    
    # Database configuration
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('DB_SSLMODE', 'require')
    }
    
    print(f"🔍 Searching blog content for: '{query}'")
    
    try:
        # Create query embedding
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
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
            
            cursor.execute("""
                SELECT 
                    source, source_id, title, content, metadata, chunk_index,
                    1 - (embedding <=> %s::vector) AS similarity_score
                FROM content_embeddings
                WHERE source = 'blog'
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, (query_embedding, query_embedding, limit))
            
            results = cursor.fetchall()
            
            print(f"\n📊 Found {len(results)} similar results:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result['title']}")
                print(f"   Similarity: {result['similarity_score']:.3f}")
                print(f"   Content: {result['content'][:200]}...")
                
                # Show blog metadata if available
                if result['metadata']:
                    metadata = result['metadata']
                    category = metadata.get('category', 'Unknown')
                    date = metadata.get('date', 'Unknown')
                    tags = metadata.get('tags', [])
                    
                    print(f"   📂 Category: {category}")
                    print(f"   📅 Date: {date}")
                    if tags:
                        print(f"   🏷️ Tags: {', '.join(tags)}")
        
        conn.close()
        print(f"\n✅ Search completed successfully!")
        return results
        
    except Exception as e:
        print(f"❌ Search error: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    parser = argparse.ArgumentParser(description="Search blog content semantically")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", type=int, default=5, help="Number of results to return")
    
    args = parser.parse_args()
    
    search_blog_content(args.query, args.limit)

if __name__ == "__main__":
    main()

# USAGE EXAMPLES:
#
# python scripts/search_blog.py "FTP testing methods"
# python scripts/search_blog.py "indoor training setup" --limit 10
# python scripts/search_blog.py "zone 2 training benefits"