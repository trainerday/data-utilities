#!/usr/bin/env python3
"""
Priority Topics Review: User Questions & Draft Titles

This script presents the top priority cycling feature topics with all related 
user questions so you can review and draft appropriate article titles.

Workflow:
1. Show prioritized topics with actual user questions
2. Human reviews and drafts article titles  
3. Save draft titles for Claude API refinement
4. Generate articles with proper research context
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.db_connection import get_db_connection

def get_topic_details_with_questions(topic_ids, limit=10):
    """
    Get detailed information for specific topics including all user questions
    """
    
    if not topic_ids:
        return []
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Convert topic_ids to proper format (handle floats from JSON)
    topic_id_list = [str(int(float(tid))) for tid in topic_ids]
    placeholders = ','.join(['%s'] * len(topic_id_list))
    
    query = f"""
    SELECT 
        ftr.topic_id,
        ftr.title,
        ft.analysis_category,
        ftr.created_at_original,
        
        -- Extract metrics from raw JSON
        COALESCE((jsonb_extract_path_text(ftr.raw_content, 'topic', 'views'))::int, 0) as views,
        COALESCE((jsonb_extract_path_text(ftr.raw_content, 'topic', 'posts_count'))::int, 0) as posts_count,
        
        -- Get all user questions and responses for this topic
        COUNT(qa.id) as total_questions,
        MAX(qa.date_posted) as latest_question_date,
        
        -- Collect all pain points and questions
        JSON_AGG(
            JSON_BUILD_OBJECT(
                'date_posted', qa.date_posted,
                'pain_point', qa.pain_point,
                'question_content', LEFT(qa.question_content, 300),
                'response_content', LEFT(qa.response_content, 200),
                'response_type', qa.response_type,
                'user_language', qa.user_language
            ) ORDER BY qa.date_posted DESC
        ) as all_questions
        
    FROM forum_topics_raw ftr
    LEFT JOIN forum_topics ft ON ftr.topic_id = ft.topic_id
    LEFT JOIN forum_qa_pairs qa ON ftr.topic_id = qa.topic_id
    WHERE ftr.topic_id IN ({placeholders})
        AND qa.date_posted >= CURRENT_DATE - INTERVAL '365 days'
    GROUP BY ftr.topic_id, ftr.title, ft.analysis_category, ftr.created_at_original, ftr.raw_content
    ORDER BY COUNT(qa.id) DESC, MAX(qa.date_posted) DESC
    LIMIT %s
    """
    
    cursor.execute(query, topic_id_list + [limit])
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return results

def display_topic_for_review(topic_data, index):
    """
    Display a topic with all user questions for human review
    """
    
    print(f"\n{'='*80}")
    print(f"TOPIC #{index}: {topic_data[1]}")  # title
    print(f"{'='*80}")
    
    print(f"📊 **Topic Metrics:**")
    print(f"   • Topic ID: {topic_data[0]}")
    print(f"   • Category: {topic_data[2] or 'Uncategorized'}")
    print(f"   • Views: {topic_data[4]:,}")
    print(f"   • Posts: {topic_data[5]:,}")
    print(f"   • Questions: {topic_data[6]}")
    print(f"   • Latest Activity: {topic_data[7]}")
    print(f"   • Created: {topic_data[3]}")
    
    print(f"\n🗣️ **User Questions & Pain Points:**")
    print("-" * 60)
    
    questions = topic_data[8]  # all_questions JSON
    
    if questions:
        for i, q in enumerate(questions[:8], 1):  # Show top 8 questions
            date_posted = q.get('date_posted', 'Unknown')
            pain_point = q.get('pain_point', '')
            question_content = q.get('question_content', '')
            response_type = q.get('response_type', '')
            
            print(f"\n   {i}. **{date_posted}** ({response_type})")
            
            if pain_point and pain_point.strip():
                print(f"      Pain Point: {pain_point}")
            
            if question_content and question_content.strip():
                question_preview = question_content[:250] + "..." if len(question_content) > 250 else question_content
                print(f"      Question: {question_preview}")
        
        if len(questions) > 8:
            print(f"\n   ... and {len(questions) - 8} more questions")
    else:
        print("   No questions found for this topic.")
    
    print(f"\n📝 **Article Title Suggestion Area:**")
    print("-" * 60)
    print("   Based on the user questions above, what would be a good article title?")
    print("   Consider what users are actually asking about and trying to solve.")
    print()

def save_review_session(topics_data, output_file=None):
    """
    Save the review session data for future reference
    """
    
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"topic_review_session_{timestamp}.json"
    
    # Prepare data for JSON serialization
    review_data = {
        'generated_at': datetime.now().isoformat(),
        'purpose': 'Human review of priority topics for article title drafting',
        'topics_reviewed': len(topics_data),
        'topics': []
    }
    
    for topic_data in topics_data:
        topic_info = {
            'topic_id': topic_data[0],
            'title': topic_data[1],
            'category': topic_data[2],
            'created_at': topic_data[3].isoformat() if topic_data[3] else None,
            'views': topic_data[4],
            'posts_count': topic_data[5],
            'total_questions': topic_data[6],
            'latest_question_date': topic_data[7].isoformat() if topic_data[7] else None,
            'questions': topic_data[8] if topic_data[8] else [],
            'draft_article_title': '',  # To be filled in by human review
            'article_notes': '',  # To be filled in by human review
            'approved_for_content': False  # To be set by human review
        }
        review_data['topics'].append(topic_info)
    
    output_path = Path(__file__).parent / output_file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(review_data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n📁 Review session saved to: {output_path}")
    return output_path

def main():
    """
    Main review process
    """
    
    print("📋 PRIORITY TOPICS REVIEW SESSION")
    print("=" * 60)
    print("Review cycling feature topics with actual user questions")
    print("Draft article titles based on what users are really asking")
    print()
    
    try:
        # Load the cycling priority topics
        cycling_file = None
        script_dir = Path(__file__).parent
        
        # Find the most recent cycling strategy file (check both scripts dir and current dir)
        cycling_files = list(script_dir.glob("cycling_features_only_*.json"))
        current_dir_files = list(Path.cwd().glob("cycling_features_only_*.json"))
        all_cycling_files = cycling_files + current_dir_files
        
        if all_cycling_files:
            cycling_file = max(all_cycling_files, key=lambda f: f.stat().st_mtime)
        
        if not cycling_file:
            print("❌ No cycling feature strategy found. Run cycling_features_only.py first.")
            return
        
        print(f"📁 Loading cycling topics from: {cycling_file.name}")
        
        with open(cycling_file, 'r') as f:
            cycling_data = json.load(f)
        
        cycling_topics = cycling_data['topics']
        
        if not cycling_topics:
            print("❌ No cycling topics found in strategy file.")
            return
        
        # Get the top N topics for review
        top_n = min(8, len(cycling_topics))  # Review top 8 topics
        topic_ids = [t['topic_id'] for t in cycling_topics[:top_n]]
        
        print(f"🎯 Reviewing top {top_n} cycling feature topics...")
        
        # Get detailed topic information with user questions
        topics_data = get_topic_details_with_questions(topic_ids, top_n)
        
        if not topics_data:
            print("❌ No topic details found. Check database connection.")
            return
        
        print(f"✅ Retrieved {len(topics_data)} topics with user questions")
        
        # Display each topic for review
        for i, topic_data in enumerate(topics_data, 1):
            display_topic_for_review(topic_data, i)
            
            # Pause for human review (in actual use, this would be interactive)
            if i < len(topics_data):
                print(f"\n{'⬇'*80}")
                print("NEXT TOPIC:")
        
        # Save review session for future use
        review_file = save_review_session(topics_data)
        
        print(f"\n✅ REVIEW SESSION COMPLETE!")
        print(f"   • {len(topics_data)} topics presented for review")
        print(f"   • Review data saved to: {review_file.name}")
        print("\n🎯 NEXT STEPS:")
        print("   1. Review each topic and user questions above")
        print("   2. Draft article titles based on actual user needs")
        print("   3. Edit the saved JSON file with your draft titles")
        print("   4. Use Claude API to refine titles and generate content")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()