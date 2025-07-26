#!/usr/bin/env python3
"""
Query workout features with optimized distance thresholds based on testing
"""

import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from llama_index.embeddings.openai import OpenAIEmbedding
import time

load_dotenv()

class OptimizedWorkoutQuery:
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
        
        # OPTIMIZED thresholds based on testing
        # Generic queries need much higher thresholds
        self.thresholds = {
            'facts': 0.6,      # Was 0.25, increased for generic queries
            'blog': 0.6,       # Was 0.35, increased significantly
            'youtube': 0.65,   # Was 0.4, increased
            'forum': 0.7       # Was 0.5, increased
        }
        
        # Sample of key features to test
        self.test_features = {
            "Workout Creation": {
                "Visual Workout Editor": [
                    "visual workout editor",
                    "drag and drop workout",
                    "graphical workout interface"
                ],
                "Fastest Workout Editor": [
                    "fastest workout editor",
                    "Excel-like workout editor",
                    "copy paste workout editor",
                    "keyboard shortcuts workout"
                ],
                "Interval Comments": [
                    "interval comments",
                    "workout coaching notes",
                    "interval instructions",
                    "ZWO file comments"
                ],
                "W'bal Integration": [
                    "W'bal",
                    "W prime",
                    "anaerobic capacity",
                    "interval design W'bal"
                ]
            }
        }
    
    def query_with_optimized_thresholds(self, query_text):
        """Query with optimized distance thresholds"""
        
        conn = psycopg2.connect(**self.db_config)
        results = []
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get embedding
                query_embedding = self.embedding_model.get_text_embedding(query_text)
                
                # Query with optimized thresholds
                cur.execute("""
                    WITH ranked_results AS (
                        SELECT 
                            text,
                            metadata_->>'title' as title,
                            metadata_->>'source' as source,
                            metadata_->>'url' as url,
                            metadata_->>'content_type' as content_type,
                            embedding <=> %s::vector as distance
                        FROM llamaindex_knowledge_base 
                        WHERE embedding IS NOT NULL
                        AND (
                            (metadata_->>'source' = 'facts' AND embedding <=> %s::vector <= %s) OR
                            (metadata_->>'source' = 'blog' AND embedding <=> %s::vector <= %s) OR
                            (metadata_->>'source' = 'youtube' AND embedding <=> %s::vector <= %s) OR
                            (metadata_->>'source' = 'forum' AND embedding <=> %s::vector <= %s)
                        )
                    )
                    SELECT * FROM ranked_results
                    ORDER BY 
                        CASE source
                            WHEN 'blog' THEN 1
                            WHEN 'youtube' THEN 2
                            WHEN 'facts' THEN 3
                            WHEN 'forum' THEN 4
                        END,
                        distance
                    LIMIT 20
                """, (
                    query_embedding,
                    query_embedding, self.thresholds['facts'],
                    query_embedding, self.thresholds['blog'],
                    query_embedding, self.thresholds['youtube'],
                    query_embedding, self.thresholds['forum']
                ))
                
                results = cur.fetchall()
                
        finally:
            conn.close()
        
        return results
    
    def test_optimized_queries(self):
        """Test queries with optimized thresholds"""
        
        print("🚀 Testing with OPTIMIZED distance thresholds...")
        print(f"Thresholds: {self.thresholds}")
        
        all_results = {}
        
        for category, features in self.test_features.items():
            print(f"\n📁 {category}")
            category_results = {}
            
            for feature_name, queries in features.items():
                print(f"\n  🔍 {feature_name}")
                feature_results = []
                
                for query in queries:
                    results = self.query_with_optimized_thresholds(query)
                    feature_results.extend(results)
                    
                    # Summary
                    sources = {}
                    for r in results:
                        source = r['source']
                        sources[source] = sources.get(source, 0) + 1
                    
                    print(f"    Query: '{query}'")
                    print(f"    Found: {' | '.join([f'{s}: {c}' for s, c in sources.items()])}")
                    
                    # Show sample results
                    for r in results[:2]:
                        print(f"      - [{r['source']}] {r['title'] or 'No title'} (distance: {r['distance']:.3f})")
                
                # Deduplicate
                unique_results = []
                seen = set()
                for r in feature_results:
                    key = (r['source'], r['text'][:100])
                    if key not in seen:
                        seen.add(key)
                        unique_results.append(r)
                
                category_results[feature_name] = unique_results
                print(f"    Total unique results: {len(unique_results)}")
            
            all_results[category] = category_results
        
        # Save results
        output_file = Path("./script-testing/workout_comprehensive_results/optimized_query_results.json")
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2)
        
        print(f"\n✅ Results saved to: {output_file}")
        
        return all_results

if __name__ == "__main__":
    querier = OptimizedWorkoutQuery()
    results = querier.test_optimized_queries()