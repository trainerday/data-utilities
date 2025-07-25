#!/usr/bin/env python3
"""
Improved LlamaIndex retrieval with similarity thresholds and query routing
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from llama_index.core import VectorStoreIndex, Document, Settings, PromptTemplate
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine

import frontmatter

load_dotenv()

class ImprovedRAGSystem:
    def __init__(self):
        Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-large", dimensions=1536)
        Settings.llm = OpenAI(model="gpt-4-turbo-preview", temperature=0.0)
        
        # Known topics/integrations in TrainerDay content
        self.known_integrations = {
            'garmin', 'wahoo', 'elemnt', 'zwift', 'trainingpeaks', 'trainer', 
            'coach jack', 'ftp', 'cycling', 'workouts', 'training', 'power',
            'heart rate', 'indoor', 'bike', 'ramp test'
        }
        
        self.index = None
        self.query_engine = None
    
    def load_documents(self):
        """Load documents with better metadata"""
        documents = []
        blog_path = Path("../vector-processor/source-data/blog_articles")
        
        print("Loading documents with improved metadata...")
        for md_file in list(blog_path.glob("*.md"))[:6]:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)
                
                title = post.metadata.get('title', md_file.stem)
                
                # Extract key topics from title and content for routing
                content_lower = post.content.lower()
                topics = []
                for integration in self.known_integrations:
                    if integration in content_lower or integration in title.lower():
                        topics.append(integration)
                
                documents.append(Document(
                    text=post.content,
                    metadata={
                        "title": title,
                        "filename": md_file.stem,
                        "topics": topics,
                        "content_type": "blog"
                    }
                ))
                print(f"  - {title} (topics: {topics[:3]})")
                
            except Exception as e:
                print(f"  - Error loading {md_file}: {e}")
        
        print(f"\\nCreated index from {len(documents)} documents")
        self.index = VectorStoreIndex.from_documents(documents)
    
    def query_router(self, query: str) -> dict:
        """Route queries and detect out-of-domain requests"""
        query_lower = query.lower()
        
        # Check if query contains known topics
        mentioned_topics = []
        for topic in self.known_integrations:
            if topic in query_lower:
                mentioned_topics.append(topic)
        
        # Detect obviously out-of-domain queries
        out_of_domain_keywords = {
            'spotify', 'apple music', 'netflix', 'facebook', 'instagram', 
            'twitter', 'linkedin', 'slack', 'discord', 'whatsapp'
        }
        
        out_of_domain = any(keyword in query_lower for keyword in out_of_domain_keywords)
        
        return {
            "should_search": not out_of_domain,
            "confidence": "high" if mentioned_topics else "low",
            "mentioned_topics": mentioned_topics,
            "out_of_domain": out_of_domain,
            "reason": f"Contains out-of-domain keyword" if out_of_domain else "Proceeding with search"
        }
    
    def setup_improved_retrieval(self):
        """Setup retrieval with similarity thresholds"""
        
        # Create retriever with similarity filtering
        retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=3,  # Get more candidates for filtering
        )
        
        # Custom fact extraction prompt
        fact_prompt = PromptTemplate(
            "Extract specific facts from the provided content that directly answer the question. "
            "Rules:\\n"
            "1. Only include information explicitly stated in the content\\n"
            "2. If the content doesn't contain relevant information, state 'No relevant information found'\\n"
            "3. Format facts as clear bullet points\\n"
            "4. Do not infer or extrapolate beyond what's stated\\n\\n"
            "Content: {context_str}\\n\\n"
            "Question: {query_str}\\n\\n"
            "Facts:"
        )
        
        # Create query engine with strict similarity filtering
        self.query_engine = RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=None,  # We'll handle this manually
            node_postprocessors=[
                SimilarityPostprocessor(similarity_cutoff=0.75)  # Key improvement!
            ]
        )
        
        # Create separate engine for fact extraction
        self.fact_engine = self.index.as_query_engine(
            text_qa_template=fact_prompt,
            response_mode="compact",
            similarity_top_k=2,
            node_postprocessors=[
                SimilarityPostprocessor(similarity_cutoff=0.75)
            ]
        )
    
    def improved_query(self, query: str):
        """Query with routing and improved retrieval"""
        print(f"\\n{'='*80}")
        print(f"QUERY: {query}")
        print(f"{'='*80}")
        
        # Step 1: Query routing
        routing = self.query_router(query)
        print(f"Routing Decision: {routing}")
        
        if not routing["should_search"]:
            print(f"\\n❌ OUT-OF-DOMAIN QUERY DETECTED")
            print(f"Response: No information available about {query.split()[-1].rstrip('?')} in TrainerDay documentation.")
            return
        
        # Step 2: Retrieval with similarity threshold
        print(f"\\n🔍 RETRIEVING WITH SIMILARITY THRESHOLD...")
        try:
            response = self.fact_engine.query(query)
            
            print(f"\\n✅ EXTRACTED FACTS:")
            print(f"{response}")
            
            # Show what was actually retrieved
            if hasattr(response, 'source_nodes') and response.source_nodes:
                print(f"\\n📚 SOURCES USED ({len(response.source_nodes)}):")
                for i, node in enumerate(response.source_nodes):
                    title = node.metadata.get('title', 'Unknown')
                    score = getattr(node, 'score', 'Unknown')
                    topics = node.metadata.get('topics', [])
                    print(f"  {i+1}. {title}")
                    print(f"     Similarity: {score}")
                    print(f"     Topics: {topics}")
                    print(f"     Preview: {node.text[:100].replace(chr(10), ' ')}...")
                    print()
            else:
                print(f"\\n❌ NO RELEVANT SOURCES FOUND (below similarity threshold)")
                
        except Exception as e:
            print(f"Error during retrieval: {e}")

def test_improved_system():
    """Test the improved retrieval system"""
    
    system = ImprovedRAGSystem()
    system.load_documents()
    system.setup_improved_retrieval()
    
    # Test queries
    test_queries = [
        "What is the Ride Feel feature?",  # Should work well
        "How do I connect to Spotify?",   # Should be rejected by router
        "How do I sync with Garmin?",     # Should find some info or reject cleanly
        "What is FTP testing?",           # May or may not have info
    ]
    
    for query in test_queries:
        system.improved_query(query)
        input("\\nPress Enter for next query...")

if __name__ == "__main__":
    test_improved_system()