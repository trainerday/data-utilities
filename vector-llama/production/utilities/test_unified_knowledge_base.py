#!/usr/bin/env python3
"""
Test Unified Knowledge Base - Quick test to verify blog + forum data
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.storage.storage_context import StorageContext
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

import sqlalchemy

load_dotenv()

def test_unified_knowledge_base():
    """Test the unified knowledge base with blog + forum data"""
    
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
    
    print("🧪 UNIFIED KNOWLEDGE BASE TEST")
    print("=" * 50)
    
    # Check database stats first
    try:
        connection_string = f"postgresql://{local_db_config['user']}@{local_db_config['host']}:{local_db_config['port']}/{local_db_config['database']}"
        engine = sqlalchemy.create_engine(connection_string)
        
        with engine.connect() as conn:
            # Total documents
            result = conn.execute(sqlalchemy.text(
                "SELECT COUNT(*) as total FROM llamaindex_knowledge_base"
            ))
            total_docs = result.fetchone()[0]
            print(f"📄 Total Documents: {total_docs:,}")
            
            # By source and priority
            result = conn.execute(sqlalchemy.text(
                "SELECT metadata_->>'source' as source, metadata_->>'priority' as priority, COUNT(*) as count FROM llamaindex_knowledge_base GROUP BY metadata_->>'source', metadata_->>'priority' ORDER BY count DESC"
            ))
            breakdown = result.fetchall()
            print(f"📊 Content Breakdown:")
            for source, priority, count in breakdown:
                print(f"  • {source} ({priority}): {count:,}")
            
            # Sample blog content
            result = conn.execute(sqlalchemy.text(
                "SELECT metadata_->>'title' as title FROM llamaindex_knowledge_base WHERE metadata_->>'source' = 'blog' LIMIT 3"
            ))
            blog_titles = result.fetchall()
            print(f"\n📖 Sample Blog Articles:")
            for title, in blog_titles:
                print(f"  • {title}")
                
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return
    
    # Test LlamaIndex connection
    try:
        print(f"\n🔧 Connecting to unified knowledge base...")
        
        # Connect to unified knowledge base
        vector_store = PGVectorStore.from_params(
            database=local_db_config['database'],
            host=local_db_config['host'],
            password=local_db_config['password'],
            port=local_db_config['port'],
            user=local_db_config['user'],
            table_name="llamaindex_knowledge_base",
            embed_dim=1536,
        )
        
        # Create fresh index
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            storage_context=storage_context
        )
        
        print("✅ Connected successfully")
        
        # Test simple query
        print(f"\n🔍 Testing blog content priority...")
        query_engine = index.as_query_engine(
            similarity_top_k=5,
            response_mode="compact"
        )
        
        response = query_engine.query("What is TrainerDay Coach Jack?")
        print(f"Query: 'What is TrainerDay Coach Jack?'")
        print(f"Response: {response}")
        
        # Check sources
        if hasattr(response, 'source_nodes'):
            print(f"\n📚 Sources ({len(response.source_nodes)} found):")
            for i, node in enumerate(response.source_nodes[:3]):
                metadata = node.metadata
                source = metadata.get('source', 'unknown')
                priority = metadata.get('priority', 'unknown')
                title = metadata.get('title', 'Unknown')[:50]
                print(f"  {i+1}. {source} ({priority}): {title}...")
        
    except Exception as e:
        print(f"❌ LlamaIndex test failed: {e}")

if __name__ == "__main__":
    test_unified_knowledge_base()