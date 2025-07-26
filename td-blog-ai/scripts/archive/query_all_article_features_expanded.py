#!/usr/bin/env python3
"""
Query all workout features from the vector database with expanded thresholds
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Use LlamaIndex embedding
from llama_index.embeddings.openai import OpenAIEmbedding

load_dotenv()

class WorkoutFeatureQuerier:
    def __init__(self, query_set='workout-queries'):
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'trainerday_local',
            'user': os.getenv('USER', 'alex'),
            'password': '',
            'options': '-c search_path=td-business,public'
        }
        
        self.embedding_model = OpenAIEmbedding(
            model="text-embedding-3-large",
            dimensions=1536
        )
        self.query_set = query_set
        self.all_features = self.load_features_from_markdown(f"article-queries/{query_set}.md")
    
    def load_features_from_markdown(self, file_path):
        """Load feature queries from markdown file"""
        
        features = {}
        current_category = None
        current_feature = None
        current_queries = []
        
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and main title
            if not line or line.startswith('# '):
                continue
            
            # Category headers (## headers)
            if line.startswith('## '):
                # Save previous feature if exists
                if current_feature and current_queries:
                    if current_category not in features:
                        features[current_category] = {}
                    features[current_category][current_feature] = current_queries
                
                current_category = line[3:].strip()
                current_feature = None
                current_queries = []
                continue
            
            # Feature headers (### headers)
            if line.startswith('### '):
                # Save previous feature if exists
                if current_feature and current_queries:
                    if current_category not in features:
                        features[current_category] = {}
                    features[current_category][current_feature] = current_queries
                
                current_feature = line[4:].strip()
                current_queries = []
                continue
            
            # Query lines (lines starting with -)
            if line.startswith('- "') and line.endswith('"'):
                query = line[3:-1]  # Remove - " and closing "
                current_queries.append(query)
        
        # Don't forget the last feature
        if current_feature and current_queries and current_category:
            if current_category not in features:
                features[current_category] = {}
            features[current_category][current_feature] = current_queries
        
        return features
    
    def query_feature(self, feature_name, queries, category):
        """Query for a specific feature using multiple search terms with expanded limits"""
        
        conn = psycopg2.connect(**self.db_config)
        all_results = []
        
        # EXPANDED THRESHOLDS AND LIMITS
        distance_thresholds = {
            'facts': 0.75,      # was 0.6
            'blog': 0.75,       # was 0.6
            'youtube': 0.8,     # was 0.65
            'forum': 0.85       # was 0.7
        }
        
        results_limit = 30      # was 10
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                for query in queries:
                    # Get embedding
                    query_embedding = self.embedding_model.get_text_embedding(query)
                    
                    # Query with expanded thresholds
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
                        ORDER BY distance
                        LIMIT %s
                    """, (
                        query_embedding, 
                        query_embedding, distance_thresholds['facts'],
                        query_embedding, distance_thresholds['blog'],
                        query_embedding, distance_thresholds['youtube'],
                        query_embedding, distance_thresholds['forum'],
                        results_limit
                    ))
                    
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
        
        print("🚀 Starting EXPANDED workout feature queries...")
        print(f"   Distance thresholds: facts=0.75, blog=0.75, youtube=0.8, forum=0.85")
        print(f"   Results per query: 30 (was 10)")
        
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
        output_dir = Path("./article-temp-files")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / "article_features_expanded.json"
        with open(output_file, 'w') as f:
            json.dump(all_feature_results, f, indent=2)
        
        print(f"\n✅ Results saved to: {output_file}")
        
        # Summary statistics
        total_content = 0
        content_by_source = {}
        
        for category_results in all_feature_results.values():
            for feature_results in category_results.values():
                for result in feature_results:
                    total_content += 1
                    source = result['source']
                    content_by_source[source] = content_by_source.get(source, 0) + 1
        
        print(f"\n📊 SUMMARY STATISTICS:")
        print(f"Total features queried: {total_features}")
        print(f"Features with content found: {sum(1 for cat in all_feature_results.values() for feat in cat.values() if feat)}")
        print(f"Total content pieces found: {total_content}")
        print(f"\nContent by source:")
        for source, count in sorted(content_by_source.items(), key=lambda x: x[1], reverse=True):
            print(f"  {source}: {count}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Query workout features from vector database')
    parser.add_argument('query_set', nargs='?', default='workout-queries', 
                       help='Name of the query set file (without .md extension)')
    
    args = parser.parse_args()
    
    print(f"Using query file: {args.query_set}")
    
    querier = WorkoutFeatureQuerier(args.query_set)
    querier.query_all_features()

if __name__ == "__main__":
    main()