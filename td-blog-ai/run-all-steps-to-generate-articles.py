#!/usr/bin/env python3
"""
Run all steps to generate TrainerDay articles
This script orchestrates the complete article generation workflow
"""

import sys
import subprocess
import time
from pathlib import Path


def run_step(step_name: str, script_path: str, args: list = None) -> bool:
    """Run a single step and return success status"""
    print(f"\n{'='*60}")
    print(f"🚀 Running {step_name}")
    print(f"{'='*60}")
    
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n✅ {step_name} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {step_name} failed with error code {e.returncode}")
        return False
    except Exception as e:
        print(f"\n❌ {step_name} failed with error: {e}")
        return False


def main():
    """Run all steps to generate articles"""
    
    # Check if query file is provided
    if len(sys.argv) < 2:
        print("❌ Error: No query file specified")
        print("Usage: python run-all-steps-to-generate-articles.py <query-file-name>")
        print("Example: python run-all-steps-to-generate-articles.py workout-queries")
        sys.exit(1)
    
    query_file = sys.argv[1]
    
    print("\n🎯 TrainerDay Article Generation Pipeline")
    print("=" * 60)
    print(f"Query file: {query_file}")
    print("=" * 60)
    
    # Define all steps
    steps = [
        {
            "name": "Step 1: Query Vector Database",
            "script": "scripts/step1-query-vector-database.py",
            "args": [query_file],
            "description": "Queries the LlamaIndex vector database for relevant content"
        },
        {
            "name": "Step 2: Generate Article Content",
            "script": "scripts/step2-generate-article-content.py",
            "args": None,
            "description": "Generates main content for each article section (LLM call)"
        },
        {
            "name": "Step 3: Generate YAML Metadata",
            "script": "scripts/step3-generate-yaml-metadata.py",
            "args": None,
            "description": "Adds YAML front matter to each article (LLM call)"
        },
        {
            "name": "Step 4: Apply Style and Edits",
            "script": "scripts/step4-apply-style-and-edits.py",
            "args": None,
            "description": "Applies Alex's writing style and user edits (LLM call)"
        },
        {
            "name": "Step 5: Generate Overview",
            "script": "scripts/step5-generate-overview.py",
            "args": None,
            "description": "Creates overview article linking to all sections (LLM call)"
        }
    ]
    
    # Track timing
    start_time = time.time()
    
    # Run each step
    for i, step in enumerate(steps, 1):
        print(f"\n📋 {step['description']}")
        
        if not run_step(step['name'], step['script'], step['args']):
            print(f"\n❌ Pipeline failed at {step['name']}")
            print("Please check the error above and try again.")
            sys.exit(1)
        
        # Add a small delay between steps
        if i < len(steps):
            time.sleep(2)
    
    # Calculate total time
    total_time = time.time() - start_time
    minutes = int(total_time // 60)
    seconds = int(total_time % 60)
    
    # Success message
    print("\n" + "=" * 60)
    print("✨ 🎉 Article Generation Complete! 🎉 ✨")
    print("=" * 60)
    print(f"⏱️  Total time: {minutes}m {seconds}s")
    print(f"📁 Articles saved to: output/articles-ai/")
    print(f"📁 Originals saved to: output/_originals/")
    print("\n📋 Generated files:")
    
    # List generated files
    output_dir = Path("output/articles-ai")
    if output_dir.exists():
        files = sorted(output_dir.glob("*.md"))
        for f in files:
            print(f"   - {f.name}")
    
    print("\n🚀 Next steps:")
    print("   1. Review the generated articles")
    print("   2. Make any manual edits")
    print("   3. Run finalize_edits.py to track changes")
    print("   4. Copy to blog system as needed")


if __name__ == "__main__":
    main()