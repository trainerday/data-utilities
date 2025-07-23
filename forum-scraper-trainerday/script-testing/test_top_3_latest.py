#!/usr/bin/env python3
"""
Test with Top 3 Latest Topics
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

def main():
    print("🧪 Test Top 3 Latest Topics")
    print("=" * 35)
    
    successful = 0
    failed = 0
    
    for i in range(3):
        print(f"\n🎯 Test topic {i+1}/3")
        
        try:
            result = subprocess.run([
                'python3', 'process_next_latest.py'
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                output = result.stdout
                if "No unprocessed topics found!" in output:
                    print("✅ No more topics available")
                    break
                elif "✅ Success!" in output:
                    successful += 1
                    # Extract topic info
                    lines = output.split('\n')
                    for line in lines:
                        if "ID:" in line:
                            print(f"   {line.strip()}")
                        elif "Category:" in line:
                            print(f"   {line.strip()}")
                        elif "Duration:" in line:
                            print(f"   {line.strip()}")
                else:
                    failed += 1
                    print("❌ Failed")
            else:
                failed += 1
                print(f"❌ Process failed")
                
        except subprocess.TimeoutExpired:
            failed += 1
            print("❌ Timed out")
        except Exception as e:
            failed += 1
            print(f"❌ Error: {e}")
        
        time.sleep(1)  # Small delay between topics
    
    print(f"\n🎯 Test Complete: {successful} successful, {failed} failed")

if __name__ == "__main__":
    main()