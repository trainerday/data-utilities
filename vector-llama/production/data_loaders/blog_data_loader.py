#!/usr/bin/env python3
"""
Blog Data Loader for Unified Knowledge Base
Loads blog articles with CRITICAL priority (0.3 threshold)
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

# LlamaIndex imports
from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.core.storage.storage_context import StorageContext
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

import sqlalchemy

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('blog_loader_progress.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class BlogDataLoader:
    def __init__(self):
        """Initialize blog data loader for unified knowledge base"""
        
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
        Settings.llm = OpenAI(model="gpt-4")
        
        # Use unified knowledge base table
        self.vector_store = None
        self.storage_context = None
        self.index = None
        
        # Progress tracking
        self.progress = {
            'start_time': None,
            'blog_docs_processed': 0,
            'total_blog_docs': 0,
            'embedding_cost_estimate': 0.0,
            'errors': []
        }
    
    def setup_vector_store(self):
        """Setup connection to unified knowledge base"""
        logger.info("🔧 Connecting to unified knowledge base...")
        
        # Connect to existing unified knowledge base
        self.vector_store = PGVectorStore.from_params(
            database=self.local_db_config['database'],
            host=self.local_db_config['host'],
            password=self.local_db_config['password'],
            port=self.local_db_config['port'],
            user=self.local_db_config['user'],
            table_name="llamaindex_knowledge_base",  # Unified table
            embed_dim=1536,
        )
        
        # Create storage context and index
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        self.index = VectorStoreIndex.from_vector_store(
            vector_store=self.vector_store,
            storage_context=self.storage_context
        )
        
        logger.info("✅ Connected to unified knowledge base")
    
    def estimate_embedding_cost(self, documents: List[Document]) -> float:
        """Estimate OpenAI embedding cost for documents"""
        total_chars = sum(len(doc.text) for doc in documents)
        estimated_tokens = total_chars / 4
        estimated_cost = (estimated_tokens / 1000) * 0.00013
        return estimated_cost
    
    def load_blog_articles_from_vector_processor(self) -> List[Document]:
        """Load blog articles from markdown files in vector-processor"""
        logger.info("📖 Loading blog articles from vector-processor...")
        
        # Path to vector-processor blog articles directory
        blog_dir = Path("../../vector-processor/source-data/blog_articles")
        
        if not blog_dir.exists():
            logger.error(f"❌ Blog directory not found: {blog_dir}")
            return []
        
        documents = []
        
        try:
            import frontmatter
            
            # Get all markdown files
            md_files = list(blog_dir.glob("*.md"))
            logger.info(f"Found {len(md_files)} blog article files")
            
            for md_file in md_files:
                try:
                    # Parse frontmatter and content
                    with open(md_file, 'r', encoding='utf-8') as f:
                        post = frontmatter.load(f)
                    
                    title = post.metadata.get('title', md_file.stem)
                    content = post.content
                    url = post.metadata.get('url', '')
                    date = post.metadata.get('date', '')
                    
                    if not content.strip():
                        continue
                    
                    # Create full article text
                    article_text = f"Blog Article: {title}\n\n{content}"
                    
                    # Create document with CRITICAL priority metadata
                    doc = Document(
                        text=article_text,
                        metadata={
                            "source": "blog",
                            "content_type": "article", 
                            "priority": "critical",
                            "similarity_threshold": 0.3,  # CRITICAL priority threshold
                            "authority": "official",
                            "title": title,
                            "url": url,
                            "date": str(date),
                            "feature_status": "current",
                            "created_date": datetime.now().isoformat(),
                            "estimated_tokens": len(article_text) // 4
                        }
                    )
                    
                    documents.append(doc)
                    
                except Exception as e:
                    logger.error(f"Error processing {md_file}: {e}")
                    continue
        
        except ImportError:
            logger.error("❌ frontmatter package required: pip install python-frontmatter")
            return []
        except Exception as e:
            logger.error(f"❌ Error loading blog articles: {e}")
            return []
        
        self.progress['total_blog_docs'] = len(documents)
        logger.info(f"✅ Loaded {len(documents)} blog articles")
        return documents
    
    def create_embeddings_batch(self, documents: List[Document], batch_size: int = 50):
        """Add blog documents to existing knowledge base"""
        logger.info(f"🔄 Adding {len(documents)} blog articles to knowledge base...")
        
        # Estimate cost
        cost_estimate = self.estimate_embedding_cost(documents)
        self.progress['embedding_cost_estimate'] = cost_estimate
        logger.info(f"💰 Estimated embedding cost: ${cost_estimate:.4f}")
        
        # Process in batches
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(documents) + batch_size - 1) // batch_size
            
            logger.info(f"⚙️  Processing batch {batch_num}/{total_batches} ({len(batch)} articles)...")
            
            try:
                # Add to existing index
                for doc in batch:
                    self.index.insert(doc)
                
                # Update progress
                self.progress['blog_docs_processed'] += len(batch)
                
                logger.info(f"📊 Progress: {self.progress['blog_docs_processed']}/{self.progress['total_blog_docs']} blog articles processed")
                
                # Small delay to prevent overwhelming the API
                time.sleep(1)
                
            except Exception as e:
                error_msg = f"Error processing batch {batch_num}: {e}"
                logger.error(error_msg)
                self.progress['errors'].append(error_msg)
        
        return self.index
    
    def get_knowledge_base_stats(self):
        """Get current knowledge base statistics"""
        try:
            connection_string = f"postgresql://{self.local_db_config['user']}@{self.local_db_config['host']}:{self.local_db_config['port']}/{self.local_db_config['database']}"
            engine = sqlalchemy.create_engine(connection_string)
            
            with engine.connect() as conn:
                # Total documents
                result = conn.execute(sqlalchemy.text(
                    "SELECT COUNT(*) as total FROM llamaindex_knowledge_base"
                ))
                total_docs = result.fetchone()[0]
                
                # By source
                result = conn.execute(sqlalchemy.text(
                    "SELECT metadata_->>'source' as source, COUNT(*) as count FROM llamaindex_knowledge_base GROUP BY metadata_->>'source'"
                ))
                sources = result.fetchall()
                
                # By priority
                result = conn.execute(sqlalchemy.text(
                    "SELECT metadata_->>'priority' as priority, COUNT(*) as count FROM llamaindex_knowledge_base GROUP BY metadata_->>'priority'"
                ))
                priorities = result.fetchall()
                
                return {
                    'total': total_docs,
                    'sources': dict(sources),
                    'priorities': dict(priorities)
                }
                
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def run_blog_loading(self):
        """Execute blog data loading into unified knowledge base"""
        self.progress['start_time'] = datetime.now()
        
        logger.info("🚀 LOADING BLOG DATA INTO UNIFIED KNOWLEDGE BASE")
        logger.info("=" * 60)
        logger.info("📋 Blog Data Configuration:")
        logger.info("  • Source: blog")
        logger.info("  • Priority: CRITICAL (threshold: 0.3)")
        logger.info("  • Authority: official")
        logger.info("=" * 60)
        
        try:
            # Setup connection to unified knowledge base
            self.setup_vector_store()
            
            # Get current stats
            before_stats = self.get_knowledge_base_stats()
            logger.info("📊 CURRENT KNOWLEDGE BASE:")
            logger.info(f"  • Total documents: {before_stats.get('total', 0):,}")
            for source, count in before_stats.get('sources', {}).items():
                logger.info(f"  • {source}: {count:,}")
            
            # Load blog articles
            blog_docs = self.load_blog_articles_from_vector_processor()
            
            if not blog_docs:
                logger.error("❌ No blog articles to load")
                return None
            
            # Add to knowledge base
            logger.info(f"\n💰 ESTIMATED COST: ${self.estimate_embedding_cost(blog_docs):.4f}")
            
            index = self.create_embeddings_batch(blog_docs)
            
            # Final statistics
            end_time = datetime.now()
            duration = end_time - self.progress['start_time']
            after_stats = self.get_knowledge_base_stats()
            
            logger.info("\n" + "=" * 60)
            logger.info("🎉 BLOG DATA LOADING COMPLETE!")
            logger.info("=" * 60)
            logger.info(f"⏱️  Duration: {duration}")
            logger.info(f"📊 Blog articles added: {self.progress['blog_docs_processed']}")
            logger.info(f"💰 Embedding cost: ${self.progress['embedding_cost_estimate']:.4f}")
            logger.info(f"❌ Errors: {len(self.progress['errors'])}")
            
            logger.info(f"\n📊 UPDATED KNOWLEDGE BASE:")
            logger.info(f"  • Total documents: {after_stats.get('total', 0):,}")
            for source, count in after_stats.get('sources', {}).items():
                logger.info(f"  • {source}: {count:,}")
            
            return index
            
        except Exception as e:
            logger.error(f"🚨 CRITICAL ERROR: {e}")
            raise
    
    def save_progress_report(self):
        """Save detailed progress report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'progress': self.progress,
            'local_db_config': {k: v for k, v in self.local_db_config.items() if k != 'password'},
            'table_name': 'llamaindex_knowledge_base',
            'embedding_model': 'text-embedding-3-large'
        }
        
        with open('blog_loading_progress_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info("📄 Progress report saved to: blog_loading_progress_report.json")

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Load blog data into unified knowledge base')
    parser.add_argument('--test', action='store_true', help='Run with small subset for testing')
    
    args = parser.parse_args()
    
    # Initialize and run loader
    loader = BlogDataLoader()
    
    try:
        index = loader.run_blog_loading()
        loader.save_progress_report()
        
        print("\n✅ Blog data loading completed successfully!")
        print("📁 Check blog_loader_progress.log for detailed logs")
        print("📊 Check blog_loading_progress_report.json for progress summary")
        
    except KeyboardInterrupt:
        print("\n🛑 Loading interrupted by user")
        loader.save_progress_report()
    except Exception as e:
        print(f"\n🚨 Loading failed: {e}")
        loader.save_progress_report()
        sys.exit(1)

if __name__ == "__main__":
    main()