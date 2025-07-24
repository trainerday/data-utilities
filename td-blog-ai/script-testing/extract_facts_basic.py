#!/usr/bin/env python3
"""
Basic Fact Extraction Script

Extracts factual statements from the first article using Claude Sonnet 4
and writes them to a temporary file for review.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic
import openai
import frontmatter

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

class BasicFactExtractor:
    def __init__(self):
        # Initialize Claude client
        self.anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        # Initialize OpenAI client as fallback
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    def extract_facts_from_article(self, article_content, article_title):
        """Extract factual statements from article using Claude Sonnet 4"""
        
        prompt = f"""
Extract factual statements from this TrainerDay article. Focus on concrete, verifiable facts about features, functionality, and technical specifications.

Article Title: {article_title}

Article Content:
{article_content}

Please extract factual statements and return them in this format:
FACT: [Clear, standalone factual statement]

Guidelines:
- Focus on features, capabilities, technical specifications
- Include facts about how things work, what's supported, what's available
- Make each fact a complete, standalone statement
- Avoid subjective opinions or user preferences
- Include specific details like modes, integrations, file formats, etc.

Example format:
FACT: TrainerDay workout creator supports ERG mode, slope mode, and heart rate mode
FACT: W'bal integration requires entering FTP and W' values
FACT: Workouts can be duplicated by holding ALT key and dragging
"""

        # Try Claude first
        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=3000,
                temperature=0.3,  # Low temperature for consistent fact extraction
                messages=[{"role": "user", "content": prompt}]
            )
            
            print("✅ Used Claude Sonnet 4")
            return response.content[0].text
            
        except Exception as e:
            print(f"⚠️  Claude failed ({e}), trying OpenAI GPT-4 as fallback...")
            
            # Fallback to OpenAI GPT-4
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=3000,
                    temperature=0.3
                )
                
                print("✅ Used OpenAI GPT-4 (fallback)")
                return response.choices[0].message.content
                
            except Exception as e2:
                print(f"❌ Both Claude and OpenAI failed. Claude: {e}, OpenAI: {e2}")
                return None

    def parse_facts_from_response(self, claude_response):
        """Parse individual facts from Claude's response"""
        facts = []
        
        if not claude_response:
            return facts
            
        lines = claude_response.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('FACT:'):
                fact_text = line[5:].strip()  # Remove 'FACT:' prefix
                if fact_text:
                    facts.append(fact_text)
        
        return facts

    def process_first_article(self):
        """Process the first article and extract facts"""
        
        # Get the output path from environment
        content_output_path = os.getenv('CONTENT_OUTPUT_PATH', '.')
        articles_dir = Path(content_output_path) / 'articles-ai'
        
        if not articles_dir.exists():
            print(f"❌ Articles directory not found: {articles_dir}")
            return None
        
        # Find the first article (sorted)
        article_files = sorted(list(articles_dir.glob('*.md')))
        
        if not article_files:
            print(f"❌ No articles found in {articles_dir}")
            return None
        
        first_article = article_files[0]
        print(f"📄 Processing first article: {first_article.name}")
        
        # Read and parse the article
        try:
            with open(first_article, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            article_title = post.metadata.get('title', first_article.stem)
            article_content = post.content
            
            print(f"📖 Title: {article_title}")
            print(f"📊 Content length: {len(article_content)} characters")
            print()
            
        except Exception as e:
            print(f"❌ Error reading article: {e}")
            return None
        
        # Extract facts using Claude
        print("🤖 Extracting facts with Claude Sonnet 4...")
        claude_response = self.extract_facts_from_article(article_content, article_title)
        
        if not claude_response:
            print("❌ Failed to extract facts")
            return None
        
        # Parse facts from response
        facts = self.parse_facts_from_response(claude_response)
        
        print(f"✅ Extracted {len(facts)} facts")
        print()
        
        # Write to temporary file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_file = Path(__file__).parent / f'extracted_facts_{timestamp}.txt'
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(f"FACT EXTRACTION RESULTS\n")
            f.write(f"=" * 50 + "\n")
            f.write(f"Article: {article_title}\n")
            f.write(f"File: {first_article.name}\n")
            f.write(f"Extraction Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Facts: {len(facts)}\n")
            f.write(f"\n")
            
            f.write("EXTRACTED FACTS:\n")
            f.write("-" * 30 + "\n")
            
            for i, fact in enumerate(facts, 1):
                f.write(f"{i:2d}. {fact}\n")
            
            f.write(f"\n")
            f.write("RAW CLAUDE RESPONSE:\n")
            f.write("-" * 30 + "\n")
            f.write(claude_response)
        
        print(f"💾 Facts saved to: {temp_file}")
        print(f"📈 Summary:")
        print(f"   - Article: {first_article.name}")
        print(f"   - Facts extracted: {len(facts)}")
        print(f"   - Output file: {temp_file.name}")
        
        # Display first few facts for preview
        print(f"\n🔍 Preview of extracted facts:")
        for i, fact in enumerate(facts[:5], 1):
            print(f"   {i}. {fact}")
        
        if len(facts) > 5:
            print(f"   ... and {len(facts) - 5} more facts")
        
        return {
            'article_file': first_article,
            'article_title': article_title,
            'facts': facts,
            'output_file': temp_file
        }

def main():
    """Main function"""
    print("🎯 BASIC FACT EXTRACTION")
    print("=" * 40)
    
    extractor = BasicFactExtractor()
    
    try:
        result = extractor.process_first_article()
        
        if result:
            print("\n✅ Fact extraction completed successfully!")
        else:
            print("\n❌ Fact extraction failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()