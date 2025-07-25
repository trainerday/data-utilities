#!/usr/bin/env python3
"""
YouTube Data Loader for Unified Knowledge Base
Loads YouTube transcripts with CRITICAL priority (0.3 threshold)
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
        logging.FileHandler('youtube_loader_progress.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class YouTubeDataLoader:
    def __init__(self):
        """Initialize YouTube data loader for unified knowledge base"""
        
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
            'youtube_docs_processed': 0,
            'total_youtube_docs': 0,
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
    
    def load_youtube_transcripts(self) -> List[Document]:
        """Load YouTube transcripts from JSON files"""
        logger.info("🎥 Loading YouTube transcripts...")
        
        # Path to YouTube content
        youtube_path = Path("../../vector-processor/source-data/youtube_content")
        
        if not youtube_path.exists():
            logger.error(f"❌ YouTube directory not found: {youtube_path}")
            return []
        
        documents = []
        
        try:
            # Get all video JSON files
            json_files = list(youtube_path.glob("video_*.json"))
            logger.info(f"Found {len(json_files)} YouTube video files")
            
            for json_file in json_files:
                try:
                    # Load video data
                    with open(json_file, 'r', encoding='utf-8') as f:
                        video_data = json.load(f)
                    
                    # Extract full transcript text (no timing)
                    transcript_text = ""
                    if 'transcript' in video_data and 'full_text' in video_data['transcript']:
                        # Use the full_text field which has no timing
                        transcript_text = video_data['transcript']['full_text']
                    elif 'transcript' in video_data and 'segments' in video_data['transcript']:
                        # Fallback: combine segments if full_text not available
                        segments = video_data['transcript']['segments']
                        transcript_text = " ".join([seg.get('text', '') for seg in segments])
                    
                    if not transcript_text.strip():
                        logger.warning(f"No transcript found for {json_file.name}")
                        continue
                    
                    # Extract metadata
                    title = video_data.get('title', 'Unknown Video')
                    video_id = video_data.get('video_id', json_file.stem.replace('video_', ''))
                    url = video_data.get('url', f"https://www.youtube.com/watch?v={video_id}")
                    duration = video_data.get('duration', 0)
                    topics = video_data.get('topics', [])
                    
                    # Create full transcript text
                    video_text = f"YouTube Video: {title}\n\nTranscript:\n{transcript_text}"
                    
                    # Create document with CRITICAL priority metadata
                    doc = Document(
                        text=video_text,
                        metadata={
                            "source": "youtube",
                            "content_type": "video_transcript", 
                            "priority": "critical",
                            "similarity_threshold": 0.3,  # CRITICAL priority threshold
                            "authority": "official",
                            "title": title,
                            "video_id": video_id,
                            "url": url,
                            "duration": duration,
                            "topics": topics,
                            "feature_status": "current",
                            "created_date": datetime.now().isoformat(),
                            "estimated_tokens": len(video_text) // 4
                        }
                    )
                    
                    documents.append(doc)
                    
                except Exception as e:
                    logger.error(f"Error processing {json_file}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"❌ Error loading YouTube transcripts: {e}")
            return []
        
        self.progress['total_youtube_docs'] = len(documents)
        logger.info(f"✅ Loaded {len(documents)} YouTube transcripts")
        return documents
    
    def create_embeddings_batch(self, documents: List[Document], batch_size: int = 25):
        """Add YouTube documents to existing knowledge base"""
        logger.info(f"🔄 Adding {len(documents)} YouTube transcripts to knowledge base...")
        
        # Estimate cost
        cost_estimate = self.estimate_embedding_cost(documents)
        self.progress['embedding_cost_estimate'] = cost_estimate
        logger.info(f"💰 Estimated embedding cost: ${cost_estimate:.4f}")
        
        # Process in batches (smaller batches for YouTube due to longer content)
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(documents) + batch_size - 1) // batch_size
            
            logger.info(f"⚙️  Processing batch {batch_num}/{total_batches} ({len(batch)} videos)...")
            
            try:
                # Add to existing index
                for doc in batch:
                    self.index.insert(doc)
                
                # Update progress
                self.progress['youtube_docs_processed'] += len(batch)
                
                logger.info(f"📊 Progress: {self.progress['youtube_docs_processed']}/{self.progress['total_youtube_docs']} YouTube videos processed")
                
                # Small delay to prevent overwhelming the API
                time.sleep(2)
                
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
    
    def run_youtube_loading(self):
        """Execute YouTube data loading into unified knowledge base"""
        self.progress['start_time'] = datetime.now()
        
        logger.info("🚀 LOADING YOUTUBE DATA INTO UNIFIED KNOWLEDGE BASE")
        logger.info("=" * 60)
        logger.info("📋 YouTube Data Configuration:")
        logger.info("  • Source: youtube")
        logger.info("  • Priority: CRITICAL (threshold: 0.3)")
        logger.info("  • Authority: official")
        logger.info("  • Content: Full transcripts without timing")
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
            
            # Load YouTube transcripts
            youtube_docs = self.load_youtube_transcripts()
            
            if not youtube_docs:
                logger.error("❌ No YouTube transcripts to load")
                return None
            
            # Add to knowledge base
            logger.info(f"\n💰 ESTIMATED COST: ${self.estimate_embedding_cost(youtube_docs):.4f}")
            
            index = self.create_embeddings_batch(youtube_docs)
            
            # Final statistics
            end_time = datetime.now()
            duration = end_time - self.progress['start_time']
            after_stats = self.get_knowledge_base_stats()
            
            logger.info("\n" + "=" * 60)
            logger.info("🎉 YOUTUBE DATA LOADING COMPLETE!")
            logger.info("=" * 60)
            logger.info(f"⏱️  Duration: {duration}")
            logger.info(f"🎥 YouTube videos added: {self.progress['youtube_docs_processed']}")
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
        
        with open('youtube_loading_progress_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info("📄 Progress report saved to: youtube_loading_progress_report.json")

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Load YouTube data into unified knowledge base')
    parser.add_argument('--test', action='store_true', help='Run with small subset for testing')
    
    args = parser.parse_args()
    
    # Initialize and run loader
    loader = YouTubeDataLoader()
    
    try:
        index = loader.run_youtube_loading()
        loader.save_progress_report()
        
        print("\n✅ YouTube data loading completed successfully!")
        print("📁 Check youtube_loader_progress.log for detailed logs")
        print("📊 Check youtube_loading_progress_report.json for progress summary")
        
    except KeyboardInterrupt:
        print("\n🛑 Loading interrupted by user")
        loader.save_progress_report()
    except Exception as e:
        print(f"\n🚨 Loading failed: {e}")
        loader.save_progress_report()
        sys.exit(1)

if __name__ == "__main__":
    main()