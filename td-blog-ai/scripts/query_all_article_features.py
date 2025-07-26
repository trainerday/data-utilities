#!/usr/bin/env python3
"""
Query LlamaIndex for features from article-queries markdown files
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from llama_index.embeddings.openai import OpenAIEmbedding
import time

load_dotenv()

class ComprehensiveWorkoutQuery:
    def __init__(self, query_file=None):
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
        
        # Load queries from markdown file if provided
        if query_file:
            self.query_filename = query_file
            self.all_features = self.load_queries_from_markdown(query_file)
        else:
            print("❌ Error: No query file specified")
            print("Usage: python query_all_article_features.py <query-file-name>")
            print("Example: python query_all_article_features.py workout-queries")
            sys.exit(1)
    
    def load_queries_from_markdown(self, query_file):
        """Load queries from a markdown file in article-queries directory"""
        file_path = Path(f"./article-queries/{query_file}.md")
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            sys.exit(1)
        
        print(f"📄 Loading queries from: {file_path}")
        
        features = {}
        current_category = None
        current_feature = None
        current_queries = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and main title
                if not line or line.startswith('# '):
                    continue
                
                # Category (## heading)
                if line.startswith('## '):
                    # Save previous feature if exists
                    if current_feature and current_queries:
                        if current_category not in features:
                            features[current_category] = {}
                        features[current_category][current_feature] = current_queries
                        current_queries = []
                    
                    current_category = line[3:].strip()
                    current_feature = None
                
                # Feature (### heading)
                elif line.startswith('### '):
                    # Save previous feature if exists
                    if current_feature and current_queries:
                        if current_category not in features:
                            features[current_category] = {}
                        features[current_category][current_feature] = current_queries
                        current_queries = []
                    
                    current_feature = line[4:].strip()
                
                # Query (- bullet point)
                elif line.startswith('- ') and line[2:].strip():
                    query = line[2:].strip().strip('"')  # Remove quotes if present
                    current_queries.append(query)
        
        # Save last feature
        if current_feature and current_queries and current_category:
            if current_category not in features:
                features[current_category] = {}
            features[current_category][current_feature] = current_queries
        
        return features
    
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
                                (metadata_->>'source' = 'facts' AND embedding <=> %s::vector <= 0.75) OR
                                (metadata_->>'source' = 'blog' AND embedding <=> %s::vector <= 0.75) OR
                                (metadata_->>'source' = 'youtube' AND embedding <=> %s::vector <= 0.8) OR
                                (metadata_->>'source' = 'forum' AND embedding <=> %s::vector <= 0.85)
                            )
                        )
                        SELECT * FROM ranked_results
                        ORDER BY distance
                        LIMIT 30
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
        output_dir = Path("./article-temp-files")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / "article_features.json"
        
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
    # Check for command-line argument
    if len(sys.argv) > 1:
        query_file = sys.argv[1]
        print(f"Using query file: {query_file}")
        querier = ComprehensiveWorkoutQuery(query_file=query_file)
        querier.query_all_features()
    else:
        # Initialize with None to trigger error message
        ComprehensiveWorkoutQuery()