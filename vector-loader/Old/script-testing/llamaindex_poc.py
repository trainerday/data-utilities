#!/usr/bin/env python3
"""
LlamaIndex Proof of Concept for TrainerDay Vector Database
Demonstrates LlamaIndex capabilities vs custom implementation
"""

import os
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# LlamaIndex imports
from llama_index.core import (
    VectorStoreIndex, 
    Document, 
    StorageContext,
    Settings
)
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor

import frontmatter
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment
load_dotenv()

class LlamaIndexPOC:
    """LlamaIndex proof of concept for TrainerDay content"""
    
    def __init__(self):
        # Configure LlamaIndex settings
        Settings.embed_model = OpenAIEmbedding(
            model="text-embedding-3-large",
            dimensions=1536
        )
        Settings.llm = OpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.1
        )
        
        # Database configuration
        self.db_config = {
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_DATABASE'),
            'user': os.getenv('DB_USERNAME'),
            'password': os.getenv('DB_PASSWORD'),
            'sslmode': os.getenv('DB_SSLMODE', 'require')
        }
        
        # Initialize vector store (separate table for POC)
        self.vector_store = PGVectorStore.from_params(
            database=self.db_config['database'],
            host=self.db_config['host'],
            password=self.db_config['password'],
            port=int(self.db_config['port']),
            user=self.db_config['user'],
            table_name="llamaindex_poc_embeddings",
            embed_dim=1536,
        )
        
        # Storage context
        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )
        
        self.index = None
        self.query_engine = None
    
    def load_blog_documents(self, blog_dir: str = "source-data/blog_articles") -> List[Document]:
        """Load blog articles as LlamaIndex documents"""
        documents = []
        blog_path = Path(blog_dir)
        
        if not blog_path.exists():
            blog_path = Path("../source-data/blog_articles")
        
        for md_file in blog_path.glob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)
                
                # Create document with metadata
                doc = Document(
                    text=post.content,
                    metadata={
                        "source": "blog",
                        "source_id": md_file.stem,
                        "title": post.metadata.get('title', md_file.stem),
                        "category": post.metadata.get('category', 'Unknown'),
                        "engagement": post.metadata.get('engagement', 'Unknown'),
                        "tags": post.metadata.get('tags', []),
                        "file_path": str(md_file)
                    }
                )
                documents.append(doc)
                
            except Exception as e:
                print(f"Error loading {md_file}: {e}")
        
        print(f"Loaded {len(documents)} blog documents")
        return documents
    
    def load_youtube_documents(self, youtube_dir: str = "source-data/youtube_content") -> List[Document]:
        """Load YouTube transcripts as LlamaIndex documents"""
        documents = []
        youtube_path = Path(youtube_dir)
        
        if not youtube_path.exists():
            youtube_path = Path("../source-data/youtube_content")
        
        for json_file in youtube_path.glob("video_*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    video_data = json.load(f)
                
                # Combine transcript segments
                transcript_text = ""
                if 'transcript' in video_data:
                    for segment in video_data['transcript']:
                        transcript_text += f"{segment.get('text', '')} "
                
                if transcript_text.strip():
                    doc = Document(
                        text=transcript_text.strip(),
                        metadata={
                            "source": "youtube",
                            "source_id": video_data.get('video_id', json_file.stem),
                            "title": video_data.get('title', 'Unknown Video'),
                            "duration": video_data.get('duration', 0),
                            "view_count": video_data.get('view_count', 0),
                            "topics": video_data.get('topics', []),
                            "video_url": f"https://youtube.com/watch?v={video_data.get('video_id', '')}"
                        }
                    )
                    documents.append(doc)
                
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
        
        print(f"Loaded {len(documents)} YouTube documents")
        return documents
    
    def load_forum_documents(self) -> List[Document]:
        """Load forum Q&A pairs as LlamaIndex documents"""
        documents = []
        
        try:
            conn = psycopg2.connect(**self.db_config)
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        id,
                        question,
                        answer,
                        category,
                        posts_count,
                        created_at
                    FROM forum_analysis 
                    WHERE question IS NOT NULL 
                    AND answer IS NOT NULL
                    LIMIT 100
                """)
                
                forum_data = cur.fetchall()
                
                for row in forum_data:
                    # Combine question and answer
                    content = f"Question: {row['question']}\n\nAnswer: {row['answer']}"
                    
                    doc = Document(
                        text=content,
                        metadata={
                            "source": "forum",
                            "source_id": str(row['id']),
                            "title": row['question'][:100] + "..." if len(row['question']) > 100 else row['question'],
                            "category": row['category'] or 'general',
                            "posts_count": row['posts_count'] or 0,
                            "created_at": str(row['created_at']) if row['created_at'] else None
                        }
                    )
                    documents.append(doc)
            
            conn.close()
            print(f"Loaded {len(documents)} forum documents")
            
        except Exception as e:
            print(f"Error loading forum data: {e}")
        
        return documents
    
    def create_index(self):
        """Create or load the vector index"""
        # Load all documents
        documents = []
        documents.extend(self.load_blog_documents())
        documents.extend(self.load_youtube_documents())
        documents.extend(self.load_forum_documents())
        
        print(f"Total documents loaded: {len(documents)}")
        
        if not documents:
            print("No documents found!")
            return
        
        # Create index with custom node parser
        node_parser = SentenceSplitter(
            chunk_size=800,
            chunk_overlap=100,
        )
        
        self.index = VectorStoreIndex.from_documents(
            documents,
            storage_context=self.storage_context,
            transformations=[node_parser]
        )
        
        # Create query engine with retriever
        retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=5
        )
        
        self.query_engine = RetrieverQueryEngine(
            retriever=retriever,
            node_postprocessors=[
                SimilarityPostprocessor(similarity_cutoff=0.7)
            ]
        )
        
        print("Index created successfully!")
    
    def search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Search using LlamaIndex query engine"""
        if not self.query_engine:
            print("Index not created yet. Call create_index() first.")
            return {}
        
        print(f"\n=== LlamaIndex Search: '{query}' ===")
        
        # Get response with sources
        response = self.query_engine.query(query)
        
        results = {
            "query": query,
            "response": str(response),
            "sources": []
        }
        
        # Extract source information
        for node in response.source_nodes:
            source_info = {
                "content": node.text[:300] + "..." if len(node.text) > 300 else node.text,
                "score": node.score if hasattr(node, 'score') else 0.0,
                "metadata": node.metadata,
                "node_id": node.node_id
            }
            results["sources"].append(source_info)
        
        return results
    
    def compare_with_current_system(self, query: str):
        """Compare LlamaIndex results with current system"""
        print(f"\n=== COMPARISON: '{query}' ===")
        
        # LlamaIndex search
        llama_results = self.search(query)
        
        print(f"\n--- LlamaIndex Response ---")
        print(f"Answer: {llama_results.get('response', 'No response')}")
        print(f"\nSources ({len(llama_results.get('sources', []))}):")
        for i, source in enumerate(llama_results.get('sources', [])[:3]):
            print(f"{i+1}. [{source['metadata'].get('source', 'unknown')}] {source['metadata'].get('title', 'No title')}")
            print(f"   Score: {source.get('score', 0):.3f}")
            print(f"   Content: {source['content'][:150]}...")
            print()
        
        # Current system comparison (simulated)
        print(f"--- Current System (Simulated) ---") 
        print("Current system would return raw chunks without synthesis")
        print("No direct answer generation, just similarity matches")
        
        return llama_results

def main():
    """Main execution function"""
    poc = LlamaIndexPOC()
    
    print("Creating LlamaIndex POC...")
    poc.create_index()
    
    # Test queries
    test_queries = [
        "How do I sync my Garmin watch with TrainerDay?",
        "What is FTP testing and how do I do it?",
        "How to set up a smart trainer?",
        "Coach Jack training plans explained"
    ]
    
    print("\n" + "="*60)
    print("TESTING LLAMAINDEX PROOF OF CONCEPT")
    print("="*60)
    
    for query in test_queries:
        results = poc.compare_with_current_system(query)
        print("\n" + "-"*60 + "\n")

if __name__ == "__main__":
    main()