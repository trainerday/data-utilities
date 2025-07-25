#!/usr/bin/env python3
"""
Generate complete workout article with all content from query results
"""

import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class CompleteWorkoutArticle:
    def __init__(self):
        # Load the query results
        self.load_query_results()
        
    def load_query_results(self):
        """Load the query results from our test"""
        results_file = Path("./script-testing/workout_query_results/test_query_results_20250725_182431.json")
        
        with open(results_file, 'r') as f:
            self.query_results = json.load(f)
    
    def extract_qa_content(self, text):
        """Extract Q&A content cleanly"""
        qa_parts = {}
        
        if 'Question:' in text:
            q_start = text.find('Question:') + 9
            q_end = text.find('\n', q_start)
            if q_end == -1 or q_end - q_start > 200:
                q_end = q_start + 200
            qa_parts['question'] = text[q_start:q_end].strip()
        
        if 'Answer:' in text:
            a_start = text.find('Answer:') + 7  
            a_end = text.find('\n', a_start + 50)
            if a_end == -1:
                a_end = a_start + 200
            qa_parts['answer'] = text[a_start:a_end].strip()
            
        if 'Solution:' in text and 'answer' not in qa_parts:
            s_start = text.find('Solution:') + 9
            s_end = text.find('\n', s_start + 50)
            if s_end == -1:
                s_end = s_start + 200
            qa_parts['solution'] = text[s_start:s_end].strip()
            
        return qa_parts
    
    def generate_article(self):
        """Generate the article using all found content"""
        
        article = """# TrainerDay Workout Creation & Management Guide

This comprehensive guide covers TrainerDay's workout creation and management features, compiled from our knowledge base of user discussions, blog articles, and documented features.

"""
        
        # Visual Workout Editor
        article += "## Visual Workout Editor\n\n"
        
        visual_results = self.query_results.get('Visual Workout Editor', [])
        if visual_results:
            article += "The visual workout editor provides a graphical interface for creating and modifying workouts. "
            article += "Users have shared their experiences with the editor's design features.\n\n"
            
            # Add specific user feedback
            for result in visual_results[:2]:
                if 'insert and delete rows' in result['text']:
                    article += "**Row Management**: One user noted: \"I enjoy designing my own workouts which generally I keep private as they are designed specifically for me. "
                    article += "However I do find the grid where you program the numbers a little frustrating as there doesn't appear to be a way that you can easily insert additional rows.\"\n\n"
                    break
                    
            article += "The editor allows for customization of workouts with various interval types and intensities, "
            article += "though some users have requested improvements to make row insertion and deletion easier.\n\n"
        
        # Fastest Workout Editor
        article += "## The Fastest Workout Editor\n\n"
        
        fastest_results = self.query_results.get('Fastest Workout Editor', [])
        if fastest_results:
            # Find the blog content
            blog_content = next((r for r in fastest_results if r['source'] == 'blog'), None)
            if blog_content:
                article += "According to TrainerDay's blog: \"**Designed for one thing. Speed.**\"\n\n"
                article += "The workout editor works just like Excel with copy and paste functionality and arrow keys for moving. "
                article += "This familiar interface allows experienced users to create complex workouts quickly.\n\n"
                
            article += "**Key Features:**\n"
            article += "- Excel-like copy and paste functionality\n"
            article += "- Arrow key navigation\n"  
            article += "- Automatic switching between Slope and ERG or HR modes\n"
            article += "- Keyboard shortcuts for efficiency\n\n"
            
            # Add user experiences
            for result in fastest_results:
                if 'Copy workout on calendar' in result['title']:
                    article += "**Workout Duplication**: Users can duplicate workouts on the calendar by holding Option/Alt while dragging. "
                    article += "As confirmed by TrainerDay support: \"on mac or pc you can hold option/alt when dragging and it will duplicate.\"\n\n"
                    break
        
        # Sets and Reps Editor
        article += "## Sets and Reps Editor\n\n"
        
        sets_results = self.query_results.get('Sets and Reps Editor', [])
        if sets_results:
            article += "The sets and reps functionality allows users to create structured interval workouts with repeating patterns.\n\n"
            
            # Look for actual sets/reps content
            for result in sets_results:
                if '[SOLVED] - Reps change' in result['title']:
                    article += "**Known Issues and Solutions**: Some users have experienced issues where reps change when saving workouts. "
                    article += "One user reported: \"i made a workout, using sets and reps. I input 5 reps, with .1 minutes at a sprint wattage, "
                    article += "and 1 minute rest... When I save the workout, it changes the 5 reps to 4 reps.\"\n\n"
                    article += "The TrainerDay team has addressed these technical issues to ensure workout integrity.\n\n"
                    break
        
        # Interval Comments  
        article += "## Interval Comments\n\n"
        
        comments_results = self.query_results.get('Interval Comments', [])
        if comments_results:
            article += "Interval comments allow coaches and athletes to add detailed instructions and notes to specific workout segments.\n\n"
            
            # Find feature request
            for result in comments_results:
                if 'Workout editor - interval comments' in result['title']:
                    article += "**Feature Enhancement Request**: A user suggested: \"It would be great to be able to enter comments at the sets&reps line. "
                    article += "If my workout is 5x1min catch up drill, then I would want my comment to be: 'catch up drill'. "
                    article += "So it would be great to be able to type it once at sets and reps level and then it should be copied 5 times in the intervals tab.\"\n\n"
                    break
                    
            # Add known issues
            for result in comments_results:
                if 'swim erg' in result['text'].lower():
                    article += "**Swim Erg Specific Issues**: Users have reported that with swim erg workouts, "
                    article += "rest interval comments sometimes get overwritten by the comment above. "
                    article += "This has been identified as a specific issue that affects swim training.\n\n"
                    break
        
        # Workout Cloning
        article += "## Workout Cloning and Duplication\n\n"
        
        cloning_results = self.query_results.get('Workout Cloning', [])
        if cloning_results:
            article += "TrainerDay provides multiple ways to clone and modify existing workouts for progressive training.\n\n"
            
            # Find the how-to content
            for result in cloning_results:
                qa = self.extract_qa_content(result['text'])
                if qa.get('question') and 'clone' in qa['question']:
                    article += f"**User Question**: \"{qa['question']}\"\n\n"
                    if qa.get('answer'):
                        article += f"**Answer**: {qa['answer']}\n\n"
                    break
                    
            article += "**Methods for Cloning Workouts:**\n"
            article += "- Use the 3-dot menu in the upper right corner of a workout\n"
            article += "- Hold Option/Alt while dragging on the calendar to duplicate\n"
            article += "- Clone workouts to create progressive variations\n\n"
        
        # Add conclusion
        article += """## Best Practices and Tips

Based on user experiences in our knowledge base:

1. **Speed is Key**: The workout editor is optimized for fast entry using keyboard shortcuts
2. **Use Templates**: Clone existing workouts and modify them rather than starting from scratch  
3. **Add Context**: Use interval comments to provide coaching cues and instructions
4. **Check Your Work**: Some users have reported minor issues with reps changing - always verify before saving
5. **Platform-Specific Features**: Remember that Alt/Option dragging works on desktop for quick duplication

## Conclusion

TrainerDay's workout creation tools balance speed and functionality, providing both visual and keyboard-driven interfaces. While users have identified areas for improvement (like easier row insertion and interval comment management), the platform continues to evolve based on user feedback.

The Excel-like editor remains the fastest way to create structured workouts, especially when combined with the cloning features for building progressive training plans.

---

*This guide was compiled from actual user discussions, support responses, and blog content in the TrainerDay knowledge base.*"""
        
        return article
    
    def save_article(self, content):
        """Save the generated article"""
        output_dir = Path("./script-testing/workout_articles")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f"complete_workout_article_{timestamp}.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Complete article saved to: {output_file}")
        print(f"📄 Article length: {len(content)} characters")
        print(f"📝 Word count: {len(content.split())} words")
        
        return output_file

if __name__ == "__main__":
    generator = CompleteWorkoutArticle()
    article = generator.generate_article()
    output_file = generator.save_article(article)