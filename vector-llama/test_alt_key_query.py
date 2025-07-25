#!/usr/bin/env python3
"""
Direct Query - ALT Key Duplication Test
Query about false fact to test misinformation prevention
"""

import os
import psycopg2
from dotenv import load_dotenv
from llama_index.embeddings.openai import OpenAIEmbedding

load_dotenv()

def query_alt_key_duplication():
    """Query about ALT key duplication to test false fact detection"""
    
    print("🔍 ALT KEY DUPLICATION FALSE FACT TEST")
    print("=" * 50)
    
    # Create embedding for the query
    embedding_model = OpenAIEmbedding(
        model="text-embedding-3-large", 
        dimensions=1536
    )
    
    query = "Can I use duplication feature by holding the ALT key and dragging?"
    print(f"Query: '{query}'")
    print("=" * 50)
    
    query_embedding = embedding_model.get_text_embedding(query)
    
    # Connect to database
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='trainerday_local',
        user=os.getenv('USER', 'alex'),
        password=''
    )
    
    try:
        with conn.cursor() as cur:
            # Get top relevant documents
            cur.execute("""
                SELECT 
                    text,
                    metadata_->>'title' as title,
                    metadata_->>'source' as source,
                    metadata_->>'priority' as priority,
                    metadata_->>'content_type' as content_type,
                    metadata_->>'fact_status' as fact_status,
                    embedding <=> %s::vector as distance
                FROM llamaindex_knowledge_base 
                ORDER BY distance 
                LIMIT 10
            """, (query_embedding,))
            
            results = cur.fetchall()
            
            print(f"📊 Found {len(results)} relevant documents:\n")
            
            false_fact_found = False
            
            for i, row in enumerate(results, 1):
                text, title, source, priority, content_type, fact_status, distance = row
                
                print(f"**{i}. {title or 'None'}** ({source} - {priority} priority)")
                print(f"   Content Type: {content_type or 'N/A'}")
                if fact_status:
                    print(f"   Fact Status: {fact_status}")
                print(f"   Relevance: {distance:.3f}")
                
                # Check for false fact warning
                if "DO NOT USE IN ARTICLES" in text:
                    print("   🚨 **FALSE FACT WARNING DETECTED!**")
                    false_fact_found = True
                
                # Show preview
                preview = text[:150] + "..." if len(text) > 150 else text
                print(f"   Preview: {preview}")
                print()
            
            # Search specifically for facts about ALT/duplication
            print("🔍 SEARCHING SPECIFICALLY FOR ALT/DUPLICATION FACTS:")
            print("=" * 50)
            
            cur.execute("""
                SELECT 
                    text,
                    metadata_->>'content_type' as content_type,
                    metadata_->>'fact_status' as fact_status,
                    embedding <=> %s::vector as distance
                FROM llamaindex_knowledge_base 
                WHERE metadata_->>'source' = 'facts'
                AND (LOWER(text) LIKE '%alt%' OR LOWER(text) LIKE '%drag%' OR LOWER(text) LIKE '%duplicat%')
                ORDER BY distance 
                LIMIT 5
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
                        print("   🚨 **CORRECTIVE WARNING FOUND!**")
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
                print("   This might mean:")
                print("   - The false fact isn't in the knowledge base")
                print("   - The query doesn't match it closely enough")
                print("   - The facts were loaded into a different table")
        
    finally:
        conn.close()

if __name__ == "__main__":
    query_alt_key_duplication()