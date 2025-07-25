#!/usr/bin/env python3
"""
Fixed fact extraction test - properly show the extracted facts
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from llama_index.core import VectorStoreIndex, Document, Settings, PromptTemplate
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

import frontmatter

load_dotenv()

def test_fact_extraction_properly():
    """Test fact extraction and actually show the results clearly"""
    
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-large", dimensions=1536)
    Settings.llm = OpenAI(model="gpt-4-turbo-preview", temperature=0.0)
    
    # Load documents
    documents = []
    blog_path = Path("../vector-processor/source-data/blog_articles")
    
    print("Loading documents...")
    for md_file in list(blog_path.glob("*.md"))[:5]:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            title = post.metadata.get('title', md_file.stem)
            documents.append(Document(
                text=post.content,
                metadata={"title": title}
            ))
            print(f"  - {title}")
        except Exception as e:
            print(f"  - Error loading {md_file}: {e}")
    
    print(f"\nCreating index from {len(documents)} documents...")
    index = VectorStoreIndex.from_documents(documents)
    
    # Create structured fact extraction prompt
    fact_prompt = PromptTemplate(
        "Extract specific facts from the content about the topic. "
        "Present facts as bullet points with clear statements. "
        "Only include information explicitly mentioned in the sources. "
        "If no relevant information exists, state 'No information found about this topic.'\n\n"
        "Context: {context_str}\n\n"
        "Question: {query_str}\n\n"
        "Extracted Facts:"
    )
    
    fact_engine = index.as_query_engine(
        text_qa_template=fact_prompt,
        response_mode="compact",
        similarity_top_k=2
    )
    
    # Test with specific query
    query = "What is the Ride Feel feature?"
    
    print(f"\n{'='*80}")
    print(f"QUERY: {query}")
    print(f"{'='*80}")
    
    try:
        print("Processing query...")
        response = fact_engine.query(query)
        
        print(f"\nEXTRACTED FACTS:")
        print(f"{response}")
        
        # Show sources
        if hasattr(response, 'source_nodes') and response.source_nodes:
            print(f"\nSOURCE DOCUMENTS USED:")
            for i, node in enumerate(response.source_nodes):
                title = node.metadata.get('title', 'Unknown Document')
                print(f"  {i+1}. {title}")
                # Show first 200 chars of the source content
                preview = node.text[:200].replace('\n', ' ').strip() + "..."
                print(f"     Preview: {preview}")
        else:
            print(f"\nNo source nodes found in response")
            
    except Exception as e:
        print(f"ERROR during query: {e}")
        import traceback
        traceback.print_exc()
    
    # Test with question that should have no answer
    print(f"\n\n{'='*80}")
    print("TESTING QUERY WITH NO ANSWER: 'How do I connect to Spotify?'")
    print(f"{'='*80}")
    
    try:
        no_answer_response = fact_engine.query("How do I connect to Spotify?")
        print(f"\nRESPONSE: {no_answer_response}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_fact_extraction_properly()