#!/usr/bin/env python3
"""
Simple Batch Runner - Runs multiple single processors in sequence
No complex threading/locking - just runs the working single processor multiple times
"""

import subprocess
import time
from datetime import datetime

def run_single_processor():
    """Run the single topic processor that we know works"""
    try:
        result = subprocess.run(
            ['python3', 'process_next_latest.py'],
            capture_output=True,
            text=True,
            timeout=90
        )
        
        if result.returncode == 0:
            output = result.stdout
            
            # Check for completion
            if "No unprocessed topics found!" in output:
                return {'status': 'no_more_topics'}
            
            # Parse success
            if "✅ Success!" in output:
                # Extract details
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
                    elif "Q&A pairs extracted:" in line:
                        try:
                            qa_count = int(line.split("Q&A pairs extracted: ")[1].strip())
                        except:
                            pass
                    elif "Duration:" in line:
                        try:
                            duration_str = line.split("Duration: ")[1].replace('s', '').strip()
                            duration = float(duration_str)
                        except:
                            pass
                
                return {
                    'status': 'success',
                    'topic_id': topic_id,
                    'category': category,
                    'qa_count': qa_count,
                    'duration': duration
                }
            else:
                return {'status': 'failed', 'error': 'Analysis failed'}
        else:
            return {'status': 'failed', 'error': f'Process failed (code: {result.returncode})'}
            
    except subprocess.TimeoutExpired:
        return {'status': 'timeout'}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def main():
    print("🚀 Simple Batch Runner")
    print("=" * 25)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Configuration
    TARGET_TOPICS = 30  # Process 30 topics in this batch
    
    print(f"Target: {TARGET_TOPICS} topics")
    print("Using proven single processor in loop")
    print("=" * 25)
    
    # Statistics
    successful = 0
    failed = 0
    timeouts = 0
    total_qa_pairs = 0
    categories = {}
    durations = []
    
    start_time = time.time()
    
    for i in range(TARGET_TOPICS):
        current_time = datetime.now().strftime('%H:%M:%S')
        print(f"\n[{current_time}] 🎯 Processing {i+1}/{TARGET_TOPICS}")
        
        result = run_single_processor()
        
        if result['status'] == 'success':
            successful += 1
            total_qa_pairs += result['qa_count']
            category = result['category']
            categories[category] = categories.get(category, 0) + 1
            durations.append(result['duration'])
            
            print(f"   ✅ Topic {result['topic_id']}: {result['qa_count']} Q&A, {category}, {result['duration']:.1f}s")
            
        elif result['status'] == 'no_more_topics':
            print("   ✅ No more unprocessed topics available!")
            break
            
        elif result['status'] == 'timeout':
            timeouts += 1
            print("   ⏱️ Timeout (>90s)")
            
        else:
            failed += 1
            error_msg = result.get('error', 'Unknown error')[:30]
            print(f"   ❌ Failed: {error_msg}")
        
        # Progress updates every 5 topics
        if (i + 1) % 5 == 0:
            elapsed = time.time() - start_time
            total_processed = successful + failed + timeouts
            
            print(f"\n📊 Progress: {i+1}/{TARGET_TOPICS}")
            print(f"   Successful: {successful}")
            print(f"   Failed: {failed}")
            print(f"   Timeouts: {timeouts}")
            print(f"   Success rate: {(successful/total_processed)*100:.1f}%")
            print(f"   Elapsed: {elapsed/60:.1f}m")
            
            if successful > 0 and durations:
                avg_time = sum(durations) / len(durations)
                rate = successful / elapsed
                remaining = TARGET_TOPICS - (i + 1)
                eta = (remaining * avg_time) / 60
                
                print(f"   Avg per topic: {avg_time:.1f}s")
                print(f"   Rate: {rate:.2f} topics/sec")
                print(f"   ETA: {eta:.1f}m")
        
        # Brief pause between topics
        time.sleep(1)
    
    # Final summary
    total_time = time.time() - start_time
    total_processed = successful + failed + timeouts
    
    print(f"\n🎯 BATCH PROCESSING COMPLETE")
    print("=" * 35)
    print(f"Duration: {total_time/60:.1f} minutes")
    print(f"Processed: {total_processed}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Timeouts: {timeouts}")
    print(f"Success rate: {(successful/total_processed)*100:.1f}%" if total_processed > 0 else "0%")
    print(f"Q&A pairs: {total_qa_pairs}")
    
    if successful > 0 and durations:
        avg_time = sum(durations) / len(durations)
        rate = successful / total_time
        print(f"Avg time: {avg_time:.1f}s")
        print(f"Rate: {rate:.2f} topics/sec")
    
    if categories:
        print(f"\nCategories:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count}")

if __name__ == "__main__":
    main()