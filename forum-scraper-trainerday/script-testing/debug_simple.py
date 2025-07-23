#!/usr/bin/env python3
"""
Simple debugging of batch hang - step by step
"""

import os
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.analyze_forum_topics import ForumTopicAnalyzerV2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("🔍 Simple Batch Debug")
    print("=" * 30)
    
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
        print("Step 1: Creating analyzer...")
        start = time.time()
        analyzer = ForumTopicAnalyzerV2(db_config=db_config)
        print(f"  ✅ Done in {time.time() - start:.2f}s")
        
        print("\nStep 2: Calling process_topics_with_raw_storage with tiny batch...")
        start = time.time()
        
        # This is the call that hangs - let's see which step hangs
        results = analyzer.process_topics_with_raw_storage(
            max_topics=1,  # Just 1 topic
            start_from=0,
            force_reanalyze=False
        )
        
        duration = time.time() - start
        print(f"  ✅ Completed in {duration:.2f}s")
        print(f"  Results: {results['analysis_metadata']['successful_analyses']} successful")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()