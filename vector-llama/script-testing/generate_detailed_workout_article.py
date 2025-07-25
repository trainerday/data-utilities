#!/usr/bin/env python3
"""
Generate detailed workout article with extensive quotes from actual content
"""

import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class DetailedWorkoutArticle:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Load the comprehensive content
        content_file = Path("./script-testing/workout_query_results/comprehensive_workout_content.json")
        with open(content_file, 'r', encoding='utf-8') as f:
            self.content = json.load(f)
    
    def extract_key_content(self):
        """Extract the most important content pieces"""
        
        key_content = {
            'fastest_editor': None,
            'sets_reps': None,
            'interval_comments': None,
            'modes': None,
            'wbal': None,
            'facts': [],
            'forum_issues': []
        }
        
        # Get the full blog articles
        for article in self.content['raw_content']['blog']:
            title = article.get('title', '').lower()
            
            if 'fastest workout editor' in title:
                key_content['fastest_editor'] = article['text']
            elif 'sets reps editor' in title:
                key_content['sets_reps'] = article['text']
            elif 'interval comments' in title:
                key_content['interval_comments'] = article['text']
            elif 'mixing and matching' in title:
                key_content['modes'] = article['text']
            elif "w'bal" in title or 'perfect interval' in title:
                key_content['wbal'] = article['text']
        
        # Get key facts
        for fact in self.content['raw_content']['facts']:
            text = fact.get('text', '')
            if any(keyword in text.lower() for keyword in ['workout', 'editor', 'interval', 'sets', 'reps']):
                key_content['facts'].append(text)
        
        # Get forum issues
        for forum in self.content['raw_content']['forum'][:30]:
            if 'issue' in forum.get('title', '').lower() or 'problem' in forum.get('title', '').lower():
                key_content['forum_issues'].append({
                    'title': forum['title'],
                    'content': forum['text'][:500]
                })
        
        return key_content
    
    def create_detailed_prompt(self):
        """Create a very detailed prompt with extensive content"""
        
        content = self.extract_key_content()
        
        prompt = """You are Alex, founder of TrainerDay, writing a comprehensive guide about workout creation features.

IMPORTANT: Use extensive quotes and specific details from the provided content. This should be a detailed reference guide.

# CONTENT TO USE:

## 1. THE FASTEST WORKOUT EDITOR
{fastest_editor_content}

## 2. SETS AND REPS EDITOR
{sets_reps_content}

## 3. INTERVAL COMMENTS
{interval_comments_content}

## 4. TRAINING MODES
{modes_content}

## 5. W'BAL AND ADVANCED FEATURES
{wbal_content}

## 6. KEY FACTS ABOUT FEATURES
{facts_list}

## 7. COMMON USER ISSUES
{issues_list}

# INSTRUCTIONS:

Write a comprehensive 2500-3000 word guide that:

1. **Introduction** (200 words)
   - Explain TrainerDay's approach to workout creation
   - Mention the Excel-like speed focus

2. **The Fastest Workout Editor** (400 words)
   - Quote directly from the blog: "Designed for one thing. Speed."
   - Explain the Excel-like functionality in detail
   - Include the keyboard shortcuts and copy/paste features
   - Mention the 30-second video

3. **Sets and Reps Editor** (400 words)
   - Use the specific example from the blog about the long workout
   - Explain how it simplifies complex intervals
   - Include the visual comparison mentioned

4. **Interval Comments** (300 words)
   - Explain current ZWO file support for Zwift
   - Mention future platform support plans
   - Include how to delete comments

5. **Training Modes** (500 words)
   - Detail ERG, Slope, Resistance, and HR modes
   - Explain automatic mode switching
   - Include specific use cases for each mode

6. **Workout Cloning and Management** (300 words)
   - Explain the Alt/Option drag feature
   - Discuss workout library management
   - Include user feedback about this feature

7. **Advanced Features: W'bal** (400 words)
   - Explain progressive overload concept
   - Detail how W'bal helps design perfect intervals
   - Include the mathematical example if present

8. **Common Issues and Solutions** (300 words)
   - List specific issues users have reported
   - Provide solutions mentioned in forums
   - Be honest about known limitations

9. **Best Practices** (200 words)
   - Summarize key tips for using the editor effectively
   - Include workflow recommendations

Use direct quotes, specific examples, and detailed explanations throughout. This should be the definitive guide to workout creation in TrainerDay.
""".format(
            fastest_editor_content=content['fastest_editor'] or "Content not found",
            sets_reps_content=content['sets_reps'] or "Content not found",
            interval_comments_content=content['interval_comments'] or "Content not found",
            modes_content=content['modes'] or "Content not found",
            wbal_content=content['wbal'] or "Content not found",
            facts_list="\n".join([f"- {fact}" for fact in content['facts'][:20]]),
            issues_list="\n".join([f"**{issue['title']}**\n{issue['content']}\n" for issue in content['forum_issues'][:5]])
        )
        
        return prompt
    
    def generate_article(self):
        """Generate the detailed article"""
        
        print("📊 Extracting key content...")
        prompt = self.create_detailed_prompt()
        
        # Save prompt for review
        prompt_file = Path("./script-testing/workout_articles/detailed_prompt.txt")
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
        print(f"💾 Prompt saved to: {prompt_file}")
        
        print("🤖 Generating detailed article...")
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are Alex, founder of TrainerDay. Write in first person, conversational style."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        article = response.choices[0].message.content
        
        # Save article
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = Path(f"./script-testing/workout_articles/workout_features_detailed_{timestamp}.md")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(article)
        
        print(f"\n✅ Detailed article saved to: {output_file}")
        print(f"📄 Article length: {len(article)} characters")
        print(f"📝 Word count: {len(article.split())} words")

if __name__ == "__main__":
    generator = DetailedWorkoutArticle()
    generator.generate_article()