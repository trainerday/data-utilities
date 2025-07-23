# Multi-Source Vector Database & Content Processing

A unified vector database system using PostgreSQL + pgvector for semantic search across all TrainerDay content sources. All content is processed, chunked, and stored in a single embeddings table for cross-content discovery and analysis.

## 🎯 Overview

This system processes diverse content sources into a unified vector database, enabling semantic search across all TrainerDay content types. Instead of separate systems for different content types, everything is stored in one PostgreSQL table with pgvector for efficient similarity search.

## 📊 Data Sources

### **Content Sources Overview**
- **Forum Q&A Pairs**: Community discussions and support questions ([see source-data/forum/](source-data/forum/))
- **YouTube Transcripts**: Educational video content and tutorials ([see source-data/youtube/](source-data/youtube/))
- **Blog Articles**: Documentation, guides, and feature explanations ([see source-data/blog/](source-data/blog/))
- **Project Features**: Product development and feature mapping ([see source-data/project_feature_map/](source-data/project_feature_map/))

### **Processing Approach**
- **Semantic Chunking**: Content-type specific strategies for optimal search results
- **Cross-Content Discovery**: Find related information across all sources
- **Unified Storage**: Single embeddings table for efficient similarity search

## 🚀 Quick Start

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Required Configuration**

Create a `.env` file with the following:

```env
# OpenAI API for embeddings
OPENAI_API_KEY=your_openai_api_key_here

# Embedding Model Configuration
# IMPORTANT: Always use text-embedding-3-large for human content (cycling discussions, forums, tutorials)
# For code content, different models may be more appropriate
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
OPENAI_EMBEDDING_DIMENSIONS=1536

# PostgreSQL Database (TrainerDay Data Warehouse)
DB_HOST=postgress-dw-do-user-979029-0.b.db.ondigitalocean.com
DB_PORT=25060
DB_DATABASE=defaultdb
DB_USERNAME=doadmin
DB_PASSWORD=MafHqU5x4JwXcZu3
DB_SSLMODE=require
DB_SSLROOTCERT=.postgres.crt

# Forum API (for additional data if needed)
DISCOURSE_API_KEY=fa1f64a0f6c4d35a1e958d09cd5f0d9673b399907fa8d1909ba365134ea0048c
DISCOURSE_API_USERNAME=Alex

# YouTube Data API (for video content processing)
YOUTUBE_API_KEY=AIzaSyCkKl7Egl9NAFkrAKTKb8RWWmUByTfveN8
```

**Required Files:**
- `.postgres.crt` - SSL certificate for PostgreSQL connection (included in this folder)
- `.env` - Environment configuration (create from example above)

### 3. **Database Setup**
```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create unified content embeddings table
CREATE TABLE IF NOT EXISTS content_embeddings (
    id SERIAL PRIMARY KEY,
    source VARCHAR(20) NOT NULL,        -- 'forum', 'blog', 'youtube'
    source_id VARCHAR(100) NOT NULL,    -- topic_id, article_filename, video_id
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,    -- OpenAI embeddings are 1536 dimensions
    metadata JSONB,                     -- source-specific fields
    chunk_index INTEGER DEFAULT 0,     -- for multi-chunk content
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(source, source_id, chunk_index)
);

-- Create indexes for fast similarity search
CREATE INDEX IF NOT EXISTS idx_content_embeddings_similarity 
ON content_embeddings USING ivfflat (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_content_embeddings_source 
ON content_embeddings(source, source_id);

CREATE INDEX IF NOT EXISTS idx_content_embeddings_source_type 
ON content_embeddings(source);
```

## 🧩 Content Processing & Chunking

### **Unified Processing Pipeline** (`unified_content_processor.py`)
Each content source has its own specialized processing strategy optimized for semantic search:

- **Forum Q&A**: Question/answer pairs as semantic units ([details](source-data/forum/))
- **YouTube Content**: Time-based transcript segments ([details](source-data/youtube/))
- **Blog Articles**: Section-based chunking with context ([details](source-data/blog/))
- **Project Features**: Development and feature documentation ([details](source-data/project_feature_map/))

All content is processed through a unified pipeline that handles:
- Source-specific extraction and chunking
- OpenAI embedding generation using **text-embedding-3-large** (optimized for cycling technical content)
- PostgreSQL storage with metadata
- Incremental updates and change detection

### **Embedding Model Strategy**
- **Human Content**: `text-embedding-3-large` at 1536 dimensions for superior understanding of cycling terminology, technical discussions, and user language patterns
- **Code Content**: Different models may be used for source code analysis (not applicable to this content pipeline)

## 📋 Usage

### **Process All Content Sources**
```bash
# Process all content sources (forum, YouTube, blog)
python unified_content_processor.py

# Process with custom directories
python unified_content_processor.py --blog-dir /custom/path/to/blog
```

### **Search Across Content**
```bash
# Search across all sources
python unified_content_processor.py --search "How do I sync to Garmin?"

# Search specific source
python unified_content_processor.py --search "power zones" --source-filter youtube
```

### **Search Across All Content**
```sql
-- Find similar content across all sources
SELECT 
    source, title, content, metadata,
    1 - (embedding <=> %s) AS similarity_score
FROM content_embeddings
ORDER BY embedding <=> %s
LIMIT 10;
```

