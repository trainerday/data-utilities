#!/usr/bin/env python3
"""
Simple Query Test - Debug why queries are returning empty
"""

import os
from dotenv import load_dotenv

from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.storage.storage_context import StorageContext
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

load_dotenv()

def simple_query_test():
    # Setup
    embedding_model = OpenAIEmbedding(model="text-embedding-3-large", dimensions=1536)
    Settings.embed_model = embedding_model
    Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0.1)
    
    local_db_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'trainerday_local',
        'user': os.getenv('USER', 'alex'),
        'password': '',
    }
    
    print("🔍 SIMPLE QUERY DEBUG TEST")
    print("=" * 40)
    
    try:
        # Connect
        vector_store = PGVectorStore.from_params(
            database=local_db_config['database'],
            host=local_db_config['host'],
            password=local_db_config['password'],
            port=local_db_config['port'],
            user=local_db_config['user'],
            table_name="llamaindex_knowledge_base",
            embed_dim=1536,
        )
        
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            storage_context=storage_context
        )
        
        # Test with very basic query and low threshold
        retriever = index.as_retriever(similarity_top_k=10)
        
        print("🔍 Testing retrieval with 'TrainerDay'...")
        nodes = retriever.retrieve("TrainerDay")
        print(f"Retrieved {len(nodes)} nodes")
        
        for i, node in enumerate(nodes[:3]):
            metadata = node.metadata
            score = getattr(node, 'score', 'N/A')
            source = metadata.get('source', 'unknown')
            priority = metadata.get('priority', 'unknown')
            content_preview = node.text[:100].replace('\n', ' ')
            
            print(f"  {i+1}. Score: {score}")
            print(f"     Source: {source} ({priority})")
            print(f"     Content: {content_preview}...")
            print()
        
        # Now test query engine with no similarity filtering
        query_engine = index.as_query_engine(
            similarity_top_k=10,
            response_mode="compact"
        )
        
        print("🔍 Testing query engine with 'What is TrainerDay?'...")
        response = query_engine.query("What is TrainerDay?")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_query_test()