#!/usr/bin/env python3
"""
Query system for the loaded LlamaIndex blog content
Perfect for blog post generation and fact extraction
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from llama_index.core import StorageContext, load_index_from_storage, Settings, PromptTemplate
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.postprocessor import SimilarityPostprocessor

load_dotenv()

class TrainerDayKnowledgeBase:
    def __init__(self):
        # Configure LlamaIndex
        Settings.embed_model = OpenAIEmbedding(
            model="text-embedding-3-large", 
            dimensions=1536
        )
        Settings.llm = OpenAI(model="gpt-4-turbo-preview", temperature=0.1)
        
        self.index = None
        self.fact_engine = None
        self.blog_engine = None
        
        # Load the saved index
        self.load_index()
    
    def load_index(self):
        """Load the pre-built index from storage"""
        storage_dir = Path("./llamaindex_storage")
        
        if not storage_dir.exists():
            print("❌ No index found. Run the data loader first.")
            return False
        
        try:
            # Load index from storage
            storage_context = StorageContext.from_defaults(persist_dir=str(storage_dir))
            self.index = load_index_from_storage(storage_context)
            
            print("✅ TrainerDay knowledge base loaded successfully")
            print(f"📚 Content: 69 blog articles ready for querying")
            
            self.setup_query_engines()
            return True
            
        except Exception as e:
            print(f"❌ Error loading index: {e}")
            return False
    
    def setup_query_engines(self):
        """Setup different query engines for different use cases"""
        
        # Fact extraction engine (for blog post research)
        fact_prompt = PromptTemplate(
            "Extract specific facts and information from TrainerDay content that relate to the question. "
            "Rules:\\n"
            "- Only include information explicitly stated in the content\\n"
            "- Format as clear bullet points with specific details\\n"
            "- Include relevant quotes where helpful\\n"
            "- If no relevant information exists, state 'No information found'\\n\\n"
            "Content: {context_str}\\n\\n"
            "Question: {query_str}\\n\\n"
            "Extracted Information:"
        )
        
        self.fact_engine = self.index.as_query_engine(
            text_qa_template=fact_prompt,
            response_mode="compact",
            similarity_top_k=3,
            node_postprocessors=[
                SimilarityPostprocessor(similarity_cutoff=0.6)  # Conservative threshold
            ]
        )
        
        # Blog content engine (for content generation)
        blog_prompt = PromptTemplate(
            "Generate content for a blog post based on TrainerDay's knowledge base. "
            "Use the provided information to create helpful, accurate content. "
            "Maintain TrainerDay's voice and expertise.\\n\\n"
            "Source Content: {context_str}\\n\\n"
            "Topic: {query_str}\\n\\n"
            "Blog Content:"
        )
        
        self.blog_engine = self.index.as_query_engine(
            text_qa_template=blog_prompt,
            response_mode="tree_summarize",
            similarity_top_k=5,
            node_postprocessors=[
                SimilarityPostprocessor(similarity_cutoff=0.5)  # More permissive for content
            ]
        )
        
        print("✅ Query engines configured")
        print("   🔍 Fact extraction engine ready")
        print("   📝 Blog content engine ready")
    
    def extract_facts(self, query: str):
        """Extract facts for research and verification"""
        if not self.fact_engine:
            return "❌ Knowledge base not loaded"
        
        print(f"\\n🔍 EXTRACTING FACTS: {query}")
        print("=" * 60)
        
        try:
            response = self.fact_engine.query(query)
            
            # Show results
            print(f"📋 FACTS FOUND:")
            print(f"{response}")
            
            # Show sources
            if hasattr(response, 'source_nodes') and response.source_nodes:
                print(f"\\n📚 SOURCES ({len(response.source_nodes)}):")
                for i, node in enumerate(response.source_nodes):
                    title = node.metadata.get('title', 'Unknown')
                    score = getattr(node, 'score', 0.0)
                    print(f"  {i+1}. {title} (relevance: {score:.3f})")
            else:
                print(f"\\n❌ No relevant sources found")
            
            return response
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def generate_blog_content(self, topic: str):
        """Generate blog content based on knowledge base"""
        if not self.blog_engine:
            return "❌ Knowledge base not loaded"
        
        print(f"\\n📝 GENERATING BLOG CONTENT: {topic}")
        print("=" * 60)
        
        try:
            response = self.blog_engine.query(topic)
            
            print(f"📄 GENERATED CONTENT:")
            print(f"{response}")
            
            # Show sources used
            if hasattr(response, 'source_nodes') and response.source_nodes:
                print(f"\\n📚 BASED ON SOURCES ({len(response.source_nodes)}):")
                for i, node in enumerate(response.source_nodes):
                    title = node.metadata.get('title', 'Unknown')
                    print(f"  {i+1}. {title}")
            
            return response
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def search_content(self, query: str, top_k: int = 5):
        """Search for relevant content pieces"""
        if not self.index:
            return "❌ Knowledge base not loaded"
        
        print(f"\\n🔍 SEARCHING: {query}")
        print("=" * 60)
        
        try:
            retriever = self.index.as_retriever(similarity_top_k=top_k)
            nodes = retriever.retrieve(query)
            
            print(f"📋 FOUND {len(nodes)} RELEVANT ARTICLES:")
            
            for i, node in enumerate(nodes):
                title = node.metadata.get('title', 'Unknown')
                score = getattr(node, 'score', 0.0)
                category = node.metadata.get('category', 'Unknown')
                
                print(f"\\n{i+1}. {title}")
                print(f"   Category: {category}")
                print(f"   Relevance: {score:.3f}")
                print(f"   Preview: {node.text[:200]}...")
            
            return nodes
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

def demo_knowledge_base():
    """Demonstrate the knowledge base capabilities"""
    kb = TrainerDayKnowledgeBase()
    
    if not kb.index:
        print("❌ Could not load knowledge base")
        return
    
    print("\\n🚀 TRAINERDAY KNOWLEDGE BASE DEMO")
    print("=" * 60)
    print("Loaded content: 69 TrainerDay blog articles")
    print("Use cases: Blog post generation, fact checking, content research")
    
    # Demo queries
    demo_queries = [
        {
            "type": "facts",
            "query": "What is Coach Jack and how does it work?",
            "purpose": "Research for blog post about Coach Jack features"
        },
        {
            "type": "blog", 
            "query": "How to get started with indoor cycling training",
            "purpose": "Generate blog content for beginners"
        },
        {
            "type": "search",
            "query": "FTP testing methods",
            "purpose": "Find existing content about FTP testing"
        }
    ]
    
    for demo in demo_queries:
        print(f"\\n\\n{'='*80}")
        print(f"DEMO: {demo['purpose']}")
        print(f"{'='*80}")
        
        if demo["type"] == "facts":
            kb.extract_facts(demo["query"])
        elif demo["type"] == "blog":
            kb.generate_blog_content(demo["query"])
        elif demo["type"] == "search":
            kb.search_content(demo["query"], top_k=3)
        
        input("\\nPress Enter to continue...")

if __name__ == "__main__":
    demo_knowledge_base()