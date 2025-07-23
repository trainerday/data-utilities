#!/usr/bin/env python3
"""
Test 10 Topics with Fast Processing
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

def main():
    print("🧪 Test 10 Topics - Fast Processing")
    print("=" * 40)
    print(f"Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    successful = 0
    failed = 0
    total_qa_pairs = 0
    categories = {}
    start_time = time.time()
    
    for i in range(10):
        print(f"\n🎯 Topic {i+1}/10")
        
        try:
            result = subprocess.run([
                'python3', 'process_next_latest.py'
            ], capture_output=True, text=True, timeout=60)  # 1 minute timeout
            
            if result.returncode == 0:
                output = result.stdout
                
                # Check if no more topics
                if "No unprocessed topics found!" in output:
                    print("✅ No more topics available")
                    break
                
                # Check if successful
                if "✅ Success!" in output:
                    successful += 1
                    
                    # Extract info from output
                    topic_id = "Unknown"
                    category = "Unknown"
                    qa_count = 0
                    duration = 0
                    
                    lines = output.split('\n')
                    for line in lines:
                        if "ID:" in line:
                            topic_id = line.split("ID: ")[1].strip()
                        elif "Category:" in line:
                            category = line.split("Category: ")[1].strip()
                            categories[category] = categories.get(category, 0) + 1
                        elif "Q&A pairs extracted:" in line:
                            try:
                                qa_count = int(line.split("Q&A pairs extracted: ")[1].strip())
                                total_qa_pairs += qa_count
                            except:
                                pass
                        elif "Duration:" in line:
                            try:
                                duration = float(line.split("Duration: ")[1].replace('s', '').strip())
                            except:
                                pass
                    
                    print(f"   ✅ Topic {topic_id}: {qa_count} Q&A, {category}, {duration:.1f}s")
                else:
                    failed += 1
                    print("   ❌ Failed")
            else:
                failed += 1
                print(f"   ❌ Process failed (code: {result.returncode})")
                
        except subprocess.TimeoutExpired:
            failed += 1
            print("   ❌ Timed out (>60s)")
        except Exception as e:
            failed += 1
            print(f"   ❌ Error: {e}")
    
    # Final summary
    total_time = time.time() - start_time
    total_processed = successful + failed
    
    print(f"\n🎯 TEST COMPLETE")
    print("=" * 25)
    print(f"Duration: {total_time/60:.1f} minutes")
    print(f"Topics processed: {total_processed}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(successful/total_processed)*100:.1f}%")
    print(f"Total Q&A pairs: {total_qa_pairs}")
    
    if successful > 0:
        avg_time = total_time / successful
        rate = successful / total_time
        print(f"Average per topic: {avg_time:.1f}s")
        print(f"Processing rate: {rate:.2f} topics/second")
        print(f"Projected time for 100 topics: {(100 * avg_time)/60:.1f} minutes")
    
    if categories:
        print(f"\nCategories:")
        for cat, count in sorted(categories.items()):
            print(f"  {cat}: {count}")
    
    print(f"\nFinished at: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()