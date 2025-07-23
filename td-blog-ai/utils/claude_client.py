#!/usr/bin/env python3
"""
Claude Sonnet 4 client for article generation
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class ClaudeClient:
    def __init__(self):
        self.client = Anthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        
    def generate_article(self, prompt: str, max_tokens: int = 8000) -> str:
        """Generate article using Claude Sonnet 4"""
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",  # Sonnet 4
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            print(f"❌ Claude API error: {e}")
            return None
    
    def test_connection(self):
        """Test Claude API connection"""
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=100,
                messages=[
                    {
                        "role": "user", 
                        "content": "Hello! This is a test. Please respond with 'Claude Sonnet 4 is working correctly.'"
                    }
                ]
            )
            
            result = response.content[0].text
            print(f"✅ Claude API connection successful!")
            print(f"Response: {result}")
            return True
            
        except Exception as e:
            print(f"❌ Claude API connection failed: {e}")
            return False

def create_article_prompt(topic: str, category: str, engagement: str, research_data: dict, suggested_tags: list = None) -> str:
    """Create comprehensive prompt for article generation"""
    
    # Category specifications with styles
    category_specs = {
        "Training": {
            "description": "Training methodology, periodization, performance analysis",
            "style": "Blue theme (#dbeafe background, #1e40af text)",
            "focus": "Evidence-based training concepts and practical application"
        },
        "Features": {
            "description": "TrainerDay app features and functionality",
            "style": "Purple theme (#f3e8ff background, #7c3aed text)", 
            "focus": "App functionality, user workflows, feature explanations"
        },
        "Indoor": {
            "description": "Indoor cycling setup, equipment, basics",
            "style": "Green theme (#ecfdf5 background, #059669 text)",
            "focus": "Equipment setup, troubleshooting, indoor-specific guidance"
        },
        "Other": {
            "description": "Reviews, comparisons, general topics", 
            "style": "Gray theme (#f1f5f9 background, #475569 text)",
            "focus": "Comparative analysis, reviews, general cycling topics"
        }
    }
    
    # Engagement level specifications
    engagement_specs = {
        "Quick": {
            "length": "800 words",
            "style": "Direct, actionable steps with minimal theory", 
            "structure": "Problem → Solution → Action Steps",
            "theme": "Green theme (#dcfce7 background, #16a34a text)",
            "approach": "Just tell me how to do it"
        },
        "Complete": {
            "length": "1200 words",
            "style": "Comprehensive explanation with practical examples",
            "structure": "Overview → Detailed Explanation → Examples → Implementation", 
            "theme": "Blue theme (#e0e7ff background, #3730a3 text)",
            "approach": "Give me the full picture"
        },
        "Geek-Out": {
            "length": "1500+ words",
            "style": "Technical depth with advanced concepts and nuances",
            "structure": "Background → Technical Details → Advanced Applications → Expert Insights",
            "theme": "Red theme (#fee2e2 background, #dc2626 text)", 
            "approach": "I want ALL the details"
        }
    }
    
    category_spec = category_specs.get(category, category_specs["Other"])
    engagement_spec = engagement_specs.get(engagement, engagement_specs["Complete"])
    
    tags_section = ""
    if suggested_tags:
        tags_section = f"""
**Suggested Tags (select 3-5 most relevant):**
{', '.join([f'#{tag}' for tag in suggested_tags])}
"""

    prompt = f"""Write a TrainerDay blog article about: {topic}

**Article Specifications:**
- Category: {category} ({category_spec['description']})
- Category Focus: {category_spec['focus']}
- Engagement Level: {engagement} ({engagement_spec['approach']})
- Target Length: {engagement_spec['length']}
- Writing Style: {engagement_spec['style']}
- Structure: {engagement_spec['structure']}

**Research Context:**

User Questions from Forum:
{format_forum_content(research_data.get('forum_results', []))}

Related Existing Content:
{format_blog_content(research_data.get('blog_results', []))}

Video Context:
{format_youtube_content(research_data.get('youtube_results', []))}

**TrainerDay Voice Guidelines:**
- Write in Alex's direct, practical voice
- Use cycling terminology naturally (FTP, TSS, power zones, etc.)
- Address real user pain points from forum discussions
- Explain complex concepts simply
- Focus on actionable insights over theory
- Reference specific TrainerDay features when relevant
- Avoid marketing speak - be genuine and helpful

**Content Requirements:**
- Engaging introduction that addresses the user problem from forum discussions
- Clear sections with practical subheadings matching {engagement} engagement level
- Include specific examples from TrainerDay app/features
- Address common misconceptions or confusion points found in forum
- Provide actionable takeaways and next steps
- End with encouragement and community connection

{tags_section}

**Format Requirements:**
Return the article in markdown format with:
- Title (H1)
- Category: {category}
- Engagement: {engagement}
- Clear section headers (H2, H3) 
- Bullet points and numbered lists where appropriate
- Emphasis on key points
- Frontmatter with category, engagement, and suggested tags

**Tag Guidelines:**
Choose tags from these groups based on article content:
- App & Platform: web-app, mobile-app, about-trainerday
- Training Concepts: training, indoor-cycling, time-crunched, polarized, zone-2, heart-rate, recovery, w-prime, ftp
- Features & Tools: coach-jack, workout-creator, plan-creator, my-workouts, my-plans, my-calendar, WOD, plans, organization, sharing, export, dynamic-training
- Equipment & Tech: equipment, technology, speed-distance
- Integrations: garmin, zwift, training-peaks, intervals-icu, wahoo
- Activities: vasa-swim, rowing
- Content: reviews, health, integrations, web-trainer

Write as if you are Alex from TrainerDay, speaking directly to cyclists who want practical, actionable advice that matches their forum question complexity level."""

    return prompt

def format_forum_content(forum_results: list) -> str:
    """Format forum Q&A results for prompt"""
    if not forum_results:
        return "No relevant forum discussions found."
    
    formatted = []
    for i, result in enumerate(forum_results[:10], 1):  # Limit to top 10
        formatted.append(f"{i}. Q: {result.get('title', 'Unknown')}")
        formatted.append(f"   Content: {result.get('content', '')[:200]}...")
        formatted.append("")
    
    return "\n".join(formatted)

def format_blog_content(blog_results: list) -> str:
    """Format existing blog content for prompt"""
    if not blog_results:
        return "No related existing content found."
    
    formatted = []
    for i, result in enumerate(blog_results[:8], 1):  # Limit to top 8
        formatted.append(f"{i}. {result.get('title', 'Unknown')}")
        formatted.append(f"   Excerpt: {result.get('content', '')[:150]}...")
        formatted.append("")
    
    return "\n".join(formatted)

def format_youtube_content(youtube_results: list) -> str:
    """Format YouTube content for prompt"""
    if not youtube_results:
        return "No relevant video content found."
    
    formatted = []
    for i, result in enumerate(youtube_results[:6], 1):  # Limit to top 6
        formatted.append(f"{i}. {result.get('title', 'Unknown')}")
        formatted.append(f"   Context: {result.get('content', '')[:150]}...")
        if 'video_id' in result.get('metadata', {}):
            formatted.append(f"   Video: https://www.youtube.com/watch?v={result['metadata']['video_id']}")
        formatted.append("")
    
    return "\n".join(formatted)

if __name__ == "__main__":
    client = ClaudeClient()
    client.test_connection()