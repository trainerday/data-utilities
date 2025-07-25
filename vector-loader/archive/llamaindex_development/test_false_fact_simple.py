#!/usr/bin/env python3
"""
Simplified test for false fact detection using direct query approach
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv
import openai
import json

load_dotenv()

def test_false_fact_simple():
    """Simple test for ALT key false fact detection"""
    
    # Set OpenAI API key
    openai.api_key = os.getenv('OPENAI_API_KEY')
    
    # Query about ALT key duplication
    query = "Can I use duplication feature by holding the ALT key and dragging?"
    
    try:
        print("🔍 TESTING FALSE FACT DETECTION")
        print("=" * 50)
        print(f"Query: {query}")
        print()
        
        # Create embedding for the query
        response = openai.embeddings.create(
            model="text-embedding-3-large",
            input=query,
            dimensions=1536
        )
        query_embedding = response.data[0].embedding
        
        # Connect to local PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="trainerday_local",
            user=os.getenv('USER', 'alex'),
            password=""
        )
        
        cur = conn.cursor()
        
        # Search for similar documents
        cur.execute("""
            SELECT text, metadata_->>'source' as source,
                   metadata_->>'content_type' as content_type,
                   metadata_->>'priority' as priority,
                   metadata_->>'fact_status' as fact_status,
                   embedding <=> %s::vector as distance
            FROM llamaindex_knowledge_base 
            ORDER BY distance LIMIT 10
        """, (query_embedding,))
        
        results = cur.fetchall()
        
        print("📊 TOP SEARCH RESULTS:")
        print("=" * 50)
        
        false_fact_found = False
        
        for i, row in enumerate(results, 1):
            text, source, content_type, priority, fact_status, distance = row
            
            # Truncate text for display
            display_text = text[:150] + "..." if len(text) > 150 else text
            
            print(f"{i}. Distance: {distance:.4f}")
            print(f"   Source: {source} ({content_type or 'N/A'})")
            print(f"   Priority: {priority}")
            if fact_status:
                print(f"   Status: {fact_status}")
            print(f"   Text: {display_text}")
            
            # Check if this is a false fact warning
            if "DO NOT USE IN ARTICLES" in text:
                print("   🚨 FALSE FACT WARNING DETECTED!")
                false_fact_found = True
            
            print()
        
        # Search specifically for facts about ALT/duplication
        print("🔍 SEARCHING FOR ALT/DUPLICATION FACTS:")
        print("=" * 50)
        
        cur.execute("""
            SELECT text, metadata_->>'content_type' as content_type,
                   metadata_->>'fact_status' as fact_status,
                   embedding <=> %s::vector as distance
            FROM llamaindex_knowledge_base 
            WHERE metadata_->>'source' = 'facts'
            AND (LOWER(text) LIKE '%alt%' OR LOWER(text) LIKE '%drag%' OR LOWER(text) LIKE '%duplicat%')
            ORDER BY distance LIMIT 5
        """, (query_embedding,))
        
        fact_results = cur.fetchall()
        
        if fact_results:
            for i, row in enumerate(fact_results, 1):
                text, content_type, fact_status, distance = row
                print(f"{i}. Distance: {distance:.4f}")
                print(f"   Type: {content_type}")
                print(f"   Status: {fact_status}")
                print(f"   Text: {text}")
                
                if "DO NOT USE IN ARTICLES" in text:
                    print("   🚨 CORRECTIVE WARNING FOUND!")
                    false_fact_found = True
                
                print()
        else:
            print("No specific facts found about ALT key or duplication")
        
        print("=" * 50)
        if false_fact_found:
            print("✅ SUCCESS: False fact detection system is working!")
            print("   The system found corrective warnings to prevent misinformation.")
        else:
            print("⚠️  No false fact warnings found for this query.")
            print("   This might mean the false fact isn't in the knowledge base,")
            print("   or the query doesn't match it closely enough.")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error testing query: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_false_fact_simple()