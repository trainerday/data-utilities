#!/usr/bin/env python3
"""
Simple LlamaIndex test - minimal POC to verify setup
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Simple test without database first
from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

load_dotenv()

def simple_test():
    """Simple test with in-memory storage"""
    
    # Configure LlamaIndex
    Settings.embed_model = OpenAIEmbedding(
        model="text-embedding-3-large",
        dimensions=1536
    )
    Settings.llm = OpenAI(model="gpt-4-turbo-preview")
    
    # Create sample documents
    documents = [
        Document(
            text="TrainerDay is a cycling training platform that helps cyclists improve their performance through structured workouts and training plans.",
            metadata={"source": "blog", "title": "TrainerDay Overview"}
        ),
        Document(
            text="To sync your Garmin watch with TrainerDay, go to Settings > Connections > Garmin Connect and follow the authorization process.",
            metadata={"source": "forum", "title": "Garmin Sync Guide"}
        ),
        Document(
            text="FTP testing is crucial for power-based training. The ramp test is the most accurate way to determine your Functional Threshold Power.",
            metadata={"source": "youtube", "title": "FTP Testing Explained"}
        )
    ]
    
    print("Creating simple in-memory index...")
    index = VectorStoreIndex.from_documents(documents)
    
    # Create query engine
    query_engine = index.as_query_engine()
    
    # Test queries
    queries = [
        "How do I sync my Garmin?",
        "What is FTP testing?",
        "Tell me about TrainerDay"
    ]
    
    print("\n=== SIMPLE LLAMAINDEX TEST ===")
    
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 40)
        
        response = query_engine.query(query)
        print(f"Response: {response}")
        
        # Show sources
        if hasattr(response, 'source_nodes'):
            print(f"Sources: {len(response.source_nodes)} documents used")
            for i, node in enumerate(response.source_nodes[:2]):
                print(f"  {i+1}. {node.metadata.get('title', 'Unknown')}")

if __name__ == "__main__":
    simple_test()