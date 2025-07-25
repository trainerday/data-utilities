#!/usr/bin/env python3
"""
Final LlamaIndex solution with proper similarity thresholds
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

class OptimizedRAGSystem:
    def __init__(self):
        Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-large", dimensions=1536)
        Settings.llm = OpenAI(model="gpt-4-turbo-preview", temperature=0.0)
        
        self.index = None
        self.query_engine = None
        self.similarity_threshold = 0.6  # Optimal threshold from testing
    
    def setup(self):
        """Load documents and create optimized query engine"""
        
        # Load documents
        documents = []
        blog_path = Path("../vector-processor/source-data/blog_articles")
        
        print("Loading TrainerDay content...")
        for md_file in list(blog_path.glob("*.md"))[:8]:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)
                title = post.metadata.get('title', md_file.stem)
                documents.append(Document(
                    text=post.content,
                    metadata={"title": title}
                ))
                print(f"  ✅ {title}")
            except Exception as e:
                print(f"  ❌ Error loading {md_file}: {e}")
        
        print(f"\\nIndexed {len(documents)} documents")
        self.index = VectorStoreIndex.from_documents(documents)
        
        # Create optimized fact extraction prompt
        fact_prompt = PromptTemplate(
            "Extract specific facts from the content that directly answer the question.\\n\\n"
            "Rules:\\n"
            "- Only include information explicitly stated in the content\\n"
            "- Format as clear bullet points\\n"
            "- If content doesn't answer the question, respond: 'No relevant information found'\\n\\n"
            "Content: {context_str}\\n\\n"
            "Question: {query_str}\\n\\n"
            "Extracted Facts:"
        )
        
        # Create query engine with similarity threshold
        self.query_engine = self.index.as_query_engine(
            text_qa_template=fact_prompt,
            response_mode="compact",
            similarity_top_k=2,
            node_postprocessors=[
                SimilarityPostprocessor(similarity_cutoff=self.similarity_threshold)
            ]
        )
        
        print(f"✅ System ready with similarity threshold: {self.similarity_threshold}")
    
    def query(self, question: str):
        """Query the system with improved retrieval"""
        print(f"\\n{'='*80}")
        print(f"QUERY: {question}")
        print(f"{'='*80}")
        
        try:
            response = self.query_engine.query(question)
            
            if hasattr(response, 'source_nodes') and response.source_nodes:
                print(f"\\n✅ ANSWER FOUND:")
                print(f"{response}")
                
                print(f"\\n📚 SOURCES ({len(response.source_nodes)}):")
                for i, node in enumerate(response.source_nodes):
                    title = node.metadata.get('title', 'Unknown')
                    score = getattr(node, 'score', 'Unknown')
                    print(f"  {i+1}. {title} (relevance: {score:.3f})")
                    
            else:
                print(f"\\n❌ NO RELEVANT INFORMATION FOUND")
                print(f"No content in the TrainerDay documentation matches this query above the similarity threshold ({self.similarity_threshold}).")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    def demo(self):
        """Demonstrate the improved system"""
        test_cases = [
            {
                "query": "What is the Ride Feel feature?",
                "expected": "Should find relevant information about Coach Jack Ride Feel"
            },
            {
                "query": "How do I connect to Spotify?", 
                "expected": "Should reject - no relevant content exists"
            },
            {
                "query": "What is Coach Jack?",
                "expected": "Should find information about Coach Jack training system"
            },
            {
                "query": "How do I setup my smart TV?",
                "expected": "Should reject - completely unrelated to cycling"
            }
        ]
        
        print("\\n🚀 DEMONSTRATING IMPROVED RAG SYSTEM")
        print("Benefits: Similarity thresholds prevent irrelevant matches")
        print("="*80)
        
        for test in test_cases:
            print(f"\\nExpected: {test['expected']}")
            self.query(test["query"])
            print("\\n" + "-"*80)

if __name__ == "__main__":
    system = OptimizedRAGSystem()
    system.setup()
    system.demo()