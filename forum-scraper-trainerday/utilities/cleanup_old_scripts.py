#!/usr/bin/env python3
"""
Cleanup Old Forum Scraping Scripts
Safely removes old file-based scripts and moves them to archive.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def main():
    print("Forum Scraper Cleanup - Archive Old Scripts")
    print("=" * 50)
    
    script_dir = Path(__file__).parent
    archive_dir = script_dir / "archived_scripts"
    
    # Create archive directory
    archive_dir.mkdir(exist_ok=True)
    
    # Files to archive
    files_to_archive = [
        "get_forum_data.py",
        "consolidate_forum_data.py"
    ]
    
    # Optional: Archive the forum_data directory too
    forum_data_dir = script_dir / "forum_data"
    
    archived_count = 0
    
    # Archive old scripts
    for filename in files_to_archive:
        file_path = script_dir / filename
        if file_path.exists():
            archive_path = archive_dir / filename
            shutil.move(str(file_path), str(archive_path))
            print(f"✅ Archived: {filename} → archived_scripts/")
            archived_count += 1
        else:
            print(f"⚠️  Not found: {filename}")
    
    # Archive forum_data directory automatically since data is now in database
    if forum_data_dir.exists():
        file_count = len(list(forum_data_dir.glob("*.json")))
        print(f"\n📁 Found forum_data directory with {file_count} files")
        print("   This contains the old JSON files from file-based scraping")
        print("   Data is now stored in database - archiving automatically...")
        
        archive_forum_path = archive_dir / "forum_data"
        shutil.move(str(forum_data_dir), str(archive_forum_path))
        print(f"✅ Archived: forum_data/ → archived_scripts/forum_data/")
        archived_count += 1
    
    print(f"\n📊 Summary:")
    print(f"   Archived files: {archived_count}")
    print(f"   Archive location: {archive_dir}")
    
    if archived_count > 0:
        print(f"\n🎯 Migration Complete!")
        print("   ✅ Old file-based scripts archived")
        print("   ✅ New database-based scraper ready: discourse_to_database.py")
        print("   ✅ Enhanced analysis system ready: analyze_forum_topics_v2.py")
        print("\n📋 Next Steps:")
        print("   1. Run: python discourse_to_database.py --mode full")
        print("   2. Run: python script-testing/analyze_forum_topics_v2.py")
        print("   3. Use: python script-testing/incremental_analysis_v2.py for updates")
    
    # Create a README for the new system
    readme_content = """# TrainerDay Forum Analysis System v2

## New Database-Based Architecture

The forum analysis system has been upgraded to use PostgreSQL for both raw content storage and analysis results.

## Scripts Overview

### Data Collection
- `discourse_to_database.py` - Scrapes Discourse forum API and stores raw content directly to database
- Replaces old file-based scraping (`get_forum_data.py`, `consolidate_forum_data.py`)

### Analysis & Processing
- `script-testing/analyze_forum_topics_v2.py` - Analyzes raw content with LLM and stores insights
- `script-testing/incremental_analysis_v2.py` - Handles incremental updates efficiently
- `script-testing/query_analysis_results_v2.py` - Query and view analysis results

### Utilities
- `script-testing/clear_database.py` - Clear all analysis tables for fresh start
- `script-testing/debug_failed_topic.py` - Debug failed analysis topics

## Quick Start

1. **Scrape Forum Data:**
   ```bash
   python discourse_to_database.py --mode full --max-pages 10
   ```

2. **Analyze Content:**
   ```bash
   python script-testing/analyze_forum_topics_v2.py
   ```

3. **View Results:**
   ```bash
   python script-testing/query_analysis_results_v2.py
   ```

4. **Incremental Updates:**
   ```bash
   python discourse_to_database.py --mode incremental
   python script-testing/incremental_analysis_v2.py
   ```

## Benefits of v2 System

- **Complete Data Warehouse**: Raw content and analysis stored in database
- **Incremental Updates**: Only process changed content
- **Enhanced Error Reporting**: Clear failure tracking and reporting
- **Future-Proof**: Can re-analyze raw content with different strategies
- **Efficient**: Smart change detection saves API costs and processing time

## Database Tables

- `forum_topics_raw` - Complete raw forum content from Discourse API
- `forum_topics` - Topic metadata and analysis categories
- `forum_qa_pairs` - Extracted question/answer pairs
- `forum_voice_patterns` - User vs platform voice analysis
- `forum_insights` - Content opportunities and messaging insights

## Environment Variables Required

```env
# Database Connection
DB_HOST=your-postgres-host
DB_PORT=5432
DB_DATABASE=your-database
DB_USERNAME=your-username
DB_PASSWORD=your-password
DB_SSLMODE=require
DB_SSLROOTCERT=.postgres.crt

# Discourse API
DISCOURSE_API_KEY=your-api-key
DISCOURSE_API_USERNAME=your-username

# OpenAI API
OPENAI_API_KEY=your-openai-key
```
"""
    
    readme_path = script_dir / "README_v2.md"
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"\n📖 Created: README_v2.md with usage instructions")

if __name__ == "__main__":
    main()