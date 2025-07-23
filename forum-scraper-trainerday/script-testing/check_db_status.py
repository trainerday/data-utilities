#!/usr/bin/env python3
"""
Simple DB Status Checker
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv
    import psycopg2
    
    # Load environment variables
    load_dotenv()
    
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('DB_SSLMODE', 'require')
    }
    
    # Add SSL cert if exists
    if os.getenv('DB_SSLROOTCERT'):
        ssl_cert_filename = os.getenv('DB_SSLROOTCERT')
        ssl_cert_path = Path(__file__).parent.parent / ssl_cert_filename
        if ssl_cert_path.exists():
            db_config['sslrootcert'] = str(ssl_cert_path)
    
    print("🔍 Connecting to database...")
    connection = psycopg2.connect(**db_config)
    
    with connection.cursor() as cursor:
        # Get total raw topics
        cursor.execute('SELECT COUNT(*) FROM forum_topics_raw')
        total_raw = cursor.fetchone()[0]
        
        # Get analyzed topics
        cursor.execute('SELECT COUNT(*) FROM forum_topics')
        analyzed = cursor.fetchone()[0]
        
        # Get Q&A pairs
        cursor.execute('SELECT COUNT(*) FROM forum_qa_pairs')
        qa_pairs = cursor.fetchone()[0]
        
        # Check for incomplete topics (topics without Q&A pairs)
        cursor.execute('''
            SELECT COUNT(*)
            FROM forum_topics ft
            LEFT JOIN forum_qa_pairs qa ON ft.topic_id = qa.topic_id
            WHERE qa.topic_id IS NULL
        ''')
        incomplete = cursor.fetchone()[0]
        
        # Get recent analysis activity
        cursor.execute('''
            SELECT COUNT(*) 
            FROM forum_topics 
            WHERE analyzed_at >= NOW() - INTERVAL '1 hour'
        ''')
        recent_hour = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) 
            FROM forum_topics 
            WHERE analyzed_at >= NOW() - INTERVAL '10 minutes'
        ''')
        recent_10min = cursor.fetchone()[0]

    connection.close()
    
    # Calculate stats
    remaining = total_raw - analyzed
    percentage = (analyzed / total_raw) * 100
    complete_topics = analyzed - incomplete
    
    print(f"\n📊 DATABASE STATUS:")
    print(f"=" * 30)
    print(f"Total topics in database: {total_raw:,}")
    print(f"Topics analyzed: {analyzed:,} ({percentage:.1f}%)")
    print(f"Complete topics (with Q&A): {complete_topics:,}")
    print(f"Incomplete topics: {incomplete:,}")
    print(f"Remaining to process: {remaining:,}")
    print(f"")
    print(f"Q&A pairs extracted: {qa_pairs:,}")
    print(f"Average Q&A per complete topic: {qa_pairs/complete_topics:.1f}" if complete_topics > 0 else "N/A")
    print(f"")
    print(f"Recent activity:")
    print(f"  Last hour: {recent_hour:,} topics")
    print(f"  Last 10 min: {recent_10min:,} topics")
    
    if incomplete > 0:
        print(f"\n⚠️  WARNING: {incomplete} topics are incomplete (need cleanup)")
    
    if remaining == 0:
        print(f"\n🎉 ALL TOPICS PROCESSED!")
    else:
        print(f"\n📋 {remaining:,} topics remaining ({remaining/total_raw*100:.1f}%)")

except ImportError as e:
    print(f"❌ Missing module: {e}")
    print("Install required packages: pip install psycopg2-binary python-dotenv")
except Exception as e:
    print(f"❌ Database error: {e}")