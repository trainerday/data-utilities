#!/usr/bin/env python3
"""
Process 200 Topics - Production Run
Uses the fast gpt-4o-mini model
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

def main():
    print("🚀 Processing 200 Topics - Production Run")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Configuration
    TARGET_TOPICS = 200
    
    # Statistics tracking
    successful = 0
    failed = 0
    total_qa_pairs = 0
    categories = {}
    durations = []
    start_time = time.time()
    
    print(f"Target: {TARGET_TOPICS} topics")
    print(f"Using fast gpt-4o-mini model")
    print("=" * 50)
    
    for i in range(TARGET_TOPICS):
        current_time = datetime.now().strftime('%H:%M:%S')
        print(f"\n[{current_time}] 🎯 Topic {i+1}/{TARGET_TOPICS}")
        
        try:
            # Run the single topic processor
            result = subprocess.run([
                'python3', 'process_next_latest.py'
            ], capture_output=True, text=True, timeout=90)  # 90 second timeout
            
            if result.returncode == 0:
                output = result.stdout
                
                # Check if no more topics
                if "No unprocessed topics found!" in output:
                    print("✅ No more unprocessed topics available!")
                    break
                
                # Parse successful result
                if "✅ Success!" in output:
                    successful += 1
                    
                    # Extract details from output
                    topic_id = "Unknown"
                    category = "Unknown" 
                    qa_count = 0
                    duration = 0
                    posts = 0
                    
                    lines = output.split('\n')
                    for line in lines:
                        if "ID:" in line:
                            topic_id = line.split("ID: ")[1].strip()
                        elif "Posts:" in line:
                            try:
                                posts = int(line.split("Posts: ")[1].strip())
                            except:
                                pass
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
                                duration_str = line.split("Duration: ")[1].replace('s', '').strip()
                                duration = float(duration_str)
                                durations.append(duration)
                            except:
                                pass
                    
                    print(f"   ✅ Topic {topic_id}: {qa_count} Q&A, {category}, {duration:.1f}s ({posts} posts)")
                
                else:
                    failed += 1
                    print("   ❌ Analysis failed")
                    
            else:
                failed += 1
                print(f"   ❌ Process failed (return code: {result.returncode})")
                
        except subprocess.TimeoutExpired:
            failed += 1
            print("   ❌ Timed out after 90 seconds")
        except Exception as e:
            failed += 1
            print(f"   ❌ Error: {str(e)[:50]}...")
        
        # Progress updates every 10 topics
        if (i + 1) % 10 == 0:
            elapsed = time.time() - start_time
            total_processed = successful + failed
            
            print(f"\n📊 Progress Update - {i+1}/{TARGET_TOPICS}")
            print(f"   Successful: {successful}")
            print(f"   Failed: {failed}")
            print(f"   Success rate: {(successful/total_processed)*100:.1f}%")
            print(f"   Elapsed time: {elapsed/60:.1f} minutes")
            
            if successful > 0:
                avg_time = sum(durations) / len(durations) if durations else 0
                rate = successful / elapsed
                remaining = TARGET_TOPICS - (i + 1)
                eta_minutes = (remaining / rate / 60) if rate > 0 else 0
                
                print(f"   Average per topic: {avg_time:.1f}s")
                print(f"   Processing rate: {rate:.2f} topics/second")
                print(f"   ETA: {eta_minutes:.1f} minutes")
        
        # Brief pause between topics to avoid overwhelming the system
        time.sleep(1)
    
    # Final summary
    total_time = time.time() - start_time
    total_processed = successful + failed
    
    print(f"\n🎯 PRODUCTION RUN COMPLETE")
    print("=" * 40)
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total duration: {total_time/60:.1f} minutes ({total_time/3600:.1f} hours)")
    print(f"Topics processed: {total_processed}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(successful/total_processed)*100:.1f}%")
    print(f"Total Q&A pairs extracted: {total_qa_pairs}")
    
    if successful > 0:
        avg_time = sum(durations) / len(durations) if durations else 0
        rate = successful / total_time
        print(f"Average time per topic: {avg_time:.1f}s")
        print(f"Overall processing rate: {rate:.2f} topics/second")
        print(f"Q&A pairs per topic: {total_qa_pairs/successful:.1f}")
        
        # Project completion time
        remaining_topics = 1536 - successful  # Rough estimate
        completion_hours = (remaining_topics / rate) / 3600 if rate > 0 else 0
        print(f"Estimated time to complete all topics: {completion_hours:.1f} hours")
    
    if categories:
        print(f"\n📂 Categories Processed:")
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        for category, count in sorted_categories:
            percentage = (count / successful) * 100 if successful > 0 else 0
            print(f"   {category}: {count} ({percentage:.1f}%)")
    
    if durations:
        print(f"\n⏱️  Timing Statistics:")
        print(f"   Fastest topic: {min(durations):.1f}s")
        print(f"   Slowest topic: {max(durations):.1f}s")
        print(f"   Median time: {sorted(durations)[len(durations)//2]:.1f}s")
    
    print(f"\n🎉 Processed {successful} topics successfully!")

if __name__ == "__main__":
    main()