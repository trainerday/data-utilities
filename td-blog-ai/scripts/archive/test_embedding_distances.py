#!/usr/bin/env python3
"""
Test embedding distances to understand why queries aren't matching
"""

import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from llama_index.embeddings.openai import OpenAIEmbedding

load_dotenv()

class EmbeddingDistanceTester:
    def __init__(self):
        self.embedding_model = OpenAIEmbedding(
            model="text-embedding-3-large",
            dimensions=1536
        )
        
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'trainerday_local',
            'user': os.getenv('USER', 'alex'),
            'password': '',
        }
    
    def test_known_content(self):
        """Test queries against content we know exists"""
        
        # Test queries for content we know exists
        test_cases = [
            {
                'query': 'The Fastest Workout Editor',
                'expected': 'blog article about fastest workout editor'
            },
            {
                'query': 'Learn About Interval Comments',
                'expected': 'blog article about interval comments'
            },
            {
                'query': 'fastest workout editor',
                'expected': 'same as title but lowercase'
            },
            {
                'query': 'interval comments',
                'expected': 'generic query for interval comments'
            },
            {
                'query': 'workout editor Excel',
                'expected': 'query mentioning Excel functionality'
            }
        ]
        
        conn = psycopg2.connect(**self.db_config)
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                for test in test_cases:
                    print(f"\n{'='*60}")
                    print(f"Testing: {test['query']}")
                    print(f"Expected: {test['expected']}")
                    print('='*60)
                    
                    # Get embedding
                    query_embedding = self.embedding_model.get_text_embedding(test['query'])
                    
                    # Query WITHOUT distance filter to see all distances
                    cur.execute("""
                        SELECT 
                            text,
                            metadata_->>'title' as title,
                            metadata_->>'source' as source,
                            embedding <=> %s::vector as distance
                        FROM llamaindex_knowledge_base 
                        WHERE embedding IS NOT NULL
                        AND (
                            text ILIKE %s OR 
                            metadata_->>'title' ILIKE %s
                        )
                        ORDER BY embedding <=> %s::vector
                        LIMIT 10
                    """, (query_embedding, f"%{test['query']}%", f"%{test['query']}%", query_embedding))
                    
                    results = cur.fetchall()
                    
                    if results:
                        print(f"\nFound {len(results)} text matches:")
                        for i, r in enumerate(results[:5]):
                            print(f"\n{i+1}. Distance: {r['distance']:.4f} | Source: {r['source']}")
                            print(f"   Title: {r['title']}")
                            print(f"   Text: {r['text'][:150]}...")
                    else:
                        print("No text matches found!")
                    
                    # Now check top semantic matches regardless of text
                    cur.execute("""
                        SELECT 
                            text,
                            metadata_->>'title' as title,
                            metadata_->>'source' as source,
                            embedding <=> %s::vector as distance
                        FROM llamaindex_knowledge_base 
                        WHERE embedding IS NOT NULL
                        ORDER BY embedding <=> %s::vector
                        LIMIT 5
                    """, (query_embedding, query_embedding))
                    
                    semantic_results = cur.fetchall()
                    
                    print(f"\nTop 5 semantic matches (any content):")
                    for i, r in enumerate(semantic_results):
                        print(f"\n{i+1}. Distance: {r['distance']:.4f} | Source: {r['source']}")
                        print(f"   Title: {r['title']}")
                        print(f"   Text: {r['text'][:150]}...")
                
                # Check distance distribution
                print(f"\n\n{'='*60}")
                print("DISTANCE DISTRIBUTION ANALYSIS")
                print('='*60)
                
                cur.execute("""
                    SELECT 
                        metadata_->>'source' as source,
                        COUNT(*) as total_count,
                        MIN(LENGTH(text)) as min_length,
                        MAX(LENGTH(text)) as max_length,
                        AVG(LENGTH(text))::int as avg_length
                    FROM llamaindex_knowledge_base
                    WHERE embedding IS NOT NULL
                    GROUP BY metadata_->>'source'
                    ORDER BY source
                """)
                
                for row in cur.fetchall():
                    print(f"\n{row['source'].upper()}:")
                    print(f"  Count: {row['total_count']}")
                    print(f"  Text length - Min: {row['min_length']}, Max: {row['max_length']}, Avg: {row['avg_length']}")
                    
        finally:
            conn.close()

if __name__ == "__main__":
    tester = EmbeddingDistanceTester()
    tester.test_known_content()