#!/usr/bin/env python3
"""
Individual Question Articles Strategy

Break down forum topics into individual user questions, each becoming 
a focused blog article. Create topic clusters with overview articles
linking to specific solutions.

Approach:
1. Extract individual user questions from priority topics
2. Suggest specific article title for each question
3. Group related questions into topic clusters
4. Suggest overview articles that link to specific solutions
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.db_connection import get_db_connection

def extract_individual_questions(topic_data):
    """
    Extract individual user questions from a topic and suggest article titles
    """
    
    topic_id = topic_data[0]
    topic_title = topic_data[1]
    topic_category = topic_data[2]
    questions = topic_data[8] if topic_data[8] else []
    
    individual_articles = []
    
    for i, q in enumerate(questions):
        pain_point = (q.get('pain_point') or '').strip()
        question_content = (q.get('question_content') or '').strip()
        response_type = q.get('response_type', '')
        date_posted = q.get('date_posted', '')
        
        # Skip if no meaningful content
        if not pain_point and not question_content:
            continue
            
        # Skip announcements and praise
        if response_type in ['announcement', 'praise']:
            continue
        
        # Use pain point as primary content, fallback to question
        primary_content = pain_point if pain_point else question_content
        
        # Generate specific article title based on the actual user question
        article_title = suggest_specific_article_title(primary_content, question_content, topic_title)
        
        # Determine article type and scope
        article_type, estimated_words = classify_question_type(primary_content, question_content, response_type)
        
        individual_articles.append({
            'topic_id': topic_id,
            'parent_topic_title': topic_title,
            'parent_category': topic_category,
            'question_date': date_posted,
            'response_type': response_type,
            'user_pain_point': pain_point,
            'user_question': question_content[:500] + "..." if len(question_content) > 500 else question_content,
            'suggested_article_title': article_title,
            'article_type': article_type,
            'estimated_words': estimated_words,
            'priority_score': calculate_question_priority(pain_point, question_content, response_type, date_posted)
        })
    
    return individual_articles

def suggest_specific_article_title(pain_point, question_content, topic_title):
    """
    Suggest specific article titles based on individual user questions
    """
    
    # Combine pain point and question for analysis
    full_content = f"{pain_point} {question_content}".lower()
    
    # Calendar and sync issues
    if any(word in full_content for word in ['calendar', 'different workout', 'app vs web', 'scheduled']):
        if 'calendar' in full_content and 'app' in full_content:
            return "How to View Your Training Calendar in the TrainerDay App"
        elif 'different' in full_content and 'website' in full_content:
            return "Why TrainerDay App and Website Show Different Workouts"
        elif 'sync' in full_content:
            return "How to Sync Workouts Between TrainerDay App and Website"
        else:
            return "TrainerDay Calendar: App vs Website Differences"
    
    # External workout logging
    if any(word in full_content for word in ['external', 'strava', 'done outside', 'recorded externally']):
        return "How to Log External Workouts in TrainerDay"
    
    # Coach Jack issues
    if 'coach jack' in full_content:
        if 'blank screen' in full_content or 'not working' in full_content:
            return "Fixing Coach Jack Blank Screen Issues"
        elif 'edit' in full_content or 'customize' in full_content:
            return "How to Edit and Customize Coach Jack Plans"
        else:
            return "Coach Jack Troubleshooting Guide"
    
    # App crash issues
    if any(word in full_content for word in ['crash', 'crashing', 'save', 'finish workout']):
        if 'ramp test' in full_content:
            return "Fixing App Crashes During FTP Ramp Tests"
        elif 'save' in full_content or 'finish' in full_content:
            return "How to Save Workouts When TrainerDay App Crashes"
        else:
            return "Troubleshooting TrainerDay App Crashes"
    
    # Trainer connection issues
    if any(word in full_content for word in ['trainer', 'connection', 'bluetooth', 'elite', 'tacx']):
        if 'connection' in full_content or 'lost' in full_content:
            return "Fixing Trainer Connection Issues in TrainerDay"
        elif 'elite' in full_content:
            return "TrainerDay Setup Guide for Elite Trainers"
        else:
            return "Smart Trainer Troubleshooting in TrainerDay"
    
    # Interval and workout features
    if any(word in full_content for word in ['interval', 'description', 'dropdown', 'expand']):
        if 'dropdown' in full_content or 'expand' in full_content:
            return "How to Use TrainerDay's Interval Description Feature"
        else:
            return "Understanding Workout Intervals in TrainerDay"
    
    # Heart rate and zones
    if any(word in full_content for word in ['heart rate', 'zone 2', 'hr', 'zone calculation']):
        if 'conversion' in full_content or 'convert' in full_content:
            return "TrainerDay Heart Rate Data Conversion Guide"
        elif 'zone 2' in full_content:
            return "Setting Up Zone 2 Training in TrainerDay"
        else:
            return "Heart Rate Zone Setup in TrainerDay"
    
    # Generic fallback based on pain point
    if pain_point:
        # Clean up pain point for title
        clean_pain = pain_point[:60].strip()
        if clean_pain.endswith('.'):
            clean_pain = clean_pain[:-1]
        return f"How to Fix: {clean_pain}"
    
    # Last resort: extract key topic from content
    if 'workout' in full_content:
        return "TrainerDay Workout Management Guide"
    elif 'plan' in full_content:
        return "TrainerDay Training Plan Guide"
    else:
        return f"TrainerDay Guide: {topic_title[:50]}"

def classify_question_type(pain_point, question_content, response_type):
    """
    Classify the type of article and estimate word count needed
    """
    
    full_content = f"{pain_point} {question_content}".lower()
    
    # Quick fix articles (800 words)
    if response_type == 'troubleshooting' or any(word in full_content for word in ['crash', 'error', 'not working', 'blank screen']):
        return 'TROUBLESHOOTING', 800
    
    # How-to guides (1000 words)
    elif any(phrase in full_content for phrase in ['how to', 'how do i', 'way to', 'setup', 'configure']):
        return 'HOW_TO_GUIDE', 1000
    
    # Feature explanations (1200 words)
    elif response_type == 'explanation' or any(word in full_content for word in ['what is', 'explain', 'understand', 'difference']):
        return 'FEATURE_EXPLANATION', 1200
    
    # Setup guides (1000 words)
    elif any(word in full_content for word in ['setup', 'install', 'configure', 'connect']):
        return 'SETUP_GUIDE', 1000
    
    # General guides (800 words)
    else:
        return 'GENERAL_GUIDE', 800

def calculate_question_priority(pain_point, question_content, response_type, date_posted):
    """
    Calculate priority score for individual questions
    """
    
    priority_score = 5.0  # Base score
    
    # Recent questions get higher priority
    if date_posted:
        try:
            from datetime import datetime
            question_date = datetime.strptime(str(date_posted), '%Y-%m-%d')
            days_since = (datetime.now() - question_date).days
            
            if days_since <= 30:
                priority_score += 3
            elif days_since <= 90:
                priority_score += 2
            elif days_since <= 180:
                priority_score += 1
        except:
            pass
    
    # Troubleshooting questions are high priority
    if response_type == 'troubleshooting':
        priority_score += 2
    
    # Common pain points get higher priority
    full_content = f"{pain_point} {question_content}".lower()
    
    high_priority_keywords = ['crash', 'not working', 'blank screen', 'connection', 'sync', 'calendar']
    medium_priority_keywords = ['how to', 'setup', 'configure', 'explain']
    
    if any(word in full_content for word in high_priority_keywords):
        priority_score += 2
    elif any(word in full_content for word in medium_priority_keywords):
        priority_score += 1
    
    return round(priority_score, 1)

def create_topic_clusters(individual_articles):
    """
    Group related articles into topic clusters for overview articles
    """
    
    clusters = defaultdict(list)
    
    for article in individual_articles:
        # Group by common themes
        title = article['suggested_article_title'].lower()
        
        if any(word in title for word in ['coach jack']):
            clusters['Coach Jack Features'].append(article)
        elif any(word in title for word in ['calendar', 'sync', 'app vs web']):
            clusters['Calendar & Sync'].append(article)
        elif any(word in title for word in ['crash', 'troubleshooting', 'fix']):
            clusters['App Troubleshooting'].append(article)
        elif any(word in title for word in ['trainer', 'connection', 'bluetooth']):
            clusters['Trainer Setup'].append(article)
        elif any(word in title for word in ['heart rate', 'zone', 'hr']):
            clusters['Heart Rate & Zones'].append(article)
        elif any(word in title for word in ['interval', 'workout', 'description']):
            clusters['Workout Features'].append(article)
        else:
            clusters['General Guides'].append(article)
    
    return dict(clusters)

def suggest_overview_articles(clusters):
    """
    Suggest overview articles for each topic cluster
    """
    
    overview_articles = []
    
    for cluster_name, articles in clusters.items():
        if len(articles) >= 2:  # Only create overviews for clusters with 2+ articles
            
            overview_articles.append({
                'cluster_name': cluster_name,
                'overview_title': f"TrainerDay {cluster_name}: Complete Guide",
                'article_count': len(articles),
                'linked_articles': [a['suggested_article_title'] for a in articles],
                'estimated_words': 1500,  # Overview articles are longer
                'article_type': 'OVERVIEW_HUB',
                'description': f"Comprehensive guide covering all {cluster_name.lower()} topics with links to specific solutions"
            })
    
    return overview_articles

def main():
    """
    Main execution: Extract individual questions and create article strategy
    """
    
    print("📝 INDIVIDUAL QUESTION ARTICLES STRATEGY")
    print("=" * 60)
    print("Breaking down forum topics into focused, individual articles")
    print("Each user question becomes a specific, targeted article")
    print()
    
    try:
        # Load the review session data
        script_dir = Path(__file__).parent
        review_files = list(script_dir.glob("topic_review_session_*.json"))
        
        if not review_files:
            print("❌ No review session found. Run review_priority_topics.py first.")
            return
        
        latest_review = max(review_files, key=lambda f: f.stat().st_mtime)
        print(f"📁 Loading review session: {latest_review.name}")
        
        with open(latest_review, 'r') as f:
            review_data = json.load(f)
        
        # Extract individual articles from all topics
        all_individual_articles = []
        
        print(f"🔍 Processing {len(review_data['topics'])} topics...")
        
        for topic_data_dict in review_data['topics']:
            # Convert dict back to tuple format for processing
            topic_data = (
                topic_data_dict['topic_id'],
                topic_data_dict['title'],
                topic_data_dict['category'],
                topic_data_dict['created_at'],
                topic_data_dict['views'],
                topic_data_dict['posts_count'],
                topic_data_dict['total_questions'],
                topic_data_dict['latest_question_date'],
                topic_data_dict['questions']
            )
            
            individual_articles = extract_individual_questions(topic_data)
            all_individual_articles.extend(individual_articles)
        
        # Sort by priority score
        all_individual_articles.sort(key=lambda x: x['priority_score'], reverse=True)
        
        print(f"✅ Extracted {len(all_individual_articles)} individual article ideas")
        
        # Create topic clusters
        clusters = create_topic_clusters(all_individual_articles)
        overview_articles = suggest_overview_articles(clusters)
        
        print(f"📊 Created {len(clusters)} topic clusters")
        print(f"📋 Suggested {len(overview_articles)} overview articles")
        print()
        
        # Display results
        print("🏆 TOP INDIVIDUAL ARTICLES (by priority):")
        print("-" * 60)
        
        for i, article in enumerate(all_individual_articles[:15], 1):
            print(f"{i:2d}. {article['suggested_article_title']}")
            print(f"    Type: {article['article_type']} | Words: {article['estimated_words']} | Priority: {article['priority_score']}")
            print(f"    User Need: {article['user_pain_point'][:80] + '...' if len(article['user_pain_point']) > 80 else article['user_pain_point']}")
            print()
        
        # Show topic clusters
        print("📚 TOPIC CLUSTERS & OVERVIEW ARTICLES:")
        print("-" * 60)
        
        for overview in overview_articles:
            print(f"\n🏠 **{overview['overview_title']}** ({overview['article_count']} linked articles)")
            for linked_title in overview['linked_articles'][:3]:  # Show first 3
                print(f"   • {linked_title}")
            if overview['article_count'] > 3:
                print(f"   • ... and {overview['article_count'] - 3} more")
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"individual_articles_strategy_{timestamp}.json"
        
        strategy_data = {
            'generated_at': datetime.now().isoformat(),
            'strategy': 'Individual question articles with topic clusters',
            'individual_articles': all_individual_articles,
            'topic_clusters': clusters,
            'overview_articles': overview_articles,
            'summary': {
                'individual_articles_count': len(all_individual_articles),
                'topic_clusters_count': len(clusters),
                'overview_articles_count': len(overview_articles),
                'total_articles': len(all_individual_articles) + len(overview_articles)
            }
        }
        
        output_path = Path(__file__).parent / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(strategy_data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📁 Individual articles strategy saved: {output_file}")
        
        print(f"\n✅ INDIVIDUAL ARTICLES STRATEGY COMPLETE!")
        print(f"   • {len(all_individual_articles)} focused individual articles")
        print(f"   • {len(overview_articles)} overview hub articles")
        print(f"   • {len(all_individual_articles) + len(overview_articles)} total articles planned")
        print("\n🎯 CONTENT APPROACH:")
        print("   1. Each user question = one focused article")
        print("   2. Overview articles link to specific solutions")
        print("   3. Better SEO with targeted, specific content")
        print("   4. Users find exactly what they're looking for")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()