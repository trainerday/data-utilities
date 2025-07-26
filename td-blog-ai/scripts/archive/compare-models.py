#!/usr/bin/env python3
"""Compare article generation across Claude Sonnet 4, GPT-4 Turbo, and GPT-4o"""

import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
import openai
from anthropic import Anthropic
import sys

# Import utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.google_sheets_client import get_bad_facts_for_article_generation

load_dotenv()

def prepare_content(section_name="Control Modes (ERG, Slope, Resistance, HR)"):
    """Prepare content for all models to use"""
    
    # Load results
    with open("article-temp-files/article_features.json", 'r') as f:
        data = json.load(f)
    
    # Load bad facts
    bad_facts = get_bad_facts_for_article_generation()
    
    # Load template
    with open("templates/section-generation-template.txt", 'r') as f:
        template = f.read()
    
    # Get all content
    all_content = []
    for category, features in data.items():
        for feature_name, results in features.items():
            for result in results:
                all_content.append({
                    'text': result.get('text', ''),
                    'source': result.get('source', ''),
                    'feature': feature_name,
                    'category': category,
                    'title': result.get('title', ''),
                    'distance': result.get('distance', 1.0)
                })
    
    # Keywords for Control Modes
    keywords = ["ERG mode", "automatic power control", "power targeting", "cadence gear",
                "slope mode", "gradient simulation", "gear control", "automatic slope",
                "resistance mode", "fixed resistance", "sprint training", "strength work",
                "HR+ mode", "heart rate controlled", "automatic power adjustment", "HR training"]
    
    section_content = {
        'facts': [],
        'blog_quotes': [],
        'forum_questions': [],
        'video_references': []
    }
    
    # Extract matching content
    for item in all_content:
        text_lower = item['text'].lower()
        
        matched = False
        for keyword in keywords:
            if keyword.lower() in text_lower:
                matched = True
                break
        
        if matched:
            source = item['source']
            
            if source == 'facts':
                section_content['facts'].append({
                    'text': item['text'],
                    'feature': item['feature']
                })
            elif source == 'blog':
                section_content['blog_quotes'].append({
                    'quote': item['text'],
                    'title': item['title'],
                    'feature': item['feature']
                })
            elif source == 'forum':
                section_content['forum_questions'].append({
                    'text': item['text'],
                    'feature': item['feature']
                })
            elif source == 'youtube':
                section_content['video_references'].append({
                    'title': item['title'],
                    'text': item['text'],
                    'feature': item['feature']
                })
    
    # Format content
    sections = []
    
    if section_content['facts']:
        facts_text = "\n".join([f"- {fact['text']}" for fact in section_content['facts'][:40]])
        sections.append(f"FACTS ({len(section_content['facts'])} total, showing top 40):\n{facts_text}")
    
    if section_content['blog_quotes']:
        blog_entries = []
        for q in section_content['blog_quotes'][:15]:
            quote = q['quote']
            if len(quote) > 800:
                quote = quote[:800] + "..."
            blog_entries.append(f"From '{q['title']}':\n{quote}")
        blog_text = "\n\n".join(blog_entries)
        sections.append(f"BLOG CONTENT ({len(section_content['blog_quotes'])} total, showing top 15):\n{blog_text}")
    
    if section_content['forum_questions']:
        forum_entries = []
        for q in section_content['forum_questions'][:20]:
            text = q['text']
            if len(text) > 600:
                text = text[:600] + "..."
            forum_entries.append(f"Forum discussion:\n{text}")
        forum_text = "\n\n".join(forum_entries)
        sections.append(f"FORUM DISCUSSIONS ({len(section_content['forum_questions'])} total, showing top 20):\n{forum_text}")
    
    content_formatted = "\n\n".join(sections)
    
    # Add length instruction
    length_instruction = "\n\nLENGTH REQUIREMENT: Generate a comprehensive article of at least 1000-1500 words. Include ALL relevant information from the provided content. Be thorough and detailed."
    
    prompt = template.format(
        section_name=section_name,
        content_sections=content_formatted,
        bad_facts_section=bad_facts
    ) + length_instruction
    
    matched_count = sum(len(v) for v in section_content.values())
    return prompt, matched_count

def test_claude_sonnet_4(prompt):
    """Test with Claude Sonnet 4"""
    print("\n🤖 Testing Claude Sonnet 4...")
    
    try:
        client = Anthropic()
        start_time = time.time()
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",  # This might be the Sonnet 4 model ID
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": prompt
            }],
            temperature=0.3
        )
        
        elapsed = time.time() - start_time
        article = response.content[0].text
        word_count = len(article.split())
        
        # Save
        with open("output/articles-ai/comparison_claude_sonnet_4.md", 'w') as f:
            f.write(article)
        
        return {
            "model": "Claude Sonnet 4",
            "word_count": word_count,
            "time": round(elapsed, 2),
            "chars": len(article)
        }
        
    except Exception as e:
        print(f"Error with Claude: {e}")
        return None

def test_gpt4_turbo(prompt):
    """Test with GPT-4 Turbo"""
    print("\n🤖 Testing GPT-4 Turbo...")
    
    try:
        client = openai.OpenAI()
        start_time = time.time()
        
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": prompt
            }],
            temperature=0.3
        )
        
        elapsed = time.time() - start_time
        article = response.choices[0].message.content
        word_count = len(article.split())
        
        # Save
        with open("output/articles-ai/comparison_gpt4_turbo.md", 'w') as f:
            f.write(article)
        
        return {
            "model": "GPT-4 Turbo",
            "word_count": word_count,
            "time": round(elapsed, 2),
            "chars": len(article)
        }
        
    except Exception as e:
        print(f"Error with GPT-4 Turbo: {e}")
        return None

def test_gpt4o(prompt):
    """Test with GPT-4o"""
    print("\n🤖 Testing GPT-4o...")
    
    try:
        client = openai.OpenAI()
        start_time = time.time()
        
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": prompt
            }],
            temperature=0.3
        )
        
        elapsed = time.time() - start_time
        article = response.choices[0].message.content
        word_count = len(article.split())
        
        # Save
        with open("output/articles-ai/comparison_gpt4o.md", 'w') as f:
            f.write(article)
        
        return {
            "model": "GPT-4o",
            "word_count": word_count,
            "time": round(elapsed, 2),
            "chars": len(article)
        }
        
    except Exception as e:
        print(f"Error with GPT-4o: {e}")
        return None

def main():
    print("🔬 Model Comparison Test")
    print("=" * 50)
    
    # Prepare content
    print("\n📚 Preparing content...")
    prompt, matched_count = prepare_content()
    print(f"✅ Prompt prepared: {len(prompt):,} characters")
    print(f"📊 Matched content items: {matched_count}")
    
    # Test all models
    results = []
    
    result = test_claude_sonnet_4(prompt)
    if result:
        results.append(result)
    
    result = test_gpt4_turbo(prompt)
    if result:
        results.append(result)
    
    result = test_gpt4o(prompt)
    if result:
        results.append(result)
    
    # Display comparison
    print("\n" + "=" * 70)
    print("📊 COMPARISON RESULTS")
    print("=" * 70)
    print(f"{'Model':<20} {'Words':<10} {'Chars':<10} {'Time (s)':<10}")
    print("-" * 70)
    
    for result in results:
        print(f"{result['model']:<20} {result['word_count']:<10} {result['chars']:<10} {result['time']:<10}")
    
    print("\n📄 Articles saved to output/articles-ai/comparison_*.md")
    print("\nYou can now review and compare the three generated articles!")

if __name__ == "__main__":
    main()