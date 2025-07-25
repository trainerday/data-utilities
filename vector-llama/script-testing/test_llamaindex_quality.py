#!/usr/bin/env python3
"""
Test LlamaIndex query quality with different approaches
"""

import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from llama_index.embeddings.openai import OpenAIEmbedding
# We'll test without the KB class for now

load_dotenv()

class LlamaIndexQualityTester:
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
        
        # Initialize the actual knowledge base
        # self.kb = TrainerDayKnowledgeBase()
        
    def test_direct_db_query(self, query_text, limit=10):
        """Test direct database query"""
        print(f"\n📊 Testing direct DB query: '{query_text}'")
        
        conn = psycopg2.connect(**self.db_config)
        results = []
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get embedding
                query_embedding = self.embedding_model.get_text_embedding(query_text)
                
                # Query without distance filters to see what's there
                cur.execute("""
                    SELECT 
                        text,
                        metadata_->>'title' as title,
                        metadata_->>'source' as source,
                        metadata_->>'priority' as priority,
                        metadata_->>'content_type' as content_type,
                        metadata_->>'url' as url,
                        embedding <=> %s::vector as distance
                    FROM llamaindex_knowledge_base 
                    WHERE embedding IS NOT NULL
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                """, (query_embedding, query_embedding, limit))
                
                results = cur.fetchall()
                
                print(f"Found {len(results)} results")
                for i, r in enumerate(results):
                    print(f"\n{i+1}. Distance: {r['distance']:.3f} | Source: {r['source']} | Title: {r['title']}")
                    print(f"   Content preview: {r['text'][:150]}...")
                    
        finally:
            conn.close()
            
        return results
    
    def test_kb_fact_extraction(self, query):
        """Test the knowledge base fact extraction"""
        # Skip for now
        return []
    
    def test_kb_blog_search(self, query):
        """Test the knowledge base blog search"""
        # Skip for now
        return []
    
    def test_different_queries(self):
        """Test various query approaches"""
        
        test_queries = [
            # Original queries
            "workout editor",
            "fastest workout editor",
            "sets and reps",
            
            # More specific queries
            "how to create a workout in trainerday",
            "trainerday workout creation tutorial",
            "excel like workout editor",
            
            # Broader queries
            "workout",
            "create workout",
            "edit workout",
            
            # Feature-specific
            "interval comments",
            "copy paste workout",
            "keyboard shortcuts workout"
        ]
        
        results_summary = {}
        
        for query in test_queries:
            print(f"\n{'='*80}")
            print(f"TESTING: {query}")
            print('='*80)
            
            # Test direct DB
            db_results = self.test_direct_db_query(query, limit=5)
            
            # Test KB methods
            facts = self.test_kb_fact_extraction(query)
            blog_results = self.test_kb_blog_search(query)
            
            results_summary[query] = {
                'db_count': len(db_results),
                'db_best_distance': db_results[0]['distance'] if db_results else None,
                'facts_count': len(facts),
                'blog_count': len(blog_results)
            }
        
        # Save summary
        output_file = Path("./script-testing/workout_query_results/quality_test_summary.json")
        with open(output_file, 'w') as f:
            json.dump(results_summary, f, indent=2)
            
        print(f"\n\n📊 SUMMARY saved to: {output_file}")
        
        # Print summary
        print("\n📈 Query Quality Summary:")
        print("-" * 60)
        for query, stats in results_summary.items():
            print(f"\n'{query}':")
            print(f"  DB results: {stats['db_count']} (best distance: {stats['db_best_distance']:.3f if stats['db_best_distance'] else 'N/A'})")
            print(f"  Facts: {stats['facts_count']}")
            print(f"  Blog results: {stats['blog_count']}")
    
    def check_content_stats(self):
        """Check what content is actually in the database"""
        print("\n📊 DATABASE CONTENT STATISTICS:")
        
        conn = psycopg2.connect(**self.db_config)
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Count by source
                cur.execute("""
                    SELECT 
                        metadata_->>'source' as source,
                        COUNT(*) as count
                    FROM llamaindex_knowledge_base
                    WHERE embedding IS NOT NULL
                    GROUP BY metadata_->>'source'
                    ORDER BY count DESC
                """)
                
                print("\nContent by source:")
                for row in cur.fetchall():
                    print(f"  {row['source']}: {row['count']} documents")
                
                # Sample content with 'workout' in text
                cur.execute("""
                    SELECT 
                        text,
                        metadata_->>'title' as title,
                        metadata_->>'source' as source
                    FROM llamaindex_knowledge_base
                    WHERE text ILIKE '%workout%'
                    LIMIT 10
                """)
                
                print(f"\nSample content containing 'workout':")
                results = cur.fetchall()
                for i, row in enumerate(results):
                    print(f"\n{i+1}. [{row['source']}] {row['title']}")
                    print(f"   {row['text'][:200]}...")
                    
        finally:
            conn.close()

if __name__ == "__main__":
    tester = LlamaIndexQualityTester()
    
    # Check what's in the database
    tester.check_content_stats()
    
    # Test different queries
    tester.test_different_queries()