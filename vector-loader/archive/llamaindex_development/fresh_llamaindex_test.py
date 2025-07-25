#!/usr/bin/env python3
"""
Fresh LlamaIndex Test - Clean setup that should work
"""

import os
from dotenv import load_dotenv

from llama_index.core import VectorStoreIndex, Settings, Document
from llama_index.core.storage.storage_context import StorageContext
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

load_dotenv()

def fresh_llamaindex_test():
    """Test LlamaIndex with completely fresh setup"""
    
    print("🆕 FRESH LLAMAINDEX TEST")
    print("=" * 30)
    
    # Setup LlamaIndex
    embedding_model = OpenAIEmbedding(
        model="text-embedding-3-large",
        dimensions=1536
    )
    
    Settings.embed_model = embedding_model
    Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0.1)
    
    try:
        print("🔧 Creating fresh vector store connection...")
        
        # Create vector store with from_params
        vector_store = PGVectorStore.from_params(
            database='trainerday_local',
            host='localhost',
            port=5432,
            user=os.getenv('USER', 'alex'),
            password='',
            table_name="llamaindex_knowledge_base",
            embed_dim=1536,
        )
        
        print("✅ Vector store created")
        
        # Create storage context
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        print("🔄 Creating index from vector store...")
        
        # Create index
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            storage_context=storage_context
        )
        
        print("✅ Index created")
        
        # Test retrieval with very permissive settings
        print("\n🔍 Testing retrieval...")
        
        retriever = index.as_retriever(
            similarity_top_k=10,
            # No similarity cutoff
        )
        
        nodes = retriever.retrieve("TrainerDay features")
        print(f"Retrieved {len(nodes)} nodes")
        
        for i, node in enumerate(nodes[:5]):
            metadata = node.metadata
            score = getattr(node, 'score', 'N/A')
            source = metadata.get('source', 'unknown')
            priority = metadata.get('priority', 'unknown')
            title = metadata.get('title', 'No title')[:50]
            
            print(f"  {i+1}. Score: {score}")
            print(f"     {source} ({priority}): {title}")
        
        # Test query engine
        if nodes:
            print(f"\n🎯 Testing query engine...")
            query_engine = index.as_query_engine(
                similarity_top_k=5,
                response_mode="compact"
            )
            
            response = query_engine.query("What are the main features of TrainerDay?")
            print(f"Response: {response}")
            
            if hasattr(response, 'source_nodes'):
                print(f"\nSources used: {len(response.source_nodes)}")
                for node in response.source_nodes[:3]:
                    source = node.metadata.get('source', 'unknown')
                    priority = node.metadata.get('priority', 'unknown')
                    print(f"  • {source} ({priority})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fresh_llamaindex_test()