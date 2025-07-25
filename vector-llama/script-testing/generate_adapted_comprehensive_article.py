#!/usr/bin/env python3
"""
Generate Comprehensive Workout Features Article with Adapted Template
Using the style from individual-article-prompt-template.txt
"""

import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()

def generate_adapted_article():
    """Generate comprehensive article using adapted template style"""
    
    # Load the workout features JSON
    json_file = Path("./script-testing/workout_query_results/comprehensive_workout_features.json")
    with open(json_file, 'r', encoding='utf-8') as f:
        workout_data = json.load(f)
    
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Create adapted prompt based on the template
    prompt = """You are Alex, writing a comprehensive feature guide for TrainerDay users. Write in your natural, conversational blog voice - personal but not overly formal. You interact directly with users and understand their challenges.

ARTICLE CONTEXT:
Title: The Complete TrainerDay Workout Features Guide
Category: Features/Documentation
Article Type: Comprehensive Feature Documentation
Target Length: Comprehensive (5000+ words - this is the complete guide)

YOUR TASK:
Create a comprehensive guide covering ALL TrainerDay workout features, organized by the categories in the JSON data below. This is the definitive reference for users.

FEATURE DATA TO DOCUMENT:
{json_data}

CRITICAL CONSTRAINTS:
- ONLY describe features that are explicitly listed in the JSON data
- DO NOT invent any features, capabilities, or technical details not in the source
- Use the exact feature names and descriptions from the JSON
- Base explanations on the key_features and use_cases provided
- This is a comprehensive guide, so cover EVERY feature listed

WRITING STYLE GUIDELINES:
- Write in a conversational blog tone - helpful, direct, with subtle personality
- Vary your approach for different features - some technical, some practical
- Be thorough but accessible - explain complex features clearly
- Use real-world examples and scenarios where they help clarify usage
- Keep technical accuracy while maintaining readability
- Group related features logically within each category

TONE GUIDELINES:
- Present features matter-of-factly with enthusiasm for their capabilities
- Use natural language like "This lets you...", "You can...", "This works by..."
- Be encouraging about feature possibilities
- Avoid marketing speak - just explain what things do and how they help

ARTICLE STRUCTURE:
1. **Brief Introduction** - What this guide covers, who it's for
2. **Feature Categories** - Use the exact categories from the JSON:
   - Workout Creation & Management
   - Training Modes
   - Training Execution & Real-time Features
   - Real-time Display & Monitoring
   - Workout Library & Discovery
   - Workout Export & Integration
   - Workout Organization & Management
   - Community & Sharing Features

For EACH FEATURE within categories:
- Feature name (as heading)
- What it does (from description)
- Key capabilities (from key_features)
- When/how to use it (from use_cases)
- Practical tips or examples (where helpful)

IMPORTANT GUIDELINES:
- Cover EVERY feature in the JSON data
- Don't add features not in the source
- Keep explanations clear and practical
- Use the exact terminology from the JSON
- Make it comprehensive but readable
- Group related features for better flow

Write the complete comprehensive article based on the JSON data provided. Make it the definitive reference for TrainerDay workout features.""".format(
        json_data=json.dumps(workout_data['feature_categories'], indent=2)
    )
    
    print("📝 Generating comprehensive workout features article with adapted style...")
    print("⏳ This may take a moment due to the comprehensive nature...")
    
    # Generate the article
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system", 
                "content": "You are Alex, the founder of TrainerDay, writing in a conversational, helpful blog style."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=8000
    )
    
    # Extract the article content
    article_content = response.choices[0].message.content
    
    # Save the article
    output_dir = Path("./script-testing/workout_query_results")
    output_file = output_dir / f"trainerday_comprehensive_features_adapted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(article_content)
    
    print(f"✅ Article generated successfully!")
    print(f"📄 Saved to: {output_file}")
    print(f"📊 Article length: {len(article_content.split())} words")
    print(f"🎯 Style: Adapted from individual article template")
    
    # Show preview
    preview_lines = article_content.split('\n')[:30]
    print("\n📖 Article Preview:")
    print("=" * 80)
    print('\n'.join(preview_lines))
    print("=" * 80)
    print("\n... (article continues)")
    
    return output_file

if __name__ == "__main__":
    generate_adapted_article()