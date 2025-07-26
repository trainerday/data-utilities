#!/usr/bin/env python3
"""
TrainerDay Feature-Focused Content Strategy

This script filters forum topics to identify content opportunities specifically 
about TrainerDay features, functionality, and how-to guides.

Focus: TrainerDay-specific features and functionality
Excludes: General training theory, methodology, equipment discussions
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def load_priority_data():
    """Load the prioritized topics data"""
    script_dir = Path(__file__).parent
    priority_files = list(script_dir.glob("top_*_priority_topics.json"))
    
    if not priority_files:
        print("❌ No priority topics file found. Run prioritize_recent_content.py first.")
        return None
    
    latest_file = max(priority_files, key=lambda f: f.stat().st_mtime)
    print(f"📁 Loading data from: {latest_file.name}")
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    return data['topics']

def classify_feature_content(topic):
    """
    Classify topics specifically for TrainerDay feature content
    """
    
    title = topic['title'].lower()
    sample_questions = topic.get('sample_questions', '').lower()
    category = topic.get('category', '')
    
    # TrainerDay Feature Keywords (HIGH VALUE)
    trainerday_features = [
        'coach jack', 'workout creator', 'plan creator', 'my workouts', 
        'my plans', 'my calendar', 'wod', 'app', 'sync', 'export',
        'integration', 'garmin', 'zwift', 'training peaks', 'intervals',
        'wahoo', 'strava', 'calendar', 'sharing', 'organization'
    ]
    
    # App Functionality Keywords
    app_functionality = [
        'settings', 'profile', 'account', 'subscription', 'premium',
        'mobile app', 'web app', 'interface', 'navigation', 'login',
        'dashboard', 'library', 'search', 'filter', 'import', 'export'
    ]
    
    # Feature Education Keywords  
    feature_education = [
        'how to', 'setup', 'configure', 'customize', 'optimize',
        'best practices', 'workflow', 'tips', 'guide', 'tutorial'
    ]
    
    # Integration Keywords
    integration_keywords = [
        'garmin', 'zwift', 'training peaks', 'intervals.icu', 'strava',
        'wahoo', 'sync', 'connect', 'export', 'import', 'calendar'
    ]
    
    # Exclude General Training (LOW VALUE for feature content)
    general_training = [
        'ftp', 'vo2max', 'zone 2', 'threshold', 'polarized', 'recovery',
        'periodization', 'training theory', 'physiology', 'power',
        'heart rate zones', 'lactate', 'anaerobic'
    ]
    
    # Exclude Equipment (LOW VALUE for feature content)  
    equipment_keywords = [
        'trainer', 'power meter', 'heart rate monitor', 'cadence',
        'speed sensor', 'ant+', 'bluetooth', 'kickr', 'tacx', 'elite'
    ]
    
    # Calculate feature relevance score
    feature_score = 0
    reasons = []
    article_type = "OTHER"
    
    # High value: TrainerDay-specific features
    if any(keyword in title or keyword in sample_questions for keyword in trainerday_features):
        feature_score += 4
        reasons.append("TrainerDay feature content")
        article_type = "FEATURE_GUIDE"
    
    # Medium-high value: App functionality
    if any(keyword in title or keyword in sample_questions for keyword in app_functionality):
        feature_score += 3
        reasons.append("App functionality")
        if article_type == "OTHER":
            article_type = "APP_GUIDE"
    
    # Medium value: Integration topics
    if any(keyword in title or keyword in sample_questions for keyword in integration_keywords):
        feature_score += 3
        reasons.append("Integration/sync features")
        if article_type == "OTHER":
            article_type = "INTEGRATION_GUIDE"
    
    # Bonus for educational approach
    if any(keyword in title or keyword in sample_questions for keyword in feature_education):
        feature_score += 2
        reasons.append("Educational how-to content")
    
    # Penalize general training topics
    if any(keyword in title or keyword in sample_questions for keyword in general_training):
        if not any(keyword in title or keyword in sample_questions for keyword in trainerday_features):
            feature_score -= 2
            reasons.append("General training topic (not feature-specific)")
    
    # Penalize equipment-only topics
    if any(keyword in title or keyword in sample_questions for keyword in equipment_keywords):
        if not any(keyword in title or keyword in sample_questions for keyword in trainerday_features):
            feature_score -= 1
            reasons.append("Equipment-focused (not feature-specific)")
    
    # Bonus for [SOLVED] issues that show feature solutions
    if '[solved]' in title:
        feature_score += 1
        reasons.append("Resolved issue - shows feature solution")
    
    # Determine suitability
    if feature_score >= 4:
        suitability = "HIGH_FEATURE"
    elif feature_score >= 2:
        suitability = "MEDIUM_FEATURE"  
    elif feature_score >= 0:
        suitability = "LOW_FEATURE"
    else:
        suitability = "NOT_FEATURE"
    
    return {
        'feature_suitability': suitability,
        'feature_score': feature_score,
        'article_type': article_type,
        'feature_reasons': reasons
    }

def suggest_feature_article_title(topic):
    """Suggest feature-focused article titles"""
    
    title = topic['title'].lower()
    
    if 'coach jack' in title:
        if 'weight loss' in title:
            return "How to Set Up Coach Jack for Weight Loss Goals"
        elif 'not working' in title or 'blank' in title:
            return "Coach Jack Troubleshooting: Common Setup Issues"
        elif 'edit' in title:
            return "How to Edit and Customize Your Coach Jack Plan"
        else:
            return "Coach Jack Complete Setup Guide"
    
    elif 'sync' in title or 'integration' in title:
        if 'garmin' in title:
            return "TrainerDay + Garmin Integration: Complete Setup Guide"
        elif 'strava' in title:
            return "How to Sync TrainerDay Workouts with Strava" 
        elif 'training peaks' in title:
            return "TrainerDay to TrainingPeaks Sync: Setup & Best Practices"
        else:
            return "TrainerDay Integration Guide: Connecting Your Apps"
    
    elif 'app' in title:
        if 'crash' in title and '[solved]' in title:
            return "TrainerDay App Stability: Best Practices & Solutions"
        elif 'different' in title:
            return "TrainerDay App vs Web: Understanding the Differences"
        else:
            return "TrainerDay App: Features and Functionality Guide"
    
    elif 'workout' in title:
        if 'creator' in title or 'create' in title:
            return "How to Create Custom Workouts in TrainerDay"
        elif 'send' in title or 'export' in title:
            return "Exporting and Sharing TrainerDay Workouts"
        else:
            return "TrainerDay Workout Management Guide"
    
    elif 'calendar' in title:
        return "TrainerDay Calendar: Planning and Organization Features"
    
    elif 'plan' in title:
        if 'edit' in title:
            return "How to Edit Training Plans in TrainerDay"
        else:
            return "TrainerDay Training Plan Features Guide"
    
    else:
        # Generic feature-focused title
        clean_title = topic['title'].replace('[SOLVED]', '').replace('-', '').strip()
        return f"TrainerDay Guide: {clean_title}"

def generate_feature_content_strategy():
    """Generate TrainerDay feature-focused content recommendations"""
    
    topics = load_priority_data()
    if not topics:
        return
    
    print("\n🎯 TRAINERDAY FEATURE-FOCUSED CONTENT STRATEGY")
    print("=" * 60)
    print("Identifying content opportunities for TrainerDay features and functionality")
    print()
    
    # Classify all topics for feature relevance
    feature_topics = []
    
    for topic in topics:
        classification = classify_feature_content(topic)
        
        if classification['feature_suitability'] in ['HIGH_FEATURE', 'MEDIUM_FEATURE']:
            feature_topics.append({
                **topic,
                **classification,
                'suggested_title': suggest_feature_article_title(topic)
            })
    
    # Sort by feature score and priority score
    feature_topics.sort(
        key=lambda x: (x['feature_score'], x['priority_score']), 
        reverse=True
    )
    
    # Group by article type
    by_type = {
        'FEATURE_GUIDE': [],
        'APP_GUIDE': [],
        'INTEGRATION_GUIDE': [],
        'OTHER': []
    }
    
    for topic in feature_topics:
        by_type[topic['article_type']].append(topic)
    
    # Display results
    print("📊 FEATURE CONTENT BREAKDOWN:")
    print("-" * 40)
    for article_type, topics_list in by_type.items():
        if topics_list:
            print(f"{article_type.replace('_', ' ')}: {len(topics_list)} topics")
    print()
    
    # Show top feature articles
    print("🏆 TOP TRAINERDAY FEATURE ARTICLES:")
    print("-" * 60)
    
    for i, topic in enumerate(feature_topics[:12], 1):
        print(f"{i:2d}. {topic['suggested_title']}")
        print(f"    Original Topic: {topic['title']}")
        print(f"    Type: {topic['article_type'].replace('_', ' ')} | Priority: {topic['priority_score']}")
        print(f"    Feature Score: {topic['feature_score']} | Questions: {topic['question_count']}")
        print(f"    Focus: {', '.join(topic['feature_reasons'])}")
        print()
    
    # Feature-specific recommendations
    print("📝 FEATURE CONTENT RECOMMENDATIONS:")
    print("-" * 50)
    
    print("**IMMEDIATE PRIORITIES (Coach Jack & Core Features):**")
    coach_jack_topics = [t for t in feature_topics if 'coach jack' in t['title'].lower()][:3]
    for topic in coach_jack_topics:
        print(f"  • {topic['suggested_title']}")
    
    print("\n**INTEGRATION GUIDES:**")
    integration_topics = [t for t in feature_topics if t['article_type'] == 'INTEGRATION_GUIDE'][:3]
    for topic in integration_topics:
        print(f"  • {topic['suggested_title']}")
    
    print("\n**APP FUNCTIONALITY:**")
    app_topics = [t for t in feature_topics if t['article_type'] == 'APP_GUIDE'][:3]
    for topic in app_topics:
        print(f"  • {topic['suggested_title']}")
    
    # Save results
    output_file = f"feature_focused_strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            'generated_at': datetime.now().isoformat(),
            'focus': 'TrainerDay features and functionality',
            'total_feature_topics': len(feature_topics),
            'by_type': {k: len(v) for k, v in by_type.items() if v},
            'topics': feature_topics
        }, f, indent=2, default=str)
    
    print(f"\n📁 Feature-focused strategy saved to: {output_file}")
    
    return feature_topics

def main():
    """Main execution"""
    print("🚀 TRAINERDAY FEATURE CONTENT GENERATOR")
    print("=" * 60)
    print("Focusing specifically on TrainerDay features and functionality")
    print("excluding general training methodology and equipment topics.")
    print()
    
    try:
        feature_topics = generate_feature_content_strategy()
        
        if feature_topics:
            print("\n✅ FEATURE CONTENT STRATEGY COMPLETE!")
            print(f"   • {len(feature_topics)} feature-focused articles identified")
            print("\n🎯 RECOMMENDED APPROACH:")
            print("   1. Start with Coach Jack guides (most requested)")
            print("   2. Create integration/sync tutorials")
            print("   3. Build app functionality guides")
            print("   4. Focus on user workflows and best practices")
            print("   5. Use actual user questions to guide content depth")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()