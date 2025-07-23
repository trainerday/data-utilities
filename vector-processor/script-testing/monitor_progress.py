#!/usr/bin/env python3
"""
Monitor vectorization progress in real-time
"""

import os
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def monitor_progress():
    """Monitor vectorization progress"""
    
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('DB_SSLMODE', 'require')
    }
    
    try:
        conn = psycopg2.connect(**db_config)
        
        print("🔍 Monitoring Vectorization Progress")
        print("=" * 50)
        print("Press Ctrl+C to stop monitoring\n")
        
        target_forum_count = 3513  # Expected forum Q&A pairs
        start_time = time.time()
        
        while True:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                
                # Check total embeddings by source
                cursor.execute("""
                    SELECT source, COUNT(*) as count
                    FROM content_embeddings
                    GROUP BY source
                    ORDER BY source
                """)
                
                results = cursor.fetchall()
                total_embeddings = sum(row['count'] for row in results)
                
                # Get forum count specifically
                forum_count = 0
                for row in results:
                    if row['source'] == 'forum':
                        forum_count = row['count']
                        break
                
                # Calculate progress
                forum_progress = (forum_count / target_forum_count) * 100 if target_forum_count > 0 else 0
                elapsed_time = time.time() - start_time
                
                # Clear screen and show progress
                os.system('clear' if os.name == 'posix' else 'cls')
                print("🔍 Vectorization Progress Monitor")
                print("=" * 50)
                print(f"⏱️  Runtime: {elapsed_time/60:.1f} minutes")
                print()
                
                # Progress by source
                for row in results:
                    source = row['source'].upper()
                    count = row['count']
                    
                    if source == 'FORUM':
                        print(f"{source}: {count:,} / {target_forum_count:,} ({forum_progress:.1f}%)")
                        
                        # Progress bar for forum
                        bar_length = 30
                        filled_length = int(bar_length * forum_progress / 100)
                        bar = '█' * filled_length + '░' * (bar_length - filled_length)
                        print(f"Progress: [{bar}] {forum_progress:.1f}%")
                    else:
                        print(f"{source}: {count:,} (complete)")
                
                print(f"\nTOTAL EMBEDDINGS: {total_embeddings:,}")
                
                # Completion check
                if forum_count >= target_forum_count:
                    print("\n🎉 VECTORIZATION COMPLETE!")
                    break
                
                # Rate calculation
                if forum_count > 0 and elapsed_time > 0:
                    rate = forum_count / elapsed_time
                    eta = (target_forum_count - forum_count) / rate if rate > 0 else 0
                    print(f"\n📊 Rate: {rate:.1f} embeddings/second")
                    print(f"🕐 ETA: {eta/60:.1f} minutes remaining")
                
                print(f"\nNext update in 10 seconds... (Press Ctrl+C to stop)")
                
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    monitor_progress()