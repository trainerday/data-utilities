#!/usr/bin/env python3
"""
Load blog articles and YouTube content (skip forum for now)
Fixed paths and proper background monitoring
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
import logging
from dotenv import load_dotenv

# LlamaIndex imports  
from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

import frontmatter

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('llamaindex_blog_youtube_load.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BlogYouTubeLoader:
    def __init__(self):
        # Configure LlamaIndex
        Settings.embed_model = OpenAIEmbedding(
            model="text-embedding-3-large", 
            dimensions=1536
        )
        Settings.llm = OpenAI(model="gpt-4-turbo-preview")
        
        # Progress tracking
        self.progress_file = Path("llamaindex_blog_youtube_progress.json")
        self.progress = {
            "started_at": None,
            "current_phase": None,
            "completed_phases": [],
            "stats": {
                "blog_articles": {"loaded": 0, "total": 0, "errors": 0},
                "youtube_videos": {"loaded": 0, "total": 0, "errors": 0}
            },
            "errors": [],
            "embedding_costs": {"estimated_tokens": 0, "estimated_cost": 0.0},
            "completed_at": None
        }
        
        # Determine correct paths
        self.blog_path = self._find_blog_path()
        self.youtube_path = self._find_youtube_path()
        
        logger.info(f"Blog path: {self.blog_path}")
        logger.info(f"YouTube path: {self.youtube_path}")
    
    def _find_blog_path(self):
        """Find blog articles path"""
        possible_paths = [
            Path("../vector-processor/source-data/blog_articles"),
            Path("../../vector-processor/source-data/blog_articles"),
            Path("/Users/alex/Documents/Projects/data-utilities/vector-processor/source-data/blog_articles")
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        logger.error("Blog path not found!")
        return None
    
    def _find_youtube_path(self):
        """Find YouTube content path"""
        possible_paths = [
            Path("../vector-processor/source-data/youtube_content"),
            Path("../../vector-processor/source-data/youtube_content"),
            Path("/Users/alex/Documents/Projects/data-utilities/vector-processor/source-data/youtube_content")
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        logger.error("YouTube path not found!")
        return None
    
    def save_progress(self):
        """Save progress to JSON file"""
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2, default=str)
    
    def load_blog_articles(self):
        """Load all blog articles"""
        logger.info("Loading blog articles...")
        self.progress["current_phase"] = "blog_articles"
        
        documents = []
        
        if not self.blog_path:
            logger.error("Blog path not available")
            return documents
        
        md_files = list(self.blog_path.glob("*.md"))
        self.progress["stats"]["blog_articles"]["total"] = len(md_files)
        
        logger.info(f"Found {len(md_files)} blog articles to process")
        
        for i, md_file in enumerate(md_files):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)
                
                title = post.metadata.get('title', md_file.stem)
                
                # Estimate token count
                content_tokens = len(post.content) // 4
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
                        "content_type": "blog_article",
                        "file_path": str(md_file)
                    }
                )
                documents.append(doc)
                
                self.progress["stats"]["blog_articles"]["loaded"] += 1
                
                if i % 5 == 0:  # Log every 5 articles
                    logger.info(f"Blog articles: {i+1}/{len(md_files)} - {title[:50]}...")
                    self.save_progress()
                
            except Exception as e:
                logger.error(f"Error loading {md_file}: {e}")
                self.progress["stats"]["blog_articles"]["errors"] += 1
                self.progress["errors"].append(f"Blog {md_file.name}: {e}")
        
        logger.info(f"✅ Loaded {len(documents)} blog articles")
        return documents
    
    def load_youtube_content(self):
        """Load YouTube transcripts"""
        logger.info("Loading YouTube content...")
        self.progress["current_phase"] = "youtube_videos"
        
        documents = []
        
        if not self.youtube_path:
            logger.error("YouTube path not available")
            return documents
        
        json_files = list(self.youtube_path.glob("video_*.json"))
        self.progress["stats"]["youtube_videos"]["total"] = len(json_files)
        
        logger.info(f"Found {len(json_files)} YouTube videos to process")
        
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
                    
                    title = video_data.get('title', 'Unknown Video')
                    video_id = video_data.get('video_id', json_file.stem.replace('video_', ''))
                    
                    doc = Document(
                        text=transcript_text.strip(),
                        metadata={
                            "source": "youtube",
                            "source_id": video_id,
                            "title": title,
                            "duration": video_data.get('duration', 0),
                            "view_count": video_data.get('view_count', 0),
                            "topics": video_data.get('topics', []),
                            "video_url": f"https://youtube.com/watch?v={video_id}",
                            "content_type": "youtube_transcript"
                        }
                    )
                    documents.append(doc)
                
                self.progress["stats"]["youtube_videos"]["loaded"] += 1
                
                if i % 5 == 0:
                    title = video_data.get('title', 'Unknown')[:40]
                    logger.info(f"YouTube videos: {i+1}/{len(json_files)} - {title}...")
                    self.save_progress()
                
            except Exception as e:
                logger.error(f"Error loading {json_file}: {e}")
                self.progress["stats"]["youtube_videos"]["errors"] += 1
                self.progress["errors"].append(f"YouTube {json_file.name}: {e}")
        
        logger.info(f"✅ Loaded {len(documents)} YouTube transcripts")
        return documents
    
    def create_index(self, documents):
        """Create vector index"""
        logger.info(f"Creating vector index from {len(documents)} documents...")
        self.progress["current_phase"] = "creating_index"
        
        try:
            # Calculate cost estimate
            estimated_cost = (self.progress["embedding_costs"]["estimated_tokens"] / 1000) * 0.00013
            self.progress["embedding_costs"]["estimated_cost"] = estimated_cost
            logger.info(f"💰 Estimated embedding cost: ${estimated_cost:.2f}")
            
            start_time = time.time()
            
            # Create index (in-memory for now, can switch to PostgreSQL later)
            self.index = VectorStoreIndex.from_documents(
                documents,
                show_progress=True
            )
            
            # Save index to disk
            self.index.storage_context.persist(persist_dir="./llamaindex_storage")
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            logger.info(f"✅ Index created and saved in {processing_time:.1f}s")
            logger.info(f"📁 Index saved to: ./llamaindex_storage")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Index creation failed: {e}")
            self.progress["errors"].append(f"Index creation: {e}")
            return False
    
    def run_full_load(self):
        """Run the complete loading process"""
        logger.info("🚀 Starting blog + YouTube content loading...")
        
        self.progress["started_at"] = datetime.now().isoformat()
        self.save_progress()
        
        try:
            all_documents = []
            
            # Load blog articles
            blog_docs = self.load_blog_articles()
            all_documents.extend(blog_docs)
            self.progress["completed_phases"].append("blog_articles")
            self.save_progress()
            
            # Load YouTube content
            youtube_docs = self.load_youtube_content()
            all_documents.extend(youtube_docs)
            self.progress["completed_phases"].append("youtube_videos")
            self.save_progress()
            
            logger.info(f"📊 Total documents collected: {len(all_documents)}")
            
            # Create index
            if self.create_index(all_documents):
                self.progress["completed_phases"].append("creating_index")
                self.progress["current_phase"] = "completed"
                self.progress["completed_at"] = datetime.now().isoformat()
                self.save_progress()
                
                logger.info("🎉 LOADING COMPLETED SUCCESSFULLY!")
                logger.info(f"📊 Final stats: {self.progress['stats']}")
                return True
            
        except Exception as e:
            logger.error(f"❌ Loading failed: {e}")
            self.progress["errors"].append(f"Full load: {e}")
            self.save_progress()
            return False
        
        return False

def monitor_progress():
    """Monitor loading progress"""
    progress_file = Path("llamaindex_blog_youtube_progress.json")
    
    if not progress_file.exists():
        print("❌ No loading process found")
        return
    
    with open(progress_file, 'r') as f:
        progress = json.load(f)
    
    print(f"\\n📊 BLOG + YOUTUBE LOADING PROGRESS")
    print(f"=" * 50)
    print(f"Status: {progress.get('current_phase', 'Unknown')}")
    print(f"Started: {progress.get('started_at', 'Unknown')}")
    
    stats = progress.get('stats', {})
    total_loaded = 0
    total_docs = 0
    
    for source, data in stats.items():
        loaded = data.get('loaded', 0)
        total = data.get('total', 0)
        errors = data.get('errors', 0)
        total_loaded += loaded
        total_docs += total
        
        if total > 0:
            pct = (loaded / total) * 100
            print(f"{source}: {loaded}/{total} ({pct:.1f}%) - {errors} errors")
        else:
            print(f"{source}: {loaded} loaded - {errors} errors")
    
    print(f"\\nOverall: {total_loaded}/{total_docs} documents loaded")
    
    costs = progress.get('embedding_costs', {})
    print(f"\\n💰 Estimated cost: ${costs.get('estimated_cost', 0):.2f}")
    print(f"Tokens: {costs.get('estimated_tokens', 0):,}")
    
    if progress.get('completed_at'):
        print(f"\\n✅ COMPLETED: {progress['completed_at']}")
    else:
        print(f"\\n⏳ IN PROGRESS...")
    
    errors = progress.get('errors', [])
    if errors:
        print(f"\\n❌ ERRORS ({len(errors)}):")
        for error in errors[-3:]:
            print(f"  - {error}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        monitor_progress()
    else:
        loader = BlogYouTubeLoader()
        loader.run_full_load()