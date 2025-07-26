#!/usr/bin/env python3
"""
Simple Workout Features Query - Demonstrates priority-based retrieval
"""

import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from llama_index.embeddings.openai import OpenAIEmbedding

load_dotenv()

def query_workout_features():
    """Query workout features with priority-based thresholds"""
    
    # Setup
    embedding_model = OpenAIEmbedding(model="text-embedding-3-large", dimensions=1536)
    
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'trainerday_local',
        'user': os.getenv('USER', 'alex'),
        'password': '',
    }
    
    # Example queries from workouts.md
    queries = {
        "Visual Workout Editor": '"workout editor" OR "visual workout builder" OR "drag-and-drop interface"',
        "ERG Mode": '"ERG mode" OR "automatic power control" OR "power targeting"',
        "Garmin Integration": '"Garmin Connect" OR "device sync" OR "calendar integration"',
        "Coach Jack": '"Coach Jack" OR "adaptive training" OR "training plans"',
        "Workout Sharing": '"workout sharing" OR "community library" OR "public workouts"'
    }
    
    conn = psycopg2.connect(**db_config)
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            for feature_name, query_text in queries.items():
                print(f"\n{'='*80}")
                print(f"🔍 FEATURE: {feature_name}")
                print(f"Query: {query_text}")
                print(f"{'='*80}")
                
                # Get embedding
                query_embedding = embedding_model.get_text_embedding(query_text)
                
                # Query with priority thresholds
                cur.execute("""
                    WITH ranked_results AS (
                        SELECT 
                            text,
                            metadata_->>'title' as title,
                            metadata_->>'source' as source,
                            metadata_->>'priority' as priority,
                            metadata_->>'content_type' as content_type,
                            metadata_->>'similarity_threshold' as threshold,
                            embedding <=> %s::vector as distance
                        FROM llamaindex_knowledge_base 
                        WHERE embedding IS NOT NULL
                    )
                    SELECT * FROM ranked_results
                    WHERE 
                        (source = 'facts' AND distance <= 0.2) OR
                        (source IN ('blog', 'youtube') AND distance <= 0.3) OR
                        (source = 'forum' AND content_type LIKE '%%qa%%' AND distance <= 0.4) OR
                        (source = 'forum' AND content_type NOT LIKE '%%qa%%' AND distance <= 0.6)
                    ORDER BY 
                        CASE 
                            WHEN source = 'facts' THEN 1
                            WHEN source = 'blog' THEN 2
                            WHEN source = 'youtube' THEN 3
                            WHEN source = 'forum' AND content_type LIKE '%%qa%%' THEN 4
                            WHEN source = 'forum' THEN 5
                        END,
                        distance
                    LIMIT 10
                """, (query_embedding,))
                
                results = cur.fetchall()
                
                if results:
                    print(f"\n📊 Found {len(results)} results (showing by priority):\n")
                    
                    current_source = None
                    for result in results:
                        if result['source'] != current_source:
                            current_source = result['source']
                            print(f"\n{current_source.upper()} (Priority: {result['priority']}):")
                            print("-" * 40)
                        
                        print(f"• {result['title']}")
                        print(f"  Score: {result['distance']:.3f} | Type: {result['content_type']}")
                        
                        # Show preview
                        text_preview = result['text'].replace('\n', ' ')[:150] + '...'
                        print(f"  Preview: {text_preview}\n")
                else:
                    print("❌ No results found within priority thresholds")
                    
    finally:
        conn.close()

def show_priority_system():
    """Display the priority system"""
    print("\n📋 PRIORITY-BASED RETRIEVAL SYSTEM")
    print("=" * 80)
    print("Source                  | Priority  | Threshold | Authority")
    print("-" * 80)
    print("Facts (validated)       | highest   | 0.2       | official")
    print("Facts (wrong-warnings)  | highest   | 0.2       | corrective")
    print("Blog Articles           | critical  | 0.3       | official")
    print("YouTube Transcripts     | critical  | 0.3       | official")
    print("Forum Q&A (structured)  | high      | 0.4       | community")
    print("Forum Discussions (raw) | medium    | 0.6       | community")
    print("\n✨ Lower threshold = easier to retrieve = higher priority")
    print("🎯 Official content (facts, blog) retrieved more easily than community content")

if __name__ == "__main__":
    show_priority_system()
    query_workout_features()