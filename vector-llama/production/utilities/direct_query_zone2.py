#!/usr/bin/env python3
"""
Direct Query - Zone 2 Training with TrainerDay
Uses direct PostgreSQL vector search since it's working perfectly
"""

import os
import psycopg2
from dotenv import load_dotenv
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

load_dotenv()

def query_zone2_training():
    """Query everything about Zone 2 training with TrainerDay app"""
    
    print("🔍 ZONE 2 TRAINING KNOWLEDGE QUERY")
    print("=" * 50)
    
    # Create embedding for the query
    embedding_model = OpenAIEmbedding(
        model="text-embedding-3-large", 
        dimensions=1536
    )
    
    query = "Zone 2 training TrainerDay app how to do low intensity endurance"
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
            # Get top relevant documents with content
            cur.execute("""
                SELECT 
                    text,
                    metadata_->>'title' as title,
                    metadata_->>'source' as source,
                    metadata_->>'priority' as priority,
                    embedding <=> %s::vector as distance
                FROM llamaindex_knowledge_base 
                WHERE embedding IS NOT NULL
                ORDER BY distance
                LIMIT 10
            """, (query_embedding,))
            
            results = cur.fetchall()
            
            print(f"📊 Found {len(results)} relevant documents:\n")
            
            # Collect content for LLM analysis
            relevant_content = []
            
            for i, (text, title, source, priority, distance) in enumerate(results):
                print(f"**{i+1}. {title}** ({source} - {priority} priority)")
                print(f"   Relevance: {distance:.3f}")
                print(f"   Preview: {text[:150].replace('\n', ' ')}...")
                print()
                
                # Add to content for LLM processing
                relevant_content.append({
                    'title': title,
                    'source': source,
                    'priority': priority,
                    'distance': distance,
                    'content': text
                })
            
            # Use LLM to synthesize information
            print("🤖 SYNTHESIZED ANSWER:")
            print("=" * 30)
            
            llm = OpenAI(model="gpt-4o-mini", temperature=0.1)
            
            # Create comprehensive prompt
            content_text = "\n\n---\n\n".join([
                f"Source: {item['source']} ({item['priority']} priority)\n"
                f"Title: {item['title']}\n"
                f"Content: {item['content']}"
                for item in relevant_content[:5]  # Top 5 most relevant
            ])
            
            prompt = f"""Based on the following TrainerDay knowledge base content, provide a comprehensive answer about Zone 2 training with the TrainerDay app. Include:

1. What Zone 2 training is
2. How to do Zone 2 training in TrainerDay
3. Benefits and recommendations
4. Any specific TrainerDay features for Zone 2

Knowledge Base Content:
{content_text}

Question: Everything the TrainerDay app knows about Zone 2 training - how to do it, benefits, and app-specific features.

Provide a detailed, practical answer based only on the information provided."""

            response = llm.complete(prompt)
            
            print(response.text)
            
            print("\n" + "=" * 50)
            print("📚 SOURCES USED:")
            for item in relevant_content[:5]:
                print(f"• {item['source']} ({item['priority']}): {item['title']}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    query_zone2_training()