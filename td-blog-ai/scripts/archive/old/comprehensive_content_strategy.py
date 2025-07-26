#!/usr/bin/env python3
"""
Comprehensive Content Strategy Generator

Generate 100-200 article titles with full categorization:
- Engagement levels (Quick/Complete/Geek-Out)
- TrainerDay content tags
- Related user questions
- MD table format output
- Overview articles per tag

Focus: TrainerDay features + solving user issues
Outputs to TD-Business blog directory
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.db_connection import get_db_connection
from utils.content_structure import CATEGORIES, ENGAGEMENT_LEVELS, TAG_GROUPS

def get_comprehensive_forum_data(limit=200):
    """
    Get comprehensive forum Q&A data for content strategy
    Focus on feature-related and issue-solving content
    """
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    WITH prioritized_questions AS (
        SELECT 
            ftr.topic_id,
            ftr.title as topic_title,
            ft.analysis_category,
            qa.id as qa_id,
            qa.pain_point,
            qa.question_content,
            qa.response_content,
            qa.response_type,
            qa.date_posted,
            qa.user_language,
            qa.platform_language,
            
            -- Extract topic metrics
            COALESCE((jsonb_extract_path_text(ftr.raw_content, 'topic', 'views'))::int, 0) as views,
            COALESCE((jsonb_extract_path_text(ftr.raw_content, 'topic', 'posts_count'))::int, 0) as posts_count,
            
            -- Calculate recency score
            CASE 
                WHEN qa.date_posted >= CURRENT_DATE - INTERVAL '30 days' THEN 10
                WHEN qa.date_posted >= CURRENT_DATE - INTERVAL '90 days' THEN 8
                WHEN qa.date_posted >= CURRENT_DATE - INTERVAL '180 days' THEN 6
                WHEN qa.date_posted >= CURRENT_DATE - INTERVAL '365 days' THEN 4
                ELSE 2
            END as recency_score,
            
            -- Feature relevance score
            CASE 
                WHEN LOWER(qa.pain_point || ' ' || qa.question_content) ~ '(coach jack|workout|plan|calendar|app|sync|export|integration|garmin|zwift|strava)' THEN 3
                WHEN LOWER(qa.pain_point || ' ' || qa.question_content) ~ '(setup|configure|how to|guide|tutorial)' THEN 2
                WHEN qa.response_type IN ('troubleshooting', 'explanation') THEN 2
                ELSE 1
            END as feature_relevance,
            
            -- Issue-solving score
            CASE 
                WHEN qa.response_type = 'troubleshooting' THEN 3
                WHEN LOWER(qa.pain_point || ' ' || qa.question_content) ~ '(crash|error|not working|problem|issue|fix|solve)' THEN 2
                WHEN LOWER(qa.pain_point || ' ' || qa.question_content) ~ '(how to|setup|configure)' THEN 2
                ELSE 1
            END as issue_solving_score
            
        FROM forum_qa_pairs qa
        JOIN forum_topics_raw ftr ON qa.topic_id = ftr.topic_id
        LEFT JOIN forum_topics ft ON ftr.topic_id = ft.topic_id
        WHERE qa.date_posted >= CURRENT_DATE - INTERVAL '2 years'
            AND qa.pain_point IS NOT NULL 
            AND qa.pain_point != ''
            AND LENGTH(qa.pain_point) > 10
            -- Exclude non-cycling activities
            AND NOT (LOWER(qa.pain_point || ' ' || qa.question_content) ~ '(concept2|rowing|erg|swim|run|weight loss|strength)')
            -- Focus on feature and issue content
            AND (qa.response_type IN ('troubleshooting', 'explanation', 'question_back') 
                 OR LOWER(qa.pain_point || ' ' || qa.question_content) ~ '(how to|setup|configure|coach jack|workout|plan|calendar|app)')
    ),
    scored_questions AS (
        SELECT *,
            (recency_score * 0.3 + feature_relevance * 0.4 + issue_solving_score * 0.3) as total_score
        FROM prioritized_questions
    )
    SELECT * FROM scored_questions
    ORDER BY total_score DESC, recency_score DESC, views DESC
    LIMIT %s
    """
    
    cursor.execute(query, (limit,))
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return results

