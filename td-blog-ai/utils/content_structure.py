#!/usr/bin/env python3
"""
TrainerDay content structure definitions - categories, engagement levels, and tags
Based on blog/tags-and-categories.md from TD-Business Basic Memory project
"""

# Content Categories with styling and descriptions
CATEGORIES = {
    "Training": {
        "name": "Training",
        "description": "Training methods, techniques, theory",
        "style": {"background": "#dbeafe", "color": "#1e40af"},
        "focus": "Evidence-based training concepts and practical application"
    },
    "Features": {
        "name": "Features", 
        "description": "TrainerDay app features and functionality",
        "style": {"background": "#f3e8ff", "color": "#7c3aed"},
        "focus": "App functionality, user workflows, feature explanations"
    },
    "Indoor": {
        "name": "Indoor",
        "description": "Indoor cycling setup, equipment, basics", 
        "style": {"background": "#ecfdf5", "color": "#059669"},
        "focus": "Equipment setup, troubleshooting, indoor-specific guidance"
    },
    "Other": {
        "name": "Other",
        "description": "Reviews, comparisons, general topics",
        "style": {"background": "#f1f5f9", "color": "#475569"},
        "focus": "Comparative analysis, reviews, general cycling topics"
    }
}

# Engagement Levels with styling and specifications
ENGAGEMENT_LEVELS = {
    "Quick": {
        "name": "Quick",
        "description": "Just tell me how to do it",
        "style": {"background": "#dcfce7", "color": "#16a34a"},
        "length": "800 words",
        "approach": "Direct, actionable steps with minimal theory",
        "structure": "Problem → Solution → Action Steps",
        "forum_indicators": ["how do I", "quick question", "simple", "just need to", "urgent"]
    },
    "Complete": {
        "name": "Complete", 
        "description": "Give me the full picture",
        "style": {"background": "#e0e7ff", "color": "#3730a3"},
        "length": "1200 words",
        "approach": "Comprehensive explanation with practical examples",
        "structure": "Overview → Detailed Explanation → Examples → Implementation",
        "forum_indicators": ["explain", "understand", "best way", "comprehensive", "guide"]
    },
    "Geek-Out": {
        "name": "Geek-Out",
        "description": "I want ALL the details", 
        "style": {"background": "#fee2e2", "color": "#dc2626"},
        "length": "1500+ words",
        "approach": "Technical depth with advanced concepts and nuances",
        "structure": "Background → Technical Details → Advanced Applications → Expert Insights",
        "forum_indicators": ["technical", "advanced", "optimize", "deep dive", "algorithm"]
    }
}

# Tag Groups with individual tags
TAG_GROUPS = {
    "App & Platform": [
        "web-app", "mobile-app", "about-trainerday"
    ],
    "Training Concepts": [
        "training", "indoor-cycling", "time-crunched", "polarized", "zone-2", 
        "heart-rate", "recovery", "w-prime", "ftp"
    ],
    "Features & Tools": [
        "coach-jack", "workout-creator", "plan-creator", "my-workouts", "my-plans", 
        "my-calendar", "WOD", "plans", "organization", "sharing", "export", "dynamic-training"
    ],
    "Equipment & Tech": [
        "equipment", "technology", "speed-distance"
    ],
    "Integrations": [
        "garmin", "zwift", "training-peaks", "intervals-icu", "wahoo"
    ],
    "Activities": [
        "vasa-swim", "rowing"
    ],
    "Content": [
        "reviews", "health", "integrations", "web-trainer"
    ]
}

# Flattened list of all available tags
ALL_TAGS = []
for group_tags in TAG_GROUPS.values():
    ALL_TAGS.extend(group_tags)

def get_category_info(category: str) -> dict:
    """Get complete information about a category"""
    return CATEGORIES.get(category, CATEGORIES["Other"])

def get_engagement_info(engagement: str) -> dict:
    """Get complete information about an engagement level"""
    return ENGAGEMENT_LEVELS.get(engagement, ENGAGEMENT_LEVELS["Complete"])

def suggest_tags_from_content(content: str, max_tags: int = 5) -> list:
    """Suggest tags based on content analysis"""
    content_lower = content.lower()
    suggested = []
    
    # Score tags based on keyword presence
    tag_scores = {}
    for tag in ALL_TAGS:
        score = 0
        tag_words = tag.replace('-', ' ').split()
        
        for word in tag_words:
            if word in content_lower:
                score += content_lower.count(word)
        
        if score > 0:
            tag_scores[tag] = score
    
    # Return top scoring tags
    sorted_tags = sorted(tag_scores.items(), key=lambda x: x[1], reverse=True)
    return [tag for tag, score in sorted_tags[:max_tags]]

