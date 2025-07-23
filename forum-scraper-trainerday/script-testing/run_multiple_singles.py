#!/usr/bin/env python3
"""
Run multiple single topic analyses in sequence
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def main():
    print("🔁 Multiple Single Topic Runner")
    print("=" * 40)
    
    # Configuration
    TOPICS_TO_PROCESS = 10
    
    print(f"Will process {TOPICS_TO_PROCESS} topics by running single topic analyzer multiple times")
    
    successful = 0
    failed = 0
    total_time = 0
    start_time = time.time()
    
    for i in range(TOPICS_TO_PROCESS):
        print(f"\n🎯 Run {i+1}/{TOPICS_TO_PROCESS}")
        
        try:
            # Run the single topic analyzer as a subprocess
            result = subprocess.run([
                'python3', 'analyze_single_topic.py'
            ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
            
            if result.returncode == 0:
                print("✅ Single topic analysis completed")
                successful += 1
                
                # Extract timing info from output if possible
                output = result.stdout
                if "Total time:" in output:
                    for line in output.split('\n'):
                        if "Total time:" in line:
                            try:
                                time_str = line.split("Total time: ")[1].split("s")[0]
                                topic_time = float(time_str)
                                total_time += topic_time
                                print(f"  Topic took: {topic_time:.1f}s")
                            except:
                                pass
            else:
                print(f"❌ Single topic analysis failed (return code: {result.returncode})")
                print(f"Error output: {result.stderr[:200]}...")
                failed += 1
                
        except subprocess.TimeoutExpired:
            print(f"❌ Single topic analysis timed out after 5 minutes")
            failed += 1
        except Exception as e:
            print(f"❌ Error running single topic analysis: {e}")
            failed += 1
        
        # Progress summary
        elapsed = time.time() - start_time
        print(f"Progress: {i+1} attempts, {successful} successful, {failed} failed")
        print(f"Elapsed: {elapsed/60:.1f} minutes")
        
        if successful > 0:
            avg_time = total_time / successful if total_time > 0 else elapsed / successful
            rate = successful / elapsed
            print(f"Average per topic: {avg_time:.1f}s")
            print(f"Success rate: {rate:.2f} topics/second")
    
    # Final summary
    total_elapsed = time.time() - start_time
    print(f"\n🎯 MULTIPLE RUNS COMPLETE")
    print("=" * 30)
    print(f"Total attempts: {TOPICS_TO_PROCESS}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(successful/TOPICS_TO_PROCESS)*100:.1f}%")
    print(f"Total elapsed: {total_elapsed/60:.1f} minutes")
    
    if successful > 0:
        overall_rate = successful / total_elapsed
        print(f"Overall processing rate: {overall_rate:.2f} topics/second")
        
        # Estimate completion time for remaining topics
        remaining_estimate = 1527  # Approximate remaining topics
        completion_hours = remaining_estimate / (overall_rate * 3600) if overall_rate > 0 else 0
        print(f"Estimated time to complete all remaining topics: {completion_hours:.1f} hours")

if __name__ == "__main__":
    main()