def determine_engagement_level(pain_point, question_content, response_type):
    """
    Determine engagement level based on question complexity and user intent
    """
    
    full_content = f"{pain_point} {question_content}".lower()
    
    # Quick (800 words): Simple how-to, urgent problems, basic setup
    quick_indicators = [
        'how do i', 'quick question', 'simple', 'just need to',
        'crash', 'not working', 'error', 'fix', 'broken'
    ]
    
    # Geek-Out (1500+ words): Technical discussions, advanced optimization
    geekout_indicators = [
        'technical', 'advanced', 'optimize', 'deep dive', 'algorithm',
        'detailed', 'comprehensive', 'all options', 'everything about'
    ]
    
    # Complete (1200 words): Complex workflows, understanding requests, feature explanations
    complete_indicators = [
        'explain', 'understand', 'best way', 'comprehensive', 'workflow',
        'integration', 'setup guide', 'complete', 'full picture'
    ]
    
    # Check indicators
    if any(indicator in full_content for indicator in quick_indicators):
        return 'Quick'
    elif any(indicator in full_content for indicator in geekout_indicators):
        return 'Geek-Out'
    elif any(indicator in full_content for indicator in complete_indicators):
        return 'Complete'
    elif response_type == 'troubleshooting':
        return 'Quick'
    elif response_type == 'explanation':
        return 'Complete'
    else:
        return 'Quick'  # Default for user issues

def determine_category(pain_point, question_content, analysis_category):
    """
    Determine TrainerDay content category
    """
    
    full_content = f"{pain_point} {question_content}".lower()
    
    # Features: TrainerDay app features and functionality
    if any(keyword in full_content for keyword in [
        'coach jack', 'app', 'website', 'sync', 'export', 'calendar',
        'workout creator', 'plan creator', 'my workouts', 'my plans',
        'integration', 'garmin', 'zwift', 'strava', 'settings'
    ]):
        return 'Features'
    
    # Training: Training methodology, periodization, performance analysis  
    elif any(keyword in full_content for keyword in [
        'training', 'plan', 'ftp', 'zones', 'periodization', 'analysis',
        'performance', 'ramp test', 'threshold', 'polarized'
    ]):
        return 'Training'
    
    # Indoor: Indoor cycling setup, equipment, basics
    elif any(keyword in full_content for keyword in [
        'trainer', 'setup', 'connection', 'bluetooth', 'ant+', 'kickr',
        'tacx', 'elite', 'wahoo', 'smart trainer', 'power meter'
    ]):
        return 'Indoor'
    
    # Other: Reviews, comparisons, general topics
    else:
        return 'Other'

def assign_tags(pain_point, question_content, category):
    """
    Assign relevant tags based on content analysis
    """
    
    full_content = f"{pain_point} {question_content}".lower()
    tags = []
    
    # App & Platform tags
    if any(word in full_content for word in ['web', 'website']):
        tags.append('web-app')
    if any(word in full_content for word in ['mobile', 'iphone', 'android', 'app']):
        tags.append('mobile-app')
    if 'trainerday' in full_content:
        tags.append('about-trainerday')
    
    # Training Concepts tags
    if any(word in full_content for word in ['training', 'plan']):
        tags.append('training')
    if any(word in full_content for word in ['indoor', 'trainer']):
        tags.append('indoor-cycling')
    if any(word in full_content for word in ['heart rate', 'hr']):
        tags.append('heart-rate')
    if any(word in full_content for word in ['ftp', 'ramp test']):
        tags.append('ftp')
    if any(word in full_content for word in ['zone', 'zones']):
        tags.append('zones')
    
    # Features & Tools tags  
    if 'coach jack' in full_content:
        tags.append('coach-jack')
    if any(word in full_content for word in ['workout creator', 'create workout']):
        tags.append('workout-creator')
    if any(word in full_content for word in ['plan creator', 'create plan']):
        tags.append('plan-creator')
    if any(word in full_content for word in ['my workouts', 'workout library']):
        tags.append('my-workouts')
    if any(word in full_content for word in ['my plans', 'plan library']):
        tags.append('my-plans')
    if any(word in full_content for word in ['calendar', 'schedule']):
        tags.append('my-calendar')
    if any(word in full_content for word in ['export', 'download']):
        tags.append('export')
    if any(word in full_content for word in ['sync', 'synchronize']):
        tags.append('sync')
    
    # Equipment & Tech tags
    if any(word in full_content for word in ['trainer', 'smart trainer']):
        tags.append('equipment')
    if any(word in full_content for word in ['bluetooth', 'ant+', 'connection']):
        tags.append('technology')
    
    # Integrations tags
    if 'garmin' in full_content:
        tags.append('garmin')
    if 'zwift' in full_content:
        tags.append('zwift')
    if any(word in full_content for word in ['training peaks', 'trainingpeaks']):
        tags.append('training-peaks')
    if any(word in full_content for word in ['intervals', 'intervals.icu']):
        tags.append('intervals-icu')
    if 'strava' in full_content:
        tags.append('strava')
    if 'wahoo' in full_content:
        tags.append('wahoo')
    
    # Ensure at least one tag
    if not tags:
        if category == 'Features':
            tags.append('about-trainerday')
        elif category == 'Training':
            tags.append('training')
        elif category == 'Indoor':
            tags.append('indoor-cycling')
        else:
            tags.append('about-trainerday')
    
    return tags[:5]  # Limit to 5 tags max

