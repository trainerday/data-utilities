#!/usr/bin/env python3
"""
Reorganize project structure - move files to appropriate locations
"""

import os
import shutil
from pathlib import Path

def reorganize_project():
    """Create new directory structure and move files"""
    
    base_dir = Path('.')
    
    # Create directory structure
    directories = {
        'archive': base_dir / 'archive',
        'archive_dev': base_dir / 'archive' / 'llamaindex_development', 
        'archive_old': base_dir / 'archive' / 'pre_llamaindex_system',
        'archive_logs': base_dir / 'archive' / 'logs_and_data',
        'production': base_dir / 'production',
        'production_loaders': base_dir / 'production' / 'data_loaders',
        'production_facts': base_dir / 'production' / 'facts_system',
        'production_utils': base_dir / 'production' / 'utilities',
    }
    
    print("📁 Creating directory structure...")
    for name, path in directories.items():
        path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {path}")
    
    # File categorization
    file_moves = {
        # Production Data Loaders
        'production_loaders': [
            'forum_data_loader_step1.py',
            'blog_data_loader.py', 
            'youtube_data_loader.py',
            'facts_data_loader.py',
            'merge_facts_tables.py',
        ],
        
        # Production Facts System
        'production_facts': [
            'enhance_all_articles.py',
            'enhance_articles_from_facts.py',
            'create_facts_spreadsheet.py',
            'extract_facts_to_database.py',
            'populate_existing_spreadsheet.py',
            'update_facts_preserve_status.py',
        ],
        
        # Production Utilities
        'production_utils': [
            'direct_query_zone2.py',
            'test_unified_knowledge_base.py', 
            'check_facts_status.py',
            'explore_false_facts.py',
            'monitor_progress.py',
            'check_processing_status.py',
            'list_drive_files.py',
            'export_facts_csv.py',
        ],
        
        # Archive - LlamaIndex Development
        'archive_dev': [
            'fresh_llamaindex_test.py',
            'llamaindex_comparison.py',
            'llamaindex_fact_extraction.py',
            'llamaindex_fact_extraction_fixed.py',
            'llamaindex_fact_extraction_v2.py',
            'llamaindex_final_solution.py',
            'llamaindex_improved_retrieval.py',
            'llamaindex_threshold_test.py',
            'llamaindex_blog_test.py',
            'llamaindex_blog_youtube_loader.py',
            'simple_query_test.py',
            'test_knowledge_base.py',
            'test_forum_knowledge_base.py',
            'test_vector_direct.py',
            'test_false_fact_query.py',
            'test_false_fact_simple.py',
            'rebuild_index_only.py',
        ],
        
        # Archive - Pre-LlamaIndex System
        'archive_old': [
            'enhanced_forum_loader.py',
            'explore_forum_database.py',
            'search_youtube_database.py',
            'monitor_forum_loading.py',
            'debug_facts_table.py',
            'extract_facts_basic.py',
            'extract_facts_batch.py',
            'populate_td_blog_facts.py',
            'process_negative_one_facts.py',
            'process_remaining_articles.py',
        ],
        
        # Archive - Logs and Data
        'archive_logs': [
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
            'run_background_load.sh',
            'run_continuous_processing.sh',
        ]
    }
    
    print(f"\n📦 Moving files...")
    
    # Move files
    for dest_key, files in file_moves.items():
        dest_path = directories[dest_key]
        print(f"\n  📁 Moving to {dest_path}:")
        
        for filename in files:
            src_path = base_dir / filename
            dest_file = dest_path / filename
            
            if src_path.exists():
                try:
                    shutil.move(str(src_path), str(dest_file))
                    print(f"    ✅ {filename}")
                except Exception as e:
                    print(f"    ❌ {filename}: {e}")
            else:
                print(f"    ⚠️  {filename}: Not found")
    
    # Move llamaindex_storage directory
    storage_src = base_dir / 'llamaindex_storage'
    storage_dest = directories['archive_logs'] / 'llamaindex_storage'
    if storage_src.exists():
        try:
            shutil.move(str(storage_src), str(storage_dest))
            print(f"    ✅ llamaindex_storage/ directory")
        except Exception as e:
            print(f"    ❌ llamaindex_storage/: {e}")
    
    print(f"\n✅ Reorganization complete!")
    print(f"\n📊 NEW STRUCTURE:")
    print("  production/")
    print("    ├── data_loaders/     (5 core data loading scripts)")
    print("    ├── facts_system/     (6 facts management scripts)")
    print("    └── utilities/        (8 utility and testing scripts)")
    print("  archive/")
    print("    ├── llamaindex_development/  (17 development scripts)")
    print("    ├── pre_llamaindex_system/   (10 old system scripts)")
    print("    └── logs_and_data/           (27 logs and temp files)")

if __name__ == "__main__":
    reorganize_project()