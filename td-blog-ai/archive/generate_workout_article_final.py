#!/usr/bin/env python3
"""
Generate comprehensive workout article using actual LlamaIndex content
"""

import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class WorkoutArticleGenerator:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Load the comprehensive content we extracted
        content_file = Path("./script-testing/workout_query_results/comprehensive_workout_content.json")
        with open(content_file, 'r', encoding='utf-8') as f:
            self.content = json.load(f)
    
    def organize_content_sections(self):
        """Organize content into sections for the article"""
        
        sections = {}
        
        # 1. Fastest Workout Editor
        fastest_editor = self.content['blog_articles'].get('fastest_editor', {})
        if fastest_editor:
            sections['fastest_editor'] = f"""
**From "The Fastest Workout Editor" blog article:**
{fastest_editor.get('text', '')}
"""
        
        # 2. Sets and Reps
        sets_reps = self.content['blog_articles'].get('sets_reps', {})
        if sets_reps:
            sections['sets_reps'] = f"""
**From "Intervals In The Sets Reps Editor" blog article:**
{sets_reps.get('text', '')}
"""
        
        # 3. Interval Comments
        intervals = self.content['blog_articles'].get('intervals', {})
        if intervals:
            sections['interval_comments'] = f"""
**From "Learn About Interval Comments" blog article:**
{intervals.get('text', '')}
"""
        
        # 4. Extract relevant forum discussions
        forum_content = ""
        for discussion in self.content['raw_content']['forum'][:20]:
            title = discussion.get('title', '')
            text = discussion.get('text', '')
            
            if any(keyword in title.lower() for keyword in ['editor', 'workout', 'interval', 'clone', 'copy']):
                forum_content += f"\n\n**User Discussion: {title}**\n{text[:500]}..."
        
        sections['forum_discussions'] = forum_content
        
        # 5. Facts about workouts
        facts_content = "\n\n**Key Facts:**\n"
        for fact in self.content['raw_content']['facts'][:30]:
            fact_text = fact.get('text', '')
            if 'workout' in fact_text.lower() or 'interval' in fact_text.lower():
                facts_content += f"- {fact_text}\n"
        
        sections['facts'] = facts_content
        
        # 6. Additional blog content about modes and features
        mode_content = ""
        for article in self.content['raw_content']['blog']:
            if 'mixing and matching' in article.get('title', '').lower():
                mode_content += f"\n\n**From blog article on Training Modes:**\n{article['text'][:1500]}..."
                break
        
        sections['training_modes'] = mode_content
        
        # 7. W'bal and advanced features
        wbal_content = ""
        for article in self.content['raw_content']['blog']:
            if "w'bal" in article.get('title', '').lower() or 'perfect interval' in article.get('title', '').lower():
                wbal_content += f"\n\n**From blog article: {article['title']}**\n{article['text'][:1000]}..."
                break
        
        sections['advanced_features'] = wbal_content
        
        return sections
    
    def generate_article(self):
        """Generate the article using the template and organized content"""
        
        print("📝 Organizing content sections...")
        sections = self.organize_content_sections()
        
        # Combine all sections
        content_sections = ""
        for section_name, content in sections.items():
            if content:
                content_sections += f"\n\n{'='*60}\n{section_name.upper()}\n{'='*60}\n{content}"
        
        # Load template
        template_path = Path("/Users/alex/Documents/Projects/data-utilities/vector-llama/templates/workout-features-article-template.txt")
        with open(template_path, 'r') as f:
            template = f.read()
        
        # Build prompt
        prompt = template.format(
            title="TrainerDay Workout Creation & Management: The Complete Guide",
            content_sections=content_sections
        )
        
        print("🤖 Generating comprehensive article with OpenAI...")
        
        # Generate with higher token limit for comprehensive article
        response = self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are Alex, the founder of TrainerDay, writing comprehensive documentation."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        article = response.choices[0].message.content
        
        # Save article
        output_dir = Path("./script-testing/workout_articles")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f"workout_features_comprehensive_{timestamp}.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(article)
        
        print(f"\n✅ Comprehensive article saved to: {output_file}")
        print(f"📄 Article length: {len(article)} characters")
        print(f"📝 Word count: {len(article.split())} words")
        
        return output_file

if __name__ == "__main__":
    generator = WorkoutArticleGenerator()
    generator.generate_article()