def generate_article_title(pain_point, question_content, category, engagement_level):
    """
    Generate specific article title based on user question and categorization
    """
    
    full_content = f"{pain_point} {question_content}".lower()
    
    # Clean pain point for title use
    clean_pain = pain_point.strip()
    if len(clean_pain) > 80:
        clean_pain = clean_pain[:77] + "..."
    
    # Feature-specific titles
    if 'coach jack' in full_content:
        if 'blank screen' in full_content or 'not working' in full_content:
            return "How to Fix Coach Jack Blank Screen Issues"
        elif 'edit' in full_content or 'customize' in full_content:
            return "How to Edit and Customize Coach Jack Training Plans"
        elif 'weight loss' in full_content:
            return "Setting Up Coach Jack for Weight Loss Goals"
        else:
            return "Coach Jack Setup and Troubleshooting Guide"
    
    elif any(word in full_content for word in ['calendar', 'schedule']):
        if 'app' in full_content and 'web' in full_content:
            return "TrainerDay Calendar: App vs Website Differences"
        elif 'sync' in full_content:
            return "How to Sync Your TrainerDay Calendar"
        else:
            return "How to Use TrainerDay's Training Calendar"
    
    elif any(word in full_content for word in ['sync', 'export', 'integration']):
        if 'garmin' in full_content:
            return "How to Sync TrainerDay Workouts with Garmin"
        elif 'strava' in full_content:
            return "TrainerDay to Strava Integration Guide"
        elif 'zwift' in full_content:
            return "Using TrainerDay Workouts in Zwift"
        else:
            return "TrainerDay Data Export and Integration Guide"
    
    elif any(word in full_content for word in ['crash', 'error', 'not working']):
        if 'app' in full_content:
            return f"Fixing TrainerDay App Issues: {clean_pain}"
        else:
            return f"How to Fix: {clean_pain}"
    
    elif any(word in full_content for word in ['workout', 'interval']):
        if 'create' in full_content or 'creator' in full_content:
            return "How to Create Custom Workouts in TrainerDay"
        elif 'description' in full_content:
            return "Understanding TrainerDay's Workout Interval Descriptions"
        else:
            return f"TrainerDay Workout Guide: {clean_pain}"
    
    elif any(word in full_content for word in ['setup', 'configure', 'connection']):
        if 'trainer' in full_content:
            return f"Smart Trainer Setup Guide: {clean_pain}"
        else:
            return f"TrainerDay Setup Guide: {clean_pain}"
    
    # Generic titles based on engagement level
    elif engagement_level == 'Quick':
        return f"Quick Fix: {clean_pain}"
    elif engagement_level == 'Geek-Out':
        return f"Complete Technical Guide: {clean_pain}"
    else:
        return f"How to Solve: {clean_pain}"

def create_overview_articles_by_tag(articles_by_tag):
    """
    Create overview articles for each tag that link to specific articles
    """
    
    overview_articles = []
    
    for tag, articles in articles_by_tag.items():
        if len(articles) >= 3:  # Only create overviews for tags with 3+ articles
            
            # Tag display names
            tag_names = {
                'coach-jack': 'Coach Jack',
                'my-calendar': 'Training Calendar',
                'mobile-app': 'Mobile App',
                'web-app': 'Web App',
                'sync': 'Data Sync',
                'export': 'Data Export',
                'garmin': 'Garmin Integration',
                'zwift': 'Zwift Integration',
                'strava': 'Strava Integration',
                'my-workouts': 'Workout Management',
                'my-plans': 'Training Plans',
                'equipment': 'Equipment Setup',
                'heart-rate': 'Heart Rate',
                'ftp': 'FTP Testing'
            }
            
            tag_display = tag_names.get(tag, tag.replace('-', ' ').title())
            
            overview_title = f"TrainerDay {tag_display}: Complete Guide"
            
            # Create short descriptions for linked articles
            linked_articles = []
            for article in articles[:10]:  # Top 10 articles per tag
                short_desc = article['pain_point'][:60] + "..." if len(article['pain_point']) > 60 else article['pain_point']
                linked_articles.append({
                    'title': article['article_title'],
                    'description': short_desc,
                    'engagement': article['engagement_level']
                })
            
            overview_articles.append({
                'tag': tag,
                'title': overview_title,
                'article_count': len(articles),
                'linked_articles': linked_articles,
                'category': 'Features',  # Most overview articles are feature-focused
                'engagement_level': 'Complete',
                'estimated_words': 1800,
                'description': f"Comprehensive guide to all TrainerDay {tag_display.lower()} features with links to specific solutions and troubleshooting guides."
            })
    
    return overview_articles

