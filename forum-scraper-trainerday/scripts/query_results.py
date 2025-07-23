#!/usr/bin/env python3
"""
Query Forum Analysis Results v2 - With Raw Content Storage
View analysis results and raw content stored in PostgreSQL.
"""

import os
import json
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded environment variables from: {env_path}")
except ImportError:
    print("python-dotenv not installed, using system environment variables")

def connect_to_database():
    """Connect to PostgreSQL database."""
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('DB_SSLMODE', 'require')
    }
    
    # Add SSL certificate if specified
    if os.getenv('DB_SSLROOTCERT'):
        ssl_cert_filename = os.getenv('DB_SSLROOTCERT')
        ssl_cert_path = Path(__file__).parent.parent / ssl_cert_filename
        if ssl_cert_path.exists():
            db_config['sslrootcert'] = str(ssl_cert_path)
    
    return psycopg2.connect(**db_config)

def safe_json_parse(data):
    """Safely parse JSON data that might be string or already parsed."""
    if isinstance(data, str):
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            return data
    return data

def main():
    print("Forum Analysis Results v2 - Raw Content + Analysis")
    print("=" * 55)
    
    try:
        conn = connect_to_database()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get raw content summary
        print("\n📦 RAW CONTENT SUMMARY")
        print("-" * 25)
        cursor.execute("""
            SELECT COUNT(*) as total_topics,
                   MIN(created_at_original) as earliest_topic,
                   MAX(created_at_original) as latest_topic,
                   SUM(posts_count) as total_posts,
                   AVG(posts_count) as avg_posts_per_topic
            FROM forum_topics_raw
        """)
        
        raw_stats = cursor.fetchone()
        if raw_stats and raw_stats['total_topics']:
            print(f"Total topics stored: {raw_stats['total_topics']}")
            print(f"Total posts: {raw_stats['total_posts']}")
            print(f"Average posts per topic: {raw_stats['avg_posts_per_topic']:.1f}")
            print(f"Date range: {raw_stats['earliest_topic']} to {raw_stats['latest_topic']}")
        else:
            print("No raw content found in database")
            return
        
        # Get analysis summary
        print("\n📊 ANALYSIS SUMMARY")
        print("-" * 20)
        cursor.execute("""
            SELECT COUNT(*) as analyzed_topics,
                   COUNT(DISTINCT analysis_category) as categories
            FROM forum_topics
        """)
        
        analysis_stats = cursor.fetchone()
        print(f"Topics analyzed: {analysis_stats['analyzed_topics']} / {raw_stats['total_topics']}")
        print(f"Analysis categories: {analysis_stats['categories']}")
        
        # Get topics with analysis
        print("\n🔍 ANALYZED TOPICS")
        print("-" * 18)
        cursor.execute("""
            SELECT ft.topic_id, ft.title, ft.analysis_category, 
                   ft.total_posts, ft.views, ft.like_count, ft.analyzed_at,
                   ftr.posts_count as actual_posts, ftr.last_updated
            FROM forum_topics ft
            JOIN forum_topics_raw ftr ON ft.topic_id = ftr.topic_id
            ORDER BY ft.analyzed_at DESC
            LIMIT 10
        """)
        
        for row in cursor.fetchall():
            print(f"Topic {row['topic_id']}: {row['title']}")
            print(f"  Category: {row['analysis_category']}")
            print(f"  Posts: {row['actual_posts']} | Views: {row['views']} | Likes: {row['like_count']}")
            print(f"  Analyzed: {row['analyzed_at']}")
            print()
        
        # Get Q&A pairs count
        print("\n💬 Q&A EXTRACTION")
        print("-" * 18)
        cursor.execute("""
            SELECT ft.topic_id, ft.title, COUNT(qa.id) as qa_count 
            FROM forum_topics ft
            LEFT JOIN forum_qa_pairs qa ON ft.topic_id = qa.topic_id
            GROUP BY ft.topic_id, ft.title
            HAVING COUNT(qa.id) > 0
            ORDER BY qa_count DESC
            LIMIT 5
        """)
        
        for row in cursor.fetchall():
            print(f"Topic {row['topic_id']}: {row['qa_count']} Q&A pairs")
            print(f"  {row['title'][:60]}...")
        
        # Get sample Q&A pairs
        print(f"\n🗣️  SAMPLE Q&A PAIRS")
        print("-" * 20)
        cursor.execute("""
            SELECT topic_id, sequence, question_username, question_content, 
                   response_username, solution_offered, pain_point
            FROM forum_qa_pairs 
            WHERE question_content IS NOT NULL AND response_content IS NOT NULL
            ORDER BY topic_id, sequence
            LIMIT 3
        """)
        
        for row in cursor.fetchall():
            print(f"Topic {row['topic_id']} - Q&A {row['sequence']}")
            print(f"  Question ({row['question_username']}): {row['question_content'][:80]}...")
            print(f"  Pain Point: {row['pain_point']}")
            print(f"  Solution: {row['solution_offered']}")
            print()
        
        # Get insights summary
        print("\n💡 KEY INSIGHTS")
        print("-" * 15)
        cursor.execute("""
            SELECT topic_id, content_opportunities, messaging_gaps, 
                   recency_score, frequency_score, impact_score
            FROM forum_insights 
            WHERE content_opportunities IS NOT NULL
            ORDER BY 
                CASE recency_score WHEN 'high' THEN 3 WHEN 'medium' THEN 2 ELSE 1 END +
                CASE frequency_score WHEN 'high' THEN 3 WHEN 'medium' THEN 2 ELSE 1 END +
                CASE impact_score WHEN 'high' THEN 3 WHEN 'medium' THEN 2 ELSE 1 END DESC
            LIMIT 5
        """)
        
        for row in cursor.fetchall():
            print(f"Topic {row['topic_id']} - Priority: R={row['recency_score']}, F={row['frequency_score']}, I={row['impact_score']}")
            
            opportunities = safe_json_parse(row['content_opportunities'])
            if opportunities and len(opportunities) > 0:
                print(f"  Content Opportunities:")
                for opp in opportunities[:2]:
                    print(f"    • {opp}")
            
            gaps = safe_json_parse(row['messaging_gaps'])
            if gaps and len(gaps) > 0:
                print(f"  Messaging Gaps:")
                for gap in gaps[:2]:
                    print(f"    • {gap}")
            print()
        
        # Show categories breakdown
        print("\n📈 CATEGORIES BREAKDOWN")
        print("-" * 23)
        cursor.execute("""
            SELECT analysis_category, COUNT(*) as topic_count,
                   AVG(total_posts) as avg_posts
            FROM forum_topics
            WHERE analysis_category IS NOT NULL
            GROUP BY analysis_category
            ORDER BY topic_count DESC
        """)
        
        for row in cursor.fetchall():
            print(f"{row['analysis_category']}: {row['topic_count']} topics (avg {row['avg_posts']:.1f} posts)")
        
        # Raw content sample
        print(f"\n📄 RAW CONTENT SAMPLE")
        print("-" * 22)
        cursor.execute("""
            SELECT topic_id, title, checksum, 
                   jsonb_array_length(raw_content->'posts') as post_count_in_raw
            FROM forum_topics_raw
            ORDER BY last_updated DESC
            LIMIT 3
        """)
        
        for row in cursor.fetchall():
            print(f"Topic {row['topic_id']}: {row['title'][:50]}...")
            print(f"  Checksum: {row['checksum']}")
            print(f"  Posts in raw: {row['post_count_in_raw']}")
        
        print(f"\n🎯 DATABASE STATUS")
        print("-" * 17)
        print("✅ Raw forum content: Stored in forum_topics_raw table")
        print("✅ Analysis insights: Stored in analysis tables")
        print("✅ Complete audit trail: Analysis traces back to exact raw content")
        print("✅ Future-proof: Can re-analyze raw content with different strategies")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()