#!/usr/bin/env python3
"""
Debug the vector search issue
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

def debug_vector_search():
    """Debug the vector search functionality"""
    
    # Database configuration
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('DB_SSLMODE', 'require')
    }
    
    try:
        # Connect to database
        conn = psycopg2.connect(**db_config)
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            
            # Check the embedding column type and sample data
            print("🔍 Debugging Vector Search Issue")
            print("=" * 40)
            
            # Check column information
            cursor.execute("""
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns
                WHERE table_name = 'content_embeddings' AND column_name = 'embedding'
            """)
            
            column_info = cursor.fetchone()
            print(f"Embedding column info: {column_info}")
            
            # Check if pgvector extension is properly loaded
            cursor.execute("SELECT extname FROM pg_extension WHERE extname = 'vector'")
            vector_ext = cursor.fetchone()
            print(f"pgvector extension: {'✅ Installed' if vector_ext else '❌ Not found'}")
            
            # Get a sample embedding to check format
            cursor.execute("""
                SELECT id, source, title, embedding
                FROM content_embeddings
                WHERE source = 'youtube'
                LIMIT 1
            """)
            
            sample = cursor.fetchone()
            if sample:
                print(f"\nSample record:")
                print(f"ID: {sample['id']}")
                print(f"Title: {sample['title']}")
                print(f"Embedding type: {type(sample['embedding'])}")
                print(f"Embedding length: {len(sample['embedding']) if hasattr(sample['embedding'], '__len__') else 'N/A'}")
                
                # Try to test vector operations
                try:
                    cursor.execute("""
                        SELECT embedding <-> embedding as distance
                        FROM content_embeddings
                        WHERE id = %s
                    """, (sample['id'],))
                    
                    distance = cursor.fetchone()
                    print(f"Self-distance test: {distance['distance']}")
                    
                except Exception as e:
                    print(f"Vector operation error: {e}")
            else:
                print("No sample records found")
                
            # Test OpenAI embedding creation
            print(f"\n🤖 Testing OpenAI Embedding Creation")
            print("=" * 40)
            
            client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            try:
                response = client.embeddings.create(
                    model="text-embedding-3-large",
                    input="test query for power zones"
                )
                
                embedding = response.data[0].embedding
                print(f"OpenAI embedding dimensions: {len(embedding)}")
                print(f"Sample values: {embedding[:5]}")
                
                # Try inserting this embedding
                cursor.execute("""
                    SELECT embedding <-> %s::vector as distance
                    FROM content_embeddings
                    WHERE source = 'youtube'
                    LIMIT 1
                """, (embedding,))
                
                result = cursor.fetchone()
                print(f"Distance calculation test: {result['distance'] if result else 'Failed'}")
                
            except Exception as e:
                print(f"OpenAI embedding error: {e}")
                
    except Exception as e:
        print(f"❌ Database error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    debug_vector_search()