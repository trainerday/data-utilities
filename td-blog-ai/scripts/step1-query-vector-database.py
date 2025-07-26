#!/usr/bin/env python3
"""
Step 1: Query the vector database for all features
This script queries the LlamaIndex vector database and saves results to article_features.json
"""

import sys
import subprocess
from pathlib import Path

def main():
    # Check if query file is provided
    if len(sys.argv) < 2:
        print("❌ Error: No query file specified")
        print("Usage: python step1-query-vector-database.py <query-file-name>")
        print("Example: python step1-query-vector-database.py workout-queries")
        sys.exit(1)
    
    query_file = sys.argv[1]
    
    print("\n📊 Step 1: Querying Vector Database")
    print("=" * 50)
    
    # Run the query script
    result = subprocess.run(
        [sys.executable, "scripts/query_all_article_features.py", query_file],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Error querying vector database:")
        print(result.stderr)
        sys.exit(1)
    
    print(result.stdout)
    
    # Verify output file exists
    output_file = Path("article-temp-files/article_features.json")
    if output_file.exists():
        print(f"✅ Query results saved to: {output_file}")
    else:
        print("❌ Error: Query results file not created")
        sys.exit(1)

if __name__ == "__main__":
    main()