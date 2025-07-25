#!/usr/bin/env python3
"""
Forum Data Loader - Step 1 Implementation
Loads forum data using dual document strategy into local PostgreSQL with LlamaIndex
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from dotenv import load_dotenv

# Add parent directory to path to import enhanced_forum_loader
sys.path.append(str(Path(__file__).parent))
from enhanced_forum_loader import EnhancedForumLoader

# LlamaIndex imports
from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.core.storage.storage_context import StorageContext
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

import sqlalchemy

load_dotenv()

# Setup logging with detailed output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('forum_loader_progress.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ForumDataLoaderStep1:
    def __init__(self):
        """Initialize the forum data loader with local PostgreSQL configuration"""
        
        # Local PostgreSQL configuration for LlamaIndex
        self.local_db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'trainerday_local',
            'user': os.getenv('USER', 'alex'),
            'password': '',  # No password for local development
        }
        
        # LlamaIndex configuration
        self.embedding_model = OpenAIEmbedding(
            model="text-embedding-3-large",
            dimensions=1536
        )
        
        # Configure LlamaIndex settings
        Settings.embed_model = self.embedding_model
        Settings.llm = OpenAI(model="gpt-4")
        
        # Initialize components
        self.forum_loader = EnhancedForumLoader()
        self.vector_store = None
        self.storage_context = None
        
        # Progress tracking
        self.progress = {
            'start_time': None,
            'qa_docs_processed': 0,
            'raw_docs_processed': 0,
            'total_qa_docs': 0,
            'total_raw_docs': 0,
            'embedding_cost_estimate': 0.0,
            'errors': []
        }
    
    def setup_vector_store(self, table_name: str = "llamaindex_forum_embeddings"):
        """Setup PGVectorStore for local PostgreSQL"""
        logger.info(f"🔧 Setting up vector store: {table_name}")
        
        # Create SQLAlchemy engine
        connection_string = f"postgresql://{self.local_db_config['user']}@{self.local_db_config['host']}:{self.local_db_config['port']}/{self.local_db_config['database']}"
        engine = sqlalchemy.create_engine(connection_string)
        
        # Initialize vector store
        self.vector_store = PGVectorStore.from_params(
            database=self.local_db_config['database'],
            host=self.local_db_config['host'],
            password=self.local_db_config['password'],
            port=self.local_db_config['port'],
            user=self.local_db_config['user'],
            table_name=table_name,
            embed_dim=1536,
        )
        
        # Create storage context
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        logger.info("✅ Vector store setup complete")
    
    def estimate_embedding_cost(self, documents: List[Document]) -> float:
        """Estimate OpenAI embedding cost for documents"""
        total_chars = sum(len(doc.text) for doc in documents)
        # OpenAI text-embedding-3-large: $0.00013 / 1K tokens
        # Estimate 4 chars per token
        estimated_tokens = total_chars / 4
        estimated_cost = (estimated_tokens / 1000) * 0.00013
        return estimated_cost
    
    def load_qa_documents(self, limit: Optional[int] = None) -> List[Document]:
        """Load structured Q&A documents with HIGH priority"""
        logger.info("📖 Loading structured Q&A documents (HIGH PRIORITY)...")
        
        qa_docs = self.forum_loader.load_structured_qa_pairs(limit=limit)
        
        # Add priority metadata
        for doc in qa_docs:
            doc.metadata.update({
                "priority": "high",
                "similarity_threshold": 0.4  # Lower threshold for easier retrieval
            })
        
        self.progress['total_qa_docs'] = len(qa_docs)
        logger.info(f"✅ Loaded {len(qa_docs)} Q&A documents")
        
        return qa_docs
    
    def load_raw_documents(self, limit: Optional[int] = None) -> List[Document]:
        """Load raw conversation documents with MEDIUM priority"""
        logger.info("💬 Loading raw conversation documents (MEDIUM PRIORITY)...")
        
        raw_docs = self.forum_loader.load_raw_forum_discussions(limit=limit)
        
        # Add priority metadata
        for doc in raw_docs:
            doc.metadata.update({
                "priority": "medium", 
                "similarity_threshold": 0.6  # Higher threshold for more selective retrieval
            })
        
        self.progress['total_raw_docs'] = len(raw_docs)
        logger.info(f"✅ Loaded {len(raw_docs)} raw discussion documents")
        
        return raw_docs
    
    def create_embeddings_batch(self, documents: List[Document], batch_size: int = 100):
        """Create embeddings in batches with progress tracking"""
        logger.info(f"🔄 Creating embeddings for {len(documents)} documents...")
        
        # Estimate cost
        cost_estimate = self.estimate_embedding_cost(documents)
        self.progress['embedding_cost_estimate'] += cost_estimate
        logger.info(f"💰 Estimated embedding cost: ${cost_estimate:.4f}")
        
        # Process in batches
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(documents) + batch_size - 1) // batch_size
            
            logger.info(f"⚙️  Processing batch {batch_num}/{total_batches} ({len(batch)} documents)...")
            
            try:
                # Create index for this batch
                if i == 0:
                    # First batch - create new index
                    index = VectorStoreIndex.from_documents(
                        batch, 
                        storage_context=self.storage_context,
                        show_progress=True
                    )
                else:
                    # Subsequent batches - add to existing index
                    for doc in batch:
                        index.insert(doc)
                
                # Update progress
                doc_type = batch[0].metadata.get('content_type', 'unknown')
                if 'qa_structured' in doc_type:
                    self.progress['qa_docs_processed'] += len(batch)
                else:
                    self.progress['raw_docs_processed'] += len(batch)
                
                # Log progress
                total_processed = self.progress['qa_docs_processed'] + self.progress['raw_docs_processed']
                total_docs = self.progress['total_qa_docs'] + self.progress['total_raw_docs']
                
                logger.info(f"📊 Progress: {total_processed}/{total_docs} documents processed ({(total_processed/total_docs)*100:.1f}%)")
                
                # Small delay to prevent overwhelming the API
                time.sleep(1)
                
            except Exception as e:
                error_msg = f"Error processing batch {batch_num}: {e}"
                logger.error(error_msg)
                self.progress['errors'].append(error_msg)
                
        return index
    
    def run_dual_document_loading(self, qa_limit: Optional[int] = None, raw_limit: Optional[int] = None):
        """Execute the dual document strategy loading process"""
        self.progress['start_time'] = datetime.now()
        
        logger.info("🚀 STARTING FORUM DATA LOADING - STEP 1")
        logger.info("=" * 60)
        logger.info("📋 Dual Document Strategy:")
        logger.info("  • Q&A Documents: HIGH priority (threshold: 0.4)")
        logger.info("  • Raw Discussions: MEDIUM priority (threshold: 0.6)")
        logger.info("=" * 60)
        
        try:
            # Setup vector store
            self.setup_vector_store()
            
            # Get forum statistics
            stats = self.forum_loader.get_forum_statistics()
            logger.info("📊 FORUM DATA STATISTICS:")
            logger.info(f"  • Q&A pairs available: {stats.get('qa_pairs', {}).get('total_qa_pairs', 0):,}")
            logger.info(f"  • Raw topics available: {stats.get('raw_topics', {}).get('total_topics', 0):,}")
            logger.info(f"  • Total posts: {stats.get('raw_topics', {}).get('total_posts', 0):,}")
            
            # Phase 1: Load Q&A documents (HIGH PRIORITY)
            logger.info("\n🔥 PHASE 1: Loading Q&A Documents (HIGH PRIORITY)")
            qa_docs = self.load_qa_documents(limit=qa_limit)
            
            # Phase 2: Load raw documents (MEDIUM PRIORITY) 
            logger.info("\n💬 PHASE 2: Loading Raw Discussions (MEDIUM PRIORITY)")
            raw_docs = self.load_raw_documents(limit=raw_limit)
            
            # Combine all documents
            all_docs = qa_docs + raw_docs
            total_cost = self.estimate_embedding_cost(all_docs)
            
            logger.info(f"\n💰 TOTAL ESTIMATED COST: ${total_cost:.4f}")
            logger.info(f"📈 TOTAL DOCUMENTS: {len(all_docs)}")
            
            # Create embeddings
            logger.info("\n⚡ PHASE 3: Creating Embeddings...")
            index = self.create_embeddings_batch(all_docs)
            
            # Final statistics
            end_time = datetime.now()
            duration = end_time - self.progress['start_time']
            
            logger.info("\n" + "=" * 60)
            logger.info("🎉 FORUM DATA LOADING COMPLETE!")
            logger.info("=" * 60)
            logger.info(f"⏱️  Duration: {duration}")
            logger.info(f"📊 Q&A documents processed: {self.progress['qa_docs_processed']}")
            logger.info(f"💬 Raw documents processed: {self.progress['raw_docs_processed']}")
            logger.info(f"💰 Total embedding cost: ${self.progress['embedding_cost_estimate']:.4f}")
            logger.info(f"❌ Errors: {len(self.progress['errors'])}")
            
            if self.progress['errors']:
                logger.info("🚨 Error details:")
                for error in self.progress['errors']:
                    logger.info(f"   {error}")
            
            return index
            
        except Exception as e:
            logger.error(f"🚨 CRITICAL ERROR: {e}")
            raise
        finally:
            # Close database connections
            if self.forum_loader:
                self.forum_loader.close_connection()
    
    def save_progress_report(self):
        """Save detailed progress report to file"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'progress': self.progress,
            'local_db_config': {k: v for k, v in self.local_db_config.items() if k != 'password'},
            'embedding_model': 'text-embedding-3-large',
            'embedding_dimensions': 1536
        }
        
        with open('forum_loading_progress_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info("📄 Progress report saved to: forum_loading_progress_report.json")

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Load forum data into LlamaIndex with dual document strategy')
    parser.add_argument('--qa-limit', type=int, help='Limit Q&A documents (for testing)')
    parser.add_argument('--raw-limit', type=int, help='Limit raw documents (for testing)')
    parser.add_argument('--test', action='store_true', help='Run with small limits for testing')
    
    args = parser.parse_args()
    
    # Set test limits if requested
    if args.test:
        qa_limit = 50
        raw_limit = 50
        print("🧪 TEST MODE: Loading 50 documents each type")
    else:
        qa_limit = args.qa_limit
        raw_limit = args.raw_limit
    
    # Initialize and run loader
    loader = ForumDataLoaderStep1()
    
    try:
        index = loader.run_dual_document_loading(qa_limit=qa_limit, raw_limit=raw_limit)
        loader.save_progress_report()
        
        print("\n✅ Forum data loading completed successfully!")
        print("📁 Check forum_loader_progress.log for detailed logs")
        print("📊 Check forum_loading_progress_report.json for progress summary")
        
    except KeyboardInterrupt:
        print("\n🛑 Loading interrupted by user")
        loader.save_progress_report()
    except Exception as e:
        print(f"\n🚨 Loading failed: {e}")
        loader.save_progress_report()
        sys.exit(1)

if __name__ == "__main__":
    main()