#!/usr/bin/env python3
"""
Query Workout Features - Comprehensive search for all workout-related content
Uses priority-based retrieval to find information across all sources
"""

import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.storage.storage_context import StorageContext
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.postprocessor import SimilarityPostprocessor, MetadataReplacementPostProcessor

load_dotenv()

class WorkoutFeatureQuery:
    def __init__(self):
        # Configure LlamaIndex
        self.embedding_model = OpenAIEmbedding(
            model="text-embedding-3-large",
            dimensions=1536
        )
        Settings.embed_model = self.embedding_model
        Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0.1)
        
        # Local PostgreSQL configuration
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'trainerday_local',
            'user': os.getenv('USER', 'alex'),
            'password': '',
        }
        
        self.index = None
        self.results = {}
        
    def connect_to_index(self):
        """Connect to the unified knowledge base"""
        print("🔌 Connecting to unified knowledge base...")
        
        vector_store = PGVectorStore.from_params(
            database=self.db_config['database'],
            host=self.db_config['host'],
            password=self.db_config['password'],
            port=self.db_config['port'],
            user=self.db_config['user'],
            table_name="llamaindex_knowledge_base",
            embed_dim=1536,
        )
        
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        self.index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            storage_context=storage_context
        )
        
        print("✅ Connected successfully")
        
    def query_with_priority(self, query: str, category: str):
        """
        Query with priority-based retrieval matching the thresholds:
        - Facts: 0.2 (highest priority)
        - Blog/YouTube: 0.3 (critical priority)
        - Forum Q&A: 0.4 (high priority)
        - Forum Raw: 0.6 (medium priority)
        """
        
        # Create query engine with multiple postprocessors for different priorities
        query_engine = self.index.as_query_engine(
            similarity_top_k=20,  # Get more candidates for filtering
            response_mode="no_text",  # Just retrieve, don't synthesize
            node_postprocessors=[
                # This will filter based on similarity scores
                # Lower scores = more similar (using cosine distance)
            ]
        )
        
        # Get raw nodes for manual filtering
        response = query_engine.query(query)
        
        filtered_results = {
            'facts': [],
            'blog': [],
            'youtube': [],
            'forum_qa': [],
            'forum_raw': []
        }
        
        if hasattr(response, 'source_nodes'):
            for node in response.source_nodes:
                metadata = node.metadata
                source = metadata.get('source', '')
                content_type = metadata.get('content_type', '')
                priority = metadata.get('priority', '')
                similarity_threshold = float(metadata.get('similarity_threshold', 1.0))
                
                # Get similarity score (distance)
                score = getattr(node, 'score', 1.0)
                
                # Apply threshold based on content type
                if score <= similarity_threshold:
                    result = {
                        'text': node.text[:500] + '...' if len(node.text) > 500 else node.text,
                        'title': metadata.get('title', 'Unknown'),
                        'score': score,
                        'priority': priority,
                        'content_type': content_type
                    }
                    
                    if source == 'facts':
                        filtered_results['facts'].append(result)
                    elif source == 'blog':
                        filtered_results['blog'].append(result)
                    elif source == 'youtube':
                        filtered_results['youtube'].append(result)
                    elif source == 'forum' and 'qa' in content_type:
                        filtered_results['forum_qa'].append(result)
                    elif source == 'forum':
                        filtered_results['forum_raw'].append(result)
        
        return filtered_results
    
    def direct_db_query(self, query_text: str, category: str):
        """Direct database query with priority-based filtering"""
        
        # Get embedding for query
        query_embedding = self.embedding_model.get_text_embedding(query_text)
        
        conn = psycopg2.connect(**self.db_config)
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Query with similarity thresholds
                cur.execute("""
                    WITH ranked_results AS (
                        SELECT 
                            text,
                            metadata_->>'title' as title,
                            metadata_->>'source' as source,
                            metadata_->>'priority' as priority,
                            metadata_->>'content_type' as content_type,
                            metadata_->>'similarity_threshold' as threshold,
                            metadata_->>'fact_status' as fact_status,
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
                        CASE source
                            WHEN 'facts' THEN 1
                            WHEN 'blog' THEN 2
                            WHEN 'youtube' THEN 3
                            WHEN 'forum' THEN 4
                        END,
                        distance
                    LIMIT 30
                """, (query_embedding,))
                
                results = cur.fetchall()
                return results
                
        finally:
            conn.close()
    
    def query_all_workout_features(self):
        """Query all workout feature categories from the workouts.md semantic queries"""
        
        # Workout feature categories and their queries
        workout_queries = {
            "Workout Creation & Management": [
                '"workout editor" OR "workout creator" OR "visual workout builder"',
                '"sets and reps editor" OR "interval structure" OR "complex intervals"',
                '"interval comments" OR "coaching notes" OR "workout instructions"',
                '"route importing" OR "GPS routes" OR "outdoor simulation"',
                '"target modes" OR "power targets" OR "heart rate targets" OR "slope targets"',
                '"mixed-mode workouts" OR "automatic mode switching"',
                '"workout tags" OR "workout organization" OR "public private workouts"',
                '"workout cloning" OR "duplicate workouts" OR "ALT drag"',
                '"ramps and steps" OR "gradual power changes" OR "progressive intervals"',
                '"open-ended intervals" OR "free ride intervals" OR "lap button control"',
                '"W\'bal integration" OR "anaerobic capacity" OR "interval design"',
                '"multi-sport workouts" OR "cycling rowing swimming"'
            ],
            "Training Modes": [
                '"ERG mode" OR "automatic power control" OR "power targeting"',
                '"HR+ mode" OR "heart rate controlled" OR "automatic power adjustment"',
                '"slope mode" OR "gradient simulation" OR "gear control"',
                '"resistance mode" OR "fixed resistance" OR "sprint training"',
                '"power target adjustment" OR "heart rate feedback"',
                '"mode transitions" OR "seamless switching" OR "control modes"',
                '"trainer difficulty" OR "gear usage" OR "resistance settings"'
            ],
            "Training Execution & Real-time Features": [
                '"real-time training" OR "live workout execution" OR "smart trainer control"',
                '"6-second warmup" OR "quick start" OR "ultra-fast start"',
                '"dynamic workout editing" OR "on-the-fly modifications" OR "mid-workout changes"',
                '"power adjustments" OR "intensity controls" OR "+/- buttons"',
                '"hot swap" OR "change workouts mid-session" OR "workout switching"',
                '"auto-extend workouts" OR "continue beyond duration" OR "extended training"',
                '"training effect integration" OR "Garmin training effect"',
                '"ERG spiral recovery" OR "low-cadence resistance"',
                '"ride feel adjustment" OR "intensity modification"',
                '"FTP-based scaling" OR "fitness-based adjustment"',
                '"power match compatibility" OR "external power meters"',
                '"heart rate testing" OR "zone 2 testing" OR "maximum heart rate"'
            ],
            "Real-time Display & Monitoring": [
                '"broadcast to big screen" OR "cast training data" OR "external displays"',
                '"live training display" OR "real-time viewing" OR "workout monitoring"',
                '"power zone displays" OR "visual zone indicators"',
                '"speed distance calculation" OR "indoor approximation" OR "drag coefficient"',
                '"real-time metrics" OR "power HR cadence" OR "live data"',
                '"YouTube integration" OR "embedded video" OR "entertainment"',
                '"secret URL sharing" OR "live data sharing" OR "coach viewing"',
                '"training data visualization" OR "power curves" OR "interval analysis"'
            ],
            "Workout Library & Discovery": [
                '"community workout library" OR "user-created workouts" OR "shared workouts"',
                '"open source workouts" OR "ERGdb integration" OR "free workouts"',
                '"workout search filtering" OR "tags difficulty type sport duration"',
                '"workout rating system" OR "popularity rankings" OR "community ratings"',
                '"author following" OR "favorite creators" OR "workout creators"',
                '"search by popularity" OR "highly-rated workouts" OR "discover content"',
                '"sport-specific filtering" OR "cycling rowing swimming separation"',
                '"tag-based search" OR "hashtag search" OR "workout discovery"',
                '"advanced search features" OR "detailed filtering" OR "search capabilities"',
                '"personal workout lists" OR "custom organization" OR "workout collections"',
                '"favorites system" OR "preferred workouts" OR "quick access"'
            ],
            "Workout Export & Integration": [
                '"multi-format export" OR "TCX ZWO MRC ERG files" OR "workout formats"',
                '"platform integrations" OR "send to functionality" OR "device sync"',
                '"Garmin Connect" OR "device sync" OR "calendar integration" OR "step optimization"',
                '"TrainingPeaks" OR "workout distribution" OR "calendar sync"',
                '"Zwift integration" OR "structured workout export" OR "free-ride mode"',
                '"Intervals.icu" OR "WOD integration" OR "calendar sync"',
                '"Rouvy MyWhoosh Wahoo" OR "virtual training" OR "device compatibility"',
                '"outdoor workout conversion" OR "indoor to outdoor" OR "format conversion"',
                '"heart rate zone conversion" OR "power to HR zones" OR "outdoor training"',
                '"automatic calendar distribution" OR "multiple platform delivery"'
            ],
            "Workout Organization & Management": [
                '"personal workout lists" OR "custom organization" OR "workout collections"',
                '"training app shortcuts" OR "quick access" OR "frequently used"',
                '"public private tag system" OR "community personal organization"',
                '"auto-complete tag suggestions" OR "streamlined tagging"',
                '"cross-platform sync" OR "web mobile sync" OR "library access"',
                '"bulk workout operations" OR "batch editing" OR "mass management"',
                '"workout history tracking" OR "completed workouts" OR "progression tracking"',
                '"list sharing" OR "private URLs" OR "workout collection sharing"',
                '"hierarchical tag structures" OR "organized categories" OR "export platforms"'
            ],
            "Community & Sharing Features": [
                '"workout sharing" OR "public private sharing" OR "community sharing"',
                '"list sharing" OR "private URLs" OR "collection sharing"',
                '"community contributions" OR "public workout library" OR "shared content"',
                '"coach-athlete sharing" OR "coaching relationships" OR "training partnerships"',
                '"link sharing" OR "direct workout links" OR "easy sharing"'
            ]
        }
        
        print("🏋️ QUERYING ALL WORKOUT FEATURES")
        print("=" * 80)
        
        # Results storage
        all_results = {}
        summary_stats = {
            'total_queries': 0,
            'total_results': 0,
            'by_source': {
                'facts': 0,
                'blog': 0,
                'youtube': 0,
                'forum_qa': 0,
                'forum_raw': 0
            }
        }
        
        # Query each category
        for category, queries in workout_queries.items():
            print(f"\n📂 {category}")
            print("-" * 60)
            
            category_results = []
            
            for query in queries:
                summary_stats['total_queries'] += 1
                
                # Use direct DB query for more control
                results = self.direct_db_query(query, category)
                
                if results:
                    print(f"  ✓ Found {len(results)} results for: {query[:60]}...")
                    
                    for result in results:
                        source = result['source']
                        summary_stats['by_source'][source if source != 'forum' else 
                                                  ('forum_qa' if 'qa' in result['content_type'] else 'forum_raw')] += 1
                        summary_stats['total_results'] += 1
                        
                    category_results.extend(results)
                else:
                    print(f"  ✗ No results for: {query[:60]}...")
            
            # Deduplicate by title
            unique_results = {}
            for result in category_results:
                title = result['title']
                if title not in unique_results or result['distance'] < unique_results[title]['distance']:
                    unique_results[title] = result
            
            all_results[category] = list(unique_results.values())
            print(f"  → {len(unique_results)} unique results for {category}")
        
        # Save results
        output_dir = Path("./script-testing/workout_query_results")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"workout_features_results_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timestamp,
                'summary': summary_stats,
                'results': all_results
            }, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 QUERY SUMMARY")
        print("=" * 80)
        print(f"Total Queries Run: {summary_stats['total_queries']}")
        print(f"Total Results Found: {summary_stats['total_results']}")
        print("\nResults by Source:")
        for source, count in summary_stats['by_source'].items():
            print(f"  • {source}: {count}")
        
        print(f"\n💾 Results saved to: {output_file}")
        
        # Generate markdown report
        self.generate_markdown_report(all_results, output_dir / f"workout_features_report_{timestamp}.md")
        
        return all_results
    
    def generate_markdown_report(self, results: dict, output_file: Path):
        """Generate a markdown report of findings"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# TrainerDay Workout Features - Knowledge Base Query Results\n\n")
            f.write(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            
            for category, category_results in results.items():
                f.write(f"## {category}\n\n")
                
                if not category_results:
                    f.write("*No results found for this category*\n\n")
                    continue
                
                # Group by source
                by_source = {}
                for result in category_results:
                    source = result['source']
                    if source not in by_source:
                        by_source[source] = []
                    by_source[source].append(result)
                
                # Write by source
                for source in ['facts', 'blog', 'youtube', 'forum']:
                    if source in by_source:
                        source_results = by_source[source]
                        f.write(f"### {source.upper()} ({len(source_results)} results)\n\n")
                        
                        for result in sorted(source_results, key=lambda x: x['distance'])[:5]:  # Top 5
                            f.write(f"**{result['title']}** (score: {result['distance']:.3f})\n")
                            f.write(f"- Priority: {result['priority']}\n")
                            f.write(f"- Type: {result['content_type']}\n")
                            
                            # Clean up text preview
                            text_preview = result['text'].replace('\n', ' ')[:200] + '...'
                            f.write(f"- Preview: {text_preview}\n\n")
        
        print(f"📄 Markdown report saved to: {output_file}")

def main():
    """Main execution"""
    query_system = WorkoutFeatureQuery()
    
    try:
        # Connect to knowledge base
        query_system.connect_to_index()
        
        # Query all workout features
        results = query_system.query_all_workout_features()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()