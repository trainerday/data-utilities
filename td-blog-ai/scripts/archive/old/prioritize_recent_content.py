#!/usr/bin/env python3
"""
Prioritize Recent Content for Blog Article Creation

This script analyzes the forum database to identify and prioritize topics 
that would make good blog articles based on:
1. Recent activity (questions/posts in the last year)
2. Question frequency and engagement
3. View counts and user interest
4. Problem complexity and solution potential

The script uses the correct PostgreSQL schema:
- forum_topics_raw: Raw topic data with JSONB content
- forum_topics: Analyzed topics with categories
- forum_qa_pairs: Extracted Q&A pairs with dates
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import psycopg2
from psycopg2.extras import RealDictCursor
import argparse

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
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
    
    # Add SSL cert if exists
    if os.getenv('DB_SSLROOTCERT'):
        ssl_cert_filename = os.getenv('DB_SSLROOTCERT')
        ssl_cert_path = Path(__file__).parent.parent / ssl_cert_filename
        if ssl_cert_path.exists():
            db_config['sslrootcert'] = str(ssl_cert_path)
    
    # Validate required config
    if not all([db_config['host'], db_config['database'], db_config['user'], db_config['password']]):
        raise ValueError("Database configuration incomplete. Please check environment variables.")
    
    return psycopg2.connect(**db_config)

def get_prioritized_topics(days_back=365, min_questions=1, limit=25):
    """
    Get prioritized topics for blog article creation.
    
    Args:
        days_back: How many days back to look for recent activity
        min_questions: Minimum number of questions to consider
        limit: Maximum number of topics to return
    
    Returns:
        List of prioritized topics with scores and metadata
    """
    print(f"🎯 PRIORITIZING TOPICS FOR BLOG ARTICLES")
    print(f"   Looking back: {days_back} days")
    print(f"   Min questions: {min_questions}")
    print(f"   Limit: {limit}")
    print("=" * 60)
    
    connection = connect_to_database()
    
    with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        # Create prioritization query with multiple scoring factors
        query = """
            WITH topic_scores AS (
                SELECT 
                    ftr.topic_id,
                    ftr.title,
                    ft.analysis_category,
                    ftr.created_at_original,
                    
                    -- Extract view count from raw JSON
                    COALESCE(
                        (jsonb_extract_path_text(ftr.raw_content, 'topic', 'views'))::int, 
                        0
                    ) as views,
                    
                    -- Extract post count from raw JSON
                    COALESCE(
                        (jsonb_extract_path_text(ftr.raw_content, 'topic', 'posts_count'))::int, 
                        0
                    ) as posts_count,
                    
                    -- Count questions in time period
                    COUNT(qa.id) as question_count,
                    
                    -- Most recent question date
                    MAX(qa.date_posted) as latest_question_date,
                    
                    -- Calculate recency score (0-10, more recent = higher)
                    CASE 
                        WHEN MAX(qa.date_posted) >= CURRENT_DATE - INTERVAL '30 days' THEN 10
                        WHEN MAX(qa.date_posted) >= CURRENT_DATE - INTERVAL '90 days' THEN 8
                        WHEN MAX(qa.date_posted) >= CURRENT_DATE - INTERVAL '180 days' THEN 6
                        WHEN MAX(qa.date_posted) >= CURRENT_DATE - INTERVAL '365 days' THEN 4
                        ELSE 2
                    END as recency_score,
                    
                    -- Calculate frequency score (0-10, more questions = higher, capped at 10)
                    LEAST(COUNT(qa.id) * 2, 10) as frequency_score,
                    
                    -- Calculate engagement score based on views (0-10)
                    CASE 
                        WHEN COALESCE((jsonb_extract_path_text(ftr.raw_content, 'topic', 'views'))::int, 0) >= 2000 THEN 10
                        WHEN COALESCE((jsonb_extract_path_text(ftr.raw_content, 'topic', 'views'))::int, 0) >= 1000 THEN 8
                        WHEN COALESCE((jsonb_extract_path_text(ftr.raw_content, 'topic', 'views'))::int, 0) >= 500 THEN 6
                        WHEN COALESCE((jsonb_extract_path_text(ftr.raw_content, 'topic', 'views'))::int, 0) >= 200 THEN 4
                        WHEN COALESCE((jsonb_extract_path_text(ftr.raw_content, 'topic', 'views'))::int, 0) >= 50 THEN 2
                        ELSE 1
                    END as engagement_score,
                    
                    -- Calculate discussion score based on posts (0-10)
                    CASE 
                        WHEN COALESCE((jsonb_extract_path_text(ftr.raw_content, 'topic', 'posts_count'))::int, 0) >= 20 THEN 10
                        WHEN COALESCE((jsonb_extract_path_text(ftr.raw_content, 'topic', 'posts_count'))::int, 0) >= 10 THEN 8
                        WHEN COALESCE((jsonb_extract_path_text(ftr.raw_content, 'topic', 'posts_count'))::int, 0) >= 5 THEN 6
                        WHEN COALESCE((jsonb_extract_path_text(ftr.raw_content, 'topic', 'posts_count'))::int, 0) >= 3 THEN 4
                        ELSE 2
                    END as discussion_score,
                    
                    -- Sample of pain points/questions for preview
                    STRING_AGG(
                        CASE 
                            WHEN qa.pain_point IS NOT NULL AND qa.pain_point != '' 
                            THEN LEFT(qa.pain_point, 100)
                            ELSE LEFT(qa.question_content, 100)
                        END, 
                        ' | ' 
                        ORDER BY qa.date_posted DESC
                    ) as sample_questions
                    
                FROM forum_topics_raw ftr
                LEFT JOIN forum_topics ft ON ftr.topic_id = ft.topic_id
                JOIN forum_qa_pairs qa ON ftr.topic_id = qa.topic_id
                WHERE qa.date_posted >= CURRENT_DATE - INTERVAL '%s days'
                    AND ftr.raw_content IS NOT NULL
                GROUP BY ftr.topic_id, ftr.title, ft.analysis_category, ftr.created_at_original, ftr.raw_content
                HAVING COUNT(qa.id) >= %s
            ),
            scored_topics AS (
                SELECT *,
                    -- Calculate total priority score (weighted combination)
                    (recency_score * 0.3 + 
                     frequency_score * 0.25 + 
                     engagement_score * 0.25 + 
                     discussion_score * 0.2) as priority_score
                FROM topic_scores
            )
            SELECT *
            FROM scored_topics
            ORDER BY priority_score DESC, latest_question_date DESC, views DESC
            LIMIT %s
        """
        
        cursor.execute(query, (days_back, min_questions, limit))
        topics = cursor.fetchall()
        
        print(f"Found {len(topics)} prioritized topics")
        print()
        
        # Display results
        print("TOP PRIORITY TOPICS FOR BLOG ARTICLES:")
        print("-" * 50)
        print(f"{'Rank':<4} {'Score':<5} {'Topic ID':<8} {'Views':<6} {'Questions':<9} {'Title'}")
        print("-" * 50)
        
        results = []
        for i, topic in enumerate(topics, 1):
            # Create result record
            result = {
                'rank': i,
                'topic_id': topic['topic_id'],
                'title': topic['title'],
                'category': topic['analysis_category'],
                'priority_score': round(topic['priority_score'], 2),
                'views': topic['views'],
                'posts_count': topic['posts_count'],
                'question_count': topic['question_count'],
                'latest_question_date': topic['latest_question_date'],
                'recency_score': topic['recency_score'],
                'frequency_score': topic['frequency_score'],
                'engagement_score': topic['engagement_score'],
                'discussion_score': topic['discussion_score'],
                'sample_questions': topic['sample_questions'],
                'created_at_original': topic['created_at_original']
            }
            results.append(result)
            
            # Display summary line
            print(f"{i:<4} {topic['priority_score']:<5.1f} {topic['topic_id']:<8} "
                  f"{topic['views']:<6} {topic['question_count']:<9} {topic['title'][:60]}")
        
        print("-" * 50)
        print()
        
        # Show detailed breakdown for top 10
        print("DETAILED BREAKDOWN (Top 10):")
        print("=" * 60)
        
        for result in results[:10]:
            print(f"\n{result['rank']:2d}. Topic {result['topic_id']}: {result['title']}")
            print(f"    Category: {result['category'] or 'Uncategorized'}")
            print(f"    Priority Score: {result['priority_score']} "
                  f"(Recency: {result['recency_score']}, Frequency: {result['frequency_score']}, "
                  f"Engagement: {result['engagement_score']}, Discussion: {result['discussion_score']})")
            print(f"    Stats: {result['views']} views, {result['posts_count']} posts, "
                  f"{result['question_count']} questions")
            print(f"    Latest Question: {result['latest_question_date']}")
            print(f"    Topic Created: {result['created_at_original']}")
            
            if result['sample_questions']:
                sample = result['sample_questions'][:200] + "..." if len(result['sample_questions']) > 200 else result['sample_questions']
                print(f"    Sample Issues: {sample}")
        
        print("\n" + "=" * 60)
        print(f"✅ Analysis complete! {len(results)} topics prioritized for blog content.")
        
    connection.close()
    return results

def export_results_to_json(results, output_file=None):
    """Export prioritization results to JSON file."""
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"prioritized_topics_{timestamp}.json"
    
    # Convert datetime objects and Decimal types to strings for JSON serialization
    json_results = []
    for result in results:
        json_result = {}
        for key, value in result.items():
            if hasattr(value, 'isoformat'):  # datetime objects
                json_result[key] = value.isoformat()
            elif hasattr(value, '__float__'):  # Decimal objects
                json_result[key] = float(value)
            else:
                json_result[key] = value
        json_results.append(json_result)
    
    export_data = {
        'generated_at': datetime.now().isoformat(),
        'total_topics': len(json_results),
        'methodology': {
            'scoring_factors': {
                'recency_score': 'Recent activity (30d=10, 90d=8, 180d=6, 365d=4, older=2)',
                'frequency_score': 'Number of questions * 2, capped at 10',
                'engagement_score': 'View count (2000+=10, 1000+=8, 500+=6, 200+=4, 50+=2, <50=1)',
                'discussion_score': 'Post count (20+=10, 10+=8, 5+=6, 3+=4, <3=2)'
            },
            'priority_score_formula': 'recency*0.3 + frequency*0.25 + engagement*0.25 + discussion*0.2'
        },
        'topics': json_results
    }
    
    output_path = Path(__file__).parent / output_file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"📁 Results exported to: {output_path}")
    return output_path

def analyze_categories(results):
    """Analyze category distribution in prioritized topics."""
    print("\n📊 CATEGORY ANALYSIS:")
    print("-" * 30)
    
    category_stats = defaultdict(lambda: {'count': 0, 'total_score': 0, 'topics': []})
    
    for result in results:
        category = result['category'] or 'Uncategorized'
        category_stats[category]['count'] += 1
        category_stats[category]['total_score'] += result['priority_score']
        category_stats[category]['topics'].append(result['title'][:40] + "...")
    
    # Sort by count
    sorted_categories = sorted(category_stats.items(), 
                             key=lambda x: x[1]['count'], 
                             reverse=True)
    
    for category, stats in sorted_categories:
        avg_score = stats['total_score'] / stats['count']
        print(f"{category}: {stats['count']} topics (avg score: {avg_score:.1f})")
        
        # Show top 3 topics in this category
        for topic in stats['topics'][:3]:
            print(f"  - {topic}")
        if len(stats['topics']) > 3:
            print(f"  ... and {len(stats['topics']) - 3} more")
        print()

def main():
    """Main function with command line argument support."""
    parser = argparse.ArgumentParser(
        description="Prioritize forum topics for blog article creation"
    )
    parser.add_argument(
        '--days-back', 
        type=int, 
        default=365,
        help='Number of days back to analyze (default: 365)'
    )
    parser.add_argument(
        '--min-questions', 
        type=int, 
        default=1,
        help='Minimum number of questions required (default: 1)'
    )
    parser.add_argument(
        '--limit', 
        type=int, 
        default=25,
        help='Maximum number of topics to return (default: 25)'
    )
    parser.add_argument(
        '--export', 
        type=str,
        help='Export results to JSON file (specify filename)'
    )
    parser.add_argument(
        '--category-analysis',
        action='store_true',
        help='Include category distribution analysis'
    )
    
    args = parser.parse_args()
    
    try:
        print("🚀 FORUM CONTENT PRIORITIZATION SYSTEM")
        print("=" * 60)
        print("Analyzing forum database to identify high-priority topics")
        print("for blog article creation based on recent user engagement.")
        print()
        
        # Get prioritized topics
        results = get_prioritized_topics(
            days_back=args.days_back,
            min_questions=args.min_questions,
            limit=args.limit
        )
        
        # Category analysis
        if args.category_analysis:
            analyze_categories(results)
        
        # Export results
        if args.export:
            export_results_to_json(results, args.export)
        
        print("\n🎯 NEXT STEPS:")
        print("1. Review the prioritized topics above")
        print("2. Select topics that align with your content strategy")
        print("3. Research each topic thoroughly using the sample questions")
        print("4. Create comprehensive blog articles addressing the pain points")
        print("5. Monitor engagement and update content based on feedback")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()