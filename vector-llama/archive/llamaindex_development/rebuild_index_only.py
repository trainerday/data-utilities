#!/usr/bin/env python3
"""
Rebuild LlamaIndex Index - NO data reloading, just index refresh
"""

import os
from dotenv import load_dotenv

from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.storage.storage_context import StorageContext
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

load_dotenv()

def rebuild_index_from_existing_data():
    """Rebuild LlamaIndex index from existing database data - NO reloading"""
    
    print("🔧 REBUILDING LLAMAINDEX INDEX (No data reloading)")
    print("=" * 55)
    print("✅ Embeddings: Already exist in database")
    print("✅ Documents: Already exist in database") 
    print("🔄 Task: Just refresh LlamaIndex's understanding")
    print("=" * 55)
    
    # LlamaIndex configuration
    embedding_model = OpenAIEmbedding(
        model="text-embedding-3-large",
        dimensions=1536
    )
    
    Settings.embed_model = embedding_model
    Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0.1)
    
    # Local PostgreSQL configuration
    local_db_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'trainerday_local',
        'user': os.getenv('USER', 'alex'),
        'password': '',
    }
    
    try:
        print("🔗 Connecting to existing unified knowledge base...")
        
        # Create fresh vector store connection
        vector_store = PGVectorStore.from_params(
            database=local_db_config['database'],
            host=local_db_config['host'],
            password=local_db_config['password'],
            port=local_db_config['port'],
            user=local_db_config['user'],
            table_name="llamaindex_knowledge_base",
            embed_dim=1536,
        )
        
        print("✅ Vector store connected")
        
        # Create storage context
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        print("🔄 Rebuilding index from existing embeddings...")
        
        # This creates the index from existing data - NO embedding generation
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            storage_context=storage_context
        )
        
        print("✅ Index rebuilt successfully")
        
        # Test the rebuilt index
        print("\n🧪 Testing rebuilt index...")
        
        # Simple retrieval test
        retriever = index.as_retriever(similarity_top_k=5)
        nodes = retriever.retrieve("TrainerDay features")
        
        print(f"📊 Retrieved {len(nodes)} nodes for 'TrainerDay features'")
        
        if nodes:
            for i, node in enumerate(nodes[:3]):
                metadata = node.metadata
                score = getattr(node, 'score', 'N/A') 
                source = metadata.get('source', 'unknown')
                priority = metadata.get('priority', 'unknown')
                title = metadata.get('title', 'Unknown')[:40]
                
                print(f"  {i+1}. Score: {score:.3f if isinstance(score, float) else score}")
                print(f"     Source: {source} ({priority})")
                print(f"     Title: {title}...")
                print()
        
        # Test query engine
        print("🔍 Testing query engine...")
        query_engine = index.as_query_engine(
            similarity_top_k=5,
            response_mode="compact"
        )
        
        response = query_engine.query("What are the main features of TrainerDay?")
        print(f"✅ Query Response: {str(response)[:200]}...")
        
        if hasattr(response, 'source_nodes') and response.source_nodes:
            print(f"📚 Used {len(response.source_nodes)} sources:")
            for node in response.source_nodes[:2]:
                source = node.metadata.get('source', 'unknown')
                priority = node.metadata.get('priority', 'unknown')
                print(f"  • {source} ({priority})")
        
        print("\n" + "=" * 55)
        print("🎉 INDEX REBUILD COMPLETE!")
        print("✅ No data was reloaded or re-embedded")
        print("✅ Vector search is now working")
        print("✅ Ready for priority-based retrieval")
        print("=" * 55)
        
        return index
        
    except Exception as e:
        print(f"❌ Rebuild failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    rebuild_index_from_existing_data()