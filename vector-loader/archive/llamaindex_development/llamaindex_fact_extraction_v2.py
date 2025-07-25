#!/usr/bin/env python3
"""
LlamaIndex fact extraction - adjusted prompt for better balance
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from llama_index.core import VectorStoreIndex, Document, Settings, PromptTemplate
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.node_parser import SentenceSplitter

import frontmatter

load_dotenv()

def test_controlled_responses():
    """Test different levels of controlled responses"""
    
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-large", dimensions=1536)
    Settings.llm = OpenAI(model="gpt-4-turbo-preview", temperature=0.0)
    
    # Load documents
    documents = []
    blog_path = Path("../vector-processor/source-data/blog_articles")
    
    for md_file in list(blog_path.glob("*.md"))[:8]:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            documents.append(Document(
                text=post.content,
                metadata={"title": post.metadata.get('title', md_file.stem)}
            ))
        except Exception as e:
            continue
    
    index = VectorStoreIndex.from_documents(documents)
    
    # Test different prompt styles
    prompts = {
        "Raw Facts": PromptTemplate(
            "List only direct quotes and explicit statements from the content about the topic. "
            "Format: 'According to [source]: [exact quote]'\n"
            "If no direct information exists, state: 'No explicit information found.'\n\n"
            "Context: {context_str}\n\n"
            "Question: {query_str}\n\n"
            "Direct Quotes:"
        ),
        
        "Structured Facts": PromptTemplate(
            "Extract factual information from the content and organize it clearly. "
            "Only include information explicitly stated in the sources. "
            "Use bullet points and cite sources.\n\n"
            "Context: {context_str}\n\n"
            "Question: {query_str}\n\n"
            "Facts:"
        ),
        
        "Default": None  # Uses default LlamaIndex prompt
    }
    
    # Test query that should have clear information
    query = "What features does the Ride Feel have?"
    
    print(f"TESTING QUERY: '{query}'")
    print("="*80)
    
    for mode_name, prompt in prompts.items():
        print(f"\n--- {mode_name.upper()} MODE ---")
        
        if prompt:
            engine = index.as_query_engine(
                text_qa_template=prompt,
                response_mode="compact",
                similarity_top_k=2
            )
        else:
            engine = index.as_query_engine(similarity_top_k=2)
        
        try:
            response = engine.query(query)
            print(f"Response: {response}")
            
            # Show which sources were used
            if hasattr(response, 'source_nodes') and response.source_nodes:
                print(f"\nSources:")
                for i, node in enumerate(response.source_nodes):
                    title = node.metadata.get('title', 'Unknown')
                    content_preview = node.text[:100].replace('\n', ' ') + "..."
                    print(f"  {i+1}. {title}")
                    print(f"     Content: {content_preview}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        print(f"\n{'-'*60}")
    
    # Test with a query that has NO answer in the data
    print(f"\n\nTESTING MISSING INFO: 'How do I connect to Strava?'")
    print("="*80)
    
    structured_engine = index.as_query_engine(
        text_qa_template=prompts["structured_facts"],
        response_mode="compact"
    )
    
    response = structured_engine.query("How do I connect to Strava?")
    print(f"Response: {response}")

if __name__ == "__main__":
    test_controlled_responses()