def generate_markdown_output(articles, overview_articles, output_file):
    """
    Generate comprehensive markdown output with tables and overview articles
    """
    
    content = []
    
    # Header
    content.append("# TrainerDay Content Strategy: Complete Article List")
    content.append("")
    content.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content.append(f"**Total Articles:** {len(articles)} individual + {len(overview_articles)} overview = {len(articles) + len(overview_articles)} total")
    content.append("")
    content.append("## Strategy Overview")
    content.append("")
    content.append("This content strategy focuses on **TrainerDay features** and **solving user issues** based on actual forum questions from the past 2 years.")
    content.append("")
    content.append("### Content Types:")
    content.append("- **Individual Articles**: Specific solutions to user questions")
    content.append("- **Overview Articles**: Comprehensive guides linking to related specific articles")
    content.append("")
    content.append("### Engagement Levels:")
    content.append("- **Quick** (800 words): Urgent fixes and simple how-tos")
    content.append("- **Complete** (1200 words): Feature explanations and workflows")  
    content.append("- **Geek-Out** (1500+ words): Technical deep-dives and advanced topics")
    content.append("")
    
    # Statistics
    engagement_counts = Counter(article['engagement_level'] for article in articles)
    category_counts = Counter(article['category'] for article in articles)
    
    content.append("## Content Statistics")
    content.append("")
    content.append("### By Engagement Level:")
    for engagement, count in engagement_counts.most_common():
        percentage = (count / len(articles)) * 100
        content.append(f"- **{engagement}**: {count} articles ({percentage:.1f}%)")
    content.append("")
    
    content.append("### By Category:")
    for category, count in category_counts.most_common():
        percentage = (count / len(articles)) * 100
        content.append(f"- **{category}**: {count} articles ({percentage:.1f}%)")
    content.append("")
    
    # Overview Articles Table
    content.append("## Overview Hub Articles")
    content.append("")
    content.append("These comprehensive guides link to specific solutions:")
    content.append("")
    content.append("| Title | Tag | Linked Articles | Category | Words |")
    content.append("|-------|-----|-----------------|----------|-------|")
    
    for overview in overview_articles:
        content.append(f"| {overview['title']} | `{overview['tag']}` | {overview['article_count']} articles | {overview['category']} | {overview['estimated_words']} |")
    
    content.append("")
    
    # Individual Articles Table  
    content.append("## Individual Articles")
    content.append("")
    content.append("Specific solutions to user questions, sorted by priority:")
    content.append("")
    content.append("| # | Include | Article Title | Category | Engagement | Tags | User Question/Pain Point |")
    content.append("|---|---------|---------------|----------|------------|------|--------------------------|")
    
    for i, article in enumerate(articles, 1):
        tags_str = ', '.join([f"`{tag}`" for tag in article['tags']])
        pain_point = article['pain_point'][:80] + "..." if len(article['pain_point']) > 80 else article['pain_point']
        
        # Set "yes" for first 50 articles, "later" for the rest
        include_status = "yes" if i <= 50 else "later"
        
        content.append(f"| {i} | {include_status} | {article['article_title']} | {article['category']} | {article['engagement_level']} | {tags_str} | {pain_point} |")
    
    content.append("")
    content.append("---")
    content.append("")
    content.append("## Implementation Notes")
    content.append("")
    content.append("### Content Creation Priority:")
    content.append("1. Start with **Quick** troubleshooting articles (immediate user needs)")
    content.append("2. Create **Complete** feature guides (core functionality)")
    content.append("3. Build **Overview** hub articles (comprehensive coverage)")
    content.append("4. Add **Geek-Out** technical content (advanced users)")
    content.append("")
    content.append("### SEO Strategy:")
    content.append("- Each article targets specific user search terms")
    content.append("- Overview articles establish topical authority") 
    content.append("- Internal linking between overview and individual articles")
    content.append("- Tag-based content clusters for better discoverability")
    content.append("")  
    content.append("### Quality Guidelines:")
    content.append("- All articles address real user pain points")
    content.append("- Focus on TrainerDay feature functionality")
    content.append("- Include actionable solutions and next steps")
    content.append("- Link to related articles for comprehensive coverage")
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
    
    return output_file

