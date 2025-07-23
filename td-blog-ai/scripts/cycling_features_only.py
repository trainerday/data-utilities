#!/usr/bin/env python3
"""
Cycling-Only TrainerDay Feature Content Strategy

Focus: TrainerDay cycling features and functionality only
Excludes: Concept2/rowing, weight loss, general training theory, equipment
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

def classify_cycling_feature_content(topic):
    """
    Classify topics specifically for cycling TrainerDay features
    """
    
    title = topic['title'].lower()
    sample_questions = topic.get('sample_questions', '').lower()
    category = topic.get('category', '')
    
    # EXCLUDE: Non-cycling activities
    non_cycling_keywords = [
        'concept2', 'rowing', 'erg', 'swim', 'run', 'weight loss',
        'strength', 'starts', 'vasa'
    ]
    
    # EXCLUDE: General training methodology  
    training_theory_keywords = [
        'vo2max', 'ftp', 'zone 2', 'threshold', 'polarized', 'recovery',
        'periodization', 'lactate', 'anaerobic', 'tired', 'training when'
    ]
    
    # HIGH VALUE: Core TrainerDay cycling features
    core_features = [
        'coach jack', 'workout creator', 'plan creator', 'my workouts',
        'my plans', 'my calendar', 'app', 'web', 'sync', 'export'
    ]
    
    # HIGH VALUE: Cycling integrations
    cycling_integrations = [
        'garmin', 'zwift', 'training peaks', 'intervals', 'strava',
        'wahoo', 'calendar sync', 'workout export', 'plan sync'
    ]
    
    # MEDIUM VALUE: App functionality
    app_features = [
        'interface', 'navigation', 'settings', 'profile', 'dashboard',
        'library', 'search', 'filter', 'mobile app', 'web app'
    ]
    
    # MEDIUM VALUE: Cycling-specific workflow features
    cycling_workflow = [
        'workout', 'plan', 'interval', 'target', 'power', 'heart rate',
        'cadence', 'erg mode', 'slope mode', 'resistance'
    ]
    
    # Check for exclusions first
    if any(keyword in title or keyword in sample_questions for keyword in non_cycling_keywords):
        return {
            'cycling_feature_score': -10,
            'cycling_suitability': 'EXCLUDE_NON_CYCLING',
            'cycling_reasons': ['Non-cycling activity excluded'],
            'article_type': 'EXCLUDED'
        }
    
    if any(keyword in title or keyword in sample_questions for keyword in training_theory_keywords):
        if not any(keyword in title or keyword in sample_questions for keyword in core_features):
            return {
                'cycling_feature_score': -5,
                'cycling_suitability': 'EXCLUDE_TRAINING_THEORY',
                'cycling_reasons': ['General training theory, not feature-specific'],
                'article_type': 'EXCLUDED'
            }
    
    # Calculate cycling feature score
    cycling_score = 0
    reasons = []
    article_type = "OTHER"
    
    # Core TrainerDay features (highest value)
    if any(keyword in title or keyword in sample_questions for keyword in core_features):
        cycling_score += 5
        reasons.append("Core TrainerDay cycling feature")
        
        if 'coach jack' in title or 'coach jack' in sample_questions:
            article_type = "COACH_JACK"
        elif 'workout' in title or 'my workouts' in sample_questions:
            article_type = "WORKOUT_FEATURES"
        elif 'plan' in title or 'my plans' in sample_questions:
            article_type = "PLAN_FEATURES"
        elif 'app' in title or 'web' in title:
            article_type = "APP_FEATURES"
    
    # Cycling integrations
    if any(keyword in title or keyword in sample_questions for keyword in cycling_integrations):
        cycling_score += 4
        reasons.append("Cycling platform integration")
        if article_type == "OTHER":
            article_type = "INTEGRATION"
    
    # App functionality
    if any(keyword in title or keyword in sample_questions for keyword in app_features):
        cycling_score += 3
        reasons.append("App functionality")
        if article_type == "OTHER":
            article_type = "APP_FEATURES"
    
    # Cycling workflow features
    if any(keyword in title or keyword in sample_questions for keyword in cycling_workflow):
        cycling_score += 2
        reasons.append("Cycling workflow feature")
        if article_type == "OTHER":
            article_type = "WORKFLOW"
    
    # Bonus for solved issues (educational value)
    if '[solved]' in title:
        cycling_score += 2
        reasons.append("Resolved issue with educational value")
    
    # Feature-focused language bonus
    if any(phrase in title or phrase in sample_questions for phrase in ['how to', 'setup', 'configure']):
        cycling_score += 1
        reasons.append("Feature education content")
    
    # Determine suitability
    if cycling_score >= 6:
        suitability = "HIGH_CYCLING_FEATURE"
    elif cycling_score >= 4:
        suitability = "MEDIUM_CYCLING_FEATURE"
    elif cycling_score >= 2:
        suitability = "LOW_CYCLING_FEATURE"
    else:
        suitability = "NOT_CYCLING_FEATURE"
    
    return {
        'cycling_feature_score': cycling_score,
        'cycling_suitability': suitability,
        'cycling_reasons': reasons,
        'article_type': article_type
    }

def suggest_cycling_feature_title(topic):
    """Suggest cycling-focused feature article titles"""
    
    title = topic['title'].lower()
    
    if 'coach jack' in title:
        if 'not working' in title or 'blank' in title:
            return "Coach Jack Setup Guide: Avoiding Common Issues"
        elif 'edit' in title or 'plan' in title:
            return "How to Customize Your Coach Jack Cycling Plan"
        else:
            return "Coach Jack for Cyclists: Complete Feature Guide"
    
    elif 'app' in title and 'web' in title:
        return "TrainerDay App vs Web: Which Platform for Cycling?"
    
    elif 'sync' in title or 'export' in title:
        if 'garmin' in title:
            return "Syncing TrainerDay Cycling Workouts to Garmin"
        elif 'zwift' in title:
            return "Using TrainerDay Workouts in Zwift"
        elif 'strava' in title:
            return "TrainerDay to Strava: Cycling Activity Sync"
        else:
            return "TrainerDay Cycling Workout Export Guide"
    
    elif 'workout' in title:
        if 'create' in title or 'creator' in title:
            return "Creating Custom Cycling Workouts in TrainerDay"
        elif 'send' in title or 'close' in title:
            return "TrainerDay Workout Management Features"
        else:
            return "TrainerDay Cycling Workout Features"
    
    elif 'plan' in title:
        return "TrainerDay Cycling Plan Management Guide"
    
    elif 'calendar' in title:
        return "TrainerDay Calendar: Organizing Your Cycling Training"
    
    elif 'interval' in title:
        return "TrainerDay Interval Features for Cycling"
    
    elif 'big screen' in title or 'screen' in title:
        return "TrainerDay Multi-Screen Setup for Cycling"
    
    else:
        # Clean up title and make it cycling-focused
        clean_title = topic['title'].replace('[SOLVED]', '').replace('-', '').strip()
        if len(clean_title) > 50:
            clean_title = clean_title[:47] + "..."
        return f"TrainerDay Cycling: {clean_title}"

def generate_cycling_feature_strategy():
    """Generate cycling-only TrainerDay feature content"""
    
    topics = load_priority_data()
    if not topics:
        return
    
    print("\n🚴 CYCLING-ONLY TRAINERDAY FEATURE STRATEGY")
    print("=" * 60)
    print("Pure cycling features and functionality content")
    print("Excluding: Concept2, weight loss, general training theory")
    print()
    
    # Filter and classify topics
    cycling_topics = []
    excluded_count = 0
    
    for topic in topics:
        classification = classify_cycling_feature_content(topic)
        
        if classification['cycling_suitability'].startswith('EXCLUDE'):
            excluded_count += 1
            continue
        
        if classification['cycling_suitability'] in ['HIGH_CYCLING_FEATURE', 'MEDIUM_CYCLING_FEATURE']:
            cycling_topics.append({
                **topic,
                **classification,
                'suggested_cycling_title': suggest_cycling_feature_title(topic)
            })
    
    # Sort by cycling feature score and priority
    cycling_topics.sort(
        key=lambda x: (x['cycling_feature_score'], x['priority_score']), 
        reverse=True
    )
    
    print(f"📊 FILTERING RESULTS:")
    print(f"   • Total topics analyzed: {len(topics)}")
    print(f"   • Excluded (non-cycling/theory): {excluded_count}")
    print(f"   • Cycling feature topics: {len(cycling_topics)}")
    print()
    
    # Group by article type
    by_type = {}
    for topic in cycling_topics:
        article_type = topic['article_type']
        if article_type not in by_type:
            by_type[article_type] = []
        by_type[article_type].append(topic)
    
    print("📈 CYCLING FEATURE BREAKDOWN:")
    print("-" * 40)
    for article_type, topics_list in by_type.items():
        print(f"{article_type.replace('_', ' ')}: {len(topics_list)} topics")
    print()
    
    # Show top cycling feature articles
    print("🏆 TOP CYCLING FEATURE ARTICLES:")
    print("-" * 60)
    
    for i, topic in enumerate(cycling_topics[:10], 1):
        print(f"{i:2d}. {topic['suggested_cycling_title']}")
        print(f"    Original: {topic['title']}")
        print(f"    Type: {topic['article_type']} | Priority: {topic['priority_score']}")
        print(f"    Cycling Score: {topic['cycling_feature_score']} | Questions: {topic['question_count']}")
        print(f"    Focus: {', '.join(topic['cycling_reasons'])}")
        print()
    
    # Specific recommendations
    print("🎯 IMMEDIATE CYCLING FEATURE PRIORITIES:")
    print("-" * 50)
    
    # Coach Jack topics
    coach_jack = [t for t in cycling_topics if t['article_type'] == 'COACH_JACK']
    if coach_jack:
        print("**COACH JACK CYCLING FEATURES:**")
        for topic in coach_jack[:2]:
            print(f"  • {topic['suggested_cycling_title']}")
    
    # App features
    app_features = [t for t in cycling_topics if t['article_type'] == 'APP_FEATURES']
    if app_features:
        print("\n**APP CYCLING FEATURES:**")
        for topic in app_features[:2]:
            print(f"  • {topic['suggested_cycling_title']}")
    
    # Integrations
    integrations = [t for t in cycling_topics if t['article_type'] == 'INTEGRATION']
    if integrations:
        print("\n**CYCLING PLATFORM INTEGRATIONS:**")
        for topic in integrations[:2]:
            print(f"  • {topic['suggested_cycling_title']}")
    
    # Workflow features
    workflow = [t for t in cycling_topics if t['article_type'] == 'WORKFLOW']
    if workflow:
        print("\n**CYCLING WORKFLOW FEATURES:**")
        for topic in workflow[:2]:
            print(f"  • {topic['suggested_cycling_title']}")
    
    # Save results
    output_file = f"cycling_features_only_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            'generated_at': datetime.now().isoformat(),
            'focus': 'Cycling-only TrainerDay features',
            'excluded_topics': excluded_count,
            'cycling_topics': len(cycling_topics),
            'by_type': {k: len(v) for k, v in by_type.items()},
            'topics': cycling_topics
        }, f, indent=2, default=str)
    
    print(f"\n📁 Cycling feature strategy: {output_file}")
    
    return cycling_topics

def main():
    """Main execution"""
    print("🚴 CYCLING-FOCUSED TRAINERDAY FEATURES")
    print("=" * 60)
    print("Identifying TrainerDay feature content specifically for cycling")
    print("Pure feature focus - no training theory, no other sports")
    print()
    
    try:
        cycling_topics = generate_cycling_feature_strategy()
        
        if cycling_topics:
            print("\n✅ CYCLING FEATURE STRATEGY COMPLETE!")
            print(f"   • {len(cycling_topics)} cycling feature articles identified")
            print("\n🎯 CONTENT APPROACH:")
            print("   1. Focus on TrainerDay feature functionality")
            print("   2. Cycling-specific workflows and integrations")
            print("   3. App vs web platform differences")
            print("   4. Coach Jack cycling plan features")
            print("   5. Workout management and organization tools")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()