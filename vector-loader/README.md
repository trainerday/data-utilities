# Vector Loader: TrainerDay Data Loading System

## 🎯 Project Overview

Vector Loader is the **data loading component** of the TrainerDay knowledge base system. It handles loading content from multiple sources (blog articles, YouTube transcripts, forum discussions, and validated facts) into a PostgreSQL database with pgvector for vector similarity search.

**Note**: This project handles data loading only. For querying the knowledge base and generating articles, see the `td-blog-ai` folder and its `README_vector.md` documentation.

## 📊 System Architecture

### Core Components
1. **LlamaIndex RAG System**: For intelligent content retrieval and generation
2. **PostgreSQL with pgvector**: Vector storage and similarity search
3. **Priority-based Retrieval**: Different thresholds for different content types
4. **False Fact Detection**: Prevents misinformation in generated content
5. **Multi-source Integration**: Blog, YouTube, Forum, and Facts database

### Content Sources & Priorities

| Source | Priority | Similarity Threshold | Records | Authority | Purpose |
|--------|----------|---------------------|---------|-----------|---------|
| Facts (validated) | highest | 0.2 | 653 | official | Authoritative facts |
| Facts (wrong - warnings) | highest | 0.2 | 57 | corrective | Prevent misinformation |
| Blog Articles | critical | 0.3 | 91 | official | Published content |
| YouTube Transcripts | critical | 0.3 | 54 | official | Video content |
| Forum Q&A (structured) | high | 0.4 | 3,513 | community | User solutions |
| Forum Discussions (raw) | medium | 0.6 | 1,536 | community | Context & language |

**Total Knowledge Base**: 5,904 documents

## 🚀 Data Loading Architecture

### Two Loading Approaches

#### 1. **Individual Data Loaders (Production-Ready)** ✅
Located in `production/data_loaders/`, these loaders write to the unified `llamaindex_knowledge_base` table:
- `facts_data_loader.py` - Google Sheets facts with validation status
- `blog_data_loader.py` - Blog articles from markdown files
- `youtube_data_loader.py` - YouTube transcripts from database
- `forum_data_loader_step1.py` - Forum content with dual strategy

**To load all data sources properly:**
```bash
# Run each loader individually for complete data loading
python production/data_loaders/facts_data_loader.py
python production/data_loaders/blog_data_loader.py
python production/data_loaders/youtube_data_loader.py
python production/data_loaders/forum_data_loader_step1.py
```

#### 2. **Full Data Loader (Partial Coverage)** ⚠️
`llamaindex_full_data_loader.py` - A convenience loader that loads:
- ✅ Blog articles
- ✅ YouTube transcripts
- ✅ Forum Q&A pairs
- ❌ **Missing: Facts from Google Sheets**

This loader uses a different table (`llamaindex_full_content`) and is missing the critical facts data source.

### Why LlamaIndex Over LangChain?

After systematic analysis, **LlamaIndex was chosen over LangChain** because:
- **Purpose-built for RAG**: Exactly what we need (knowledge base → blog content)
- **Better out-of-box performance** for document retrieval and fact extraction
- **Simpler configuration** for pure RAG applications
- **Working system already proven** with initial blog article integration

## 🚀 Key Features

### 1. Priority-Based Retrieval
- Different similarity thresholds for different content types
- Authoritative content (facts, blog) retrieved more easily
- Community content requires higher similarity match

### 2. False Fact Prevention
- Wrong facts stored with "DO NOT USE IN ARTICLES" prefix
- Prevents AI from using incorrect information
- Maintains fact validation status from Google Sheets

### 3. Dual Document Strategy (Forum)
- **Structured Q&A**: Clean, processed answers
- **Raw Discussions**: Authentic user language and context
- Cross-referenced by topic ID for comprehensive coverage

### 4. Unified Knowledge Base
- Single table for all content types
- Consistent metadata structure
- Fast vector similarity search with IVFFlat index

## 📁 Project Structure