def main():
    """
    Generate comprehensive content strategy
    """
    
    print("📚 COMPREHENSIVE CONTENT STRATEGY GENERATOR")
    print("=" * 60)
    print("Generating 100-200 article titles with full categorization")
    print("Focus: TrainerDay features + solving user issues")
    print()
    
    try:
        # Get comprehensive forum data
        print("🔍 Extracting forum questions (targeting 150-200 articles)...")
        forum_data = get_comprehensive_forum_data(limit=200)
        
        if not forum_data:
            print("❌ No forum data found. Check database connection.")
            return
        
        print(f"✅ Retrieved {len(forum_data)} user questions")
        
        # Process each question into an article
        articles = []
        articles_by_tag = defaultdict(list)
        
        print("📝 Generating article titles and categorization...")
        
        for row in forum_data:
            pain_point = row[4] or ""  # pain_point
            question_content = row[5] or ""  # question_content
            response_type = row[7]  # response_type
            analysis_category = row[2]  # analysis_category
            
            if not pain_point.strip():
                continue
            
            # Determine categorization
            engagement_level = determine_engagement_level(pain_point, question_content, response_type)
            category = determine_category(pain_point, question_content, analysis_category)
            tags = assign_tags(pain_point, question_content, category)
            article_title = generate_article_title(pain_point, question_content, category, engagement_level)
            
            # Estimate word count based on engagement level
            word_counts = {'Quick': 800, 'Complete': 1200, 'Geek-Out': 1500}
            estimated_words = word_counts[engagement_level]
            
            article = {
                'article_title': article_title,
                'category': category,
                'engagement_level': engagement_level,
                'tags': tags,
                'estimated_words': estimated_words,
                'pain_point': pain_point,
                'question_content': question_content[:200] + "..." if len(question_content) > 200 else question_content,
                'response_type': response_type,
                'topic_id': row[0],
                'priority_score': row[-1]  # total_score
            }
            
            articles.append(article)
            
            # Group by tags for overview articles
            for tag in tags:
                articles_by_tag[tag].append(article)
        
        print(f"✅ Generated {len(articles)} individual articles")
        
        # Create overview articles
        print("🏗️ Creating overview hub articles...")
        overview_articles = create_overview_articles_by_tag(articles_by_tag)
        print(f"✅ Created {len(overview_articles)} overview articles")
        
        # Generate markdown output to TD-Business blog directory
        today = datetime.now().strftime('%Y-%m-%d')
        output_filename = f"user-questions-{today}.md"
        
        # Get output path from environment variable
        output_base_path = os.getenv('CONTENT_OUTPUT_PATH')
        if not output_base_path:
            print("⚠️  CONTENT_OUTPUT_PATH not set in .env, using current directory")
            output_base_path = "."
        
        output_path = Path(output_base_path)
        
        # Create directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)
        
        output_file = output_path / output_filename
        
        print(f"📄 Generating markdown output to: {output_file}")
        markdown_file = generate_markdown_output(articles, overview_articles, str(output_file))
        
        # Save JSON data as well
        json_filename = f"user-questions-{today}.json"
        json_file = output_path / json_filename
        strategy_data = {
            'generated_at': datetime.now().isoformat(),
            'individual_articles': articles,
            'overview_articles': overview_articles,
            'statistics': {
                'individual_count': len(articles),
                'overview_count': len(overview_articles),
                'total_articles': len(articles) + len(overview_articles),
                'engagement_distribution': dict(Counter(a['engagement_level'] for a in articles)),
                'category_distribution': dict(Counter(a['category'] for a in articles)),
                'tag_distribution': dict(Counter(tag for a in articles for tag in a['tags']))
            }
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(strategy_data, f, indent=2, ensure_ascii=False, default=str)
        
        print()
        print("✅ COMPREHENSIVE CONTENT STRATEGY COMPLETE!")
        print(f"   • {len(articles)} individual articles")
        print(f"   • {len(overview_articles)} overview hub articles") 
        print(f"   • {len(articles) + len(overview_articles)} total articles")
        print()
        print("📁 Files generated:")
        print(f"   • {output_file} (formatted content strategy)")
        print(f"   • {json_file} (structured data)")
        print()
        print("🎯 Next steps:")
        print("   1. Review the markdown file for article titles and prioritization")
        print("   2. Select your top 10-20 articles to start with")
        print("   3. Use the JSON data for programmatic content generation")
        print("   4. Begin with Quick articles (immediate user needs)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()