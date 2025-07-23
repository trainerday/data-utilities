#!/usr/bin/env python3
"""
Forum Analysis Main Process
Complete pipeline: Scrape → Store → Analyze forum data from Discourse API
"""

import subprocess
import sys
import argparse
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}")
    print(f"Command: {' '.join(command)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        print(f"✅ {description} - COMPLETED")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Exit code: {e.returncode}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="Forum Analysis Main Process")
    parser.add_argument("--mode", choices=["full", "incremental"], default="incremental",
                       help="Processing mode: full (scrape everything) or incremental (changes only)")
    parser.add_argument("--max-pages", type=int, help="Max pages to scrape (for testing only)")
    parser.add_argument("--max-topics", type=int, help="Max topics to analyze (for testing only)")
    parser.add_argument("--skip-scraping", action="store_true", help="Skip scraping, just analyze existing data")
    parser.add_argument("--skip-analysis", action="store_true", help="Skip analysis, just scrape raw data")
    
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent
    
    print("🚀 FORUM ANALYSIS MAIN PROCESS")
    print("=" * 50)
    print(f"Mode: {args.mode}")
    
    if args.mode == "full":
        print("📋 FULL MODE: Will scrape ALL forum data, then analyze everything")
        if args.max_pages:
            print(f"⚠️  LIMITED TO {args.max_pages} pages (testing mode)")
        else:
            print("📊 NO LIMITS: Processing entire forum")
    else:
        print("🔄 INCREMENTAL MODE: Will scrape only new/changed content, then analyze")
    
    if args.max_topics:
        print(f"⚠️  Analysis limited to {args.max_topics} topics (testing)")
    
    print("=" * 50)
    
    success = True
    
    # Step 1: Scrape forum data incrementally (only new/changed content)
    if not args.skip_scraping:
        print("\n🌐 STEP 1: SCRAPE FORUM CONTENT")
        print("-" * 40)
        
        scrape_cmd = ["python", "discourse_to_database.py", "--mode", args.mode]
        
        # Only add max-pages for testing purposes
        if args.max_pages:
            scrape_cmd.extend(["--max-pages", str(args.max_pages)])
            print(f"⚠️  Testing mode: Limited to {args.max_pages} pages")
        elif args.mode == "full":
            print("🔄 Full scrape: Getting ALL forum data (this may take a while...)")
            print("   This will scrape the entire forum history")
        else:
            print("🔄 Incremental scrape: Getting only new/changed content")
            print("   Smart change detection - only processes updated topics")
        
        success = run_command(scrape_cmd, "STEP 1: Scrape forum data from Discourse API")
        
        if not success:
            print("\n❌ STEP 1 FAILED - Cannot proceed to analysis")
            print("   Fix scraping issues before running analysis")
            sys.exit(1)
        
        print("✅ STEP 1 COMPLETE: Raw forum data stored in database")
    
    # Step 2: Analyze content incrementally (only unanalyzed topics)  
    if not args.skip_analysis:
        print("\n🤖 STEP 2: ANALYZE FORUM CONTENT")  
        print("-" * 40)
        
        if args.skip_scraping:
            print("🔄 Incremental analysis: Processing unanalyzed topics in database")
        else:
            print("🔄 Incremental analysis: Processing new + unanalyzed topics")
            
        print("   Smart processing - only analyzes topics needing analysis")
        
        analyze_cmd = ["python", "scripts/analyze_forum_topics.py"]
        
        if args.max_topics:
            print(f"⚠️  Testing mode: Limited to {args.max_topics} topics")
            # Note: The analysis script would need to support this parameter
        
        success = run_command(analyze_cmd, "STEP 2: Analyze forum topics with OpenAI LLM")
        
        if not success:
            print("\n⚠️  STEP 2 FAILED - but raw data from Step 1 is safe")
            print("   You can retry analysis later with:")
            print("   python scripts/analyze_forum_topics.py")
            print("\n💡 Common analysis issues:")
            print("   - OpenAI API key not set or invalid")
            print("   - Database connection issues")
            print("   - Large topics hitting token limits")
        else:
            print("✅ STEP 2 COMPLETE: Forum analysis finished successfully")
    
    print("\n" + "=" * 50)
    
    if success:
        print("🎉 FORUM ANALYSIS PROCESS COMPLETED!")
        print("\n📊 Next steps:")
        print("   • View results: python scripts/query_results.py")
        print("   • Set up daily updates: python run_forum_analysis.py")
        print("   • Debug failures: python utilities/debug_failed_topic.py")
    else:
        print("⚠️  PROCESS COMPLETED WITH SOME FAILURES")
        print("   Check the error messages above for details")
        print("   Raw data may still be available for manual analysis")

if __name__ == "__main__":
    main()
