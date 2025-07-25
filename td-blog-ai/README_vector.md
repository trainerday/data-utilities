# Vector Query and Article Generation System

## 🎯 Overview

This document explains how to query the TrainerDay LlamaIndex knowledge base and generate comprehensive articles from the vector database. The system uses optimized similarity thresholds and priority-based retrieval to extract relevant content and create high-quality articles.

## 📊 System Architecture

### Knowledge Base Structure
The knowledge base contains ~5,900 documents from four sources:
- **Facts**: 710 validated facts (including 57 "wrong" facts for prevention)
- **Blog Articles**: 91 published articles
- **YouTube Transcripts**: 54 video transcripts
- **Forum Content**: ~5,000 Q&A pairs and discussions

### Priority-Based Retrieval
Different content types have different similarity thresholds:
- Facts: 0.6 (increased from 0.25 for generic queries)
- Blog: 0.6 (increased from 0.35)
- YouTube: 0.65 (increased from 0.4)
- Forum: 0.7 (increased from 0.5)

## 🔍 Query Process

### 1. Basic Query Script
```python
# query_workout_features.py - Query specific features
from llama_index.embeddings.openai import OpenAIEmbedding
import psycopg2

# Initialize embedding model
embedding_model = OpenAIEmbedding(
    model="text-embedding-3-large",
    dimensions=1536
)

# Get query embedding
query_embedding = embedding_model.get_text_embedding("your query here")

# Query with optimized thresholds
cur.execute("""
    SELECT text, metadata_->>'source' as source, 
           embedding <=> %s::vector as distance
    FROM llamaindex_knowledge_base 
    WHERE embedding IS NOT NULL
    AND (
        (metadata_->>'source' = 'facts' AND embedding <=> %s::vector <= 0.6) OR
        (metadata_->>'source' = 'blog' AND embedding <=> %s::vector <= 0.6) OR
        (metadata_->>'source' = 'youtube' AND embedding <=> %s::vector <= 0.65) OR
        (metadata_->>'source' = 'forum' AND embedding <=> %s::vector <= 0.7)
    )
    ORDER BY distance
    LIMIT 20
""", (query_embedding, query_embedding, query_embedding, query_embedding, query_embedding))
```

### 2. Comprehensive Feature Query
```bash
# Query all features from a structured list
python script-testing/query_all_workout_features.py
```

This script:
- Queries multiple search terms per feature
- Deduplicates results
- Saves results to JSON files
- Generates summary statistics

### 3. Testing Embedding Distances
```bash
# Understand why queries return limited results
python script-testing/test_embedding_distances.py
```

This revealed that generic queries need higher thresholds than exact title matches.

## 📝 Article Generation Process

### 1. Generate from Query Results
```bash
# Generate article from comprehensive query results
python script-testing/generate_comprehensive_workout_article.py
```

Key features:
- Loads query results from JSON
- Retrieves full blog articles when needed
- Extracts key quotes and examples
- Uses OpenAI GPT-4 to generate article
- Includes specific content from knowledge base

### 2. Article Structure Template
The system uses this structure for comprehensive articles:
1. **Introduction** - Philosophy and overview
2. **Main Sections** - Organized by category
3. **Feature Details** - What it does and why it matters
4. **User Insights** - From forum discussions
5. **Practical Examples** - From blog/video content
6. **Conclusion** - Summary and next steps

### 3. Content Extraction
The generator extracts:
- Direct quotes from blog articles
- User questions from forums
- Technical explanations from videos
- Validated facts from fact database

## 🚀 Quick Start Guide

### Step 1: Set Up Environment
```bash
# Install dependencies
pip install openai psycopg2-binary python-dotenv llama-index-embeddings-openai

# Set environment variables
export OPENAI_API_KEY="your-key-here"
export USER="your-postgres-user"
```

