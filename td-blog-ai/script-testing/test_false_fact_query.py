#!/usr/bin/env python3
"""
Test query against unified knowledge base to see if it catches FALSE facts
Query: "Can I use duplication feature by holding the ALT key and dragging?"
"""

import os
import sys
import sqlalchemy
from dotenv import load_dotenv
import openai
import numpy as np

load_dotenv()

def test_false_fact_query():
    """Test query for ALT key duplication to see if we catch the false fact"""
    
    # Set OpenAI API key
    openai.api_key = os.getenv('OPENAI_API_KEY')
    
    # Local PostgreSQL configuration
    local_db_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'trainerday_local',
        'user': os.getenv('USER', 'alex'),
        'password': '',
    }
    
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
        
        # Connect to database
        connection_string = f"postgresql://{local_db_config['user']}@{local_db_config['host']}:{local_db_config['port']}/{local_db_config['database']}"
        engine = sqlalchemy.create_engine(connection_string)
        
        with engine.connect() as conn:
            # Convert embedding to string format for PostgreSQL
            embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
            
            # Search for most similar documents with priority awareness
            result = conn.execute(sqlalchemy.text("""
                SELECT 
                    text,
                    metadata_->>'source' as source,
                    metadata_->>'content_type' as content_type,
                    metadata_->>'priority' as priority,
                    metadata_->>'similarity_threshold' as threshold,
                    metadata_->>'fact_status' as fact_status,
                    embedding <=> %(embedding)s::vector as distance
                FROM llamaindex_knowledge_base 
                ORDER BY distance 
                LIMIT 15
            """), {"embedding": embedding_str})
            
            results = result.fetchall()
            
            print("📊 TOP SEARCH RESULTS:")
            print("=" * 50)
            
            for i, row in enumerate(results[:10], 1):
                text, source, content_type, priority, threshold, fact_status, distance = row
                
                # Truncate text for display
                display_text = text[:100] + "..." if len(text) > 100 else text
                
                print(f"{i}. Distance: {distance:.4f}")
                print(f"   Source: {source} ({content_type})")
                print(f"   Priority: {priority} (threshold: {threshold})")
                if fact_status:
                    print(f"   Status: {fact_status}")
                print(f"   Text: {display_text}")
                
                # Check if this is a false fact warning
                if "DO NOT USE IN ARTICLES" in text:
                    print("   🚨 FALSE FACT WARNING DETECTED!")
                
                print()
            
            # Look specifically for facts about ALT key or duplication
            print("🔍 SEARCHING SPECIFICALLY FOR ALT/DUPLICATION FACTS:")
            print("=" * 50)
            
            result = conn.execute(sqlalchemy.text("""
                SELECT 
                    text,
                    metadata_->>'content_type' as content_type,
                    metadata_->>'fact_status' as fact_status,
                    embedding <=> %(embedding)s::vector as distance
                FROM llamaindex_knowledge_base 
                WHERE metadata_->>'source' = 'facts'
                AND (LOWER(text) LIKE '%alt%' OR LOWER(text) LIKE '%drag%' OR LOWER(text) LIKE '%duplicat%')
                ORDER BY distance 
                LIMIT 5
            """), {"embedding": embedding_str})
            
            fact_results = result.fetchall()
            
            if fact_results:
                for i, row in enumerate(fact_results, 1):
                    text, content_type, fact_status, distance = row
                    print(f"{i}. Distance: {distance:.4f}")
                    print(f"   Type: {content_type}")
                    print(f"   Status: {fact_status}")
                    print(f"   Text: {text}")
                    
                    if "DO NOT USE IN ARTICLES" in text:
                        print("   🚨 CORRECTIVE WARNING FOUND!")
                    
                    print()
            else:
                print("No specific facts found about ALT key or duplication")
                
    except Exception as e:
        print(f"Error testing query: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_false_fact_query()