## 🎯 Content Strategy Integration

### **Cross-Content Analysis**
- **Gap Identification**: Find forum questions without corresponding blog articles
- **Content Enhancement**: Use forum language to improve existing documentation
- **Topic Prioritization**: Rank content opportunities by user engagement frequency

### **Semantic Search Benefits**
- **Natural Language Queries**: Users can ask questions in their own words
- **Cross-Source Discovery**: Find related content across forums, videos, and articles
- **Context Understanding**: Semantic similarity beyond keyword matching

### **Voice Pattern Matching**
- **User Language**: How users actually describe problems ("my trainer won't connect")
- **Platform Language**: How official docs explain features ("Bluetooth pairing process")
- **Content Bridge**: Generate content using user terminology with technical accuracy

## 🏗️ Architecture

### **Unified Storage Approach**
- **Single Table**: All content types stored in one `content_embeddings` table
- **Source Differentiation**: `source` field distinguishes content types
- **Metadata Flexibility**: JSONB field stores source-specific information
- **Vector Similarity**: pgvector enables fast semantic search across all content

### **Processing Pipeline**
```
Data Sources → Content Chunking → OpenAI Embeddings → PostgreSQL Storage → Semantic Search
```

### **Data Flow**
1. **Extract**: Source-specific extraction (Forum API, YouTube API, File System)
2. **Chunk**: Strategy-specific content segmentation  
3. **Embed**: OpenAI API generates 1536-dimension vectors
4. **Store**: PostgreSQL with pgvector for similarity operations
5. **Search**: Cross-content semantic similarity search

## 📈 Performance & Scalability

### **Database Optimization**
- **Vector Indexing**: IVFFlat index for fast similarity search
- **Source Filtering**: Efficient queries by content type
- **Metadata Indexing**: Quick filtering by categories, topics, etc.

### **Processing Efficiency**
- **Incremental Updates**: Only process changed/new content
- **Batch Processing**: Optimize OpenAI API calls
- **Change Detection**: Smart identification of updated content

## 🔍 Search Capabilities

### **Semantic Search Examples**
```bash
# Natural language queries work across all content types
"How do I connect my power meter to TrainerDay?"
"Setting up Zwift integration" 
"Troubleshooting Garmin sync issues"
"Creating custom workouts"
```

### **Advanced Filtering**
```sql
-- Search within specific content types
WHERE source = 'forum' AND metadata->>'category' = 'technical'

-- Search by engagement level
WHERE source = 'blog' AND metadata->>'engagement' = 'Quick'

-- Search by video topics
WHERE source = 'youtube' AND metadata->'topics' ? 'power-zones'
```

## 🔗 Data Sources

All content sources are now consolidated within this project:

### **Current Data Inventory**
- **Forum Data**: 3,513 Q&A pairs from PostgreSQL `forum_analysis` table
- **YouTube Content**: 54+ videos with transcripts in `source-data/youtube_content/`
- **Blog Articles**: 60+ articles in `source-data/blog_articles/`
- **Feature Map**: 200+ features in `source-data/project_feature_map/`

### **Data Source Locations**
- **Forum Data**: PostgreSQL database - Q&A pairs from forum analysis (via forum-scraper-trainerday project)
- **YouTube Content**: `source-data/youtube_content/` - Video transcripts and metadata
- **Blog Articles**: `source-data/blog_articles/` - Educational and documentation content
- **Feature Map**: `source-data/project_feature_map/` - TrainerDay platform capabilities

### **Verification Commands**
```bash
# Check current forum Q&A count
cd ../forum-scraper-trainerday/script-testing && python check_db_status.py

# Check vector database status
cd scripts && python check_db_status.py

# Check available content files
ls -la source-data/*/
```

See individual source documentation in `source-data/` folders for detailed processing information.

---

## 📚 Legacy Information (Old System)

**Note**: The information below describes the previous ChromaDB-based system that processed source code repositories. This system is no longer actively used but the code and database remain in this folder for reference.

### **Previous ChromaDB System**
The original vector-processor was designed to index source code repositories using ChromaDB. This system included:

- **GitHub Repository Processing**: Multiple repos with 20+ programming languages
- **Code Chunking**: Function-level chunking with line number preservation  
- **ChromaDB Storage**: Vector database for code similarity search
- **MongoDB User Data**: 110,986+ users with incremental sync
- **Mixpanel Analytics**: Event data processing and analysis

### **Legacy Components (Not Used in New System)**
- `chroma_db/` - ChromaDB database files (legacy)
- `forum_vectorizer.py` - Old forum processing system
- `forum_search_cli.py` - ChromaDB-based search interface
- Various data ingestion scripts for MongoDB, Mixpanel, GitHub repositories

The new system focuses exclusively on content (forum Q&A, YouTube, blogs) rather than source code, using PostgreSQL + pgvector instead of ChromaDB for better integration with existing TrainerDay infrastructure.

---

*This unified vector system enables TrainerDay's comprehensive content strategy by providing semantic search across all educational and support content, facilitating content gap analysis and user-driven content enhancement.*