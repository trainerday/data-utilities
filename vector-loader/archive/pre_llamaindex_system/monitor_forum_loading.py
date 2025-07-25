#!/usr/bin/env python3
"""
Monitor forum data loading progress
"""

import os
import time
import json
from pathlib import Path
from datetime import datetime

def format_duration(seconds):
    """Format duration in human readable format"""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    elif minutes > 0:
        return f"{int(minutes)}m {int(seconds)}s"
    else:
        return f"{int(seconds)}s"

def monitor_progress():
    """Monitor the forum loading progress"""
    log_file = Path("forum_loader_progress.log")
    progress_file = Path("forum_loading_progress_report.json")
    
    print("🔍 FORUM DATA LOADING MONITOR")
    print("=" * 50)
    print("📁 Monitoring files:")
    print(f"  • Log: {log_file}")
    print(f"  • Progress: {progress_file}")
    print("=" * 50)
    
    last_log_size = 0
    last_progress_check = None
    
    while True:
        try:
            # Check log file for new content
            if log_file.exists():
                current_size = log_file.stat().st_size
                if current_size > last_log_size:
                    # Read new content
                    with open(log_file, 'r') as f:
                        f.seek(last_log_size)
                        new_content = f.read()
                        if new_content.strip():
                            print("\n📄 NEW LOG CONTENT:")
                            print("-" * 30)
                            for line in new_content.strip().split('\n'):
                                if any(keyword in line for keyword in ['Progress:', 'PHASE', 'COMPLETE', 'ERROR', 'batch']):
                                    print(f"  {line}")
                    last_log_size = current_size
            
            # Check progress report
            if progress_file.exists():
                try:
                    with open(progress_file, 'r') as f:
                        progress = json.load(f)
                    
                    current_check = progress.get('timestamp')
                    if current_check != last_progress_check:
                        print(f"\n📊 PROGRESS UPDATE ({datetime.now().strftime('%H:%M:%S')}):")
                        print("-" * 40)
                        
                        prog_data = progress.get('progress', {})
                        start_time = prog_data.get('start_time')
                        if start_time:
                            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                            duration = datetime.now().replace(tzinfo=start_dt.tzinfo) - start_dt
                            print(f"  ⏱️  Running time: {format_duration(duration.total_seconds())}")
                        
                        qa_processed = prog_data.get('qa_docs_processed', 0)
                        raw_processed = prog_data.get('raw_docs_processed', 0)
                        total_qa = prog_data.get('total_qa_docs', 0)
                        total_raw = prog_data.get('total_raw_docs', 0)
                        
                        print(f"  📖 Q&A Documents: {qa_processed}/{total_qa}")
                        print(f"  💬 Raw Documents: {raw_processed}/{total_raw}")
                        print(f"  💰 Estimated Cost: ${prog_data.get('embedding_cost_estimate', 0):.4f}")
                        
                        errors = prog_data.get('errors', [])
                        if errors:
                            print(f"  ❌ Errors: {len(errors)}")
                            for error in errors[-3:]:  # Show last 3 errors
                                print(f"     {error}")
                        
                        last_progress_check = current_check
                
                except json.JSONDecodeError:
                    pass  # File might be being written
            
            time.sleep(5)  # Check every 5 seconds
            
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped")
            break
        except Exception as e:
            print(f"\n⚠️  Monitor error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_progress()