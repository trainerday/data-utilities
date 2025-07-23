#!/usr/bin/env python3
"""
Efficient Batch Processor for Forum Analysis
Processes topics in manageable chunks with progress tracking
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.analyze_forum_topics import ForumTopicAnalyzerV2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_progress_stats():
    """Get current progress statistics"""
    
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
    
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    try:
        connection = psycopg2.connect(**db_config)
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT COUNT(*) as analyzed FROM forum_topics")
            analyzed = cursor.fetchone()['analyzed']
            
            cursor.execute("""
                SELECT COUNT(*) as total FROM forum_topics_raw 
                WHERE (jsonb_array_length(COALESCE(raw_content -> 'posts', '[]'::jsonb)) > 0
                       OR jsonb_array_length(COALESCE(raw_content -> 'post_stream' -> 'posts', '[]'::jsonb)) > 0)
            """)
            total = cursor.fetchone()['total']
            
        connection.close()
        return analyzed, total
    except Exception as e:
        print(f"Error getting progress: {e}")
        return 0, 0

def run_efficient_batch():
    """Run efficient batch processing"""
    
    print("🚀 Efficient Forum Analysis Batch Processor")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key required")
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
    
    # Configuration
    TOPICS_PER_BATCH = 10  # Small batches to avoid hangs
    MAX_BATCHES = 10       # Limit to 100 topics per run
    
    print(f"Configuration:")
    print(f"  Topics per batch: {TOPICS_PER_BATCH}")
    print(f"  Max batches: {MAX_BATCHES}")
    print(f"  Max topics this run: {TOPICS_PER_BATCH * MAX_BATCHES}")
    
    # Get current progress
    analyzed, total = get_progress_stats()
    remaining = total - analyzed
    
    print(f"\nCurrent Progress:")
    print(f"  Analyzed: {analyzed}")
    print(f"  Total: {total}")
    print(f"  Remaining: {remaining}")
    print(f"  Progress: {(analyzed/total)*100:.1f}%")
    
    if remaining == 0:
        print("✅ All topics already analyzed!")
        return
    
    # Calculate how many topics we'll actually process
    topics_this_run = min(TOPICS_PER_BATCH * MAX_BATCHES, remaining)
    print(f"  Will process: {topics_this_run} topics this run")
    
    # Run batches
    total_processed = 0
    total_successful = 0
    start_time = time.time()
    
    for batch_num in range(MAX_BATCHES):
        if total_processed >= remaining:
            print(f"\n✅ No more topics to process!")
            break
            
        print(f"\n📦 BATCH {batch_num + 1}/{MAX_BATCHES}")
        print("-" * 30)
        
        batch_start = time.time()
        
        try:
            # Create fresh analyzer for each batch
            analyzer = ForumTopicAnalyzerV2(db_config=db_config)
            
            # Process this batch
            results = analyzer.process_topics_with_raw_storage(
                max_topics=TOPICS_PER_BATCH,
                start_from=analyzed + total_processed,  # Skip already processed
                force_reanalyze=False
            )
            
            batch_duration = time.time() - batch_start
            batch_processed = results["analysis_metadata"]["total_topics_processed"]
            batch_successful = results["analysis_metadata"]["successful_analyses"]
            batch_failed = results["analysis_metadata"]["failed_analyses"]
            
            total_processed += batch_processed
            total_successful += batch_successful
            
            # Batch summary
            print(f"\nBatch {batch_num + 1} Results:")
            print(f"  Processed: {batch_processed}")
            print(f"  Successful: {batch_successful}")
            print(f"  Failed: {batch_failed}")
            print(f"  Duration: {batch_duration:.1f}s")
            
            if batch_successful > 0:
                rate = batch_successful / batch_duration
                print(f"  Rate: {rate:.2f} topics/second")
                print(f"  Avg per topic: {batch_duration/batch_successful:.1f}s")
            
            # Show failures if any
            if batch_failed > 0:
                print(f"  ❌ Failures:")
                for failure in results["analysis_metadata"]["failed_topics"]:
                    print(f"    {failure['topic_id']}: {failure['failure_reason']}")
            
            # Stop if we didn't get a full batch (reached the end)
            if batch_processed < TOPICS_PER_BATCH:
                print(f"\n🏁 Reached end of data (got {batch_processed} < {TOPICS_PER_BATCH})")
                break
                
        except KeyboardInterrupt:
            print(f"\n⚠️ Interrupted by user after {batch_num + 1} batches")
            break
        except Exception as e:
            print(f"\n❌ Batch {batch_num + 1} failed: {e}")
            import traceback
            traceback.print_exc()
            break
        
        # Progress update
        current_analyzed = analyzed + total_successful
        current_progress = (current_analyzed / total) * 100
        print(f"\n📊 Overall Progress: {current_analyzed}/{total} ({current_progress:.1f}%)")
        
        # ETA calculation
        if total_successful > 0:
            elapsed = time.time() - start_time
            rate = total_successful / elapsed
            remaining_topics = total - current_analyzed
            eta_seconds = remaining_topics / rate
            eta_hours = eta_seconds / 3600
            print(f"  Current rate: {rate:.2f} topics/second")
            print(f"  ETA for completion: {eta_hours:.1f} hours")
    
    # Final summary
    total_duration = time.time() - start_time
    print(f"\n🎯 BATCH RUN COMPLETE")
    print("=" * 40)
    print(f"Duration: {total_duration/60:.1f} minutes")
    print(f"Batches processed: {batch_num + 1}")
    print(f"Topics processed: {total_processed}")
    print(f"Successful analyses: {total_successful}")
    
    if total_successful > 0:
        overall_rate = total_successful / total_duration
        print(f"Overall rate: {overall_rate:.2f} topics/second")
        
        final_analyzed = analyzed + total_successful
        final_progress = (final_analyzed / total) * 100
        print(f"\nFinal Progress: {final_analyzed}/{total} ({final_progress:.1f}%)")
        
        if final_analyzed < total:
            remaining = total - final_analyzed
            print(f"Remaining topics: {remaining}")
            print(f"Estimated additional time: {(remaining/overall_rate)/3600:.1f} hours")
        else:
            print("🎉 ALL TOPICS COMPLETED!")

if __name__ == "__main__":
    run_efficient_batch()