#!/usr/bin/env python3
"""
Generate comprehensive workout article section by section for better length control
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

class ComprehensiveWorkoutArticleGeneratorV2:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'trainerday_local',
            'user': os.getenv('USER', 'alex'),
            'password': '',
        }
        
        # Load the comprehensive query results
        results_file = Path("./script-testing/workout_comprehensive_results/all_workout_features_20250725_200223.json")
        with open(results_file, 'r', encoding='utf-8') as f:
            self.all_results = json.load(f)
    
    def get_full_blog_content(self, text_snippet):
        """Get full blog article content from database"""
        conn = psycopg2.connect(**self.db_config)
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT text, metadata_->>'title' as title
                    FROM llamaindex_knowledge_base
                    WHERE metadata_->>'source' = 'blog'
                    AND text LIKE %s
                    ORDER BY LENGTH(text) DESC
                    LIMIT 1
                """, (f"{text_snippet[:100]}%",))
                
                result = cur.fetchone()
                if result:
                    return result['text'], result['title']
        finally:
            conn.close()
        
        return text_snippet, None
    
    def generate_introduction(self):
        """Generate comprehensive introduction section"""
        
        # Collect key facts and stats
        total_features = sum(len(features) for features in self.all_results.values())
        
        # Get the fastest workout editor content
        editor_content = ""
        for feature, results in self.all_results.get("Workout Creation & Management", {}).items():
            if "Fastest Workout Editor" in feature:
                for r in results:
                    if r['source'] == 'blog' and "Designed for one thing" in r['text']:
                        editor_content = r['text'][:1000]
                        break
        
        prompt = f"""Write a comprehensive introduction (600-800 words) for an article about TrainerDay's workout features.

CONTEXT:
- {total_features} distinct workout features
- 854 pieces of content from knowledge base
- Core philosophy: "Designed for one thing. Speed."
- Excel-like workout editor
- 30,000+ open-source workouts

KEY CONTENT TO REFERENCE:
{editor_content}

REQUIREMENTS:
- Write as Alex (first person), founder of TrainerDay
- Conversational but informative tone
- Cover: philosophy, what makes TrainerDay unique, overview of major feature categories
- Include specific examples and quotes
- Build excitement about the features to come
- Mention the journey from concept to implementation
- Reference user feedback and community growth"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are Alex, founder of TrainerDay. Write in first person with authority and passion."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    def generate_workout_creation_section(self):
        """Generate comprehensive workout creation section"""
        
        features = self.all_results.get("Workout Creation & Management", {})
        
        # Collect all relevant content
        content_examples = []
        
        # Visual Editor content
        for result in features.get("Visual Workout Editor", [])[:5]:
            if result['source'] == 'blog':
                full_text, title = self.get_full_blog_content(result['text'])
                content_examples.append(f"BLOG - {title}:\n{full_text[:800]}")
            elif result['source'] == 'facts':
                content_examples.append(f"FACT: {result['text']}")
        
        # Sets and Reps content
        for result in features.get("Sets and Reps Editor", [])[:3]:
            if result['source'] == 'blog' and "hard workout" in result['text']:
                content_examples.append(f"\nSETS AND REPS EXAMPLE:\n{result['text'][:600]}")
        
        # Forum discussions
        for result in features.get("Visual Workout Editor", []):
            if result['source'] == 'forum' and "Question:" in result['text']:
                content_examples.append(f"\nUSER QUESTION:\n{result['text'][:400]}")
        
        prompt = f"""Write a comprehensive section about Workout Creation & Management features (1000-1200 words).

FEATURES TO COVER:
1. Visual Workout Editor (Excel-like functionality)
2. Fastest Workout Editor philosophy
3. Sets and Reps Editor
4. Interval Comments
5. Route Importing
6. Target Modes
7. W'bal Integration

CONTENT TO USE:
{chr(10).join(content_examples[:8])}

