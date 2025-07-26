#!/usr/bin/env python3
"""
Generate final comprehensive workout article using all queried content
"""

import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

class FinalWorkoutArticleGenerator:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Load results
        results_file = Path("./script-testing/workout_comprehensive_results/all_workout_features_20250725_200223.json")
        with open(results_file, 'r', encoding='utf-8') as f:
            self.all_results = json.load(f)
    
    def extract_key_quotes(self):
        """Extract the most important quotes and examples"""
        
        key_quotes = {
            "philosophy": "",
            "excel_like": "",
            "sets_reps": "",
            "interval_comments": "",
            "w_bal": "",
            "modes": "",
            "user_questions": []
        }
        
        # Find key content
        for category, features in self.all_results.items():
            for feature_name, results in features.items():
                for result in results:
                    text = result['text']
                    
                    # Philosophy quote
                    if "Designed for one thing. Speed." in text:
                        key_quotes["philosophy"] = text[:500]
                    
                    # Excel-like functionality
                    if "works just like Excel" in text:
                        key_quotes["excel_like"] = text[:600]
                    
                    # Sets and Reps
                    if "Sets and Reps editor" in text and "hard workout" in text:
                        key_quotes["sets_reps"] = text[:800]
                    
                    # Interval comments
                    if "interval comments" in text.lower() and result['source'] == 'blog':
                        key_quotes["interval_comments"] = text[:500]
                    
                    # W'bal
                    if "W'bal" in text and "anaerobic" in text:
                        key_quotes["w_bal"] = text[:600]
                    
                    # Training modes
                    if "automatically switch" in text and "ERG" in text:
                        key_quotes["modes"] = text[:500]
                    
                    # User questions
                    if result['source'] == 'forum' and "Question:" in text and len(key_quotes["user_questions"]) < 5:
                        key_quotes["user_questions"].append(text[:400])
        
        return key_quotes
    
    def generate_article(self):
        """Generate the complete article"""
        
        print("🔍 Extracting key quotes and examples...")
        key_quotes = self.extract_key_quotes()
        
        # Count features by category
        feature_counts = {cat: len(features) for cat, features in self.all_results.items()}
        
        # Build comprehensive prompt
        prompt = f"""Write a comprehensive guide about TrainerDay's workout features (3500-4000 words).

STATISTICS:
- {sum(feature_counts.values())} distinct features across {len(feature_counts)} categories
- 854 pieces of content from our knowledge base

KEY QUOTES TO INCORPORATE:

PHILOSOPHY:
{key_quotes['philosophy']}

EXCEL-LIKE EDITOR:
{key_quotes['excel_like']}

SETS AND REPS:
{key_quotes['sets_reps']}

TRAINING MODES:
{key_quotes['modes']}

W'BAL FEATURE:
{key_quotes['w_bal']}

USER QUESTIONS:
{chr(10).join(key_quotes['user_questions'][:3])}

ARTICLE STRUCTURE:
1. Introduction (400 words)
   - Personal story as founder
   - Philosophy: "Designed for one thing. Speed."
   - Overview of what makes TrainerDay unique

2. The Fastest Workout Editor (800 words)
   - Excel-like functionality with specific examples
   - Visual editor capabilities
   - Sets and Reps editor for complex workouts
   - Copy/paste workflow examples
   - Real user feedback

3. Advanced Workout Features (800 words)
   - Interval comments and coaching notes
   - W'bal integration for anaerobic capacity
   - Route importing from GPS files
   - Mixed-mode workouts
   - Free ride intervals

4. Training Modes Explained (600 words)
   - ERG mode for power control
   - HR+ mode for heart rate training
   - Slope mode for gradient simulation
   - Resistance mode for sprints
   - Auto-mode switching

5. Real-time Training & Execution (500 words)
   - 6-second warmup feature
   - Dynamic workout editing
   - Power adjustments on the fly
   - Hot swap feature
   - Display options

6. Workout Library & Integration (600 words)
   - 30,000+ open-source workouts
   - Search and filtering
   - Multi-format export (TCX, ZWO, MRC, ERG)
   - Platform integrations (Garmin, TrainingPeaks, Zwift)

7. Conclusion (300 words)
   - Summary of key benefits
   - Getting started guide
   - Community and support

WRITING REQUIREMENTS:
- Write as Alex (first person), founder of TrainerDay
- Conversational but authoritative tone
- Use specific quotes and examples from the content provided
- Include practical use cases for each feature
- Reference actual user questions and feedback
- Explain technical features in accessible terms
- Build a narrative that shows how features work together
- Be thorough and comprehensive - this is the definitive guide"""

        print("🤖 Generating comprehensive article...")
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are Alex, founder of TrainerDay. Write a comprehensive, detailed guide using the specific quotes and examples provided. Be thorough and aim for the full word count."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4096
        )
        
        article = response.choices[0].message.content
        
        # Save the article
        output_dir = Path("./script-testing/workout_articles")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f"final_comprehensive_workout_features_{timestamp}.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(article)
        
        print(f"\n✅ Article saved to: {output_file}")
        print(f"📄 Article length: {len(article)} characters")
        print(f"📝 Word count: {len(article.split())} words")
        
        return output_file

if __name__ == "__main__":
    generator = FinalWorkoutArticleGenerator()
    generator.generate_article()