#!/usr/bin/env python3
"""
Generate Comprehensive Workout Features Article using OpenAI API
"""

import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def generate_workout_article():
    """Generate a comprehensive article about TrainerDay workout features"""
    
    # Load the JSON data
    json_file = Path("./script-testing/workout_query_results/comprehensive_workout_features.json")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        workout_data = json.load(f)
    
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Prepare a condensed version of the data focusing on the feature categories
    condensed_data = {
        "metadata": workout_data["metadata"],
        "feature_categories": workout_data["feature_categories"]
    }
    
    # Create the prompt
    prompt = f"""You are a professional technical writer creating a comprehensive article about TrainerDay's workout features. 

Using the following data about TrainerDay's workout capabilities, create a detailed, well-structured article that:

1. Provides an engaging introduction to TrainerDay's workout system
2. Organizes features into logical sections with clear headings
3. Explains each feature in detail with practical examples
4. Highlights unique capabilities and benefits
5. Uses a professional yet accessible tone
6. Includes use cases and scenarios where each feature shines
7. Creates a cohesive narrative that shows how features work together
8. Concludes with a summary of TrainerDay's comprehensive workout ecosystem

The article should be comprehensive and suitable for both beginners and experienced cyclists.

Feature Data:
{json.dumps(condensed_data, indent=2)}

Please write the comprehensive article in markdown format. Make it detailed and thorough, covering all features comprehensively."""

    print("📝 Generating comprehensive workout features article...")
    print("⏳ This may take a moment...")
    
    # Generate the article
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system", 
                "content": "You are an expert technical writer specializing in fitness technology and cycling training platforms."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=4000
    )
    
    # Extract the article content
    article_content = response.choices[0].message.content
    
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