#!/usr/bin/env python3
"""
LlamaIndex test with actual blog data from vector-processor
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add vector-processor to path to access blog data
sys.path.append(str(Path("../vector-processor").resolve()))

# LlamaIndex imports
from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.node_parser import SentenceSplitter

import frontmatter

load_dotenv()

def load_blog_documents_simple():
    """Load some blog articles from vector-processor"""
    documents = []
    blog_path = Path("../vector-processor/source-data/blog_articles")
    
    print(f"Looking for blog articles in: {blog_path.absolute()}")
    
    if not blog_path.exists():
        print(f"Blog path does not exist: {blog_path}")
        return documents
    
    # Load just first 5 articles for testing
    count = 0
    for md_file in blog_path.glob("*.md"):
        if count >= 5:
            break
            
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            # Create document
            doc = Document(
                text=post.content,
                metadata={
                    "source": "blog",
                    "source_id": md_file.stem,
                    "title": post.metadata.get('title', md_file.stem),
                    "category": post.metadata.get('category', 'Unknown'),
                    "file_path": str(md_file)
                }
            )
            documents.append(doc)
            count += 1
            print(f"Loaded: {post.metadata.get('title', md_file.stem)}")
            
        except Exception as e:
            print(f"Error loading {md_file}: {e}")
    
    print(f"Total loaded: {len(documents)} blog documents")
    return documents

def test_llamaindex_with_blog_data():
    """Test LlamaIndex with actual blog data"""
    
    # Configure LlamaIndex
    Settings.embed_model = OpenAIEmbedding(
        model="text-embedding-3-large",
        dimensions=1536
    )
    Settings.llm = OpenAI(
        model="gpt-4-turbo-preview",
        temperature=0.1
    )
    
    # Load blog documents
    documents = load_blog_documents_simple()
    
    if not documents:
        print("No documents loaded - cannot proceed with test")
        return
    
    print("\nCreating LlamaIndex...")
    
    # Create index with chunking
    node_parser = SentenceSplitter(
        chunk_size=800,
        chunk_overlap=100,
    )
    
    index = VectorStoreIndex.from_documents(
        documents,
        transformations=[node_parser]
    )
    
    # Create query engine
    query_engine = index.as_query_engine(similarity_top_k=3)
    
    print("\n=== LLAMAINDEX BLOG TEST ===")
    
    # Test queries
    test_queries = [
        "How do I sync my Garmin watch with TrainerDay?",
        "What is FTP testing?",
        "How to set up indoor training?",
        "What are Coach Jack training plans?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        
        try:
            response = query_engine.query(query)
            print(f"Answer: {response}")
            
            # Show sources
            if hasattr(response, 'source_nodes'):
                print(f"\nSources ({len(response.source_nodes)}):")
                for i, node in enumerate(response.source_nodes):
                    title = node.metadata.get('title', 'Unknown')
                    score = getattr(node, 'score', 0.0)
                    print(f"  {i+1}. {title} (score: {score:.3f})")
                    
        except Exception as e:
            print(f"Error processing query: {e}")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    test_llamaindex_with_blog_data()