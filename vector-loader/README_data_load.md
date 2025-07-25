# TrainerDay LlamaIndex Knowledge Base - Data Loading Guide

## Overview

This guide explains how we loaded all TrainerDay content sources into a unified LlamaIndex knowledge base using PostgreSQL with pgvector extension. The system implements a priority-based retrieval strategy with false fact detection to power high-quality article generation.

## Architecture

### Database Setup
- **Database**: PostgreSQL with pgvector extension
- **Table**: `llamaindex_knowledge_base` (unified table for all content types)
- **Embeddings**: OpenAI text-embedding-3-large (1536 dimensions)
- **Vector Index**: IVFFlat index for fast similarity search

### Content Sources & Priorities

| Source | Priority | Similarity Threshold | Records | Authority |
|--------|----------|---------------------|---------|-----------|
| Facts (validated) | highest | 0.2 | 653 | official |
| Facts (wrong - warnings) | highest | 0.2 | 57 | corrective |
| Blog Articles | critical | 0.3 | 91 | official |
| YouTube Transcripts | critical | 0.3 | 54 | official |
| Forum Q&A (structured) | high | 0.4 | 3,513 | community |
| Forum Discussions (raw) | medium | 0.6 | 1,536 | community |

**Total Knowledge Base**: 5,904 documents

## Data Loading Process

### 1. Forum Data Loading (`forum_data_loader_step1.py`)

**Dual Document Strategy**: Loads both structured Q&A pairs and raw forum discussions to maximize knowledge coverage.

```python
# Q&A Structured (High Priority)
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

# Raw Discussions (Medium Priority)  
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

**Source**: Production database `trainerday_production.forum_analysis` table
- **Q&A Pairs**: Extracted question-answer pairs with high relevance
- **Raw Topics**: Complete threaded discussions for context

### 2. Blog Data Loading (`blog_data_loader.py`)

**Critical Priority Content**: Official TrainerDay blog articles with authoritative information.

```python
doc = Document(
    text=article_text,
    metadata={
        "source": "blog",
        "content_type": "article",
        "priority": "critical", 
        "similarity_threshold": 0.3,
        "authority": "official"
    }
)
```

**Source**: Local markdown files with frontmatter parsing
- **Content**: Full article text with metadata
- **Processing**: Markdown parsing, frontmatter extraction, clean text

### 3. YouTube Data Loading (`youtube_data_loader.py`)

**Video Transcript Processing**: Extracts educational content from TrainerDay YouTube videos.

```python
doc = Document(
    text=transcript_text,
    metadata={
        "source": "youtube", 
        "content_type": "video_transcript",
        "priority": "critical",
        "similarity_threshold": 0.3,
        "authority": "official"
    }
)
```

**Source**: Production database `trainerday_production.youtube_content` table
- **Content**: Full transcript text (timing data excluded)
- **Processing**: JSON parsing, text extraction, metadata preservation

### 4. Facts Data Loading (`facts_data_loader.py`)

**Highest Priority with False Fact Detection**: Validated facts with corrective warnings for misinformation.

```python
# Valid Facts
if status != 'WRONG':
    document_text = f"Fact: {fact_text}"
    content_type = "valid_fact"

# False Facts (Corrective Warnings)
else:
    document_text = f"DO NOT USE IN ARTICLES: This is incorrect information - {fact_text}"
    content_type = "wrong_fact"

