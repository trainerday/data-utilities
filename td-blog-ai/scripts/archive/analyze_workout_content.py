#!/usr/bin/env python3
"""
Analyze what workout content we actually have in the database
"""

import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

class WorkoutContentAnalyzer:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'trainerday_local',
            'user': os.getenv('USER', 'alex'),
            'password': '',
        }
        
    def analyze_workout_content(self):
        """Find all content related to workouts"""
        
        conn = psycopg2.connect(**self.db_config)
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Search for workout-related content
                workout_keywords = [
                    'workout editor',
                    'create workout',
                    'sets and reps',
                    'interval',
                    'fastest workout',
                    'visual workout',
                    'workout creation',
                    'edit workout',
                    'clone workout',
                    'copy workout'
                ]
                
                all_results = {}
                
                for keyword in workout_keywords:
                    print(f"\n{'='*60}")
                    print(f"Searching for: '{keyword}'")
                    print('='*60)
                    
                    # Text search
                    cur.execute("""
                        SELECT 
                            text,
                            metadata_->>'title' as title,
                            metadata_->>'source' as source,
                            metadata_->>'content_type' as content_type,
                            metadata_->>'priority' as priority
                        FROM llamaindex_knowledge_base
                        WHERE text ILIKE %s
                        ORDER BY 
                            CASE metadata_->>'source'
                                WHEN 'facts' THEN 1
                                WHEN 'blog' THEN 2
                                WHEN 'youtube' THEN 3
                                WHEN 'forum' THEN 4
                            END,
                            LENGTH(text)
                        LIMIT 10
                    """, (f'%{keyword}%',))
                    
                    results = cur.fetchall()
                    all_results[keyword] = results
                    
                    print(f"Found {len(results)} results")
                    
                    # Group by source
                    by_source = {}
                    for r in results:
                        source = r['source']
                        if source not in by_source:
                            by_source[source] = []
                        by_source[source].append(r)
                    
                    # Print summary
                    for source, items in by_source.items():
                        print(f"\n{source.upper()} ({len(items)} items):")
                        for item in items[:3]:  # First 3 from each source
                            print(f"  - {item['title'] or 'No title'}")
                            print(f"    {item['text'][:150]}...")
                
                # Save detailed results
                output_file = Path("./script-testing/workout_query_results/workout_content_analysis.json")
                
                # Convert to serializable format
                serializable_results = {}
                for keyword, results in all_results.items():
                    serializable_results[keyword] = [
                        {
                            'text': r['text'][:1000],  # First 1000 chars
                            'title': r['title'],
                            'source': r['source'],
                            'content_type': r['content_type']
                        }
                        for r in results
                    ]
                
                with open(output_file, 'w') as f:
                    json.dump(serializable_results, f, indent=2)
                
                print(f"\n\n✅ Detailed results saved to: {output_file}")
                
                # Get some specific blog content
                print("\n\n📝 BLOG ARTICLES ABOUT WORKOUTS:")
                cur.execute("""
                    SELECT 
                        text,
                        metadata_->>'title' as title
                    FROM llamaindex_knowledge_base
                    WHERE metadata_->>'source' = 'blog'
                    AND (text ILIKE '%workout%' OR metadata_->>'title' ILIKE '%workout%')
                    LIMIT 5
                """)
                
                blog_results = cur.fetchall()
                for i, blog in enumerate(blog_results):
                    print(f"\n{i+1}. {blog['title']}")
                    print(f"   Content: {blog['text'][:500]}...")
                    
        finally:
            conn.close()

if __name__ == "__main__":
    analyzer = WorkoutContentAnalyzer()
    analyzer.analyze_workout_content()