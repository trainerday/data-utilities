#!/usr/bin/env python3
"""
Generate Features Table from Complete Features

Takes the complete-features.md file and processes it through Claude Sonnet 4 to generate
a proper markdown table of feature articles with:
- Proper page/category tags
- Appropriate "How does X work" questions
- Feature-focused titles
- Engagement levels
"""

import os
import sys
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_complete_features():
    """Load the complete-features.md file"""
    features_file = Path("/Users/alex/Documents/bm-projects/TD-Business/blog/in-progress/complete-features.md")
    
    if not features_file.exists():
        print(f"Error: {features_file} not found")
        return None
    
    with open(features_file, 'r', encoding='utf-8') as f:
        return f.read()

def generate_features_table(complete_features_content):
    """Use Claude Sonnet 4 to convert the features into a proper table"""
    
    client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    prompt = f"""
You are helping create a features article list for TrainerDay's AI content generation system. 

I have a comprehensive features document that lists all the actual features and capabilities of TrainerDay. I need you to convert this into a markdown table format for generating "How to use" articles.

Here's the complete features document:

{complete_features_content}

Please create a markdown table with these columns:
- # (sequential numbering starting from 1)  
- Include (set all to "yes" for now)
- Article Title (format: "How to Use [Feature Name]" or "Guide to [Feature Name]")
- Engagement (use "Complete" for complex features, "Quick" for simple ones)
- Tags (use page/section names like `my-calendar`, `coach-jack`, `workout-creator`, etc.)
- User Question/Pain Point (format: "How does [feature] work?" or "How do I use [feature]?")

Important guidelines:
1. Focus on major user-facing features, not technical details
2. Group related features logically by the main page/section they appear in
3. Use appropriate tags that match TrainerDay's interface sections
4. Make titles actionable and user-focused
5. Prioritize features that users would actually want to learn about
6. Skip highly technical features like APIs or infrastructure
7. Each row should represent one learnable feature/capability

Aim for 50-100 feature articles covering the main user-facing capabilities.

Return only the markdown table, starting with the header row.
"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514", 
            max_tokens=8000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
        
    except Exception as e:
        print(f"Error calling Claude API: {e}")
        return None

def save_features_table(table_content):
    """Save the generated table to a new features file"""
    
    header = """# TrainerDay AI Articles - Features (Generated from Complete Features)

Articles focused on how-to guides, feature explanations, setup guides, and platform functionality.

"""
    
    full_content = header + table_content
    
    output_file = Path("/Users/alex/Documents/bm-projects/TD-Business/blog/in-progress/ai-articles-features-generated.md")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_content)
    
    print(f"✅ Generated features table saved to: {output_file}")
    return output_file

def main():
    print("🎯 GENERATING FEATURES TABLE FROM COMPLETE FEATURES")
    print("=" * 60)
    
    # Load complete features document
    print("📖 Loading complete-features.md...")
    complete_features = load_complete_features()
    if not complete_features:
        sys.exit(1)
    
    print(f"   Loaded {len(complete_features)} characters of feature data")
    
    # Generate features table using Claude
    print("🤖 Processing through Claude Sonnet 4...")
    features_table = generate_features_table(complete_features)
    if not features_table:
        print("❌ Failed to generate features table")
        sys.exit(1)
    
    print(f"   Generated {len(features_table)} characters of table content")
    
    # Save the results
    print("💾 Saving generated features table...")
    output_file = save_features_table(features_table)
    
    print()
    print("🎉 SUCCESS! Features table generated from complete features list")
    print(f"📄 Output file: {output_file}")
    print()
    print("Next steps:")
    print("1. Review the generated table for accuracy")
    print("2. Adjust tags and engagement levels as needed") 
    print("3. Replace the current ai-articles-features.md if satisfied")
    print("4. Generate articles using the new feature-focused list")

if __name__ == "__main__":
    main()