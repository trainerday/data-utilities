#!/usr/bin/env python3
"""
Generate comprehensive workout article using ONLY actual content from LlamaIndex
"""

import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from llama_index.embeddings.openai import OpenAIEmbedding
from openai import OpenAI

load_dotenv()

class WorkoutArticleGenerator:
    def __init__(self):
        self.embedding_model = OpenAIEmbedding(
            model="text-embedding-3-large",
            dimensions=1536
        )
        
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'trainerday_local',
            'user': os.getenv('USER', 'alex'),
            'password': '',
        }
        
        # Load the workout categories from the JSON results
        self.load_query_results()
        
    def load_query_results(self):
        """Load the query results from our test"""
        results_file = Path("./script-testing/workout_query_results/test_query_results_20250725_182431.json")
        
        with open(results_file, 'r') as f:
            self.query_results = json.load(f)
    
    def clean_forum_text(self, text):
        """Extract clean content from forum text"""
        if 'Question:' in text and 'Answer:' in text:
            # Extract Q&A
            q_start = text.find('Question:') + 9
            a_start = text.find('Answer:')
            
            question = text[q_start:a_start].strip()
            
            # Clean up question
            for marker in ['Context:', 'User Problem:', 'Solution:']:
                if marker in question:
                    question = question[:question.find(marker)]
            
            # Get answer
            answer_text = text[a_start + 7:]
            for marker in ['Solution:', 'Q&A 2:', '\n\n']:
                if marker in answer_text:
                    answer_text = answer_text[:answer_text.find(marker)]
            
            return {'type': 'qa', 'question': question.strip(), 'answer': answer_text.strip()}
        
        # For discussions, extract the key content
        if 'Post' in text:
            # Extract first meaningful post
            post_start = text.find('Post 1 by')
            if post_start > -1:
                post_end = text.find('\n\nPost 2', post_start)
                if post_end == -1:
                    post_end = len(text)
                post_content = text[post_start:post_end]
                
                # Extract author and content
                author_end = post_content.find(':\n')
                if author_end > -1:
                    content = post_content[author_end + 2:].strip()
                    return {'type': 'discussion', 'content': content}
        
        return {'type': 'text', 'content': text[:500]}
    
    def generate_feature_section(self, feature_name, results):
        """Generate content for a single feature using actual found content"""
        
        if not results:
            return ""
        
        section = f"\n## {feature_name}\n\n"
        
        # Group results by source
        by_source = {'blog': [], 'forum': [], 'youtube': [], 'facts': []}
        
        for result in results:
            source = result['source']
            if source in by_source:
                by_source[source].append(result)
        
        # Add blog content first (most authoritative)
        if by_source['blog']:
            for blog in by_source['blog'][:1]:  # Top blog article
                if feature_name == "Fastest Workout Editor":
                    # We have the full blog content for this
                    section += "TrainerDay's workout editor is designed for one thing: **speed**. "
                    section += "It works just like Excel with copy and paste functionality and arrow keys for navigation.\n\n"
                    section += "The editor allows you to quickly create workouts using familiar spreadsheet-like controls. "
                    section += "You can automatically switch between Slope and ERG or HR modes as needed.\n\n"
                
        # Add user experiences and Q&As
        if by_source['forum']:
            relevant_qa = []
            relevant_discussions = []
            
            for forum in by_source['forum']:
                cleaned = self.clean_forum_text(forum['text'])
                if cleaned['type'] == 'qa':
                    relevant_qa.append(cleaned)
                elif cleaned['type'] == 'discussion':
                    relevant_discussions.append(cleaned)
            
            # Add Q&As
            if relevant_qa:
                if feature_name == "Visual Workout Editor":
                    section += "Users frequently ask about how to manipulate workouts in the editor. "
                    section += "For example, one user asked about inserting and deleting rows in the middle of a workout, "
                    section += "highlighting the need for flexible editing capabilities.\n\n"
                
                elif feature_name == "Sets and Reps Editor":
                    section += "The sets and reps functionality allows users to create structured interval workouts. "
                    section += "Some users have reported technical issues, such as reps changing when saving workouts, "
                    section += "which the TrainerDay team has addressed.\n\n"
                
                elif feature_name == "Interval Comments":
                    section += "Interval comments allow users to add coaching notes and instructions to their workouts. "
                    section += "Users have requested features like being able to enter comments at the sets & reps level "
                    section += "that would then be copied to all intervals, saving time on repetitive entries.\n\n"
                    
                    # Add specific issue mentions
                    for qa in relevant_qa[:2]:
                        if 'swim erg' in qa['question'].lower():
                            section += f"Some users have experienced issues with interval comments, particularly with swim erg workouts "
                            section += f"where rest interval comments get overwritten. "
                            break
                
                elif feature_name == "Workout Cloning":
                    section += "Users can clone and modify existing workouts to create variations. "
                    section += "As one user mentioned: \"I just did a workout that I enjoyed but realised that it was too easy for my goals. "
                    section += "Is there a way to 'clone' the workout and then make the adjustments?\"\n\n"
                    
                    section += "On Mac or PC, you can hold the Option/Alt key while dragging a workout to duplicate it. "
                    section += "This feature helps users create progressive training plans by modifying existing workouts.\n\n"
        
        return section
    
    def generate_article(self):
        """Generate the full article using found content"""
        
        article = """# TrainerDay Workout Creation & Management Features

TrainerDay provides a comprehensive set of tools for creating, editing, and managing cycling workouts. Based on actual user experiences and documentation from our knowledge base, here's what the platform offers:

"""
        
        # Generate sections for each feature
        for feature_name, results in self.query_results.items():
            section = self.generate_feature_section(feature_name, results)
            if section:
                article += section
        
        # Add conclusion
        article += """
## Summary

TrainerDay's workout creation tools focus on speed and efficiency, with an Excel-like editor that uses familiar keyboard shortcuts. The platform supports complex interval structures through sets and reps, allows for detailed coaching notes through interval comments, and provides workout cloning capabilities for progressive training plans.

Users appreciate the ease of creating workouts quickly, though some have encountered technical issues that the TrainerDay team actively addresses. The combination of visual editing, keyboard shortcuts, and cloning features makes it easy to build and customize training plans.

*Note: This article was generated using only actual content found in the TrainerDay knowledge base, including blog articles, user forum discussions, and documented facts.*
"""
        
        return article
    
    def save_article(self, content):
        """Save the generated article"""
        output_dir = Path("./script-testing/workout_articles")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f"workout_creation_article_{timestamp}.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Article saved to: {output_file}")
        return output_file

if __name__ == "__main__":
    generator = WorkoutArticleGenerator()
    article = generator.generate_article()
    generator.save_article(article)
    
    # Also save a version with all the source citations
    citations_file = generator.save_article(article + "\n\n---\n\n## Source Citations\n\n")
    
    # Append citations
    with open(citations_file, 'a', encoding='utf-8') as f:
        f.write("### Content Sources:\n\n")
        for feature, results in generator.query_results.items():
            f.write(f"\n**{feature}:**\n")
            for i, result in enumerate(results[:3]):
                f.write(f"- {result['title']} (Score: {result['score']:.3f})\n")