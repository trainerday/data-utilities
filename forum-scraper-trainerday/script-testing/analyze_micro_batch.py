#!/usr/bin/env python3
"""
Micro Batch Processing - Process 3 topics at a time to debug batch issues
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
    """Run micro-batch analysis (3 topics at a time)"""
    
    print("🔬 Micro-Batch Analysis Mode (3 topics)")
    print("=" * 50)
    
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
        # Initialize analyzer
        analyzer = ForumTopicAnalyzerV2(db_config=db_config)
        
        print("🔄 Starting micro-batch processing...")
        start_time = time.time()
        
        # Process 3 topics starting from current progress
        results = analyzer.process_topics_with_raw_storage(
            max_topics=3,  # Very small batch
            start_from=0,  # Will automatically skip analyzed ones
            force_reanalyze=False
        )
        
        duration = time.time() - start_time
        
        print(f"\n✅ MICRO-BATCH COMPLETE")
        print("=" * 30)
        print(f"Duration: {duration:.1f} seconds")
        print(f"Topics processed: {results['analysis_metadata']['total_topics_processed']}")
        print(f"Successful analyses: {results['analysis_metadata']['successful_analyses']}")
        print(f"Failed analyses: {results['analysis_metadata']['failed_analyses']}")
        
        if results['analysis_metadata']['successful_analyses'] > 0:
            rate = results['analysis_metadata']['successful_analyses'] / duration
            print(f"Processing rate: {rate:.2f} topics/second")
            print(f"Average time per topic: {duration/results['analysis_metadata']['successful_analyses']:.1f} seconds")
        
        # Show any failures
        failed_topics = results['analysis_metadata'].get('failed_topics', [])
        if failed_topics:
            print(f"\n❌ FAILURES ({len(failed_topics)}):")
            for failure in failed_topics:
                print(f"  Topic {failure['topic_id']}: {failure['failure_reason']}")
        
    except Exception as e:
        print(f"❌ Error during micro-batch processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()