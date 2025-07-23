#!/usr/bin/env python3
"""
Step-by-step debugging of the batch processing hang
"""

import os
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.analyze_forum_topics import ForumTopicAnalyzerV2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

# Load environment variables
load_dotenv()

def debug_batch_processing():
    """Debug each step of batch processing"""
    
    print("🔍 Debugging Batch Processing Hang")
    print("=" * 40)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ No OpenAI API key")
        return
    
    # Database configuration
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('DB_SSLMODE', 'require')
    }
    
    if os.getenv('DB_SSLROOTCERT'):
        ssl_cert_filename = os.getenv('DB_SSLROOTCERT')
        ssl_cert_path = Path(__file__).parent.parent / ssl_cert_filename
        if ssl_cert_path.exists():
            db_config['sslrootcert'] = str(ssl_cert_path)
    
    try:
        # Step 1: Initialize analyzer
        print("Step 1: Initializing analyzer...")
        step_start = time.time()
        analyzer = ForumTopicAnalyzerV2(db_config=db_config)
        print(f"  ✅ Initialized in {time.time() - step_start:.2f}s")
        
        # Step 2: Connect to database
        print("\nStep 2: Connecting to database...")
        step_start = time.time()
        analyzer.connect_to_database()
        print(f"  ✅ Connected in {time.time() - step_start:.2f}s")
        
        # Step 3: Create schema
        print("\nStep 3: Creating database schema...")
        step_start = time.time()
        analyzer.create_database_schema()
        print(f"  ✅ Schema ready in {time.time() - step_start:.2f}s")
        
        # Step 4: Database query (the suspected problem area)
        print("\nStep 4: Getting topics from database...")
        step_start = time.time()
        
        max_topics = 3  # Small batch for testing
        start_from = 0
        
        with analyzer.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT topic_id, title, posts_count 
                FROM forum_topics_raw 
                WHERE (jsonb_array_length(COALESCE(raw_content -> 'posts', '[]'::jsonb)) > 0
                       OR jsonb_array_length(COALESCE(raw_content -> 'post_stream' -> 'posts', '[]'::jsonb)) > 0)
                ORDER BY topic_id
                LIMIT %s OFFSET %s
            """, (max_topics, start_from))
            
            db_topics = cursor.fetchall()\n        \n        topic_list = [(row['topic_id'], row['title'], row['posts_count']) for row in db_topics]\n        print(f\"  ✅ Found {len(topic_list)} topics in {time.time() - step_start:.2f}s\")\n        \n        # Step 5: Initialize results structure\n        print(\"\\nStep 5: Initializing results structure...\")\n        step_start = time.time()\n        \n        results = {\n            \"analysis_metadata\": {\n                \"analyzed_at\": \"2025-07-22T08:30:00\",\n                \"total_topics_processed\": 0,\n                \"topics_stored_raw\": 0,\n                \"topics_analyzed\": 0,\n                \"successful_analyses\": 0,\n                \"failed_analyses\": 0,\n                \"unchanged_topics\": 0,\n                \"topics_by_category\": {},\n                \"storage_method\": \"database_with_raw_content\",\n                \"failed_topics\": []\n            }\n        }\n        print(f\"  ✅ Results structure ready in {time.time() - step_start:.2f}s\")\n        \n        # Step 6: The main processing loop (this is likely where it hangs)\n        print(\"\\nStep 6: Starting main processing loop...\")\n        \n        for i, (topic_id, title, posts_count) in enumerate(topic_list):\n            print(f\"\\n  Processing [{i+1}/{len(topic_list)}] Topic {topic_id}: {title[:30]}...\")\n            \n            loop_start = time.time()\n            \n            try:\n                # Substep 6a: Content changed logic\n                print(f\"    6a: Checking content changes...\")\n                substep_start = time.time()\n                content_changed = True  # This line in original\n                results[\"analysis_metadata\"][\"topics_stored_raw\"] += 1\n                print(f\"        ✅ Done in {time.time() - substep_start:.2f}s\")\n                \n                # Substep 6b: Should analyze logic  \n                print(f\"    6b: Deciding if analysis needed...\")\n                substep_start = time.time()\n                should_analyze = False or content_changed  # force_reanalyze = False\n                print(f\"        ✅ Should analyze: {should_analyze} in {time.time() - substep_start:.2f}s\")\n                \n                if not should_analyze:\n                    print(f\"    → Skipping analysis (no changes detected)\")\n                    results[\"analysis_metadata\"][\"unchanged_topics\"] += 1\n                else:\n                    print(f\"    → Running analysis...\")\n                    \n                    # Substep 6c: Clear existing analysis\n                    print(f\"    6c: Clearing existing analysis...\")\n                    substep_start = time.time()\n                    analyzer.delete_existing_analysis(topic_id)\n                    print(f\"        ✅ Cleared in {time.time() - substep_start:.2f}s\")\n                    \n                    # Substep 6d: Analyze topic (THIS MIGHT BE WHERE IT HANGS)\n                    print(f\"    6d: Analyzing topic {topic_id}... (THIS MIGHT HANG)\")\n                    substep_start = time.time()\n                    \n                    # Let's test if this is where it hangs by calling it directly\n                    analysis = analyzer.analyze_stored_topic(topic_id)\n                    \n                    print(f\"        ✅ Analysis completed in {time.time() - substep_start:.2f}s\")\n                    \n                    if analysis:\n                        # Substep 6e: Save to database\n                        print(f\"    6e: Saving analysis to database...\")\n                        substep_start = time.time()\n                        analyzer.save_analysis_to_database(analysis)\n                        results[\"analysis_metadata\"][\"successful_analyses\"] += 1\n                        print(f\"        ✅ Saved in {time.time() - substep_start:.2f}s\")\n                        \n                        print(f\"  ✅ Topic {topic_id} completed successfully!\")\n                    else:\n                        print(f\"  ❌ Topic {topic_id} analysis returned None\")\n                        results[\"analysis_metadata\"][\"failed_analyses\"] += 1\n                    \n                    results[\"analysis_metadata\"][\"topics_analyzed\"] += 1\n                \n                results[\"analysis_metadata\"][\"total_topics_processed\"] += 1\n                loop_duration = time.time() - loop_start\n                print(f\"  📊 Topic loop completed in {loop_duration:.2f}s\")\n                \n                # Rate limiting\n                print(f\"    → Sleeping 1 second for rate limiting...\")\n                time.sleep(1)\n                \n            except Exception as e:\n                print(f\"  ❌ Error processing topic {topic_id}: {e}\")\n                import traceback\n                traceback.print_exc()\n                break  # Stop on first error for debugging\n        \n        # Close connection\n        analyzer.close_database_connection()\n        \n        print(f\"\\n✅ DEBUG BATCH PROCESSING COMPLETED!\")\n        print(f\"Processed {results['analysis_metadata']['total_topics_processed']} topics\")\n        print(f\"Successful: {results['analysis_metadata']['successful_analyses']}\")\n        print(f\"Failed: {results['analysis_metadata']['failed_analyses']}\")\n        \n    except Exception as e:\n        print(f\"❌ Fatal error during debugging: {e}\")\n        import traceback\n        traceback.print_exc()\n\nif __name__ == \"__main__\":\n    debug_batch_processing()