```
vector-loader/
├── README.md                        # This file
│
├── production/                      # Production-ready scripts
│   ├── data_loaders/               # Data loading scripts
│   │   ├── blog_data_loader.py     # Blog article loader
│   │   ├── facts_data_loader.py    # Facts with validation
│   │   ├── forum_data_loader_step1.py # Forum dual strategy
│   │   ├── youtube_data_loader.py  # YouTube transcript loader
│   │   └── merge_facts_tables.py   # Table consolidation
│   │
│   ├── facts_system/               # Fact management
│   │   ├── create_facts_spreadsheet.py
│   │   ├── extract_facts_to_database.py
│   │   ├── enhance_all_articles.py
│   │   └── update_facts_preserve_status.py
│   │
│   └── utilities/                  # Helper scripts
│       ├── check_facts_status.py
│       ├── test_unified_knowledge_base.py
│       └── monitor_progress.py
│
├── archive/                        # Historical development
│   ├── llamaindex_development/     # LlamaIndex experiments
│   ├── logs_and_data/             # Processing logs
│   └── pre_llamaindex_system/     # Earlier implementations
│
├── Old/                           # Legacy vector-processor
│   ├── scripts/                   # Original scripts
│   ├── source-data/              # Source content files
│   └── unified_content_processor.py
│
├── llamaindex_full_data_loader.py # Partial data loader (missing facts)
└── script-testing/                # Test and development scripts
```

## 🔧 Setup & Installation

### Prerequisites
- PostgreSQL with pgvector extension
- Python 3.8+
- OpenAI API key
- Google Sheets API credentials (for facts)

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Setup PostgreSQL with pgvector
CREATE DATABASE trainerday_local;
CREATE EXTENSION vector;

# Configure environment variables
cp .env.example .env
# Edit .env with your credentials
```

### Environment Variables
```env
# Database - Local PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_DATABASE=trainerday_local
DB_USERNAME=your_user
DB_PASSWORD=your_password

# Database - Production (Read-only)
PROD_DB_HOST=your_production_host
PROD_DB_PORT=25060
PROD_DB_DATABASE=defaultdb
PROD_DB_USERNAME=readonly_user
PROD_DB_PASSWORD=readonly_password

# APIs
OPENAI_API_KEY=your_openai_key
GOOGLE_SHEETS_ID=your_sheets_id
```

## 📊 Data Loading Process

### Complete Data Loading (Recommended)

Run all individual loaders for complete knowledge base:

```bash
# 1. Load facts from Google Sheets (highest priority)
python production/data_loaders/facts_data_loader.py

# 2. Load blog articles (critical priority)
python production/data_loaders/blog_data_loader.py

# 3. Load YouTube transcripts (critical priority)
python production/data_loaders/youtube_data_loader.py

# 4. Load forum content with dual strategy
python production/data_loaders/forum_data_loader_step1.py
```

### Monitor Progress
```bash
# Check loading progress
python production/utilities/monitor_progress.py

# Verify data in database
python production/utilities/test_unified_knowledge_base.py
```

### Data Loading Details

#### Forum Data Loading (Dual Strategy)
The forum loader implements a sophisticated dual document strategy:

**Q&A Structured (High Priority)**
```python
doc = Document(
    text=qa_content,
    metadata={
        "source": "forum",
        "content_type": "forum_qa_structured", 
        "priority": "high",
        "similarity_threshold": 0.4,
        "authority": "community"
    }
)
```

**Raw Discussions (Medium Priority)**
```python
doc = Document(
    text=full_discussion,
    metadata={
        "source": "forum",
        "content_type": "forum_discussion",
        "priority": "medium", 
        "similarity_threshold": 0.6,
        "authority": "community"
    }
)
```

#### Facts Data Loading (False Fact Prevention)
The facts loader includes critical misinformation prevention:

```python
# Valid Facts
if status != 'WRONG':
    document_text = f"Fact: {fact_text}"
    content_type = "valid_fact"

# False Facts (Corrective Warnings)
else:
    document_text = f"DO NOT USE IN ARTICLES: This is incorrect information - {fact_text}"
    content_type = "wrong_fact"
```

## 📈 Performance & Costs

### Embedding Costs
- Initial load: ~$0.35 for entire knowledge base
- Monthly updates: ~$0.10 for incremental changes
- Query costs: Negligible (embeddings cached)

### Query Performance
- Vector search: <100ms
- Full RAG response: 2-5 seconds
- Concurrent queries: Supported

### Storage Requirements
- Embeddings: ~50MB
- Text content: ~25MB  
- Total database: ~100MB

## 🛠️ Development Workflow

### 1. Fact Management

#### Fact Review Process (Used by td-blog-ai)
When the td-blog-ai project generates articles, it extracts facts that need review. The fact update process:

```bash
# 1. Update fact statuses from Google Sheets (after human review)
python production/facts_system/update_facts_preserve_status.py

