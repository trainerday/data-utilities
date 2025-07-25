#!/usr/bin/env python3
"""
Analyze and categorize scripts for organization
"""

import os
from pathlib import Path

def categorize_scripts():
    """Categorize scripts into keep vs archive"""
    
    # Current LlamaIndex Production Scripts (KEEP)
    llamaindex_production = [
        'forum_data_loader_step1.py',          # ✅ Main forum loader
        'blog_data_loader.py',                 # ✅ Main blog loader  
        'youtube_data_loader.py',              # ✅ Main YouTube loader
        'facts_data_loader.py',                # ✅ Main facts loader
        'merge_facts_tables.py',               # ✅ Facts table merger
        'direct_query_zone2.py',               # ✅ Working query example
        'test_unified_knowledge_base.py',      # ✅ Main testing script
        'check_facts_status.py',               # ✅ Status checker
        'explore_false_facts.py',              # ✅ False fact explorer
    ]
    
    # Current Facts System Scripts (KEEP)
    facts_production = [
        'enhance_all_articles.py',             # ✅ Main enhancement script
        'enhance_articles_from_facts.py',      # ✅ Fact-based enhancement
        'create_facts_spreadsheet.py',         # ✅ Google Sheets integration
        'extract_facts_to_database.py',        # ✅ Fact extraction
        'populate_existing_spreadsheet.py',    # ✅ Sheet population
        'update_facts_preserve_status.py',     # ✅ Status preservation
    ]
    
    # Utility Scripts (KEEP)
    utilities = [
        'monitor_progress.py',                  # ✅ Progress monitoring
        'check_processing_status.py',          # ✅ Status checking
        'list_drive_files.py',                 # ✅ Drive file listing
        'export_facts_csv.py',                 # ✅ CSV export
    ]
    
    # LlamaIndex Development/Testing (ARCHIVE - but useful for reference)
    llamaindex_development = [
        'fresh_llamaindex_test.py',            # 📦 Initial testing
        'llamaindex_comparison.py',            # 📦 System comparison
        'llamaindex_fact_extraction.py',       # 📦 Fact extraction tests
        'llamaindex_fact_extraction_fixed.py', # 📦 Fixed extraction
        'llamaindex_fact_extraction_v2.py',    # 📦 Version 2
        'llamaindex_final_solution.py',        # 📦 Final solution test
        'llamaindex_improved_retrieval.py',    # 📦 Retrieval improvement
        'llamaindex_threshold_test.py',        # 📦 Threshold testing
        'llamaindex_blog_test.py',             # 📦 Blog testing
        'llamaindex_blog_youtube_loader.py',   # 📦 Combined loader (superseded)
        'simple_query_test.py',                # 📦 Simple query test
        'test_knowledge_base.py',              # 📦 KB testing
        'test_forum_knowledge_base.py',        # 📦 Forum KB testing
        'test_vector_direct.py',               # 📦 Direct vector test
        'test_false_fact_query.py',            # 📦 False fact testing
        'test_false_fact_simple.py',           # 📦 Simplified false fact test
        'rebuild_index_only.py',               # 📦 Index rebuilding
    ]
    
    # Pre-LlamaIndex System (ARCHIVE - old system)
    pre_llamaindex = [
        'enhanced_forum_loader.py',            # 📦 Old forum loader
        'explore_forum_database.py',           # 📦 Database exploration
        'search_youtube_database.py',          # 📦 YouTube search
        'monitor_forum_loading.py',            # 📦 Forum monitoring
        'debug_facts_table.py',                # 📦 Debug script
        'extract_facts_basic.py',              # 📦 Basic extraction
        'extract_facts_batch.py',              # 📦 Batch extraction
        'populate_td_blog_facts.py',           # 📦 Facts population
        'process_negative_one_facts.py',       # 📦 Negative facts
        'process_remaining_articles.py',       # 📦 Remaining articles
    ]
    
    # Log Files and Data (ARCHIVE/CLEAN)
    logs_and_data = [
        'all_articles_enhancement.log',
        'blog_loader_progress.log',
        'enhancement_full.log', 
        'enhancement_log.txt',
        'facts_loader_progress.log',
        'facts_loading_output.log',
        'forum_loader_progress.log',
        'forum_loading_output.log',
        'llamaindex_bg_load.log',
        'llamaindex_blog_youtube_load.log',
        'llamaindex_full_load.log',
        'llamaindex_load_output.log',
        'youtube_loader_progress.log',
        'blog_loading_progress_report.json',
        'facts_loading_progress_report.json',
        'forum_loading_progress_report.json',
        'llamaindex_blog_youtube_progress.json',
        'llamaindex_load_progress.json',
        'youtube_loading_progress_report.json',
        'extracted_facts_20250723_224104.txt',
        'td-blog-facts_20250723_231114.csv',
        'forum_database_analysis_report.md',
        'forum_database_investigation_report.md',
        'llamaindex_poc_summary.md',
        'llamaindex_storage/',
        'run_background_load.sh',
        'run_continuous_processing.sh',
    ]
    
    print("📊 SCRIPT ORGANIZATION PLAN")
    print("=" * 60)
    
    print(f"\n✅ KEEP - LlamaIndex Production ({len(llamaindex_production)} files):")
    for script in llamaindex_production:
        print(f"  • {script}")
    
    print(f"\n✅ KEEP - Facts System Production ({len(facts_production)} files):")
    for script in facts_production:
        print(f"  • {script}")
    
    print(f"\n✅ KEEP - Utilities ({len(utilities)} files):")
    for script in utilities:
        print(f"  • {script}")
    
    print(f"\n📦 ARCHIVE - LlamaIndex Development ({len(llamaindex_development)} files):")
    for script in llamaindex_development:
        print(f"  • {script}")
    
    print(f"\n📦 ARCHIVE - Pre-LlamaIndex System ({len(pre_llamaindex)} files):")
    for script in pre_llamaindex:
        print(f"  • {script}")
    
    print(f"\n🗑️ CLEAN - Logs and Temporary Data ({len(logs_and_data)} files):")
    for item in logs_and_data:
        print(f"  • {item}")
    
    total_keep = len(llamaindex_production) + len(facts_production) + len(utilities)
    total_archive = len(llamaindex_development) + len(pre_llamaindex) 
    total_clean = len(logs_and_data)
    
    print(f"\n📊 SUMMARY:")
    print(f"  • Keep: {total_keep} files")
    print(f"  • Archive: {total_archive} files") 
    print(f"  • Clean: {total_clean} files")
    
    return {
        'keep': {
            'llamaindex_production': llamaindex_production,
            'facts_production': facts_production,
            'utilities': utilities
        },
        'archive': {
            'llamaindex_development': llamaindex_development,
            'pre_llamaindex': pre_llamaindex
        },
        'clean': logs_and_data
    }

if __name__ == "__main__":
    categories = categorize_scripts()