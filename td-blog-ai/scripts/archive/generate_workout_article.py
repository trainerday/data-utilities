#!/usr/bin/env python3
"""
Generate Comprehensive Workout Features Article using Claude API
"""

import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import anthropic

load_dotenv()

def generate_workout_article():
    """Generate a comprehensive article about TrainerDay workout features"""
    
    # Load the JSON data
    json_file = Path("./script-testing/workout_query_results/comprehensive_workout_features.json")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        workout_data = json.load(f)
    
    # Initialize Claude client
    client = anthropic.Anthropic(
        api_key=os.getenv('ANTHROPIC_API_KEY')
    )
    
    # Create the prompt
    prompt = f"""You are a professional technical writer creating a comprehensive article about TrainerDay's workout features. 

Using the following JSON data about TrainerDay's workout capabilities, create a detailed, well-structured article that:

1. Provides an engaging introduction to TrainerDay's workout system
2. Organizes features into logical sections with clear headings
3. Explains each feature in detail with practical examples
4. Highlights unique capabilities and benefits
5. Uses a professional yet accessible tone
6. Includes use cases and scenarios where each feature shines
7. Creates a cohesive narrative that shows how features work together
8. Concludes with a summary of TrainerDay's comprehensive workout ecosystem

The article should be approximately 3000-4000 words and suitable for both beginners and experienced cyclists.

JSON Data:
{json.dumps(workout_data, indent=2)}

Please write the comprehensive article in markdown format."""

    print("📝 Generating comprehensive workout features article...")
    print("⏳ This may take a moment...")
    
    # Generate the article
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=8000,
        temperature=0.7,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    
    # Extract the article content
    article_content = response.content[0].text
    
    # Save the article
    output_dir = Path("./script-testing/workout_query_results")
    output_file = output_dir / f"trainerday_workout_features_article_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(article_content)
    
    print(f"✅ Article generated successfully!")
    print(f"📄 Saved to: {output_file}")
    print(f"📊 Article length: {len(article_content.split())} words")
    
    # Also save a preview
    preview_lines = article_content.split('\n')[:50]
    print("\n📖 Article Preview:")
    print("=" * 80)
    print('\n'.join(preview_lines))
    print("=" * 80)
    print("\n... (article continues)")
    
    return output_file

if __name__ == "__main__":
    generate_workout_article()