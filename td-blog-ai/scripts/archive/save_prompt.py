#!/usr/bin/env python3
"""
Save the complete prompt to a file for debugging
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.google_sheets_client import get_bad_facts_for_article_generation

load_dotenv()

def save_prompt():
    """Extract and save the complete prompt"""
    
    # Load query results
    results_file = Path("article-temp-files/article_features.json")
    with open(results_file, 'r') as f:
        query_results = json.load(f)
    
    # Extract content
    content = {
        'facts': [],
        'blog_quotes': [],
        'forum_questions': [],
        'video_references': []
    }
    
    # Process results
    for category, features in query_results.items():
        for feature_name, results in features.items():
            for result in results:
                source = result.get('source', '')
                text = result.get('text', '')
                
                if source == 'facts':
                    content['facts'].append({
                        'text': text,
                        'feature': feature_name
                    })
                elif source == 'blog':
                    content['blog_quotes'].append({
                        'quote': text[:500] + '...' if len(text) > 500 else text,
                        'title': result.get('title', 'Blog Article'),
                        'feature': feature_name
                    })
                elif source == 'forum':
                    content['forum_questions'].append({
                        'question': text[:200] + '...' if len(text) > 200 else text,
                        'answer': text[200:500] + '...' if len(text) > 200 else '',
                        'feature': feature_name
                    })
                elif source == 'youtube':
                    content['video_references'].append({
                        'title': result.get('title', 'Video'),
                        'excerpt': text[:300] + '...' if len(text) > 300 else text,
                        'feature': feature_name
                    })
    
    # Build content sections
    content_sections = []
    
    # Facts
    if content['facts']:
        facts_text = "\n".join([f"- {fact['text']}" for fact in content['facts']])
        content_sections.append(f"## FACTS FROM KNOWLEDGE BASE ({len(content['facts'])} total facts)\n{facts_text}")
    
    # Blog
    if content['blog_quotes']:
        blog_text = "\n\n".join([
            f"From '{q['title']}':\n\"{q['quote']}\""
            for q in content['blog_quotes']
        ])
        content_sections.append(f"## BLOG CONTENT ({len(content['blog_quotes'])} total quotes)\n{blog_text}")
    
    # Forum
    if content['forum_questions']:
        forum_entries = []
        for q in content['forum_questions'][:100]:
            answer = q['answer']
            if len(answer) > 300:
                answer = answer[:300] + "..."
            forum_entries.append(f"Q: {q['question']}\nA: {answer}")
        
        forum_text = "\n\n".join(forum_entries)
        content_sections.append(f"## FORUM DISCUSSIONS ({len(content['forum_questions'])} total Q&As, showing top 100)\n{forum_text}")
    
    # Video
    if content['video_references']:
        video_entries = []
        for v in content['video_references'][:50]:
            excerpt = v['excerpt']
            if len(excerpt) > 200:
                excerpt = excerpt[:200] + "..."
            video_entries.append(f"Video: {v['title']}\n{excerpt}")
        
        video_text = "\n\n".join(video_entries)
        content_sections.append(f"## VIDEO CONTENT ({len(content['video_references'])} total videos, showing top 50)\n{video_text}")
    
    # Load template
    template_path = Path("templates/comprehensive-article-template.txt")
    with open(template_path, 'r') as f:
        template = f.read()
    
    # Get bad facts
    bad_facts_section = get_bad_facts_for_article_generation()
    
    # Build prompt
    prompt = template.format(
        title="TrainerDay Workout Creation and Management Features - Complete Guide",
        content_sections="\n\n".join(content_sections),
        bad_facts_section=bad_facts_section
    )
    
    # Save prompt
    output_file = Path("script-testing/complete_prompt.txt")
    with open(output_file, 'w') as f:
        f.write(prompt)
    
    print(f"✅ Saved prompt to: {output_file}")
    print(f"📊 Prompt size: {len(prompt):,} characters")
    print(f"📝 Content stats:")
    print(f"   - Facts: {len(content['facts'])}")
    print(f"   - Blog quotes: {len(content['blog_quotes'])}")
    print(f"   - Forum Q&As: {len(content['forum_questions'])}")
    print(f"   - Videos: {len(content['video_references'])}")

if __name__ == "__main__":
    save_prompt()