#!/usr/bin/env python3
"""
Test different similarity thresholds to find the right balance
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from llama_index.core import VectorStoreIndex, Document, Settings, PromptTemplate
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.postprocessor import SimilarityPostprocessor

import frontmatter

load_dotenv()

def test_similarity_thresholds():
    """Test different similarity thresholds to find optimal setting"""
    
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-large", dimensions=1536)
    Settings.llm = OpenAI(model="gpt-4-turbo-preview", temperature=0.0)
    
    # Load documents
    documents = []
    blog_path = Path("../vector-processor/source-data/blog_articles")
    
    for md_file in list(blog_path.glob("*.md"))[:5]:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            title = post.metadata.get('title', md_file.stem)
            documents.append(Document(
                text=post.content,
                metadata={"title": title}
            ))
        except Exception as e:
            continue
    
    print(f"Testing with {len(documents)} documents")
    index = VectorStoreIndex.from_documents(documents)
    
    # Test different thresholds
    thresholds = [0.5, 0.6, 0.7, 0.75, 0.8]
    queries = [
        "What is the Ride Feel feature?",  # Should have good match
        "How do I connect to Spotify?"     # Should have poor match
    ]
    
    fact_prompt = PromptTemplate(
        "Extract facts from the content. If no relevant info, say 'No relevant information found'.\\n\\n"
        "Context: {context_str}\\n\\nQuestion: {query_str}\\n\\nFacts:"
    )
    
    for query in queries:
        print(f"\\n{'='*80}")
        print(f"TESTING QUERY: '{query}'")
        print(f"{'='*80}")
        
        for threshold in thresholds:
            print(f"\\n--- THRESHOLD: {threshold} ---")
            
            try:
                engine = index.as_query_engine(
                    text_qa_template=fact_prompt,
                    response_mode="compact",
                    similarity_top_k=2,
                    node_postprocessors=[
                        SimilarityPostprocessor(similarity_cutoff=threshold)
                    ]
                )
                
                response = engine.query(query)
                
                if hasattr(response, 'source_nodes') and response.source_nodes:
                    print(f"Sources found: {len(response.source_nodes)}")
                    for i, node in enumerate(response.source_nodes):
                        score = getattr(node, 'score', 'Unknown')
                        title = node.metadata.get('title', 'Unknown')
                        print(f"  {i+1}. {title} (score: {score})")
                    print(f"Response: {str(response)[:100]}...")
                else:
                    print("No sources above threshold")
                    print(f"Response: {response}")
                    
            except Exception as e:
                print(f"Error: {e}")
    
    # Manual similarity check
    print(f"\\n{'='*80}")
    print("MANUAL SIMILARITY CHECK")
    print(f"{'='*80}")
    
    # Get raw retriever to see actual scores
    retriever = index.as_retriever(similarity_top_k=3)
    
    for query in queries:
        print(f"\\nQuery: '{query}'")
        print("Raw similarity scores:")
        
        nodes = retriever.retrieve(query)
        for i, node in enumerate(nodes):
            score = getattr(node, 'score', 'Unknown')
            title = node.metadata.get('title', 'Unknown')
            print(f"  {i+1}. {title}: {score}")

if __name__ == "__main__":
    test_similarity_thresholds()