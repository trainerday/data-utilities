#!/usr/bin/env python3
"""
Refined Content Strategy: Solution-Focused Blog Articles

This script filters forum topics to prioritize educational and solution-oriented 
content while avoiding current unresolved technical issues.

Focus Areas:
1. Training methodology and concepts
2. Feature education and best practices  
3. Setup and optimization guides
4. Resolved issue explanations (how we fixed X)

Excludes:
- Active bugs and crashes
- Unresolved technical issues
- Support-ticket style problems
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def load_priority_data():
    """Load the prioritized topics data"""
    # Find the most recent priority file
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

def classify_content_suitability(topic):
    """
    Classify if a topic is suitable for blog content based on:
    - Educational value
    - Solution-oriented nature  
    - Not an active unresolved issue
    """
    
    title = topic['title'].lower()
    sample_questions = topic.get('sample_questions', '').lower()
    category = topic.get('category', '')
    
    # Educational/Training Topics (HIGH SUITABILITY)
    training_indicators = [
        'training', 'vo2max', 'ftp', 'zone', 'coach jack', 
        'plan', 'workout', 'recovery', 'polarized', 'threshold'
    ]
    
    # Feature Education Topics (HIGH SUITABILITY)  
    feature_indicators = [
        'how to', 'setup', 'integration', 'sync', 'export',
        'calendar', 'garmin', 'zwift', 'intervals'
    ]
    
    # Resolved Issue Indicators (MEDIUM SUITABILITY)
    resolved_indicators = ['[solved]', 'fixed', 'resolved', 'how we']
    
    # Current Issue Indicators (LOW SUITABILITY)  
    issue_indicators = [
        'crash', 'error', 'bug', 'not working', 'broken',
        'problem', 'issue', 'help', 'can\'t', 'won\'t'
    ]
    
    # Calculate suitability score
    suitability_score = 0
    reasons = []
    
    # High value content
    if any(indicator in title or indicator in sample_questions for indicator in training_indicators):
        suitability_score += 3
        reasons.append("Training/education content")
        
    if any(indicator in title or indicator in sample_questions for indicator in feature_indicators):
        suitability_score += 2
        reasons.append("Feature education content")
    
    # Resolved issues can be valuable
    if any(indicator in title for indicator in resolved_indicators):
        suitability_score += 1
        reasons.append("Resolved issue - educational value")
    
    # Penalize current issues
    if any(indicator in title or indicator in sample_questions for indicator in issue_indicators):
        if not any(indicator in title for indicator in resolved_indicators):
            suitability_score -= 2
            reasons.append("Current unresolved issue")
    
    # Category-based adjustments
    if category == 'Training Theory' or category == 'Training Execution':
        suitability_score += 1
        reasons.append("Training category bonus")
    elif category == 'Technical Issues' and '[solved]' not in title.lower():
        suitability_score -= 1
        reasons.append("Unresolved technical issue")
    
    # Determine suitability level
    if suitability_score >= 3:
        suitability = "HIGH"
    elif suitability_score >= 1:
        suitability = "MEDIUM" 
    elif suitability_score >= 0:
        suitability = "LOW"
    else:
        suitability = "EXCLUDE"
    
    return {
        'suitability': suitability,
        'score': suitability_score,
        'reasons': reasons
    }

def generate_content_recommendations():
    """Generate refined content recommendations"""
    
    topics = load_priority_data()
    if not topics:
        return
    
    print("\n🎯 REFINED CONTENT STRATEGY ANALYSIS")
    print("=" * 60)
    print("Filtering topics for educational and solution-oriented blog content")
    print()
    
    # Classify all topics
    classified_topics = []
    
    for topic in topics:
        classification = classify_content_suitability(topic)
        
        classified_topics.append({
            **topic,
            **classification
        })
    
    # Sort by suitability and then by priority score
    suitability_order = {'HIGH': 4, 'MEDIUM': 3, 'LOW': 2, 'EXCLUDE': 1}
    
    classified_topics.sort(
        key=lambda x: (suitability_order[x['suitability']], x['priority_score']), 
        reverse=True
    )
    
    # Generate recommendations by suitability
    recommendations = {
        'HIGH': [],
        'MEDIUM': [], 
        'LOW': [],
        'EXCLUDE': []
    }
    
    for topic in classified_topics:
        recommendations[topic['suitability']].append(topic)
    
    # Print results
    print("📊 CONTENT SUITABILITY BREAKDOWN:")
    print("-" * 40)
    for suitability, topics_list in recommendations.items():
        print(f"{suitability}: {len(topics_list)} topics")
    print()
    
    # Show HIGH priority recommendations
    print("🏆 HIGH PRIORITY BLOG ARTICLES (Educational/Solution-Focused):")
    print("-" * 60)
    
    for i, topic in enumerate(recommendations['HIGH'][:10], 1):
        print(f"{i:2d}. {topic['title']}")
        print(f"    Category: {topic['category']} | Priority Score: {topic['priority_score']}")
        print(f"    Suitability Score: {topic['score']} | Reasons: {', '.join(topic['reasons'])}")
        
        # Suggest article approach
        article_approach = suggest_article_approach(topic)
        print(f"    Suggested Approach: {article_approach}")
        print()
    
    # Show MEDIUM priority with caveats
    print("📝 MEDIUM PRIORITY ARTICLES (Review Required):")
    print("-" * 50)
    
    for i, topic in enumerate(recommendations['MEDIUM'][:5], 1):
        print(f"{i:2d}. {topic['title']}")
        print(f"    Reasons: {', '.join(topic['reasons'])}")
        print(f"    ⚠️  Review needed: Check if issue is resolved before creating content")
        print()
    
    # Save refined recommendations
    output_file = f"refined_content_strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            'generated_at': datetime.now().isoformat(),
            'methodology': 'Solution-focused content filtering',
            'recommendations': recommendations
        }, f, indent=2, default=str)
    
    print(f"📁 Refined recommendations saved to: {output_file}")
    
    return recommendations

def suggest_article_approach(topic):
    """Suggest how to approach writing an article for this topic"""
    
    title = topic['title'].lower()
    category = topic['category']
    
    if 'training' in title or 'vo2max' in title or 'zone' in title:
        return "Educational guide: Explain concepts, provide actionable tips"
    elif 'coach jack' in title:
        return "Feature guide: How to use Coach Jack effectively"
    elif '[solved]' in title:
        return "Solution article: Explain the problem and how it was resolved"
    elif 'integration' in title or 'sync' in title:
        return "Setup guide: Step-by-step instructions"
    elif category == 'Training Theory':
        return "Deep-dive explanation with practical examples"
    elif category == 'Feature Requests':
        return "Feature education: Show users how to achieve similar goals"
    else:
        return "General guide: Address user questions with solutions"

def main():
    """Main execution"""
    print("🚀 REFINED CONTENT STRATEGY GENERATOR")
    print("=" * 60)
    print("Filtering forum topics for educational, solution-oriented blog content")
    print("while avoiding current unresolved technical issues.")
    print()
    
    try:
        recommendations = generate_content_recommendations()
        
        if recommendations:
            high_count = len(recommendations['HIGH'])
            medium_count = len(recommendations['MEDIUM'])
            
            print("\n✅ CONTENT STRATEGY COMPLETE!")
            print(f"   • {high_count} HIGH-priority educational articles identified")
            print(f"   • {medium_count} MEDIUM-priority articles (review required)")
            print("\n🎯 RECOMMENDED NEXT STEPS:")
            print("   1. Start with HIGH-priority educational content")
            print("   2. Focus on training concepts and feature guides")
            print("   3. Avoid technical issues unless they're [SOLVED]")
            print("   4. Create solution-oriented, evergreen content")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()