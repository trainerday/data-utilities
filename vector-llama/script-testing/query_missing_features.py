#!/usr/bin/env python3
"""
Query for missing workout features content
"""

import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from llama_index.embeddings.openai import OpenAIEmbedding

load_dotenv()

class MissingFeaturesQuery:
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
        
        # Missing features to query
        self.missing_features = {
            "Training Execution & Real-time Features (Additional)": {
                "Training Effect Integration": [
                    "Garmin training effect",
                    "training effect monitoring",
                    "intensity adjustment"
                ],
                "ERG Spiral Recovery": [
                    "ERG spiral recovery",
                    "low-cadence resistance",
                    "cadence recovery"
                ],
                "Ride Feel Adjustment": [
                    "ride feel adjustment",
                    "Coach Jack ride feel",
                    "intensity modification"
                ],
                "FTP-based Scaling": [
                    "FTP-based scaling",
                    "fitness-based adjustment",
                    "workout scaling"
                ],
                "Zone 2 Testing": [
                    "zone 2 testing",
                    "aerobic testing",
                    "heart rate zones"
                ]
            },
            "Real-time Display & Monitoring (Additional)": {
                "YouTube Integration": [
                    "YouTube integration",
                    "embedded video",
                    "entertainment during training"
                ],
                "Secret URL Sharing": [
                    "secret URL sharing",
                    "live data sharing",
                    "coach viewing"
                ],
                "Training Data Visualization": [
                    "training data visualization",
                    "power curves",
                    "interval analysis"
                ]
            },
            "Workout Organization & Management": {
                "Training App Shortcuts": [
                    "training app shortcuts",
                    "quick access",
                    "frequently used workouts"
                ],
                "Bulk Workout Operations": [
                    "bulk workout operations",
                    "batch editing",
                    "mass management"
                ],
                "Workout History Tracking": [
                    "workout history tracking",
                    "completed workouts",
                    "progression tracking"
                ],
                "Hierarchical Tag Structures": [
                    "hierarchical tag structures",
                    "organized categories",
                    "export platforms"
                ]
            },
            "Community & Sharing Features": {
                "Coach-Athlete Sharing": [
                    "coach-athlete sharing",
                    "coaching relationships",
                    "training partnerships"
                ],
                "Workout Link Sharing": [
                    "workout link sharing",
                    "direct workout links",
                    "easy sharing"
                ],
                "Community Contributions": [
                    "community contributions",
                    "public workout library",
                    "shared content"
                ]
            }
        }
    
    def query_feature(self, feature_name, queries, category):
        """Query for a specific feature"""
        
        conn = psycopg2.connect(**self.db_config)
        all_results = []
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                for query in queries:
                    query_embedding = self.embedding_model.get_text_embedding(query)
                    
                    cur.execute("""
                        WITH ranked_results AS (
                            SELECT 
                                text,
                                metadata_->>'title' as title,
                                metadata_->>'source' as source,
                                metadata_->>'url' as url,
                                embedding <=> %s::vector as distance
                            FROM llamaindex_knowledge_base 
                            WHERE embedding IS NOT NULL
                            AND (
                                (metadata_->>'source' = 'facts' AND embedding <=> %s::vector <= 0.6) OR
                                (metadata_->>'source' = 'blog' AND embedding <=> %s::vector <= 0.6) OR
                                (metadata_->>'source' = 'youtube' AND embedding <=> %s::vector <= 0.65) OR
                                (metadata_->>'source' = 'forum' AND embedding <=> %s::vector <= 0.7)
                            )
                        )
                        SELECT * FROM ranked_results
                        ORDER BY distance
                        LIMIT 5
                    """, (query_embedding, query_embedding, query_embedding, query_embedding, query_embedding))
                    
                    results = cur.fetchall()
                    all_results.extend(results)
                    
        finally:
            conn.close()
        
        # Deduplicate
        unique_results = []
        seen_texts = set()
        
        for result in all_results:
            text_key = result['text'][:200]
            if text_key not in seen_texts:
                seen_texts.add(text_key)
                unique_results.append({
                    'feature': feature_name,
                    'category': category,
                    'text': result['text'],
                    'title': result['title'],
                    'source': result['source'],
                    'url': result['url'],
                    'distance': result['distance']
                })
        
        return unique_results
    
    def query_all_missing_features(self):
        """Query for all missing features"""
        
        print("🚀 Querying for missing workout features...")
        
        all_results = {}
        
        for category, features in self.missing_features.items():
            print(f"\n📁 Category: {category}")
            category_results = {}
            
            for feature_name, queries in features.items():
                print(f"  🔍 Querying: {feature_name}")
                
                results = self.query_feature(feature_name, queries, category)
                category_results[feature_name] = results
                
                # Summary
                sources = {}
                for r in results:
                    source = r['source']
                    sources[source] = sources.get(source, 0) + 1
                
                print(f"    Found: {' | '.join([f'{s}: {c}' for s, c in sources.items()])}")
            
            all_results[category] = category_results
        
        # Save results
        output_file = Path("./script-testing/workout_comprehensive_results/missing_features_results.json")
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2)
        
        print(f"\n✅ Results saved to: {output_file}")
        
        return all_results

if __name__ == "__main__":
    querier = MissingFeaturesQuery()
    querier.query_all_missing_features()