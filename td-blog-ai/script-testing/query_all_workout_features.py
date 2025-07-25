#!/usr/bin/env python3
"""
Query LlamaIndex for ALL workout features from workouts.md
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

class ComprehensiveWorkoutQuery:
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
        
        # All workout features and their queries from workouts.md
        self.all_features = {
            "Workout Creation & Management": {
                "Visual Workout Editor": [
                    "visual workout editor",
                    "drag-and-drop interface", 
                    "Excel-like functionality"
                ],
                "Fastest Workout Editor": [
                    "fastest workout editor",
                    "copy paste workout",
                    "arrow keys workout",
                    "speed-focused design"
                ],
                "Sets and Reps Editor": [
                    "sets and reps editor",
                    "interval structure",
                    "complex intervals",
                    "repeated patterns"
                ],
                "Interval Comments": [
                    "interval comments",
                    "coaching notes",
                    "workout instructions",
                    "offset timing"
                ],
                "Route Importing": [
                    "route importing",
                    "GPS routes",
                    "outdoor simulation",
                    "power slope data"
                ],
                "Target Modes": [
                    "target modes",
                    "power targets",
                    "heart rate targets",
                    "slope targets"
                ],
                "Mixed-Mode Workouts": [
                    "mixed-mode workouts",
                    "automatic mode switching",
                    "switch between modes"
                ],
                "Workout Tags": [
                    "workout tags",
                    "workout organization",
                    "public private workouts"
                ],
                "Workout Cloning": [
                    "workout cloning",
                    "duplicate workouts",
                    "ALT drag",
                    "copy workout"
                ],
                "Auto-Mode Switching": [
                    "auto-mode switching",
                    "automatically switch",
                    "slope to ERG",
                    "HR modes"
                ],
                "Ramps and Steps": [
                    "ramps and steps",
                    "gradual power",
                    "progressive intervals",
                    "Garmin conversion"
                ],
                "Free Ride Intervals": [
                    "free ride intervals",
                    "open-ended intervals",
                    "lap button control",
                    "manual stop"
                ],
                "W'bal Integration": [
                    "W'bal integration",
                    "anaerobic capacity",
                    "interval design",
                    "W prime"
                ],
                "Multi-Sport Workouts": [
                    "multi-sport workouts",
                    "cycling rowing swimming",
                    "sport-specific targeting"
                ]
            },
            "Training Modes": {
                "ERG Mode": [
                    "ERG mode",
                    "automatic power control",
                    "power targeting",
                    "cadence gear"
                ],
                "HR+ Mode": [
                    "HR+ mode",
                    "heart rate controlled",
                    "automatic power adjustment",
                    "HR training"
                ],
                "Slope Mode": [
                    "slope mode",
                    "gradient simulation",
                    "gear control",
                    "automatic slope"
                ],
                "Resistance Mode": [
                    "resistance mode",
                    "fixed resistance",
                    "sprint training",
                    "strength work"
                ]
            },
            "Training Execution": {
                "Real-time Training": [
                    "real-time training",
                    "live workout execution",
                    "smart trainer control"
                ],
                "6-Second Warmup": [
                    "6-second warmup",
                    "quick start",
                    "ultra-fast start"
                ],
                "Dynamic Workout Editing": [
                    "dynamic workout editing",
                    "on-the-fly modifications",
                    "mid-workout changes"
                ],
                "Power Adjustments": [
                    "power adjustments",
                    "intensity controls",
                    "+/- buttons",
                    "10-second increments"
                ],
                "Hot Swap Feature": [
                    "hot swap",
                    "change workouts mid-session",
                    "workout switching"
                ]
            },
            "Display & Monitoring": {
                "Broadcast to Big Screen": [
                    "broadcast to big screen",
                    "cast training data",
                    "external displays"
                ],
                "Live Training Display": [
                    "live training display",
                    "real-time viewing",
                    "workout monitoring"
                ],
                "Real-time Metrics": [
                    "real-time metrics",
                    "power HR cadence",
                    "live data"
                ]
            },
            "Workout Library": {
                "Community Workout Library": [
                    "community workout library",
                    "user-created workouts",
                    "shared workouts"
                ],
                "30000+ Workouts": [
                    "open source workouts",
                    "ERGdb integration",
                    "free workouts"
                ],
                "Workout Search": [
                    "workout search filtering",
                    "tags difficulty type",
                    "sport duration"
                ],
                "Workout Rating": [
                    "workout rating system",
                    "popularity rankings",
                    "community ratings"
                ]
            },
            "Export & Integration": {
                "Multi-Format Export": [
                    "multi-format export",
                    "TCX ZWO MRC ERG",
                    "workout formats"
                ],
                "Garmin Connect": [
                    "Garmin Connect",
                    "device sync",
                    "calendar integration",
                    "step optimization"
                ],
                "TrainingPeaks": [
                    "TrainingPeaks",
                    "workout distribution",
                    "calendar sync"
                ],
                "Zwift Integration": [
                    "Zwift integration",
                    "structured workout export",
                    "free-ride mode"
                ],
                "Intervals.icu": [
                    "Intervals.icu",
                    "WOD integration",
                    "calendar sync"
                ]
            }
        }
    
    def query_feature(self, feature_name, queries, category):
        """Query for a specific feature using multiple search terms"""
        
        conn = psycopg2.connect(**self.db_config)
        all_results = []
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                for query in queries:
                    # Get embedding
                    query_embedding = self.embedding_model.get_text_embedding(query)
                    
                    # Query with priority thresholds
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
                                (metadata_->>'source' = 'facts' AND embedding <=> %s::vector <= 0.6) OR
                                (metadata_->>'source' = 'blog' AND embedding <=> %s::vector <= 0.6) OR
                                (metadata_->>'source' = 'youtube' AND embedding <=> %s::vector <= 0.65) OR
                                (metadata_->>'source' = 'forum' AND embedding <=> %s::vector <= 0.7)
                            )
                        )
                        SELECT * FROM ranked_results
                        ORDER BY distance
                        LIMIT 10
                    """, (query_embedding, query_embedding, query_embedding, query_embedding, query_embedding))
                    
                    results = cur.fetchall()
                    all_results.extend(results)
                    
        finally:
            conn.close()
        
        # Deduplicate results
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
    
    def query_all_features(self):
        """Query for all workout features"""
        
        print("🚀 Starting comprehensive workout feature queries...")
        
        all_feature_results = {}
        feature_count = 0
        total_features = sum(len(features) for features in self.all_features.values())
        
        for category, features in self.all_features.items():
            print(f"\n📁 Category: {category}")
            category_results = {}
            
            for feature_name, queries in features.items():
                feature_count += 1
                print(f"  [{feature_count}/{total_features}] Querying: {feature_name}")
                
                results = self.query_feature(feature_name, queries, category)
                category_results[feature_name] = results
                
                # Summary
                sources = {}
                for r in results:
                    source = r['source']
                    sources[source] = sources.get(source, 0) + 1
                
                print(f"    Found: {' | '.join([f'{s}: {c}' for s, c in sources.items()])}")
                
                # Small delay to avoid overwhelming the database
                time.sleep(0.1)
            
            all_feature_results[category] = category_results
        
        # Save results
        output_dir = Path("./script-testing/workout_comprehensive_results")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f"all_workout_features_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_feature_results, f, indent=2)
        
        print(f"\n✅ Results saved to: {output_file}")
        
        # Generate summary statistics
        self.generate_summary(all_feature_results)
        
        return all_feature_results
    
    def generate_summary(self, results):
        """Generate summary statistics"""
        
        total_results = 0
        source_counts = {}
        features_with_content = 0
        
        for category, features in results.items():
            for feature, feature_results in features.items():
                if feature_results:
                    features_with_content += 1
                    total_results += len(feature_results)
                    
                    for result in feature_results:
                        source = result['source']
                        source_counts[source] = source_counts.get(source, 0) + 1
        
        print("\n📊 SUMMARY STATISTICS:")
        print(f"Total features queried: {sum(len(f) for f in self.all_features.values())}")
        print(f"Features with content found: {features_with_content}")
        print(f"Total content pieces found: {total_results}")
        print("\nContent by source:")
        for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {source}: {count}")

if __name__ == "__main__":
    querier = ComprehensiveWorkoutQuery()
    querier.query_all_features()