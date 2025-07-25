#!/usr/bin/env python3
"""
Test OpenAI embedding creation directly
"""

import os
from dotenv import load_dotenv
import openai

load_dotenv()

def test_embedding_creation():
    """Test embedding creation with environment variables"""
    
    print("🧪 Testing OpenAI Embedding Creation")
    print("=" * 40)
    
    # Print environment variables
    model = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-large')
    dimensions = int(os.getenv('OPENAI_EMBEDDING_DIMENSIONS', '1536'))
    
    print(f"Model: {model}")
    print(f"Dimensions: {dimensions}")
    print(f"API Key present: {'✅' if os.getenv('OPENAI_API_KEY') else '❌'}")
    
    # Test embedding creation
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    try:
        response = client.embeddings.create(
            model=model,
            input="test query for power zones training",
            dimensions=dimensions
        )
        
        embedding = response.data[0].embedding
        print(f"\n✅ Embedding created successfully!")
        print(f"Actual dimensions: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
        
        return embedding
        
    except Exception as e:
        print(f"❌ Error creating embedding: {e}")
        return None

if __name__ == "__main__":
    test_embedding_creation()