# Vector-Llama: TrainerDay LlamaIndex Knowledge Base System

## 🎯 Project Overview

Vector-Llama is a comprehensive knowledge base system built with LlamaIndex for TrainerDay content generation. It implements a priority-based retrieval strategy with false fact detection across multiple content sources to power high-quality blog article generation.

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
vector-llama/
├── README.md                        # This file
├── README_llamaindex_step1.md       # Initial implementation plan
├── README_facts.md                  # Fact extraction system docs
├── README_data_load.md              # Data loading guide
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
├── llamaindex_query_system.py     # Main query interface
├── llamaindex_full_data_loader.py # Complete data loader
└── test_alt_key_query.py         # Query testing script
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

### 1. Load All Data Sources
```bash
# Run the full data loader
python llamaindex_full_data_loader.py
```

This will:
- Connect to production database (read-only)
- Extract forum Q&A pairs and discussions
- Process blog articles from markdown files
- Load YouTube transcripts
- Fetch facts from Google Sheets
- Create embeddings and store in PostgreSQL
- Build LlamaIndex with priority metadata

### 2. Individual Data Loaders
```bash
# Load specific data sources
python production/data_loaders/forum_data_loader_step1.py
python production/data_loaders/blog_data_loader.py
python production/data_loaders/youtube_data_loader.py
python production/data_loaders/facts_data_loader.py
```

### 3. Monitor Progress
```bash
# Check loading progress
python production/utilities/monitor_progress.py
```

## 🔍 Using the Query System

### Basic Query Example
```python
from llamaindex_query_system import TrainerDayKnowledgeBase

# Initialize knowledge base
kb = TrainerDayKnowledgeBase()

# Extract facts
facts = kb.extract_facts("How do I sync workouts to Garmin?")

# Generate blog content
content = kb.generate_blog_content("Zone 2 training benefits")

# Search with custom parameters
results = kb.search("Coach Jack features", top_k=10)
```

### Query Testing
```bash
# Test queries with alternative keys
python test_alt_key_query.py

# Interactive query testing
python llamaindex_query_system.py
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
```bash
# Extract facts from new articles
python production/facts_system/extract_facts_to_database.py

# Update fact statuses from Google Sheets
python production/facts_system/update_facts_preserve_status.py

# Enhance articles with validated facts
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

## 📚 Key Scripts Documentation

### `llamaindex_query_system.py`
Main query interface for the knowledge base
- Fact extraction engine
- Blog content generation engine  
- Customizable retrieval parameters

### `llamaindex_full_data_loader.py`
Complete data loading pipeline
- Loads all content sources
- Progress tracking and resumption
- Error handling and logging

### `production/data_loaders/facts_data_loader.py`
Facts loading with validation
- Google Sheets integration
- Status-based content prefixing
- False fact warning system

### `production/data_loaders/forum_data_loader_step1.py`
Dual strategy forum loading
- Structured Q&A extraction
- Raw discussion preservation
- Cross-reference by topic ID

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

---

**Last Updated**: July 25, 2025  
**Maintainer**: TrainerDay Development Team  
**Status**: Production Ready