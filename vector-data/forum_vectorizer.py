#!/usr/bin/env python3
"""
Forum Data Vector Database using ChromaDB
Indexes Discourse forum topics and posts for semantic search
"""

import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import re

import chromadb
from chromadb.config import Settings
import openai
import tiktoken
from dotenv import load_dotenv

load_dotenv()

@dataclass
class ForumDocument:
    content: str
    doc_type: str  # 'topic', 'post', 'conversation'
    doc_id: str
    metadata: Dict[str, Any]

class ForumVectorizer:
    def __init__(self, db_path: str = "../chroma_db", openai_api_key: str = None):
        self.db_path = db_path
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.openai_api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")
        
        openai.api_key = self.openai_api_key
        
        # Initialize ChromaDB (same as SourceVectorizer)
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(allow_reset=True)
        )
        
        # Get or create forum collection
        self.collection = self.client.get_or_create_collection(
            name="forum_data",
            metadata={"description": "Forum topics and posts embeddings"}
        )
        
        # Initialize tokenizer for chunking (same as SourceVectorizer)
        self.tokenizer = tiktoken.encoding_for_model("text-embedding-3-small")
        
    def clean_html(self, text: str) -> str:
        """Remove HTML tags and clean text"""
        # Remove HTML tags
        clean = re.sub('<.*?>', '', text)
        # Replace HTML entities
        clean = clean.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        # Clean up whitespace
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean
    
    def get_embedding(self, text: str) -> List[float]:
        """Get OpenAI embedding for text (same as SourceVectorizer)"""
        try:
            response = openai.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return None
    
    def chunk_text(self, text: str, max_tokens: int = 1000) -> List[str]:
        """Split text into chunks based on token limit"""
        tokens = self.tokenizer.encode(text)
        
        if len(tokens) <= max_tokens:
            return [text]
        
        # Split into sentences first
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            sentence_tokens = len(self.tokenizer.encode(sentence))
            
            if current_tokens + sentence_tokens > max_tokens and current_chunk:
                chunks.append('. '.join(current_chunk) + '.')
                current_chunk = [sentence]
                current_tokens = sentence_tokens
            else:
                current_chunk.append(sentence)
                current_tokens += sentence_tokens
        
        if current_chunk:
            chunks.append('. '.join(current_chunk) + '.')
        
        return chunks
    
    def process_topic_file(self, file_path: Path) -> List[ForumDocument]:
        """Process a single topic JSON file into forum documents"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return []
        
        documents = []
        topic = data.get('topic', {})
        posts = data.get('posts', [])
        
        if not topic or not posts:
            return documents
        
        # 1. Create topic document
        topic_content = f"Topic: {topic.get('title', '')}\n"
        if topic.get('excerpt'):
            topic_content += f"Excerpt: {self.clean_html(topic['excerpt'])}\n"
        
        # Add first post content to topic
        first_post = next((p for p in posts if p.get('post_number') == 1), None)
        if first_post and first_post.get('cooked'):
            topic_content += f"Content: {self.clean_html(first_post['cooked'])}"
        
        topic_doc = ForumDocument(
            content=topic_content,
            doc_type="topic",
            doc_id=f"topic_{topic['id']}",
            metadata={
                'topic_id': topic['id'],
                'title': topic.get('title', ''),
                'category_id': topic.get('category_id'),
                'posts_count': topic.get('posts_count', 0),
                'views': topic.get('views', 0),
                'like_count': topic.get('like_count', 0),
                'created_at': topic.get('created_at', ''),
                'doc_type': 'topic'
            }
        )
        documents.append(topic_doc)
        
        # 2. Create individual post documents
        for post in posts:
            if not post.get('cooked'):
                continue
                
            post_content = self.clean_html(post['cooked'])
            if not post_content.strip():
                continue
            
            post_doc = ForumDocument(
                content=post_content,
                doc_type="post",
                doc_id=f"post_{post['id']}",
                metadata={
                    'post_id': post['id'],
                    'topic_id': topic['id'],
                    'topic_title': topic.get('title', ''),
                    'post_number': post.get('post_number', 0),
                    'username': post.get('username', ''),
                    'user_id': post.get('user_id'),
                    'reply_to_post_number': post.get('reply_to_post_number'),
                    'like_count': post.get('like_count', 0),
                    'created_at': post.get('created_at', ''),
                    'trust_level': post.get('trust_level'),
                    'doc_type': 'post'
                }
            )
            documents.append(post_doc)
        
        # 3. Create conversation document (topic + all posts)
        conversation_content = topic_content + "\n\n"
        for post in posts:
            if post.get('cooked'):
                clean_content = self.clean_html(post['cooked'])
                if clean_content.strip():
                    conversation_content += f"Post by {post.get('username', 'Unknown')}: {clean_content}\n\n"
        
        # Chunk conversation if too long
        chunks = self.chunk_text(conversation_content)
        for i, chunk in enumerate(chunks):
            conv_doc = ForumDocument(
                content=chunk,
                doc_type="conversation",
                doc_id=f"conversation_{topic['id']}_{i}",
                metadata={
                    'topic_id': topic['id'],
                    'title': topic.get('title', ''),
                    'category_id': topic.get('category_id'),
                    'posts_count': len(posts),
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'participants': len(set(p.get('username', '') for p in posts if p.get('username'))),
                    'created_at': topic.get('created_at', ''),
                    'doc_type': 'conversation'
                }
            )
            documents.append(conv_doc)
        
        return documents
    
    def index_forum_data(self, forum_data_path: str) -> int:
        """Index all forum data from directory or consolidated JSON"""
        forum_path = Path(forum_data_path)
        documents_processed = 0
        
        print(f"Indexing forum data from: {forum_path}")
        
        if forum_path.is_file() and forum_path.suffix == '.json':
            # Handle consolidated JSON file
            try:
                with open(forum_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if 'posts' in data:
                    # Handle consolidated format
                    documents = self.process_consolidated_data(data)
                else:
                    # Handle single topic file
                    documents = self.process_topic_file(forum_path)
                    
                documents_processed += self.add_documents_to_db(documents)
                    
            except Exception as e:
                print(f"Error processing {forum_path}: {e}")
                
        elif forum_path.is_dir():
            # Look for forum_data subdirectory first
            forum_data_dir = forum_path / "forum_data"
            if forum_data_dir.exists():
                topic_files = list(forum_data_dir.glob("topic_*.json"))
                print(f"Found {len(topic_files)} topic files in forum_data/")
            else:
                # Handle directory of topic files directly
                topic_files = list(forum_path.glob("topic_*.json"))
                print(f"Found {len(topic_files)} topic files in root directory")
            
            for file_path in topic_files:
                try:
                    documents = self.process_topic_file(file_path)
                    documents_processed += self.add_documents_to_db(documents)
                    
                    if documents_processed % 50 == 0:
                        print(f"Processed {documents_processed} documents...")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                    continue
        
        print(f"Finished indexing forum data: {documents_processed} documents")
        return documents_processed
    
    def clean_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Clean metadata to remove None values and ensure ChromaDB compatibility"""
        cleaned = {}
        for key, value in metadata.items():
            if value is not None:
                # Convert to string if it's not a basic type
                if isinstance(value, (str, int, float, bool)):
                    cleaned[key] = value
                else:
                    cleaned[key] = str(value)
        return cleaned

    def add_documents_to_db(self, documents: List[ForumDocument]) -> int:
        """Add forum documents to ChromaDB"""
        if not documents:
            return 0
            
        added_count = 0
        for doc in documents:
            embedding = self.get_embedding(doc.content)
            if embedding is None:
                continue
                
            try:
                cleaned_metadata = self.clean_metadata(doc.metadata)
                self.collection.add(
                    ids=[doc.doc_id],
                    embeddings=[embedding],
                    documents=[doc.content],
                    metadatas=[cleaned_metadata]
                )
                added_count += 1
            except Exception as e:
                print(f"Error adding document {doc.doc_id}: {e}")
                continue
        
        return added_count
    
    def search_forum(self, query: str, n_results: int = 10, doc_type: str = None, 
                    topic_id: int = None, username: str = None, after_date: str = None) -> List[Dict]:
        """Search forum data with filters"""
        embedding = self.get_embedding(query)
        if embedding is None:
            return []
            
        where_clause = {}
        if doc_type:
            where_clause['doc_type'] = doc_type
        if topic_id:
            where_clause['topic_id'] = topic_id
        if username:
            where_clause['username'] = username
            
        # Get more results than needed to filter by date
        query_limit = n_results * 3 if after_date else n_results
            
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=query_limit,
            where=where_clause if where_clause else None
        )
        
        formatted_results = []
        for i in range(len(results['ids'][0])):
            metadata = results['metadatas'][0][i]
            
            # Filter by date if specified
            if after_date and 'created_at' in metadata:
                created_date = metadata['created_at'][:10]  # Get YYYY-MM-DD part
                if created_date < after_date:
                    continue
            
            formatted_results.append({
                'id': results['ids'][0][i],
                'content': results['documents'][0][i],
                'metadata': metadata,
                'distance': results['distances'][0][i] if 'distances' in results else None
            })
            
            # Stop when we have enough results
            if len(formatted_results) >= n_results:
                break
            
        return formatted_results
    
    def get_stats(self) -> Dict:
        """Get forum database statistics"""
        count = self.collection.count()
        
        if count == 0:
            return {'total_documents': 0}
        
        # Get sample metadata to analyze
        sample = self.collection.get(limit=min(1000, count))
        metadatas = sample['metadatas']
        
        doc_types = {}
        topics = set()
        users = set()
        
        for meta in metadatas:
            doc_type = meta.get('doc_type', 'unknown')
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            
            if 'topic_id' in meta:
                topics.add(meta['topic_id'])
            if 'username' in meta:
                users.add(meta['username'])
        
        return {
            'total_documents': count,
            'document_types': doc_types,
            'unique_topics': len(topics),
            'unique_users': len(users)
        }

def main():
    """Example usage"""
    vectorizer = ForumVectorizer()
    
    # Index forum data
    forum_path = "/Users/alex/Documents/Projects/data-utilities/forum"
    vectorizer.index_forum_data(forum_path)
    
    # Show stats
    stats = vectorizer.get_stats()
    print(f"\n=== Forum Database Stats ===")
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Example searches
    print(f"\n=== Search Examples ===")
    
    # Search all forum content
    results = vectorizer.search_forum("authentication problem", n_results=3)
    print(f"\nGeneral search for 'authentication problem':")
    for result in results[:2]:
        meta = result['metadata']
        print(f"  {meta['doc_type']}: {result['content'][:100]}...")
    
    # Search only topics
    results = vectorizer.search_forum("training data", n_results=3, doc_type="topic")
    print(f"\nTopic search for 'training data':")
    for result in results[:2]:
        meta = result['metadata']
        print(f"  Topic: {meta.get('title', 'No title')}")

if __name__ == "__main__":
    main()