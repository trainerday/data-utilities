#!/usr/bin/env python3
"""
Enhanced article generation that applies edits during generation.
This version checks for existing edits and applies them during the generation process.
"""

import os
import sys
import json
from pathlib import Path

# Import the original generator
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from generate_article import SectionalArticleGenerator


class EnhancedArticleGenerator(SectionalArticleGenerator):
    """Enhanced generator that applies edits during generation"""
    
    def __init__(self):
        super().__init__()
        self.edits_path = Path("article-queries/edits")
    
    def load_user_edits(self) -> dict:
        """Load user edits from the edit tracking system"""
        edits_file = self.edits_path / "workout-edits.json"
        
        if edits_file.exists():
            with open(edits_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "global_instructions": {
                    "style": [],
                    "facts_to_avoid": []
                },
                "articles": {}
            }
    
    def apply_edits_to_prompt(self, prompt: str, section_name: str, user_edits: dict) -> str:
        """Modify the prompt to include edit instructions"""
        
        edit_instructions = []
        
        # Clean section name for matching
        clean_name = section_name.replace(' ', '_').replace('(', '').replace(')', '').replace(',', '').replace("'", '')
        
        # Check for article-specific edits
        for article_key in user_edits.get("articles", {}):
            if clean_name in article_key:
                article_edits = user_edits["articles"][article_key]
                
                if article_edits.get("edit_instructions"):
                    edit_instructions.extend(article_edits["edit_instructions"])
                
                if article_edits.get("facts_to_add"):
                    edit_instructions.append(f"IMPORTANT: Include these facts - {', '.join(article_edits['facts_to_add'])}")
                
                if article_edits.get("facts_to_remove"):
                    edit_instructions.append(f"IMPORTANT: Do NOT include these facts - {', '.join(article_edits['facts_to_remove'])}")
                
                if article_edits.get("custom_sections"):
                    for section in article_edits["custom_sections"]:
                        edit_instructions.append(f"Add a section titled '{section['title']}' with this content: {section['content']}")
        
        # Apply global instructions
        if user_edits.get("global_instructions", {}).get("facts_to_avoid"):
            facts_to_avoid = user_edits["global_instructions"]["facts_to_avoid"]
            if facts_to_avoid:
                edit_instructions.append(f"GLOBAL: Never include these facts - {', '.join(facts_to_avoid)}")
        
        # If we have edit instructions, append them to the prompt
        if edit_instructions:
            edits_section = "\n\nAPPLY THESE EDITS:\n" + "\n".join(f"- {edit}" for edit in edit_instructions)
            prompt += edits_section
        
        return prompt
    
    def generate_section(self, section_name: str, content: dict, bad_facts: str) -> str:
        """Generate a single instructional section with edits applied"""
        
        # Load user edits
        user_edits = self.load_user_edits()
        
        # Get base prompt
        template = self.load_section_template()
        content_formatted = self.format_section_content(content)
        
        prompt = template.format(
            section_name=section_name,
            content_sections=content_formatted,
            bad_facts_section=bad_facts
        )
        
        # Apply edits to prompt
        prompt = self.apply_edits_to_prompt(prompt, section_name, user_edits)
        
        # Generate with the modified prompt
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.3
            )
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"OpenAI error: {e}, falling back to Claude")
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.3
            )
            return response.content[0].text


def main():
    generator = EnhancedArticleGenerator()
    generator.generate()


if __name__ == "__main__":
    main()