# 2. Reload facts to LlamaIndex with appropriate prefixes
python production/data_loaders/facts_data_loader.py
```

**Fact Status Handling:**
- **NEW** → Added as normal facts
- **WRONG** → Added with "DO NOT USE IN ARTICLES:" prefix
- **USELESS** → Added with "USELESS FACT - DO NOT INCLUDE:" prefix
- **CORRECT** → Status after processing

#### Other Fact Operations
```bash
# Extract facts from existing articles (one-time operation)
python production/facts_system/extract_facts_to_database.py

# Enhance articles with validated facts (legacy workflow)
python production/facts_system/enhance_all_articles.py
```

### 2. Content Updates
```bash
# Add new blog articles
# Place markdown files in source-data/blog_articles/
python production/data_loaders/blog_data_loader.py

# Update forum content
python production/data_loaders/forum_data_loader_step1.py
```

### 3. Testing & Validation
```bash
# Test unified knowledge base
python production/utilities/test_unified_knowledge_base.py

# Check fact statuses
python production/utilities/check_facts_status.py
```

## 🚨 Important Considerations

### False Fact Prevention
- Facts marked as "WRONG" in Google Sheets are prefixed with warnings
- This prevents the AI from using incorrect information
- Always validate generated content against fact database

### Priority System
- Higher priority content (facts, blog) has lower similarity thresholds
- This ensures authoritative content is preferred
- Community content requires stronger matches

### Data Quality
- All content is cleaned and normalized
- Metadata preserved for attribution
- Duplicate content prevented across sources

## 📚 Database Schema

```sql
CREATE TABLE llamaindex_knowledge_base (
    node_id VARCHAR PRIMARY KEY,
    text TEXT NOT NULL,
    metadata_ JSONB,
    embedding VECTOR(1536)
);

CREATE INDEX llamaindex_knowledge_base_embedding_idx 
ON llamaindex_knowledge_base 
USING ivfflat (embedding vector_cosine_ops);
```

### Metadata Structure
```json
{
    "source": "forum|blog|youtube|facts",
    "content_type": "forum_qa_structured|forum_discussion|article|video_transcript|valid_fact|wrong_fact",
    "priority": "highest|critical|high|medium",
    "similarity_threshold": 0.2|0.3|0.4|0.6,
    "authority": "official|community|corrective",
    "title": "Content title",
    "category": "Content category (forum only)",
    "fact_status": "validated|ADD|WRONG (facts only)"
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection**
   ```bash
   psql -h localhost -d trainerday_local -U your_user
   SELECT * FROM pg_extension WHERE extname = 'vector';
   ```

2. **Embedding Failures**
   - Check OpenAI API key
   - Monitor rate limits
   - Verify network connectivity

3. **Memory Issues**
   - Use batch processing for large datasets
   - Monitor system resources
   - Consider incremental loading

4. **Query Quality**
   - Adjust similarity thresholds
   - Review metadata filters
   - Check content coverage

## 📊 Monitoring

### Check Database Status
```sql
-- Content distribution
SELECT 
    metadata_->>'source' as source,
    metadata_->>'priority' as priority,
    COUNT(*) as count
FROM llamaindex_knowledge_base
GROUP BY source, priority
ORDER BY source, priority;

-- Recent additions
SELECT 
    node_id,
    metadata_->>'source' as source,
    metadata_->>'title' as title,
    LENGTH(text) as text_length
FROM llamaindex_knowledge_base
ORDER BY node_id DESC
LIMIT 10;
```

### Performance Metrics
- Monitor query response times
- Track embedding generation speed
- Check vector index performance
- Review error logs regularly

## 🔮 Future Enhancements

### Planned Features
1. Real-time content synchronization
2. Feature map integration
3. Advanced query analytics
4. Multi-language support
5. Content versioning

### Scaling Considerations
- Horizontal database sharding
- Distributed vector search
- Caching layer for frequent queries
- Incremental index updates

---

**Last Updated**: July 25, 2025  
**Maintainer**: TrainerDay Development Team  
**Status**: Production Ready