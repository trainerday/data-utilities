#!/usr/bin/env python3
"""
Process Top 100 Latest Topics
Run the latest topic processor 100 times to handle the most recent topics
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

def main():
    """Process the top 100 latest topics by running single processor multiple times"""
    
    print("🚀 Top 100 Latest Topics Processor")
    print("=" * 45)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Configuration
    TARGET_TOPICS = 100
    
    print(f"Will process up to {TARGET_TOPICS} latest topics")
    print("Processing one topic at a time for maximum reliability")
    
    successful = 0
    failed = 0
    no_more_topics = 0
    categories = {}
    total_qa_pairs = 0
    start_time = time.time()
    
    for i in range(TARGET_TOPICS):
        print(f"\n🎯 Processing topic {i+1}/{TARGET_TOPICS}")
        
        try:
            # Run the latest topic processor
            result = subprocess.run([
                'python3', 'process_next_latest.py'
            ], capture_output=True, text=True, timeout=120)  # 2 minute timeout per topic
            
            if result.returncode == 0:
                output = result.stdout
                
                # Check if no more topics
                if "No unprocessed topics found!" in output:
                    print("✅ No more topics to process!")
                    no_more_topics += 1
                    break
                
                # Check if successful
                if "✅ Success!" in output:
                    successful += 1
                    print("✅ Topic processed successfully")
                    
                    # Extract category and Q&A count from output
                    for line in output.split('\n'):
                        if "Category:" in line:
                            category = line.split("Category: ")[1].strip()
                            categories[category] = categories.get(category, 0) + 1
                        elif "Q&A pairs extracted:" in line:
                            try:
                                qa_count = int(line.split("Q&A pairs extracted: ")[1].strip())
                                total_qa_pairs += qa_count
                            except:
                                pass
                else:
                    failed += 1
                    print("❌ Topic processing failed")
            else:
                failed += 1
                print(f"❌ Process failed (return code: {result.returncode})")
                if result.stderr:
                    print(f"Error: {result.stderr[:100]}...")
                
        except subprocess.TimeoutExpired:
            failed += 1
            print("❌ Topic processing timed out after 2 minutes")
        except Exception as e:
            failed += 1
            print(f"❌ Error running processor: {e}")
        
        # Progress update every 10 topics
        if (i + 1) % 10 == 0:
            elapsed = time.time() - start_time
            rate = successful / elapsed if elapsed > 0 else 0
            
            print(f"\n📊 Progress Update:")
            print(f"  Completed: {i + 1}/{TARGET_TOPICS}")
            print(f"  Successful: {successful}")
            print(f"  Failed: {failed}")
            print(f"  Success rate: {(successful/(i+1))*100:.1f}%")
            print(f"  Processing rate: {rate:.2f} topics/second")
            print(f"  Elapsed: {elapsed/60:.1f} minutes")
            
            # ETA calculation
            remaining = TARGET_TOPICS - (i + 1)
            if rate > 0:
                eta_minutes = remaining / rate / 60
                print(f"  ETA: {eta_minutes:.1f} minutes")
        
        # Small delay between topics to avoid overwhelming the system
        time.sleep(2)
    
    # Final summary
    total_duration = time.time() - start_time
    total_processed = successful + failed
    
    print(f"\n🎯 TOP 100 LATEST PROCESSING COMPLETE")
    print("=" * 50)
    print(f"Duration: {total_duration/60:.1f} minutes")
    print(f"Topics attempted: {total_processed}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(successful/total_processed)*100:.1f}%")
    print(f"Total Q&A pairs extracted: {total_qa_pairs}")
    
    if successful > 0:
        rate = successful / total_duration
        avg_time = total_duration / successful
        print(f"Processing rate: {rate:.2f} topics/second")
        print(f"Average time per successful topic: {avg_time:.1f}s")
    
    if categories:
        print(f"\n📂 Categories processed:")
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {category}: {count} topics")
    
    if no_more_topics:
        print(f"\n🎉 ALL AVAILABLE TOPICS HAVE BEEN PROCESSED!")
    else:
        print(f"\n📈 Latest {successful} topics have been successfully analyzed")
        print("Run this script again to process more topics")

if __name__ == "__main__":
    main()