def determine_category_from_content(content: str, forum_questions: list = None) -> str:
    """Determine category based on content and forum context"""
    content_lower = content.lower()
    
    # Category keyword mapping
    category_keywords = {
        "Training": ["ftp", "zones", "plan", "coach jack", "training", "workout", "power", "heart rate", "recovery"],
        "Features": ["app", "sync", "calendar", "export", "settings", "how to", "feature", "tool", "creator"],
        "Indoor": ["trainer", "setup", "equipment", "bluetooth", "connection", "indoor", "smart trainer"],
        "Other": ["review", "comparison", "vs", "best", "recommendation"]
    }
    
    # Score each category
    category_scores = {}
    for category, keywords in category_keywords.items():
        score = sum(content_lower.count(keyword) for keyword in keywords)
        category_scores[category] = score
    
    # Add forum context if available
    if forum_questions:
        for question in forum_questions:
            question_text = question.get('content', '').lower()
            for category, keywords in category_keywords.items():
                bonus_score = sum(question_text.count(keyword) for keyword in keywords)
                category_scores[category] += bonus_score * 0.5  # Weight forum context lower
    
    # Return highest scoring category
    if category_scores:
        return max(category_scores, key=category_scores.get)
    
    return "Other"

def determine_engagement_from_forum(forum_questions: list) -> str:
    """Determine engagement level based on forum question patterns"""
    if not forum_questions:
        return "Complete"
    
    engagement_scores = {"Quick": 0, "Complete": 0, "Geek-Out": 0}
    
    for question in forum_questions:
        content = question.get('content', '').lower()
        title = question.get('title', '').lower()
        combined_text = f"{title} {content}"
        
        # Score based on indicators
        for engagement, info in ENGAGEMENT_LEVELS.items():
            for indicator in info['forum_indicators']:
                if indicator in combined_text:
                    engagement_scores[engagement] += 1
    
    # Return highest scoring engagement level
    if sum(engagement_scores.values()) > 0:
        return max(engagement_scores, key=engagement_scores.get)
    
    return "Complete"

def validate_article_structure(article_data: dict) -> dict:
    """Validate article against content structure requirements"""
    issues = []
    
    # Check required fields
    required_fields = ['title', 'category', 'engagement', 'content']
    for field in required_fields:
        if not article_data.get(field):
            issues.append(f"Missing required field: {field}")
    
    # Validate category
    if article_data.get('category') not in CATEGORIES:
        issues.append(f"Invalid category: {article_data.get('category')}")
    
    # Validate engagement level
    if article_data.get('engagement') not in ENGAGEMENT_LEVELS:
        issues.append(f"Invalid engagement level: {article_data.get('engagement')}")
    
    # Validate tags
    invalid_tags = []
    article_tags = article_data.get('tags', [])
    for tag in article_tags:
        if tag not in ALL_TAGS:
            invalid_tags.append(tag)
    
    if invalid_tags:
        issues.append(f"Invalid tags: {', '.join(invalid_tags)}")
    
    # Check word count against engagement level
    content = article_data.get('content', '')
    word_count = len(content.split())
    engagement = article_data.get('engagement')
    
    if engagement and engagement in ENGAGEMENT_LEVELS:
        target_length = ENGAGEMENT_LEVELS[engagement]['length']
        if engagement == "Quick" and word_count > 1000:
            issues.append(f"Article too long for Quick engagement: {word_count} words (target: ~800)")
        elif engagement == "Geek-Out" and word_count < 1200:
            issues.append(f"Article too short for Geek-Out engagement: {word_count} words (target: 1500+)")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "suggestions": {
            "category": determine_category_from_content(content),
            "tags": suggest_tags_from_content(content)
        }
    }

if __name__ == "__main__":
    # Test the content structure functions
    print("📋 TrainerDay Content Structure")
    print("=" * 40)
    
    print(f"Categories: {list(CATEGORIES.keys())}")
    print(f"Engagement Levels: {list(ENGAGEMENT_LEVELS.keys())}")
    print(f"Tag Groups: {list(TAG_GROUPS.keys())}")
    print(f"Total Tags: {len(ALL_TAGS)}")
    
    # Test tag suggestion
    test_content = "How to set up your smart trainer with TrainerDay app and sync with Garmin"
    suggested = suggest_tags_from_content(test_content)
    print(f"\nSuggested tags for test content: {suggested}")
    
    # Test category determination
    category = determine_category_from_content(test_content)
    print(f"Suggested category: {category}")