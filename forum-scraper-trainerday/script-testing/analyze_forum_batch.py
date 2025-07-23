#!/usr/bin/env python3
"""
Forum Topic Analysis - Batch Processing Version
Modified to process topics in smaller, manageable batches
"""

import os
import sys
import time
from pathlib import Path

# Add parent directory to path to import the analyzer
sys.path.append(str(Path(__file__).parent.parent))

from scripts.analyze_forum_topics import ForumTopicAnalyzerV2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Run analysis in controlled batches"""
    
    # Configuration for batch processing
    BATCH_SIZE = 20  # Process 20 topics at a time
    MAX_BATCHES = 5  # Maximum number of batches to run (100 topics total)
    FORCE_REANALYZE = False
    
    print("TrainerDay Forum Analysis - Batch Processing Mode")
    print("=" * 60)
    print(f"Batch size: {BATCH_SIZE} topics")
    print(f"Max batches: {MAX_BATCHES}")
    print(f"Total topics to process: {BATCH_SIZE * MAX_BATCHES}")
    print()
    
    # Check if OpenAI API key is available
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set your OpenAI API key in the .env file")
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
    
    # Add SSL certificate if specified
    if os.getenv('DB_SSLROOTCERT'):
        ssl_cert_filename = os.getenv('DB_SSLROOTCERT')
        ssl_cert_path = Path(__file__).parent.parent / ssl_cert_filename
        if ssl_cert_path.exists():
            db_config['sslrootcert'] = str(ssl_cert_path)
    
    if not all([db_config['host'], db_config['database'], db_config['user'], db_config['password']]):
        print("❌ Database configuration incomplete")
        return
    
    try:
        # Find current progress to determine start_from
        analyzer = ForumTopicAnalyzerV2(db_config=db_config)
        analyzer.connect_to_database()
        
        # Get count of already analyzed topics
        with analyzer.db_connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM forum_topics")
            analyzed_count = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM forum_topics_raw 
                WHERE (jsonb_array_length(COALESCE(raw_content -> 'posts', '[]'::jsonb)) > 0
                       OR jsonb_array_length(COALESCE(raw_content -> 'post_stream' -> 'posts', '[]'::jsonb)) > 0)
            """)
            total_count = cursor.fetchone()[0]
        
        analyzer.close_database_connection()
        
        print(f"📊 Current progress: {analyzed_count}/{total_count} topics analyzed")
        print(f"📝 Remaining topics: {total_count - analyzed_count}")
        print()
        
        if analyzed_count >= total_count:
            print("✅ All topics have been analyzed!")
            return
        
        # Process in batches
        total_processed = 0
        total_successful = 0
        start_time = time.time()
        
        for batch_num in range(MAX_BATCHES):
            current_start = analyzed_count + (batch_num * BATCH_SIZE)
            
            print(f"🔄 BATCH {batch_num + 1}/{MAX_BATCHES}")
            print(f"   Starting from offset: {current_start}")
            print(f"   Processing {BATCH_SIZE} topics")
            print("-" * 40)
            
            batch_start_time = time.time()
            
            # Initialize fresh analyzer for each batch
            batch_analyzer = ForumTopicAnalyzerV2(db_config=db_config)
            
            # Process this batch
            results = batch_analyzer.process_topics_with_raw_storage(
                max_topics=BATCH_SIZE,
                start_from=current_start,
                force_reanalyze=FORCE_REANALYZE
            )
            
            batch_duration = time.time() - batch_start_time
            batch_processed = results["analysis_metadata"]["total_topics_processed"]
            batch_successful = results["analysis_metadata"]["successful_analyses"]
            
            total_processed += batch_processed
            total_successful += batch_successful
            
            print(f"✅ Batch {batch_num + 1} complete:")
            print(f"   Processed: {batch_processed} topics")
            print(f"   Successful: {batch_successful} analyses")
            print(f"   Duration: {batch_duration:.1f} seconds")
            print(f"   Rate: {batch_successful/batch_duration:.2f} topics/second")
            print()
            
            # Stop if no more topics to process
            if batch_processed < BATCH_SIZE:
                print("🏁 No more topics to process - reached end of data")
                break
        
        # Final summary
        total_duration = time.time() - start_time
        print("🎯 BATCH PROCESSING COMPLETE")
        print("=" * 50)
        print(f"Total batches run: {batch_num + 1}")
        print(f"Total topics processed: {total_processed}")
        print(f"Total successful analyses: {total_successful}")
        print(f"Total duration: {total_duration:.1f} seconds")
        
        if total_successful > 0:
            print(f"Average rate: {total_successful/total_duration:.2f} topics/second")
            
            # Update progress
            final_analyzed = analyzed_count + total_successful
            progress_pct = (final_analyzed / total_count) * 100
            print(f"Overall progress: {final_analyzed}/{total_count} ({progress_pct:.1f}%)")
            
            remaining = total_count - final_analyzed
            if remaining > 0:
                estimated_time = remaining / (total_successful/total_duration)
                print(f"Estimated time for completion: {estimated_time/3600:.1f} hours")
        
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()