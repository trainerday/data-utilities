#!/usr/bin/env python3
"""
Analyze Forum Data for Recent Activity and Date Patterns

This script analyzes the forum database to understand:
1. How dates are stored in the forum Q&A data
2. What recent activity looks like (last year)
3. How to identify topics with recent questions vs old topics
4. Date patterns for prioritizing content creation

Focus: Understanding how we can identify questions from the last year and 
prioritize content creation based on recent user activity rather than topic age.
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import psycopg2
from psycopg2.extras import RealDictCursor

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
    
    return psycopg2.connect(**db_config)

def analyze_date_storage_patterns():
    """Analyze how dates are stored in the forum data."""
    print("🗓️  ANALYZING DATE STORAGE PATTERNS")
    print("=" * 50)
    
    connection = connect_to_database()
    
    with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        # Check date fields in raw topics table
        cursor.execute("""
            SELECT 
                topic_id,
                title,
                created_at_original,
                scraped_at,
                last_updated,
                raw_content
            FROM forum_topics_raw 
            WHERE created_at_original IS NOT NULL
            ORDER BY created_at_original DESC
            LIMIT 10
        """)
        
        recent_topics = cursor.fetchall()
        
        print("Sample of most recent topics (by creation date):")
        print("-" * 50)
        for topic in recent_topics:
            raw_content = json.loads(topic['raw_content']) if isinstance(topic['raw_content'], str) else topic['raw_content']
            topic_data = raw_content.get('topic', {})
            
            print(f"Topic {topic['topic_id']}: {topic['title'][:60]}...")
            print(f"  Created: {topic['created_at_original']}")
            print(f"  Last posted: {topic_data.get('last_posted_at', 'N/A')}")
            print(f"  Bumped at: {topic_data.get('bumped_at', 'N/A')}")
            print(f"  Views: {topic_data.get('views', 0)}")
            print(f"  Posts: {topic_data.get('posts_count', 0)}")
            print()
        
        # Analyze date patterns in Q&A pairs
        cursor.execute("""
            SELECT 
                COUNT(*) as total_qa,
                MIN(date_posted) as earliest_qa,
                MAX(date_posted) as latest_qa,
                COUNT(CASE WHEN date_posted >= CURRENT_DATE - INTERVAL '365 days' THEN 1 END) as last_year_qa,
                COUNT(CASE WHEN date_posted >= CURRENT_DATE - INTERVAL '90 days' THEN 1 END) as last_90_days_qa,
                COUNT(CASE WHEN date_posted >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END) as last_30_days_qa
            FROM forum_qa_pairs
            WHERE date_posted IS NOT NULL
        """)
        
        qa_stats = cursor.fetchone()
        
        print("Q&A PAIRS DATE ANALYSIS:")
        print("-" * 30)
        print(f"Total Q&A pairs with dates: {qa_stats['total_qa']:,}")
        print(f"Date range: {qa_stats['earliest_qa']} to {qa_stats['latest_qa']}")
        print(f"Last year: {qa_stats['last_year_qa']:,} ({qa_stats['last_year_qa']/qa_stats['total_qa']*100:.1f}%)")
        print(f"Last 90 days: {qa_stats['last_90_days_qa']:,} ({qa_stats['last_90_days_qa']/qa_stats['total_qa']*100:.1f}%)")
        print(f"Last 30 days: {qa_stats['last_30_days_qa']:,} ({qa_stats['last_30_days_qa']/qa_stats['total_qa']*100:.1f}%)")
        print()
    
    connection.close()

def analyze_recent_activity_patterns():
    """Analyze patterns in recent forum activity."""
    print("📈 ANALYZING RECENT ACTIVITY PATTERNS")
    print("=" * 50)
    
    connection = connect_to_database()
    
    with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        # Get topics with recent activity (based on raw content timestamps)
        cursor.execute("""
            SELECT 
                ftr.topic_id,
                ftr.title,
                ftr.created_at_original,
                ftr.raw_content,
                ft.analysis_category,
                COUNT(qa.id) as qa_count
            FROM forum_topics_raw ftr
            LEFT JOIN forum_topics ft ON ftr.topic_id = ft.topic_id
            LEFT JOIN forum_qa_pairs qa ON ftr.topic_id = qa.topic_id
            WHERE ftr.created_at_original >= CURRENT_DATE - INTERVAL '365 days'
            GROUP BY ftr.topic_id, ftr.title, ftr.created_at_original, ftr.raw_content, ft.analysis_category
            ORDER BY ftr.created_at_original DESC
            LIMIT 20
        """)
        
        recent_topics = cursor.fetchall()
        
        print("MOST RECENT TOPICS (Last Year):")
        print("-" * 40)
        
        for topic in recent_topics:
            raw_content = json.loads(topic['raw_content']) if isinstance(topic['raw_content'], str) else topic['raw_content']
            topic_data = raw_content.get('topic', {})
            
            # Extract last activity date from raw content
            last_posted = topic_data.get('last_posted_at', '')
            bumped_at = topic_data.get('bumped_at', '')
            
            print(f"Topic {topic['topic_id']}: {topic['title'][:60]}...")
            print(f"  Category: {topic['analysis_category'] or 'Not categorized'}")
            print(f"  Created: {topic['created_at_original']}")
            print(f"  Last posted: {last_posted}")
            print(f"  Views: {topic_data.get('views', 0)}")
            print(f"  Q&A pairs: {topic['qa_count']}")
            print()
        
        # Analyze activity by month for the last year
        cursor.execute("""
            SELECT 
                DATE_TRUNC('month', ftr.created_at_original) as month,
                COUNT(*) as topics_created,
                AVG(jsonb_extract_path_text(ftr.raw_content, 'topic', 'views')::int) as avg_views,
                SUM(jsonb_extract_path_text(ftr.raw_content, 'topic', 'posts_count')::int) as total_posts
            FROM forum_topics_raw ftr
            WHERE ftr.created_at_original >= CURRENT_DATE - INTERVAL '365 days'
                AND ftr.raw_content IS NOT NULL
            GROUP BY DATE_TRUNC('month', ftr.created_at_original)
            ORDER BY month DESC
        """)
        
        monthly_stats = cursor.fetchall()
        
        print("MONTHLY ACTIVITY (Last Year):")
        print("-" * 30)
        for month_data in monthly_stats:
            month = month_data['month'].strftime('%Y-%m') if month_data['month'] else 'Unknown'
            avg_views = month_data['avg_views'] if month_data['avg_views'] else 0
            total_posts = month_data['total_posts'] if month_data['total_posts'] else 0
            print(f"{month}: {month_data['topics_created']} topics, "
                  f"{avg_views:.0f} avg views, "
                  f"{total_posts} total posts")
        print()
    
    connection.close()

def analyze_question_recency_vs_topic_age():
    """Compare question recency with topic creation dates."""
    print("🕐 ANALYZING QUESTION RECENCY vs TOPIC AGE")
    print("=" * 50)
    
    connection = connect_to_database()
    
    with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        # Find topics where questions are much more recent than topic creation
        cursor.execute("""
            SELECT 
                ftr.topic_id,
                ftr.title,
                ftr.created_at_original as topic_created,
                qa.date_posted as question_posted,
                qa.question_content,
                qa.user_language,
                qa.pain_point,
                (qa.date_posted - ftr.created_at_original::date) as days_diff
            FROM forum_topics_raw ftr
            JOIN forum_qa_pairs qa ON ftr.topic_id = qa.topic_id
            WHERE ftr.created_at_original IS NOT NULL 
                AND qa.date_posted IS NOT NULL
                AND qa.date_posted >= CURRENT_DATE - INTERVAL '365 days'
                AND (qa.date_posted - ftr.created_at_original::date) > 30
            ORDER BY qa.date_posted DESC
            LIMIT 15
        """)
        
        recent_questions_old_topics = cursor.fetchall()
        
        print("RECENT QUESTIONS IN OLD TOPICS:")
        print("-" * 40)
        print("(Questions from last year in topics older than 30 days)")
        print()
        
        for qa in recent_questions_old_topics:
            print(f"Topic {qa['topic_id']}: {qa['title'][:50]}...")
            print(f"  Topic created: {qa['topic_created']}")
            print(f"  Question posted: {qa['question_posted']} ({qa['days_diff']} days later)")
            print(f"  Pain point: {qa['pain_point'][:80]}..." if qa['pain_point'] else "  Pain point: Not identified")
            print(f"  User language: {qa['user_language'][:80]}..." if qa['user_language'] else "  User language: Not identified")
            print()
        
        # Find most active topics by recent questions
        cursor.execute("""
            SELECT 
                ftr.topic_id,
                ftr.title,
                ftr.created_at_original,
                ft.analysis_category,
                COUNT(qa.id) as recent_questions,
                MAX(qa.date_posted) as latest_question,
                jsonb_extract_path_text(ftr.raw_content, 'topic', 'views')::int as views
            FROM forum_topics_raw ftr
            LEFT JOIN forum_topics ft ON ftr.topic_id = ft.topic_id
            JOIN forum_qa_pairs qa ON ftr.topic_id = qa.topic_id
            WHERE qa.date_posted >= CURRENT_DATE - INTERVAL '365 days'
            GROUP BY ftr.topic_id, ftr.title, ftr.created_at_original, ft.analysis_category, ftr.raw_content
            HAVING COUNT(qa.id) >= 2
            ORDER BY recent_questions DESC, latest_question DESC
            LIMIT 10
        """)
        
        active_topics = cursor.fetchall()
        
        print("MOST ACTIVE TOPICS (by recent questions):")
        print("-" * 40)
        
        for topic in active_topics:
            print(f"Topic {topic['topic_id']}: {topic['title'][:50]}...")
            print(f"  Category: {topic['analysis_category'] or 'Uncategorized'}")
            print(f"  Created: {topic['created_at_original']}")
            print(f"  Recent questions: {topic['recent_questions']}")
            print(f"  Latest question: {topic['latest_question']}")
            print(f"  Views: {topic['views']}")
            print()
    
    connection.close()

def analyze_content_opportunities():
    """Analyze content opportunities based on recent activity."""
    print("💡 CONTENT OPPORTUNITIES BASED ON RECENT ACTIVITY")
    print("=" * 50)
    
    connection = connect_to_database()
    
    with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        # Get common pain points from recent questions
        cursor.execute("""
            SELECT 
                qa.pain_point,
                qa.user_language,
                COUNT(*) as frequency,
                MAX(qa.date_posted) as latest_occurrence,
                STRING_AGG(DISTINCT ftr.title, '; ' ORDER BY ftr.title) as related_topics
            FROM forum_qa_pairs qa
            JOIN forum_topics_raw ftr ON qa.topic_id = ftr.topic_id
            WHERE qa.date_posted >= CURRENT_DATE - INTERVAL '365 days'
                AND qa.pain_point IS NOT NULL 
                AND qa.pain_point != ''
            GROUP BY qa.pain_point, qa.user_language
            HAVING COUNT(*) >= 2
            ORDER BY frequency DESC, latest_occurrence DESC
            LIMIT 10
        """)
        
        pain_points = cursor.fetchall()
        
        print("FREQUENT PAIN POINTS (Last Year):")
        print("-" * 35)
        
        for pain in pain_points:
            print(f"Pain Point: {pain['pain_point'][:80]}...")
            print(f"  Frequency: {pain['frequency']} occurrences")
            print(f"  Latest: {pain['latest_occurrence']}")
            print(f"  User language: {pain['user_language'][:80]}..." if pain['user_language'] else "  User language: Not specified")
            print(f"  Related topics: {pain['related_topics'][:100]}...")
            print()
        
        # Get analysis categories with recent activity
        cursor.execute("""
            SELECT 
                ft.analysis_category,
                COUNT(qa.id) as recent_questions,
                MAX(qa.date_posted) as latest_question,
                AVG(jsonb_extract_path_text(ftr.raw_content, 'topic', 'views')::int) as avg_views
            FROM forum_topics ft
            JOIN forum_topics_raw ftr ON ft.topic_id = ftr.topic_id
            JOIN forum_qa_pairs qa ON ft.topic_id = qa.topic_id
            WHERE qa.date_posted >= CURRENT_DATE - INTERVAL '365 days'
                AND ft.analysis_category IS NOT NULL
            GROUP BY ft.analysis_category
            ORDER BY recent_questions DESC
        """)
        
        categories = cursor.fetchall()
        
        print("CATEGORIES BY RECENT ACTIVITY:")
        print("-" * 30)
        
        for cat in categories:
            avg_views = cat['avg_views'] if cat['avg_views'] else 0
            print(f"{cat['analysis_category']}: {cat['recent_questions']} questions, "
                  f"latest: {cat['latest_question']}, "
                  f"avg views: {avg_views:.0f}")
        print()
    
    connection.close()

def generate_prioritization_recommendations():
    """Generate recommendations for content prioritization."""
    print("🎯 CONTENT PRIORITIZATION RECOMMENDATIONS")
    print("=" * 50)
    
    connection = connect_to_database()
    
    with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        # Create a prioritization score based on multiple factors
        cursor.execute("""
            WITH topic_scores AS (
                SELECT 
                    ftr.topic_id,
                    ftr.title,
                    ft.analysis_category,
                    
                    -- Recent activity score (more recent = higher score)
                    CASE 
                        WHEN MAX(qa.date_posted) >= CURRENT_DATE - INTERVAL '30 days' THEN 10
                        WHEN MAX(qa.date_posted) >= CURRENT_DATE - INTERVAL '90 days' THEN 8
                        WHEN MAX(qa.date_posted) >= CURRENT_DATE - INTERVAL '180 days' THEN 6
                        WHEN MAX(qa.date_posted) >= CURRENT_DATE - INTERVAL '365 days' THEN 4
                        ELSE 2
                    END as recency_score,
                    
                    -- Question frequency score
                    LEAST(COUNT(qa.id) * 2, 10) as frequency_score,
                    
                    -- View engagement score (normalized)
                    CASE 
                        WHEN jsonb_extract_path_text(ftr.raw_content, 'topic', 'views')::int > 1000 THEN 10
                        WHEN jsonb_extract_path_text(ftr.raw_content, 'topic', 'views')::int > 500 THEN 8
                        WHEN jsonb_extract_path_text(ftr.raw_content, 'topic', 'views')::int > 200 THEN 6
                        WHEN jsonb_extract_path_text(ftr.raw_content, 'topic', 'views')::int > 100 THEN 4
                        ELSE 2
                    END as engagement_score,
                    
                    COUNT(qa.id) as question_count,
                    MAX(qa.date_posted) as latest_question,
                    jsonb_extract_path_text(ftr.raw_content, 'topic', 'views')::int as views,
                    
                    -- Combine scores
                    (CASE 
                        WHEN MAX(qa.date_posted) >= CURRENT_DATE - INTERVAL '30 days' THEN 10
                        WHEN MAX(qa.date_posted) >= CURRENT_DATE - INTERVAL '90 days' THEN 8
                        WHEN MAX(qa.date_posted) >= CURRENT_DATE - INTERVAL '180 days' THEN 6
                        WHEN MAX(qa.date_posted) >= CURRENT_DATE - INTERVAL '365 days' THEN 4
                        ELSE 2
                    END +
                    LEAST(COUNT(qa.id) * 2, 10) +
                    CASE 
                        WHEN jsonb_extract_path_text(ftr.raw_content, 'topic', 'views')::int > 1000 THEN 10
                        WHEN jsonb_extract_path_text(ftr.raw_content, 'topic', 'views')::int > 500 THEN 8
                        WHEN jsonb_extract_path_text(ftr.raw_content, 'topic', 'views')::int > 200 THEN 6
                        WHEN jsonb_extract_path_text(ftr.raw_content, 'topic', 'views')::int > 100 THEN 4
                        ELSE 2
                    END) as total_score
                    
                FROM forum_topics_raw ftr
                LEFT JOIN forum_topics ft ON ftr.topic_id = ft.topic_id
                JOIN forum_qa_pairs qa ON ftr.topic_id = qa.topic_id
                WHERE qa.date_posted >= CURRENT_DATE - INTERVAL '365 days'
                GROUP BY ftr.topic_id, ftr.title, ft.analysis_category, ftr.raw_content
            )
            SELECT *
            FROM topic_scores
            ORDER BY total_score DESC, latest_question DESC
            LIMIT 15
        """)
        
        prioritized_topics = cursor.fetchall()
        
        print("TOP PRIORITY TOPICS FOR CONTENT CREATION:")
        print("-" * 45)
        print("(Based on recency, frequency, and engagement)")
        print()
        
        for i, topic in enumerate(prioritized_topics, 1):
            print(f"{i:2d}. Topic {topic['topic_id']}: {topic['title'][:55]}...")
            print(f"     Category: {topic['analysis_category'] or 'Uncategorized'}")
            print(f"     Score: {topic['total_score']} (recency: {topic['recency_score']}, "
                  f"frequency: {topic['frequency_score']}, engagement: {topic['engagement_score']})")
            print(f"     Questions: {topic['question_count']}, Views: {topic['views']}, "
                  f"Latest: {topic['latest_question']}")
            print()
    
    connection.close()

def main():
    """Main analysis function."""
    print("🔍 FORUM DATA ANALYSIS FOR CONTENT STRATEGY")
    print("=" * 60)
    print("Analyzing forum data structure, recent activity patterns,")
    print("and content creation opportunities based on user engagement.")
    print()
    
    try:
        # Run all analyses
        analyze_date_storage_patterns()
        analyze_recent_activity_patterns()
        analyze_question_recency_vs_topic_age()
        analyze_content_opportunities()
        generate_prioritization_recommendations()
        
        print("✅ ANALYSIS COMPLETE!")
        print()
        print("KEY FINDINGS SUMMARY:")
        print("- Date information is stored in multiple fields for comprehensive tracking")
        print("- Recent questions in old topics indicate ongoing relevance")
        print("- Prioritization should consider recency, frequency, and engagement")
        print("- Content opportunities exist in topics with continued user activity")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()