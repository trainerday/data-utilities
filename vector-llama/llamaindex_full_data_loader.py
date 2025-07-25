#!/usr/bin/env python3
"""
Full data loader for LlamaIndex with all TrainerDay content sources
Runs in background with progress monitoring and persistence
"""

import os
import sys
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import logging
from dotenv import load_dotenv

# LlamaIndex imports
from llama_index.core import VectorStoreIndex, Document, Settings, StorageContext
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

import frontmatter
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('llamaindex_full_load.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FullDataLoader:
    def __init__(self):
        # Configure LlamaIndex
        Settings.embed_model = OpenAIEmbedding(
            model="text-embedding-3-large", 
            dimensions=1536
        )
        Settings.llm = OpenAI(model="gpt-4-turbo-preview")
        
        # Database config
        self.db_config = {
            'host': os.getenv('DB_HOST'),
            'port': int(os.getenv('DB_PORT', 25060)),
            'database': os.getenv('DB_DATABASE'),
            'user': os.getenv('DB_USERNAME'),
            'password': os.getenv('DB_PASSWORD'),
            'sslmode': os.getenv('DB_SSLMODE', 'require')
        }
        
        # Progress tracking
        self.progress_file = Path("llamaindex_load_progress.json")
        self.progress = {
            "started_at": None,
            "current_phase": None,
            "completed_phases": [],
            "stats": {
                "blog_articles": {"loaded": 0, "total": 0, "errors": 0},
                "youtube_videos": {"loaded": 0, "total": 0, "errors": 0},
                "forum_qa": {"loaded": 0, "total": 0, "errors": 0}
            },
            "errors": [],
            "embedding_costs": {"estimated_tokens": 0, "estimated_cost": 0.0},
            "completed_at": None
        }
        
        # Vector store setup
        self.vector_store = None
        self.index = None
        
    def save_progress(self):
        """Save progress to JSON file"""
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2, default=str)
    
    def load_progress(self):
        """Load existing progress if available"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                self.progress = json.load(f)
                logger.info(f"Resumed from previous progress: {self.progress['current_phase']}")
    
    def setup_vector_store(self):
        """Setup PostgreSQL vector store"""
        logger.info("Setting up PostgreSQL vector store...")
        
        try:
            self.vector_store = PGVectorStore.from_params(
                database=self.db_config['database'],
                host=self.db_config['host'],
                password=self.db_config['password'],
                port=self.db_config['port'],
                user=self.db_config['user'],
                table_name="llamaindex_full_content",
                embed_dim=1536,
            )
            
            self.storage_context = StorageContext.from_defaults(
                vector_store=self.vector_store
            )
            
            logger.info("✅ Vector store setup complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Vector store setup failed: {e}")
            self.progress["errors"].append(f"Vector store setup: {e}")
            return False
    
    def load_blog_articles(self) -> List[Document]:
        """Load all blog articles"""
        logger.info("Loading blog articles...")
        self.progress["current_phase"] = "blog_articles"
        
        documents = []
        blog_path = Path("../vector-processor/source-data/blog_articles")
        
        if not blog_path.exists():
            logger.error(f"Blog path not found: {blog_path}")
            return documents
        
        md_files = list(blog_path.glob("*.md"))
        self.progress["stats"]["blog_articles"]["total"] = len(md_files)
        
        for i, md_file in enumerate(md_files):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)
                
                title = post.metadata.get('title', md_file.stem)
                
                # Estimate token count for cost tracking
                content_tokens = len(post.content) // 4  # Rough estimate
                self.progress["embedding_costs"]["estimated_tokens"] += content_tokens
                
                doc = Document(
                    text=post.content,
                    metadata={
                        "source": "blog",
                        "source_id": md_file.stem,
                        "title": title,
                        "category": post.metadata.get('category', 'Unknown'),
                        "engagement": post.metadata.get('engagement', 'Unknown'),
                        "tags": post.metadata.get('tags', []),
                        "content_type": "blog_article"
                    }
                )
                documents.append(doc)
                
                self.progress["stats"]["blog_articles"]["loaded"] += 1
                
                if i % 10 == 0:  # Log every 10 articles
                    logger.info(f"Blog articles: {i+1}/{len(md_files)} loaded")
                    self.save_progress()
                
            except Exception as e:
                logger.error(f"Error loading {md_file}: {e}")
                self.progress["stats"]["blog_articles"]["errors"] += 1
                self.progress["errors"].append(f"Blog {md_file}: {e}")
        
        logger.info(f"✅ Loaded {len(documents)} blog articles")
        return documents
    
    def load_youtube_content(self) -> List[Document]:
        """Load all YouTube video transcripts"""
        logger.info("Loading YouTube content...")
        self.progress["current_phase"] = "youtube_videos"
        
        documents = []
        youtube_path = Path("../vector-processor/source-data/youtube_content")
        
        if not youtube_path.exists():
            logger.error(f"YouTube path not found: {youtube_path}")
            return documents
        
        json_files = list(youtube_path.glob("video_*.json"))
        self.progress["stats"]["youtube_videos"]["total"] = len(json_files)
        
        for i, json_file in enumerate(json_files):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    video_data = json.load(f)
                
                # Combine transcript segments
                transcript_text = ""
                if 'transcript' in video_data:
                    for segment in video_data['transcript']:
                        transcript_text += f"{segment.get('text', '')} "
                
                if transcript_text.strip():
                    # Estimate tokens
                    content_tokens = len(transcript_text) // 4
                    self.progress["embedding_costs"]["estimated_tokens"] += content_tokens
                    
                    doc = Document(
                        text=transcript_text.strip(),
                        metadata={
                            "source": "youtube",
                            "source_id": video_data.get('video_id', json_file.stem),
                            "title": video_data.get('title', 'Unknown Video'),
                            "duration": video_data.get('duration', 0),
                            "view_count": video_data.get('view_count', 0),
                            "topics": video_data.get('topics', []),
                            "video_url": f"https://youtube.com/watch?v={video_data.get('video_id', '')}",
                            "content_type": "youtube_transcript"
                        }
                    )
                    documents.append(doc)
                
                self.progress["stats"]["youtube_videos"]["loaded"] += 1
                
                if i % 10 == 0:
                    logger.info(f"YouTube videos: {i+1}/{len(json_files)} processed")
                    self.save_progress()
                
            except Exception as e:
                logger.error(f"Error loading {json_file}: {e}")
                self.progress["stats"]["youtube_videos"]["errors"] += 1
                self.progress["errors"].append(f"YouTube {json_file}: {e}")
        
        logger.info(f"✅ Loaded {len(documents)} YouTube transcripts")
        return documents
    
    def load_forum_qa(self) -> List[Document]:
        """Load forum Q&A pairs from database"""
        logger.info("Loading forum Q&A pairs...")
        self.progress["current_phase"] = "forum_qa"
        
        documents = []
        
        try:
            conn = psycopg2.connect(**self.db_config)
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # First get count
                cur.execute("SELECT COUNT(*) FROM forum_analysis WHERE question IS NOT NULL AND answer IS NOT NULL")
                total_count = cur.fetchone()['count']
                self.progress["stats"]["forum_qa"]["total"] = total_count
                
                logger.info(f"Found {total_count} forum Q&A pairs")
                
                # Load in batches
                batch_size = 100
                for offset in range(0, total_count, batch_size):
                    cur.execute("""
                        SELECT 
                            id, question, answer, category, posts_count, created_at
                        FROM forum_analysis 
                        WHERE question IS NOT NULL AND answer IS NOT NULL
                        ORDER BY id
                        LIMIT %s OFFSET %s
                    """, (batch_size, offset))
                    
                    batch = cur.fetchall()
                    
                    for row in batch:
                        try:
                            # Combine question and answer
                            content = f"Question: {row['question']}\n\nAnswer: {row['answer']}"
                            
                            # Estimate tokens
                            content_tokens = len(content) // 4
                            self.progress["embedding_costs"]["estimated_tokens"] += content_tokens
                            
                            doc = Document(
                                text=content,
                                metadata={
                                    "source": "forum",
                                    "source_id": str(row['id']),
                                    "title": row['question'][:100] + "..." if len(row['question']) > 100 else row['question'],
                                    "category": row['category'] or 'general',
                                    "posts_count": row['posts_count'] or 0,
                                    "created_at": str(row['created_at']) if row['created_at'] else None,
                                    "content_type": "forum_qa"
                                }
                            )
                            documents.append(doc)
                            
                            self.progress["stats"]["forum_qa"]["loaded"] += 1
                            
                        except Exception as e:
                            logger.error(f"Error processing forum row {row['id']}: {e}")
                            self.progress["stats"]["forum_qa"]["errors"] += 1
                    
                    # Log progress every batch
                    logger.info(f"Forum Q&A: {offset + len(batch)}/{total_count} loaded")
                    self.save_progress()
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Database error loading forum data: {e}")
            self.progress["errors"].append(f"Forum database: {e}")
        
        logger.info(f"✅ Loaded {len(documents)} forum Q&A pairs")
        return documents
    
    def create_index(self, documents: List[Document]):
        """Create the vector index from all documents"""
        logger.info(f"Creating vector index from {len(documents)} documents...")
        self.progress["current_phase"] = "creating_index"
        
        try:
            # Estimate final cost
            estimated_cost = (self.progress["embedding_costs"]["estimated_tokens"] / 1000) * 0.00013
            self.progress["embedding_costs"]["estimated_cost"] = estimated_cost
            logger.info(f"💰 Estimated embedding cost: ${estimated_cost:.2f}")
            
            start_time = time.time()
            
            self.index = VectorStoreIndex.from_documents(
                documents,
                storage_context=self.storage_context,
                show_progress=True
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            logger.info(f"✅ Index created successfully in {processing_time:.1f}s")
            logger.info(f"📊 Final stats: {self.progress['stats']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Index creation failed: {e}")
            self.progress["errors"].append(f"Index creation: {e}")
            return False
    
    def run_full_load(self):
        """Run the complete data loading process"""
        logger.info("🚀 Starting full TrainerDay content loading...")
        
        self.progress["started_at"] = datetime.now().isoformat()
        self.load_progress()
        
        try:
            # Setup vector store
            if not self.setup_vector_store():
                return False
            
            # Load all content
            all_documents = []
            
            # Blog articles
            if "blog_articles" not in self.progress["completed_phases"]:
                blog_docs = self.load_blog_articles()
                all_documents.extend(blog_docs)
                self.progress["completed_phases"].append("blog_articles")
                self.save_progress()
            
            # YouTube transcripts
            if "youtube_videos" not in self.progress["completed_phases"]:
                youtube_docs = self.load_youtube_content()
                all_documents.extend(youtube_docs)
                self.progress["completed_phases"].append("youtube_videos")
                self.save_progress()
            
            # Forum Q&A
            if "forum_qa" not in self.progress["completed_phases"]:
                forum_docs = self.load_forum_qa()
                all_documents.extend(forum_docs)
                self.progress["completed_phases"].append("forum_qa")
                self.save_progress()
            
            # Create index
            if "creating_index" not in self.progress["completed_phases"]:
                if self.create_index(all_documents):
                    self.progress["completed_phases"].append("creating_index")
                    self.progress["current_phase"] = "completed"
                    self.progress["completed_at"] = datetime.now().isoformat()
                    self.save_progress()
                    
                    logger.info("🎉 FULL DATA LOADING COMPLETED SUCCESSFULLY!")
                    return True
            
        except Exception as e:
            logger.error(f"❌ Full load failed: {e}")
            self.progress["errors"].append(f"Full load: {e}")
            self.save_progress()
            return False
        
        return False

def monitor_progress():
    """Check current loading progress"""
    progress_file = Path("llamaindex_load_progress.json")
    
    if not progress_file.exists():
        print("❌ No loading process found")
        return
    
    with open(progress_file, 'r') as f:
        progress = json.load(f)
    
    print(f"\n📊 LLAMAINDEX LOADING PROGRESS")
    print(f"=" * 50)
    print(f"Status: {progress.get('current_phase', 'Unknown')}")
    print(f"Started: {progress.get('started_at', 'Unknown')}")
    
    stats = progress.get('stats', {})
    for source, data in stats.items():
        loaded = data.get('loaded', 0)
        total = data.get('total', 0)
        errors = data.get('errors', 0)
        if total > 0:
            pct = (loaded / total) * 100
            print(f"{source}: {loaded}/{total} ({pct:.1f}%) - {errors} errors")
    
    costs = progress.get('embedding_costs', {})
    print(f"\n💰 Estimated cost: ${costs.get('estimated_cost', 0):.2f}")
    print(f"Tokens: {costs.get('estimated_tokens', 0):,}")
    
    if progress.get('completed_at'):
        print(f"\n✅ COMPLETED: {progress['completed_at']}")
    
    errors = progress.get('errors', [])
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for error in errors[-5:]:  # Show last 5 errors
            print(f"  - {error}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        monitor_progress()
    else:
        loader = FullDataLoader()
        loader.run_full_load()