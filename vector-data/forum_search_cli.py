#!/usr/bin/env python3
"""
CLI interface for searching the forum vector database
"""

import argparse
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from forum_vectorizer import ForumVectorizer

def main():
    parser = argparse.ArgumentParser(description="Search forum vector database")
    parser.add_argument("query", help="Search query")
    parser.add_argument("-n", "--num-results", type=int, default=10, help="Number of results (default: 10)")
    parser.add_argument("-t", "--doc-type", choices=["topic", "post", "conversation"], 
                       help="Filter by document type")
    parser.add_argument("--topic-id", type=int, help="Filter by specific topic ID")
    parser.add_argument("--username", help="Filter by username")
    parser.add_argument("--after-date", help="Filter by date (YYYY-MM-DD), show results after this date")
    parser.add_argument("--recent-months", type=int, help="Filter by recent months (e.g., 2 for last 2 months)")
    parser.add_argument("--db-path", default="../chroma_db", help="Database path (default: ../chroma_db)")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    parser.add_argument("--index", help="Index forum data from path before searching")
    
    args = parser.parse_args()
    
    if not Path(args.db_path).exists() and not args.index:
        print(f"Database not found at {args.db_path}")
        print("Use --index to create the database first, or run the forum indexer.")
        sys.exit(1)
    
    try:
        vectorizer = ForumVectorizer(db_path=args.db_path)
        
        # Index data if requested
        if args.index:
            print(f"Indexing forum data from: {args.index}")
            docs_processed = vectorizer.index_forum_data(args.index)
            print(f"Indexed {docs_processed} documents")
            print()
        
        if args.stats:
            stats = vectorizer.get_stats()
            print("=== Forum Database Statistics ===")
            for key, value in stats.items():
                if isinstance(value, dict):
                    print(f"{key}:")
                    for k, v in value.items():
                        print(f"  {k}: {v}")
                else:
                    print(f"{key}: {value}")
            print()
        
        # Calculate date filter if requested
        after_date = None
        if args.recent_months:
            from datetime import datetime, timedelta
            after_date = (datetime.now() - timedelta(days=args.recent_months * 30)).strftime('%Y-%m-%d')
        elif args.after_date:
            after_date = args.after_date

        print(f"Searching for: '{args.query}'")
        filters = []
        if args.doc_type:
            filters.append(f"Document type: {args.doc_type}")
        if args.topic_id:
            filters.append(f"Topic ID: {args.topic_id}")
        if args.username:
            filters.append(f"Username: {args.username}")
        if after_date:
            filters.append(f"After date: {after_date}")
        
        if filters:
            print(f"Filters: {', '.join(filters)}")
        print("=" * 60)
        
        results = vectorizer.search_forum(
            args.query, 
            n_results=args.num_results,
            doc_type=args.doc_type,
            topic_id=args.topic_id,
            username=args.username,
            after_date=after_date
        )
        
        if not results:
            print("No results found.")
            return
        
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            doc_type = metadata.get('doc_type', 'unknown')
            
            print(f"\n[{i}] {doc_type.upper()}")
            
            if doc_type == 'topic':
                print(f"    Topic: {metadata.get('title', 'No title')}")
                print(f"    ID: {metadata.get('topic_id')}")
                print(f"    Posts: {metadata.get('posts_count', 0)} | Views: {metadata.get('views', 0)}")
                
            elif doc_type == 'post':
                print(f"    Topic: {metadata.get('topic_title', 'No title')}")
                print(f"    Post #{metadata.get('post_number')} by {metadata.get('username', 'Unknown')}")
                print(f"    Topic ID: {metadata.get('topic_id')} | Post ID: {metadata.get('post_id')}")
                if metadata.get('reply_to_post_number'):
                    print(f"    Reply to post #{metadata.get('reply_to_post_number')}")
                    
            elif doc_type == 'conversation':
                print(f"    Topic: {metadata.get('title', 'No title')}")
                print(f"    Topic ID: {metadata.get('topic_id')}")
                print(f"    Posts: {metadata.get('posts_count', 0)} | Participants: {metadata.get('participants', 0)}")
                if metadata.get('chunk_index') is not None:
                    print(f"    Chunk: {metadata.get('chunk_index', 0) + 1}/{metadata.get('total_chunks', 1)}")
            
            if metadata.get('created_at'):
                print(f"    Created: {metadata['created_at'][:10]}")
            
            if 'distance' in result and result['distance'] is not None:
                similarity = 1 - result['distance']
                print(f"    Similarity: {similarity:.3f}")
            
            # Show content preview
            content = result['content']
            preview_lines = content.split('\n')[:5]  # First 5 lines
            
            print(f"    Content:")
            for line in preview_lines:
                if line.strip():
                    line_preview = line[:100] + "..." if len(line) > 100 else line
                    print(f"      {line_preview}")
            
            if len(content.split('\n')) > 5:
                print(f"      ... (content continues)")
            
            print("-" * 60)
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()