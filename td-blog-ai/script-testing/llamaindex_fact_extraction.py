#!/usr/bin/env python3
"""
LlamaIndex with custom fact-extraction prompt
Test controlled, conservative responses vs hallucination
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# LlamaIndex imports
from llama_index.core import VectorStoreIndex, Document, Settings, PromptTemplate
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.postprocessor import SimilarityPostprocessor

import frontmatter

load_dotenv()

def load_blog_documents():
    """Load blog documents to test with"""
    documents = []
    blog_path = Path("../vector-processor/source-data/blog_articles")
    
    count = 0
    for md_file in blog_path.glob("*.md"):
        if count >= 8:
            break
            
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            doc = Document(
                text=post.content,
                metadata={
                    "source": "blog",
                    "title": post.metadata.get('title', md_file.stem),
                    "category": post.metadata.get('category', 'Unknown'),
                }
            )
            documents.append(doc)
            count += 1
            print(f"Loaded: {post.metadata.get('title', md_file.stem)[:60]}...")
            
        except Exception as e:
            print(f"Error loading {md_file}: {e}")
    
    return documents

def test_fact_extraction():
    """Test fact extraction vs synthesis modes"""
    
    # Configure LlamaIndex
    Settings.embed_model = OpenAIEmbedding(
        model="text-embedding-3-large",
        dimensions=1536
    )
    Settings.llm = OpenAI(
        model="gpt-4-turbo-preview",
        temperature=0.0  # More deterministic
    )
    
    # Load documents
    documents = load_blog_documents()
    print(f"\nLoaded {len(documents)} documents")
    
    # Create index
    node_parser = SentenceSplitter(chunk_size=600, chunk_overlap=50)
    index = VectorStoreIndex.from_documents(documents, transformations=[node_parser])
    
    # Define custom fact-extraction prompt
    fact_extraction_prompt = PromptTemplate(
        "You are a precise fact extractor. Extract only explicitly stated facts from the provided content. "
        "Rules:\n"
        "1. Quote exact statements from the source\n"
        "2. Do not infer, interpret, or add information\n"
        "3. If information is not explicitly stated, say 'Not explicitly stated in the content'\n"
        "4. Cite which source each fact comes from\n\n"
        "Context: {context_str}\n\n"
        "Question: {query_str}\n\n"
        "Factual Response:"
    )
    
    # Create two query engines for comparison
    fact_engine = index.as_query_engine(
        text_qa_template=fact_extraction_prompt,
        response_mode="compact",
        similarity_top_k=3,
        node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.6)]
    )
    
    synthesis_engine = index.as_query_engine(
        response_mode="tree_summarize",
        similarity_top_k=3
    )
    
    # Test with keyword that should exist in the loaded content
    test_query = "What is Coach Jack and how does it work?"
    
    print(f"\n{'='*80}")
    print(f"TEST QUERY: '{test_query}'")
    print(f"{'='*80}")
    
    # Test fact extraction mode
    print("\n--- FACT EXTRACTION MODE ---")
    print("(Extract only explicitly stated facts)")
    try:
        fact_response = fact_engine.query(test_query)
        print(f"Response: {fact_response}")
        
        if hasattr(fact_response, 'source_nodes'):
            print(f"\nSources used:")
            for i, node in enumerate(fact_response.source_nodes):
                title = node.metadata.get('title', 'Unknown')
                print(f"  {i+1}. {title}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test synthesis mode (prone to hallucination)
    print(f"\n{'-'*80}")
    print("--- SYNTHESIS MODE ---")
    print("(Generate comprehensive answer - may hallucinate)")
    try:
        synthesis_response = synthesis_engine.query(test_query)
        print(f"Response: {synthesis_response}")
        
        if hasattr(synthesis_response, 'source_nodes'):
            print(f"\nSources used:")
            for i, node in enumerate(synthesis_response.source_nodes):
                title = node.metadata.get('title', 'Unknown')
                print(f"  {i+1}. {title}")
    except Exception as e:
        print(f"Error: {e}")
    
    print(f"\n{'-'*80}")
    print("ANALYSIS:")
    print("• Fact Extraction: Conservative, quotes sources directly")
    print("• Synthesis Mode: More comprehensive but may add inferences")
    print("• You can control the trade-off based on use case")
    print(f"{'-'*80}")

if __name__ == "__main__":
    test_fact_extraction()