#!/usr/bin/env python3
"""
Enhance Articles Based on Fact Review

This script reads fact review results from Google Sheets, groups them by article,
and sends articles to Claude API for enhancement based on WRONG/REMOVE/ADD status markings.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials
from anthropic import Anthropic
import re
from collections import defaultdict

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))


def read_facts_from_sheets():
    """Read all facts from Google Sheets with their review status"""
    
    print("📊 Reading fact review results from Google Sheets...")
    
    # Initialize Google Sheets client
    credentials_path = Path.home() / "td-drive-credentials.json"
    
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    try:
        credentials = Credentials.from_service_account_file(
            str(credentials_path), 
            scopes=scopes
        )
        
        gc = gspread.authorize(credentials)
        print(f"✅ Google Sheets client initialized")
        
    except Exception as e:
        print(f"❌ Failed to initialize Google Sheets client: {e}")
        return None
    
    # Open the shared spreadsheet by ID
    spreadsheet_id = "1YJyAVVaPUM6uhd9_DIRLAB0tE106gExTSD0sUMV5LLc"
    try:
        spreadsheet = gc.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.sheet1
        print(f"✅ Reading from: {spreadsheet.title}")
        
    except Exception as e:
        print(f"❌ Failed to open spreadsheet: {e}")
        return None
    
    # Read all data
    try:
        all_values = worksheet.get_all_values()
        
        if len(all_values) < 2:
            print("⚠️  No data found in spreadsheet")
            return {}
        
        # Parse data (assuming new column order: fact_id, status, original_fact, replacement_text, notes, source_article, created_at)
        headers = all_values[0]
        data_rows = all_values[1:]
        
        print(f"📊 Found {len(data_rows)} facts to process")
        
        facts_by_article = defaultdict(list)
        
        for row in data_rows:
            if len(row) >= 6 and row[0]:  # Ensure we have minimum required columns
                try:
                    fact_data = {
                        'fact_id': int(row[0]),
                        'status': row[1].strip().upper() if len(row) > 1 else '',
                        'original_fact': row[2] if len(row) > 2 else '',
                        'replacement_text': row[3] if len(row) > 3 else '',
                        'notes': row[4] if len(row) > 4 else '',
                        'source_article': row[5] if len(row) > 5 else '',
                        'created_at': row[6] if len(row) > 6 else ''
                    }
                    
                    # Only process facts with review status (not blank)
                    if fact_data['status'] in ['WRONG', 'REMOVE', 'ADD', 'REPLACE']:
                        source_article = fact_data['source_article']
                        if source_article:
                            facts_by_article[source_article].append(fact_data)
                
                except (ValueError, IndexError):
                    continue  # Skip invalid rows
        
        print(f"✅ Found facts needing processing for {len(facts_by_article)} articles")
        
        # Show summary
        for article, facts in facts_by_article.items():
            status_counts = {}
            for fact in facts:
                status = fact['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            status_summary = ', '.join([f"{status}: {count}" for status, count in status_counts.items()])
            print(f"  📄 {article}: {len(facts)} facts ({status_summary})")
        
        return facts_by_article
        
    except Exception as e:
        print(f"❌ Error reading spreadsheet data: {e}")
        return None

def load_article_content(article_filename):
    """Load the content of an article file"""
    
    # Check common locations for articles
    content_output_path = os.getenv('CONTENT_OUTPUT_PATH', '')
    
    possible_paths = [
        Path(content_output_path) / "articles-ai" / "ai-created" / article_filename,
        Path(content_output_path) / article_filename,
        Path(__file__).parent.parent / "output" / article_filename,
        Path(article_filename)  # Direct path
    ]
    
    for article_path in possible_paths:
        if article_path.exists():
            try:
                with open(article_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"✅ Loaded article: {article_path}")
                return content, article_path
            except Exception as e:
                print(f"⚠️  Could not read {article_path}: {e}")
                continue
    
    print(f"❌ Could not find article file: {article_filename}")
    return None, None

def load_prompt_template():
    """Load the article enhancement prompt template"""
    
    template_path = Path(__file__).parent.parent / "templates" / "article-enhancement-prompt-template.txt"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        print(f"✅ Loaded prompt template")
        return template
    except Exception as e:
        print(f"❌ Could not load prompt template: {e}")
        return None

def format_facts_for_prompt(facts, status_filter):
    """Format facts with a specific status for the prompt"""
    
    filtered_facts = [f for f in facts if f['status'] == status_filter]
    
    if not filtered_facts:
        return "None"
    
    formatted = []
    for fact in filtered_facts:
        if status_filter == 'REPLACE' and fact['replacement_text']:
            formatted.append(f"- Original: {fact['original_fact']}\n  Replace with: {fact['replacement_text']}")
        else:
            formatted.append(f"- {fact['original_fact']}")
            if fact['notes']:
                formatted.append(f"  Note: {fact['notes']}")
    
    return '\n'.join(formatted)

def enhance_article_with_claude(article_content, facts, prompt_template):
    """Send article to Claude for enhancement based on fact corrections"""
    
    print("🤖 Enhancing article with Claude API...")
    
    # Initialize Anthropic client
    client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    # Extract article title from content
    title_match = re.search(r'^title:\s*["\']?([^"\'\n]+)["\']?', article_content, re.MULTILINE)
    article_title = title_match.group(1) if title_match else "Unknown Article"
    
    # Format facts by status
    facts_to_remove = format_facts_for_prompt(facts, 'WRONG') + '\n' + format_facts_for_prompt(facts, 'REMOVE')
    facts_to_add = format_facts_for_prompt(facts, 'ADD')
    facts_to_replace = format_facts_for_prompt(facts, 'REPLACE')
    
    # Build the prompt
    prompt = prompt_template.format(
        article_title=article_title,
        article_content=article_content,
        facts_to_remove=facts_to_remove if facts_to_remove.strip() != 'None\nNone' else 'None',
        facts_to_add=facts_to_add,
        facts_to_replace=facts_to_replace
    )
    
    try:
        # Send to Claude
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            temperature=0.3,
            messages=[
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
        )
        
        enhanced_content = response.content[0].text
        print(f"✅ Article enhanced successfully")
        return enhanced_content
        
    except Exception as e:
        print(f"❌ Error calling Claude API: {e}")
        return None

def compare_and_save_article(original_content, enhanced_content, original_path):
    """Compare original and enhanced content, save only if changed"""
    
    # Check if Claude said no changes needed (exact token or within response)
    if enhanced_content.strip() == "NO_CHANGES_NEEDED" or "NO_CHANGES_NEEDED" in enhanced_content:
        print(f"✅ No changes needed for {original_path.name} - keeping original in ai-created")
        return False, None
    
    # Also check if Claude returned explanation instead of actual article
    # Real articles should start with YAML frontmatter (---)
    if not enhanced_content.strip().startswith('---'):
        print(f"✅ Claude returned explanation instead of article for {original_path.name} - keeping original")
        return False, None
    
    # Additional check: look for explanatory phrases that indicate no real enhancement
    explanation_indicators = [
        "After reviewing",  
        "I notice that",
        "Since this is the only",
        "[Note:",
        "The only change made was"
    ]
    
    if any(indicator in enhanced_content for indicator in explanation_indicators):
        print(f"✅ Claude returned explanation instead of enhanced article for {original_path.name} - keeping original")
        return False, None
    
    # Compare content (ignore minor whitespace differences)
    original_normalized = ' '.join(original_content.split())
    enhanced_normalized = ' '.join(enhanced_content.split())
    
    if original_normalized == enhanced_normalized:
        print(f"✅ No actual changes detected for {original_path.name}")
        return False, None
    
    print(f"📊 Changes detected for {original_path.name}")
    print(f"   Original length: {len(original_content)} chars")
    print(f"   Enhanced length: {len(enhanced_content)} chars")
    
    # Show content comparison preview
    print(f"\n📄 CONTENT COMPARISON FOR {original_path.name}:")
    print("=" * 60)
    print("🔵 ORIGINAL (first 300 chars):")
    print(original_content[:300] + "..." if len(original_content) > 300 else original_content)
    print("\n🟢 ENHANCED (first 300 chars):")
    print(enhanced_content[:300] + "..." if len(enhanced_content) > 300 else enhanced_content)
    print("=" * 60)
    
    # Create UPDATED subdirectory in the same parent as original
    updated_dir = original_path.parent / "UPDATED"
    updated_dir.mkdir(exist_ok=True)
    
    # Save with same filename in UPDATED directory
    updated_path = updated_dir / original_path.name
    
    try:
        with open(updated_path, 'w', encoding='utf-8') as f:
            f.write(enhanced_content)
        
        print(f"✅ Enhanced article saved: {updated_path}")
        
        # Delete original file from ai-created since we saved enhanced version
        try:
            original_path.unlink()
            print(f"🗑️  Deleted original from ai-created (enhanced version saved)")
        except Exception as e:
            print(f"⚠️  Could not delete original from ai-created: {e}")
        
        return True, updated_path
        
    except Exception as e:
        print(f"❌ Error saving enhanced article: {e}")
        return False, None

def main():
    """Main function"""
    
    print("🚀 ARTICLE ENHANCEMENT FROM FACT REVIEW")
    print("=" * 50)
    
    # Read fact review results from Google Sheets
    facts_by_article = read_facts_from_sheets()
    
    if not facts_by_article:
        print("❌ No fact review data found")
        return
    
    # Load prompt template
    prompt_template = load_prompt_template()
    if not prompt_template:
        print("❌ Could not load prompt template")
        return
    
    # Process each article that has fact corrections
    for article_filename, facts in facts_by_article.items():
            
        print(f"\n📄 Processing: {article_filename}")
        print(f"   Facts to process: {len(facts)}")
        
        # Load article content
        article_content, article_path = load_article_content(article_filename)
        if not article_content:
            print(f"⚠️  Skipping {article_filename} - could not load content")
            continue
        
        # Enhance with Claude
        enhanced_content = enhance_article_with_claude(article_content, facts, prompt_template)
        if not enhanced_content:
            print(f"⚠️  Failed to enhance {article_filename}")
            continue
        
        # Compare and save if changed
        was_changed, saved_path = compare_and_save_article(article_content, enhanced_content, article_path)
        if was_changed:
            print(f"✅ {article_filename} enhanced and saved to UPDATED directory")
        else:
            print(f"ℹ️  {article_filename} - no changes made")
    
    print(f"\n🎉 Article enhancement complete!")
    print(f"📊 Processed {len(facts_by_article)} articles")
    
    # Show final summary
    updated_dir = Path(os.getenv('CONTENT_OUTPUT_PATH', '')) / "articles-ai" / "ai-updated"
    if updated_dir.exists():
        updated_files = list(updated_dir.glob("*.md"))
        print(f"✅ {len(updated_files)} articles enhanced and saved to ai-updated directory")
        for file in sorted(updated_files):
            print(f"   📄 {file.name}")
    else:
        print("ℹ️  No articles required changes")

if __name__ == "__main__":
    main()