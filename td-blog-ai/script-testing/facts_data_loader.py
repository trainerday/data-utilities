#!/usr/bin/env python3
"""
Facts Data Loader for Unified Knowledge Base
Loads validated facts from Google Sheet with HIGHEST priority (0.2 threshold)
Includes corrective information for wrong facts to prevent article misinformation
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

# Google Sheets imports
import gspread
from google.oauth2.service_account import Credentials

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
        logging.FileHandler('facts_loader_progress.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class FactsDataLoader:
    def __init__(self):
        """Initialize facts data loader for unified knowledge base"""
        
        # Local PostgreSQL configuration
        self.local_db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'trainerday_local',
            'user': os.getenv('USER', 'alex'),
            'password': '',
        }
        
        # Google Sheets configuration
        self.spreadsheet_id = "1YJyAVVaPUM6uhd9_DIRLAB0tE106gExTSD0sUMV5LLc"
        self.credentials_path = os.path.expanduser("~/td-drive-credentials.json")
        
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
            'facts_processed': 0,
            'valid_facts': 0,
            'wrong_facts': 0,
            'excluded_facts': 0,
            'total_facts': 0,
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
    
    def setup_google_sheets(self):
        """Setup Google Sheets connection"""
        logger.info("📊 Connecting to Google Sheets...")
        
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(f"Google credentials not found at {self.credentials_path}")
        
        # Setup credentials and authorize
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials = Credentials.from_service_account_file(
            self.credentials_path, 
            scopes=scopes
        )
        
        self.gc = gspread.authorize(credentials)
        self.worksheet = self.gc.open_by_key(self.spreadsheet_id).sheet1
        
        logger.info("✅ Connected to Google Sheets")
    
    def remove_existing_facts(self):
        """Remove all existing facts from knowledge base before reloading"""
        logger.info("🗑️ Removing existing facts from knowledge base...")
        
        try:
            connection_string = f"postgresql://{self.local_db_config['user']}@{self.local_db_config['host']}:{self.local_db_config['port']}/{self.local_db_config['database']}"
            engine = sqlalchemy.create_engine(connection_string)
            
            with engine.connect() as conn:
                # Delete all facts documents
                result = conn.execute(sqlalchemy.text(
                    "DELETE FROM llamaindex_knowledge_base WHERE metadata_->>'source' = 'facts'"
                ))
                deleted_count = result.rowcount
                conn.commit()
                
                logger.info(f"✅ Removed {deleted_count} existing facts documents")
                
        except Exception as e:
            logger.error(f"Error removing existing facts: {e}")
            raise
    
    def estimate_embedding_cost(self, documents: List[Document]) -> float:
        """Estimate OpenAI embedding cost for documents"""
        total_chars = sum(len(doc.text) for doc in documents)
        estimated_tokens = total_chars / 4
        estimated_cost = (estimated_tokens / 1000) * 0.00013
        return estimated_cost
    
    def load_facts_from_sheet(self) -> List[Document]:
        """Load facts from Google Sheet with status-based processing"""
        logger.info("📋 Loading facts from Google Sheet...")
        
        try:
            # Get all records from the sheet
            records = self.worksheet.get_all_records()
            self.progress['total_facts'] = len(records)
            
            logger.info(f"Found {len(records)} facts in Google Sheet")
            
            documents = []
            
            for i, record in enumerate(records):
                try:
                    fact_text = record.get('original_fact', '').strip()
                    status = record.get('status', '').strip().upper()
                    source_article = record.get('source_article', '')
                    
                    if not fact_text:
                        logger.warning(f"Row {i+1}: Empty fact text, skipping")
                        continue
                    
                    # Process based on status
                    if status == '' or status == 'ADD':
                        # Valid facts - load normally
                        document_text = f"Fact: {fact_text}"
                        fact_type = "valid_fact"
                        self.progress['valid_facts'] += 1
                        
                    elif status == 'WRONG':
                        # Wrong facts - load with corrective warning
                        document_text = f"DO NOT USE IN ARTICLES: This is incorrect information - {fact_text}"
                        fact_type = "wrong_fact"
                        self.progress['wrong_facts'] += 1
                        
                    elif status in ['REMOVE', 'REMOVED']:
                        # Exclude these entirely
                        self.progress['excluded_facts'] += 1
                        logger.debug(f"Row {i+1}: Excluding fact with status '{status}'")
                        continue
                        
                    else:
                        logger.warning(f"Row {i+1}: Unknown status '{status}', treating as valid")
                        document_text = f"Fact: {fact_text}"
                        fact_type = "valid_fact"
                        self.progress['valid_facts'] += 1
                    
                    # Create document with HIGHEST priority metadata
                    doc = Document(
                        text=document_text,
                        metadata={
                            "source": "facts",
                            "content_type": fact_type,
                            "priority": "highest",
                            "similarity_threshold": 0.2,  # HIGHEST priority threshold
                            "authority": "validated",
                            "original_fact": fact_text,
                            "fact_status": status if status else "validated",
                            "source_article": source_article,
                            "feature_status": "current",
                            "created_date": datetime.now().isoformat(),
                            "estimated_tokens": len(document_text) // 4
                        }
                    )
                    
                    documents.append(doc)
                    self.progress['facts_processed'] += 1
                    
                    if i % 50 == 0:  # Log every 50 facts
                        logger.info(f"Progress: {i+1}/{len(records)} facts processed")
                
                except Exception as e:
                    logger.error(f"Error processing fact row {i+1}: {e}")
                    self.progress['errors'].append(f"Row {i+1}: {e}")
                    continue
            
            logger.info(f"✅ Processed {len(documents)} facts from Google Sheet")
            logger.info(f"   • Valid facts: {self.progress['valid_facts']}")
            logger.info(f"   • Wrong facts (corrective): {self.progress['wrong_facts']}")
            logger.info(f"   • Excluded facts: {self.progress['excluded_facts']}")
            
            return documents
            
        except Exception as e:
            logger.error(f"❌ Error loading facts from Google Sheet: {e}")
            raise
    
    def create_embeddings_batch(self, documents: List[Document], batch_size: int = 50):
        """Add facts to knowledge base with complete replacement"""
        logger.info(f"🔄 Adding {len(documents)} facts to knowledge base...")
        
        # Estimate cost
        cost_estimate = self.estimate_embedding_cost(documents)
        self.progress['embedding_cost_estimate'] = cost_estimate
        logger.info(f"💰 Estimated embedding cost: ${cost_estimate:.4f}")
        
        # Process in batches
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(documents) + batch_size - 1) // batch_size
            
            logger.info(f"⚙️  Processing batch {batch_num}/{total_batches} ({len(batch)} facts)...")
            
            try:
                # Add to existing index
                for doc in batch:
                    self.index.insert(doc)
                
                logger.info(f"📊 Progress: {min(i + batch_size, len(documents))}/{len(documents)} facts added")
                
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
                
                # Facts breakdown
                result = conn.execute(sqlalchemy.text(
                    "SELECT metadata_->>'content_type' as fact_type, COUNT(*) as count FROM llamaindex_knowledge_base WHERE metadata_->>'source' = 'facts' GROUP BY metadata_->>'content_type'"
                ))
                fact_types = result.fetchall()
                
                return {
                    'total': total_docs,
                    'sources': dict(sources),
                    'fact_types': dict(fact_types) if fact_types else {}
                }
                
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def run_facts_loading(self):
        """Execute facts data loading with complete replacement"""
        self.progress['start_time'] = datetime.now()
        
        logger.info("🚀 LOADING FACTS DATA INTO UNIFIED KNOWLEDGE BASE")
        logger.info("=" * 60)
        logger.info("📋 Facts Data Configuration:")
        logger.info("  • Source: Google Sheets (TD-Blog-Facts)")
        logger.info("  • Priority: HIGHEST (threshold: 0.2)")
        logger.info("  • Authority: validated")
        logger.info("  • Strategy: Complete replacement")
        logger.info("  • Valid facts: Load as-is")
        logger.info("  • Wrong facts: Load with corrective warnings")
        logger.info("=" * 60)
        
        try:
            # Setup connections
            self.setup_google_sheets()
            self.setup_vector_store()
            
            # Get current stats
            before_stats = self.get_knowledge_base_stats()
            logger.info("📊 CURRENT KNOWLEDGE BASE:")
            logger.info(f"  • Total documents: {before_stats.get('total', 0):,}")
            for source, count in before_stats.get('sources', {}).items():
                logger.info(f"  • {source}: {count:,}")
            
            # Remove existing facts (complete replacement)
            self.remove_existing_facts()
            
            # Load facts from Google Sheet
            facts_docs = self.load_facts_from_sheet()
            
            if not facts_docs:
                logger.error("❌ No facts to load")
                return None
            
            # Add to knowledge base
            logger.info(f"\n💰 ESTIMATED COST: ${self.estimate_embedding_cost(facts_docs):.4f}")
            
            index = self.create_embeddings_batch(facts_docs)
            
            # Final statistics
            end_time = datetime.now()
            duration = end_time - self.progress['start_time']
            after_stats = self.get_knowledge_base_stats()
            
            logger.info("\n" + "=" * 60)
            logger.info("🎉 FACTS DATA LOADING COMPLETE!")
            logger.info("=" * 60)
            logger.info(f"⏱️  Duration: {duration}")
            logger.info(f"📋 Total facts processed: {self.progress['facts_processed']}")
            logger.info(f"✅ Valid facts: {self.progress['valid_facts']}")
            logger.info(f"⚠️  Wrong facts (corrective): {self.progress['wrong_facts']}")
            logger.info(f"🚫 Excluded facts: {self.progress['excluded_facts']}")
            logger.info(f"💰 Embedding cost: ${self.progress['embedding_cost_estimate']:.4f}")
            logger.info(f"❌ Errors: {len(self.progress['errors'])}")
            
            logger.info(f"\n📊 UPDATED KNOWLEDGE BASE:")
            logger.info(f"  • Total documents: {after_stats.get('total', 0):,}")
            for source, count in after_stats.get('sources', {}).items():
                logger.info(f"  • {source}: {count:,}")
            
            if after_stats.get('fact_types'):
                logger.info("📋 Facts breakdown:")
                for fact_type, count in after_stats['fact_types'].items():
                    logger.info(f"  • {fact_type}: {count:,}")
            
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
            'spreadsheet_id': self.spreadsheet_id,
            'table_name': 'llamaindex_knowledge_base',
            'embedding_model': 'text-embedding-3-large'
        }
        
        with open('facts_loading_progress_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info("📄 Progress report saved to: facts_loading_progress_report.json")

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Load facts data into unified knowledge base')
    parser.add_argument('--test', action='store_true', help='Run with small subset for testing')
    
    args = parser.parse_args()
    
    # Initialize and run loader
    loader = FactsDataLoader()
    
    try:
        index = loader.run_facts_loading()
        loader.save_progress_report()
        
        print("\n✅ Facts data loading completed successfully!")
        print("📁 Check facts_loader_progress.log for detailed logs")
        print("📊 Check facts_loading_progress_report.json for progress summary")
        
    except KeyboardInterrupt:
        print("\n🛑 Loading interrupted by user")
        loader.save_progress_report()
    except Exception as e:
        print(f"\n🚨 Loading failed: {e}")
        loader.save_progress_report()
        sys.exit(1)

if __name__ == "__main__":
    main()