REQUIREMENTS:
- Write as Alex (first person)
- Use specific quotes and examples from the content
- Explain not just WHAT each feature does but WHY it matters
- Include practical use cases
- Reference user feedback where available
- Use subsections with clear headings
- Be detailed and thorough"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are Alex, founder of TrainerDay. Write detailed, informative content using the provided examples."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    
    def generate_training_modes_section(self):
        """Generate comprehensive training modes section"""
        
        features = self.all_results.get("Training Modes", {})
        
        content_examples = []
        
        # Collect mode-specific content
        for mode in ["ERG Mode", "HR+ Mode", "Slope Mode", "Resistance Mode"]:
            mode_results = features.get(mode, [])
            for result in mode_results[:3]:
                if result['source'] in ['blog', 'facts']:
                    content_examples.append(f"{mode.upper()} - {result['source']}:\n{result['text'][:400]}")
        
        # Add auto-switching content
        switching_content = self.all_results.get("Workout Creation & Management", {}).get("Auto-Mode Switching", [])
        for result in switching_content[:2]:
            if "automatically switch" in result['text']:
                content_examples.append(f"\nAUTO-SWITCHING:\n{result['text'][:500]}")
        
        prompt = f"""Write a comprehensive section about Training Modes (800-1000 words).

MODES TO COVER:
1. ERG Mode - automatic power control
2. HR+ Mode - heart rate controlled training
3. Slope Mode - gradient simulation
4. Resistance Mode - fixed resistance
5. Auto-Mode Switching

CONTENT TO USE:
{chr(10).join(content_examples[:10])}

REQUIREMENTS:
- Write as Alex (first person)
- Explain technical concepts in accessible terms
- Include when to use each mode
- Provide real-world training scenarios
- Explain the benefits of automatic mode switching
- Use specific examples from the content"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are Alex, founder of TrainerDay. Explain technical features clearly."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1200
        )
        
        return response.choices[0].message.content
    
    def generate_full_article(self):
        """Generate the complete article section by section"""
        
        print("📝 Generating comprehensive workout article...")
        
        sections = []
        
        print("  1️⃣ Generating introduction...")
        intro = self.generate_introduction()
        sections.append(("# The Complete Guide to TrainerDay Workout Features\n\n", intro))
        
        print("  2️⃣ Generating workout creation section...")
        creation = self.generate_workout_creation_section()
        sections.append(("\n## Workout Creation & Management: The Heart of TrainerDay\n\n", creation))
        
        print("  3️⃣ Generating training modes section...")
        modes = self.generate_training_modes_section()
        sections.append(("\n## Training Modes: Precision Control for Every Workout\n\n", modes))
        
        # Combine all sections
        full_article = ""
        for title, content in sections:
            full_article += title + content
        
        # Add a conclusion
        conclusion = """
## Conclusion: Your Training Journey Starts Here

Throughout this guide, I've shared the features that make TrainerDay more than just another training app. From our Excel-like workout editor designed for speed to our sophisticated training modes and comprehensive workout library, every feature has been crafted with one goal: making your training more effective and efficient.

Whether you're creating your first interval workout or designing complex training plans with W'bal integration, TrainerDay provides the tools you need. Our community of athletes continues to grow, contributing workouts and insights that benefit everyone.

Ready to experience the speed and power of TrainerDay? Visit [app.trainerday.com](https://app.trainerday.com) and see why thousands of athletes have made TrainerDay their training platform of choice.

Remember: **Designed for one thing. Speed.** That's not just our philosophy—it's your competitive advantage.

Happy training!
Alex
Founder, TrainerDay"""
        
        full_article += conclusion
        
        # Save the article
        output_dir = Path("./script-testing/workout_articles")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f"comprehensive_workout_features_v2_{timestamp}.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_article)
        
        word_count = len(full_article.split())
        
        print(f"\n✅ Article saved to: {output_file}")
        print(f"📄 Article length: {len(full_article)} characters")
        print(f"📝 Word count: {word_count} words")
        
        return output_file

if __name__ == "__main__":
    generator = ComprehensiveWorkoutArticleGeneratorV2()
    generator.generate_full_article()