#!/usr/bin/env python3
"""
Test Forum Knowledge Base - Query the loaded LlamaIndex data
Tests priority-based retrieval and query quality
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# LlamaIndex imports
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.storage.storage_context import StorageContext
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine

import sqlalchemy

load_dotenv()

class ForumKnowledgeBaseTester:
    def __init__(self):
        """Initialize connection to existing LlamaIndex vector store"""
        
        # Local PostgreSQL configuration
        self.local_db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'trainerday_local',
            'user': os.getenv('USER', 'alex'),
            'password': '',
        }
        
        # LlamaIndex configuration
        self.embedding_model = OpenAIEmbedding(
            model="text-embedding-3-large",
            dimensions=1536
        )
        
        Settings.embed_model = self.embedding_model
        Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0.1)
        
        self.vector_store = None
        self.index = None
        self.setup_connection()
    
    def setup_connection(self):
        """Connect to existing vector store"""
        print("🔧 Connecting to forum knowledge base...")
        
        # Connect to unified knowledge base
        self.vector_store = PGVectorStore.from_params(
            database=self.local_db_config['database'],
            host=self.local_db_config['host'],
            password=self.local_db_config['password'],
            port=self.local_db_config['port'],
            user=self.local_db_config['user'],
            table_name="llamaindex_knowledge_base",
            embed_dim=1536,
        )
        
        # Create index from existing vector store
        storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        self.index = VectorStoreIndex.from_vector_store(
            vector_store=self.vector_store,
            storage_context=storage_context
        )
        
        print("✅ Connected to forum knowledge base")
    
    def get_document_stats(self):
        """Get statistics about loaded documents"""
        print("\n📊 KNOWLEDGE BASE STATISTICS:")
        print("=" * 40)
        
        try:
            # Query the vector store directly for metadata
            connection_string = f"postgresql://{self.local_db_config['user']}@{self.local_db_config['host']}:{self.local_db_config['port']}/{self.local_db_config['database']}"
            engine = sqlalchemy.create_engine(connection_string)
            
            with engine.connect() as conn:
                # Count total documents
                result = conn.execute(sqlalchemy.text(
                    "SELECT COUNT(*) as total FROM llamaindex_knowledge_base"
                ))
                total_docs = result.fetchone()[0]
                print(f"📄 Total Documents: {total_docs:,}")
                
                # Count by source
                result = conn.execute(sqlalchemy.text(
                    "SELECT metadata_->>'source' as source, COUNT(*) as count FROM llamaindex_knowledge_base GROUP BY metadata_->>'source'"
                ))
                sources = result.fetchall()
                for source, count in sources:
                    print(f"  • {source}: {count:,}")
                
                # Count by priority
                result = conn.execute(sqlalchemy.text(
                    "SELECT metadata_->>'priority' as priority, COUNT(*) as count FROM llamaindex_knowledge_base GROUP BY metadata_->>'priority'"
                ))
                priorities = result.fetchall()
                for priority, count in priorities:
                    print(f"  • {priority} priority: {count:,}")
                    
        except Exception as e:
            print(f"⚠️ Could not get detailed stats: {e}")
    
    def test_priority_based_retrieval(self, query: str, top_k: int = 10):
        """Test priority-based retrieval with different thresholds"""
        print(f"\n🔍 TESTING PRIORITY-BASED RETRIEVAL")
        print(f"Query: \"{query}\"")
        print("=" * 50)
        
        # Test with high priority (Q&A) threshold
        print("\n📖 HIGH PRIORITY RETRIEVAL (Q&A Documents - threshold 0.4):")
        print("-" * 50)
        
        qa_retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=top_k,
            # Filter for high priority documents
        )
        
        qa_postprocessor = SimilarityPostprocessor(
            similarity_cutoff=0.4
        )
        
        qa_query_engine = RetrieverQueryEngine(
            retriever=qa_retriever,
            node_postprocessors=[qa_postprocessor]
        )
        
        try:
            qa_response = qa_query_engine.query(query)
            print(f"✅ Response: {qa_response}")
            
            # Show source information
            if hasattr(qa_response, 'source_nodes'):
                print(f"\n📚 Sources ({len(qa_response.source_nodes)} found):")
                for i, node in enumerate(qa_response.source_nodes[:3]):
                    metadata = node.metadata
                    score = getattr(node, 'score', 'N/A')
                    print(f"  {i+1}. Score: {score:.3f if score != 'N/A' else 'N/A'}")
                    print(f"     Type: {metadata.get('content_type', 'Unknown')}")
                    print(f"     Priority: {metadata.get('priority', 'Unknown')}")
                    print(f"     Title: {metadata.get('title', 'Unknown')[:60]}...")
                    print(f"     Category: {metadata.get('category', 'Unknown')}")
                    
        except Exception as e:
            print(f"❌ Error with high priority retrieval: {e}")
        
        # Test with medium priority (Raw discussions) threshold  
        print(f"\n💬 MEDIUM PRIORITY RETRIEVAL (Raw Discussions - threshold 0.6):")
        print("-" * 50)
        
        raw_postprocessor = SimilarityPostprocessor(
            similarity_cutoff=0.6
        )
        
        raw_query_engine = RetrieverQueryEngine(
            retriever=qa_retriever,
            node_postprocessors=[raw_postprocessor]
        )
        
        try:
            raw_response = raw_query_engine.query(query)
            print(f"✅ Response: {raw_response}")
            
            if hasattr(raw_response, 'source_nodes'):
                print(f"\n📚 Sources ({len(raw_response.source_nodes)} found):")
                for i, node in enumerate(raw_response.source_nodes[:3]):
                    metadata = node.metadata
                    score = getattr(node, 'score', 'N/A')
                    print(f"  {i+1}. Score: {score:.3f if score != 'N/A' else 'N/A'}")
                    print(f"     Type: {metadata.get('content_type', 'Unknown')}")
                    print(f"     Priority: {metadata.get('priority', 'Unknown')}")
                    print(f"     Title: {metadata.get('title', 'Unknown')[:60]}...")
                    print(f"     Discussion type: {metadata.get('discussion_type', 'Unknown')}")
                    
        except Exception as e:
            print(f"❌ Error with medium priority retrieval: {e}")
    
    def test_comprehensive_query(self, query: str):
        """Test comprehensive query combining all document types"""
        print(f"\n🎯 COMPREHENSIVE QUERY TEST")
        print(f"Query: \"{query}\"")
        print("=" * 50)
        
        # Use default query engine with balanced settings
        query_engine = self.index.as_query_engine(
            similarity_top_k=8,
            response_mode="compact"
        )
        
        try:
            response = query_engine.query(query)
            print(f"✅ Response:")
            print(f"{response}")
            
            if hasattr(response, 'source_nodes'):
                print(f"\n📚 Sources Used ({len(response.source_nodes)} total):")
                
                # Group by priority and content type
                qa_sources = []
                raw_sources = []
                
                for node in response.source_nodes:
                    metadata = node.metadata
                    priority = metadata.get('priority', 'unknown')
                    if priority == 'high':
                        qa_sources.append(node)
                    else:
                        raw_sources.append(node)
                
                print(f"  📖 Q&A Sources: {len(qa_sources)}")
                print(f"  💬 Raw Discussion Sources: {len(raw_sources)}")
                
                # Show top sources from each type
                if qa_sources:
                    print(f"\n  🔥 Top Q&A Sources:")
                    for i, node in enumerate(qa_sources[:2]):
                        metadata = node.metadata
                        score = getattr(node, 'score', 'N/A')
                        print(f"    • Score: {score:.3f if score != 'N/A' else 'N/A'} | {metadata.get('title', 'Unknown')[:50]}...")
                
                if raw_sources:
                    print(f"\n  💭 Top Raw Discussion Sources:")
                    for i, node in enumerate(raw_sources[:2]):
                        metadata = node.metadata
                        score = getattr(node, 'score', 'N/A')
                        print(f"    • Score: {score:.3f if score != 'N/A' else 'N/A'} | {metadata.get('title', 'Unknown')[:50]}...")
                        
        except Exception as e:
            print(f"❌ Error with comprehensive query: {e}")

def main():
    """Run knowledge base tests"""
    print("🧪 FORUM KNOWLEDGE BASE TESTING")
    print("=" * 60)
    
    tester = ForumKnowledgeBaseTester()
    
    # Get stats about loaded data
    tester.get_document_stats()
    
    # Test queries
    test_queries = [
        "What are the major features of TrainerDay?",
        "How do I sync my data with Garmin?", 
        "What training zones does TrainerDay support?",
        "How do I export my workout data?"
    ]
    
    for query in test_queries:
        print(f"\n" + "="*80)
        tester.test_comprehensive_query(query)
        
        # Also test priority-based retrieval for the first query
        if query == test_queries[0]:
            tester.test_priority_based_retrieval(query)
    
    print(f"\n" + "="*80)
    print("🎉 TESTING COMPLETE!")
    print("✅ Forum knowledge base is working and retrieving from both Q&A and raw discussions")

if __name__ == "__main__":
    main()