doc = Document(
    text=document_text,
    metadata={
        "source": "facts",
        "content_type": content_type,
        "priority": "highest",
        "similarity_threshold": 0.2, 
        "authority": "official" if content_type == "valid_fact" else "corrective"
    }
)
```

**Source**: Google Sheets via API
- **Valid Facts**: Status = blank (true), validated, ADD
- **Wrong Facts**: Status = WRONG (with corrective warnings)
- **Processing**: Status-based content prefixing, metadata tagging

## Loading Scripts Location

### Production Data Loaders (`production/data_loaders/`)
- `forum_data_loader_step1.py` - Dual strategy forum loading
- `blog_data_loader.py` - Blog article processing  
- `youtube_data_loader.py` - Video transcript extraction
- `facts_data_loader.py` - Facts with false fact detection
- `merge_facts_tables.py` - Table consolidation utility

### Facts System (`production/facts_system/`)
- `create_facts_spreadsheet.py` - Google Sheets setup
- `extract_facts_to_database.py` - Database fact extraction
- `populate_existing_spreadsheet.py` - Sheet population
- `update_facts_preserve_status.py` - Status maintenance
- `enhance_all_articles.py` - Article enhancement pipeline
- `enhance_articles_from_facts.py` - Fact-based enhancement

## Data Quality & Validation

### Embedding Quality
- **Model**: text-embedding-3-large (state-of-the-art)
- **Dimensions**: 1536 (high precision)
- **Cost**: ~$0.35 total for entire knowledge base

### Content Processing
- **Text Cleaning**: Removes artifacts, normalizes formatting
- **Metadata Preservation**: Maintains source attribution, priority levels
- **Duplicate Handling**: Prevents content duplication across sources

### False Fact Prevention
- **Warning System**: Wrong facts prefixed with "DO NOT USE IN ARTICLES"
- **Status Tracking**: Google Sheets integration for fact validation
- **Corrective Information**: Prevents misinformation in generated content

## Database Schema

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

## Performance Metrics

### Loading Statistics
- **Forum Data**: 5,049 documents (3,513 Q&A + 1,536 discussions)
- **Blog Data**: 91 articles processed in ~2 minutes
- **YouTube Data**: 54 transcripts processed in ~3 minutes  
- **Facts Data**: 710 facts (653 valid + 57 wrong) processed in ~1 minute

### Database Performance
- **Vector Index**: IVFFlat with 100 lists
- **Query Speed**: <100ms for similarity search
- **Storage**: ~50MB for embeddings + text

## Error Handling

### Data Validation
- **Missing Content**: Skips empty or malformed records
- **Encoding Issues**: UTF-8 normalization
- **API Limits**: Rate limiting and retry logic

### Recovery Procedures
- **Incremental Loading**: Supports partial reloads
- **Progress Tracking**: JSON progress files
- **Rollback Capability**: Table backup before major changes

## Future Enhancements

### Planned Improvements
1. **Feature Map Integration**: Product feature documentation
2. **Incremental Updates**: Real-time content synchronization
3. **Content Versioning**: Track content changes over time
4. **Advanced Filtering**: Topic-based retrieval enhancement

### Scaling Considerations
- **Horizontal Scaling**: Multi-database sharding strategy
- **Content Growth**: Automatic index optimization
- **Performance Monitoring**: Query latency tracking

## Troubleshooting

### Common Issues
1. **Connection Errors**: Verify PostgreSQL and pgvector setup
2. **Embedding Failures**: Check OpenAI API key and rate limits
3. **Memory Issues**: Monitor system resources during loading
4. **Table Conflicts**: Use merge utilities for table consolidation

### Diagnostic Commands
```bash
# Check database connection
psql -h localhost -d trainerday_local -U alex

# Verify vector extension
SELECT * FROM pg_extension WHERE extname = 'vector';

# Check table status
SELECT COUNT(*), metadata_->>'source' FROM llamaindex_knowledge_base GROUP BY metadata_->>'source';
```

## Cost Analysis

### OpenAI API Costs
- **Embeddings**: ~$0.35 for entire knowledge base
- **Monthly Updates**: ~$0.10 for incremental changes
- **Query Costs**: Negligible (embeddings cached)

### Infrastructure Costs
- **Local Development**: Free (PostgreSQL + pgvector)
- **Production Deployment**: ~$20/month for managed PostgreSQL
- **Storage**: ~1GB for full knowledge base

---

*Last Updated: July 25, 2025*
*Total Knowledge Base Size: 5,904 documents across 4 content sources*