### Step 2: Query for Content
```python
# Create a query script for your topic
from pathlib import Path
import json

# Define features to query
features = {
    "Category Name": {
        "Feature Name": [
            "search term 1",
            "search term 2",
            "search term 3"
        ]
    }
}

# Run queries and save results
results = query_all_features(features)
Path("results.json").write_text(json.dumps(results, indent=2))
```

### Step 3: Generate Article
```python
# Load results and generate article
results = json.loads(Path("results.json").read_text())

# Extract key content
key_quotes = extract_key_quotes(results)

# Build prompt
prompt = build_article_prompt(results, key_quotes)

# Generate with OpenAI
response = openai_client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[
        {"role": "system", "content": "You are Alex, founder of TrainerDay."},
        {"role": "user", "content": prompt}
    ],
    max_tokens=4096
)
```

## 📊 Query Optimization Tips

### 1. Use Multiple Search Terms
For each concept, use:
- Exact feature name
- Common variations
- Related terminology
- User language from forums

### 2. Adjust Thresholds Based on Results
- If too few results: Increase thresholds
- If too many irrelevant results: Decrease thresholds
- Test with `test_embedding_distances.py`

### 3. Prioritize Content Sources
- Facts: Most authoritative but limited
- Blog: Comprehensive official content
- YouTube: Good for procedures and demos
- Forum: User language and edge cases

## 🔧 Troubleshooting

### Common Issues

**1. Few or No Query Results**
- Generic queries need higher similarity thresholds
- Try multiple search term variations
- Check if content exists with direct database queries

**2. Article Generation Hallucinations**
- Always provide specific quotes from knowledge base
- Use "DO NOT MAKE UP INFORMATION" instructions
- Include actual content in prompts, not just summaries

**3. Performance Issues**
- Batch queries instead of individual calls
- Use database connection pooling
- Cache embedding results

**4. Content Quality**
- Verify facts against "wrong facts" database
- Cross-reference multiple sources
- Include user testimonials from forums

## 📁 Key Scripts

### Query Scripts
- `query_workout_features.py` - Basic feature queries
- `query_all_workout_features.py` - Comprehensive batch queries
- `query_workout_features_optimized.py` - With optimized thresholds
- `test_embedding_distances.py` - Debug query distances

### Generation Scripts
- `generate_comprehensive_workout_article.py` - Full article generation
- `generate_final_workout_article.py` - Simplified generation
- `create_workout_features_json.py` - Create feature database

### Test Scripts
- `test_workout_creation_section.py` - Test specific sections
- `test_llamaindex_quality.py` - Verify content quality
- `analyze_workout_content.py` - Analyze query results

## 📈 Results and Metrics

### Typical Query Results
- Simple feature query: 10-30 results
- Comprehensive feature set: 800-1000 results
- Processing time: 2-5 seconds per query
- Article generation: 30-60 seconds

### Content Distribution
From a typical comprehensive query:
- Blog articles: 15-20%
- YouTube transcripts: 10-15%
- Facts: 20-25%
- Forum content: 40-50%

## 🔮 Best Practices

1. **Always Query First, Generate Second**
   - Never generate without querying actual content
   - Save query results for debugging
   - Validate content exists before claiming features

2. **Use Real Examples**
   - Extract actual quotes from blog articles
   - Include real user questions from forums
   - Reference specific video demonstrations

3. **Maintain Context**
   - Keep original source attribution
   - Preserve technical accuracy
   - Include practical use cases

4. **Iterate on Quality**
   - Start with test sections
   - Validate against source content
   - Refine prompts based on output

## 🚨 Important Notes

- The knowledge base is read-only for queries
- Always attribute content to sources
- Respect false fact warnings in database
- Generated content should be reviewed before publishing
- Query costs are minimal (cached embeddings)
- Generation costs vary by model and length

---

**Last Updated**: July 25, 2025  
**Location**: `td-blog-ai/README_vector.md`  
**Related**: See `vector-loader/README.md` for data loading documentation