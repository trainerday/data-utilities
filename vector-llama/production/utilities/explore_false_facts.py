#!/usr/bin/env python3
"""
Explore what false facts we have in the knowledge base
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def explore_false_facts():
    """Explore the false facts we have loaded"""
    
    try:
        # Connect to local PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="trainerday_local",
            user=os.getenv('USER', 'alex'),
            password=""
        )
        
        cur = conn.cursor()
        
        print("🔍 EXPLORING FALSE FACTS IN KNOWLEDGE BASE")
        print("=" * 60)
        
        # Get all false facts (wrong_fact type)
        cur.execute("""
            SELECT text, metadata_->>'fact_status' as fact_status
            FROM llamaindex_knowledge_base 
            WHERE metadata_->>'source' = 'facts'
            AND metadata_->>'content_type' = 'wrong_fact'
            ORDER BY text
            LIMIT 20
        """)
        
        wrong_facts = cur.fetchall()
        
        print(f"Found {len(wrong_facts)} wrong facts:")
        print()
        
        for i, (text, status) in enumerate(wrong_facts, 1):
            print(f"{i}. Status: {status}")
            print(f"   Text: {text}")
            print()
        
        # Search for any facts about duplication, ALT, drag, etc.
        print("🔍 SEARCHING FOR DUPLICATION/ALT/DRAG RELATED FACTS:")
        print("=" * 60)
        
        cur.execute("""
            SELECT text, metadata_->>'content_type' as content_type,
                   metadata_->>'fact_status' as fact_status
            FROM llamaindex_knowledge_base 
            WHERE metadata_->>'source' = 'facts'
            AND (LOWER(text) LIKE '%alt%' OR LOWER(text) LIKE '%drag%' 
                 OR LOWER(text) LIKE '%duplicat%' OR LOWER(text) LIKE '%copy%'
                 OR LOWER(text) LIKE '%ctrl%' OR LOWER(text) LIKE '%key%')
            ORDER BY text
        """)
        
        related_facts = cur.fetchall()
        
        if related_facts:
            print(f"Found {len(related_facts)} related facts:")
            print()
            
            for i, (text, content_type, status) in enumerate(related_facts, 1):
                print(f"{i}. Type: {content_type}, Status: {status}")
                print(f"   Text: {text}")
                print()
        else:
            print("No facts found about ALT, drag, duplication, copy, ctrl, or key")
        
        # Sample some random wrong facts to see what kinds we have
        print("🔍 SAMPLE OF OTHER WRONG FACTS:")
        print("=" * 60)
        
        cur.execute("""
            SELECT text
            FROM llamaindex_knowledge_base 
            WHERE metadata_->>'source' = 'facts'
            AND metadata_->>'content_type' = 'wrong_fact'
            ORDER BY RANDOM()
            LIMIT 5
        """)
        
        sample_facts = cur.fetchall()
        
        for i, (text,) in enumerate(sample_facts, 1):
            # Extract just the actual fact part (after "DO NOT USE IN ARTICLES:")
            if "DO NOT USE IN ARTICLES:" in text:
                fact_part = text.split("DO NOT USE IN ARTICLES:")[-1].strip()
                print(f"{i}. {fact_part[:100]}...")
            else:
                print(f"{i}. {text[:100]}...")
            print()
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error exploring facts: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    explore_false_facts()