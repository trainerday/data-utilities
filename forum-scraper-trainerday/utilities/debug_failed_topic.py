#!/usr/bin/env python3
"""
Debug Failed Topic Analysis
Try to analyze the failed topic to see what went wrong.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from analyze_forum_topics_v2 import ForumTopicAnalyzerV2

# Load environment
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

def main():
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
        ssl_cert_path = Path(__file__).parent.parent / os.getenv('DB_SSLROOTCERT')
        if ssl_cert_path.exists():
            db_config['sslrootcert'] = str(ssl_cert_path)
    
    print("Debug Failed Topic Analysis")
    print("=" * 35)
    
    try:
        # Initialize analyzer
        analyzer = ForumTopicAnalyzerV2(db_config=db_config)
        analyzer.connect_to_database()
        
        # Try to analyze the failed topic (29)
        print("\nAttempting to analyze Topic 29...")
        analysis = analyzer.analyze_stored_topic(29)
        
        if analysis:
            print("✅ Analysis successful!")
            print(f"Title: {analysis['topic_summary']['title']}")
            print(f"Category: {analysis['topic_summary'].get('analysis_category')}")
            print(f"Q&A pairs: {len(analysis.get('qa_pairs', []))}")
            
            # Try to save it
            print("\nSaving analysis to database...")
            analyzer.save_analysis_to_database(analysis)
            print("✅ Analysis saved successfully!")
            
        else:
            print("❌ Analysis failed - check the logs above for errors")
        
        analyzer.close_database_connection()
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")

if __name__ == "__main__":
    main()