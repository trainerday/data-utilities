# TrainerDay Forum Analysis System v2

## Overview

A complete forum analysis pipeline that scrapes TrainerDay forum data, stores it in a PostgreSQL database, and analyzes it using OpenAI's GPT-4 to extract insights for content strategy and messaging improvements.

## System Architecture

### Two-Step Process
1. **STEP 1**: `discourse_to_database.py` - Scrapes forum content from Discourse API → PostgreSQL raw storage
2. **STEP 2**: `scripts/analyze_forum_topics.py` - Analyzes raw content with OpenAI LLM → Structured insights

### Database-First Design
- **Raw Content Storage**: Complete forum topics and posts stored as JSONB in PostgreSQL
- **Structured Analysis**: LLM insights stored in normalized tables for querying
- **Smart Incremental Updates**: MD5 checksums detect content changes, only process what's new
- **Future-Proof**: Can re-analyze historical content with different strategies

## 🚀 Quick Start

### Production Usage
```bash
# Daily incremental processing (recommended)
python run_forum_analysis.py

# Initial setup - scrape entire forum
python run_forum_analysis.py --mode full

# View results
python scripts/query_results.py
```

### Development/Testing
```bash
# Test with limited data
python run_forum_analysis.py --mode full --max-pages 5 --max-topics 10

# Run steps independently
python discourse_to_database.py --mode incremental
python scripts/analyze_forum_topics.py
```

## How It Works

### STEP 1: Forum Scraping (`discourse_to_database.py`)

**What it does:**
- Connects to TrainerDay Discourse forum API
- Retrieves topic lists with pagination
- For each topic, fetches complete content including all posts
- Generates MD5 checksums to detect content changes
- Stores raw forum data in `forum_topics_raw` table

**Smart Incremental Logic:**
- **Full Mode**: Processes entire forum (for initial setup)
- **Incremental Mode**: Only processes new or changed topics (for daily updates)
- **Change Detection**: Uses MD5 checksums of topic content to skip unchanged topics
- **Rate Limiting**: Respects API limits with configurable delays

**Database Storage:**
```sql
forum_topics_raw (
    topic_id INTEGER PRIMARY KEY,
    raw_content JSONB,           -- Complete topic + posts data
    checksum VARCHAR(32),        -- MD5 hash for change detection  
    title TEXT,                  -- Extracted for easy querying
    posts_count INTEGER,         -- Topic metadata
    scraped_at TIMESTAMP,        -- When scraped
    last_updated TIMESTAMP       -- When last changed
)
```

### STEP 2: Content Analysis (`scripts/analyze_forum_topics.py`)

**What it does:**
- Reads raw forum content from database
- Cleans and prepares content for LLM analysis
- Sends to OpenAI GPT-4 with structured analysis prompt
- Extracts insights using specialized prompt engineering
- Stores structured results in analysis tables

**Analysis Categories:**
- **Topic Classification**: Getting Started, Technical Issues, Feature Requests, etc.
- **Q&A Extraction**: User questions and platform responses
- **Voice Patterns**: How users vs. platform communicate
- **Content Opportunities**: Blog/video topics based on common questions
- **Messaging Gaps**: Where user language differs from platform language

### STEP 2B: Parallel Processing (`scripts/fixed_parallel.py`)

**For High-Volume Processing:**
- **Concurrent Workers**: Multiple threads process topics simultaneously
- **Database Locking**: PostgreSQL advisory locks prevent race conditions
- **Smart Queuing**: Workers automatically fetch next unprocessed topic
- **Progress Monitoring**: Real-time status updates and completion tracking
- **Error Recovery**: Failed topics are retried and logged for debugging

**Usage:**
```bash
# Run parallel analysis with 4 workers (recommended)
python scripts/fixed_parallel.py

# Adjust worker count for your system
WORKERS=8 python scripts/fixed_parallel.py
```

**Performance Benefits:**
- **4-8x Speed Improvement**: Process multiple topics concurrently
- **Efficient Resource Usage**: Optimal API call batching
- **Safe Concurrent Access**: No duplicate processing or data corruption

**Output Tables:**
```sql
forum_topics          -- Topic metadata and categories
forum_qa_pairs        -- Extracted question/answer pairs  
forum_voice_patterns  -- User vs platform communication patterns
forum_insights        -- Content opportunities and messaging insights
```

### STEP 3: Vector Embeddings (`scripts/create_embeddings.py`)

**Unified Content Vectorization:**
- **Multi-Source Support**: Forum Q&A, Blog Articles, YouTube Transcripts
- **PostgreSQL + pgvector**: Vector similarity search with cosine similarity
- **OpenAI Embeddings**: text-embedding-ada-002 (1536 dimensions)
- **Cross-Content Search**: Find similar content across all sources

**Database Schema:**
```sql
-- Unified content embeddings table
content_embeddings (
    id SERIAL PRIMARY KEY,
    source VARCHAR(20) NOT NULL,        -- 'forum', 'blog', 'youtube'  
    source_id VARCHAR(100) NOT NULL,    -- topic_id, article_filename, video_id
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    metadata JSONB,                     -- source-specific fields
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(source, source_id)
);
```

**Metadata Examples:**
- **Forum**: `{"category": "technical", "question": "...", "answer": "..."}`
- **Blog**: `{"category": "Training", "engagement": "Complete", "tags": [...]}`  
- **YouTube**: `{"topics": [...], "duration": 716, "segment_count": 277}`

**Usage:**
```bash
# Create embeddings for forum Q&A pairs
python scripts/create_embeddings.py

# Test similarity search across all content
python scripts/create_embeddings.py --test-search "How do I sync to Garmin?"
```

### Main Process Orchestrator (`run_forum_analysis.py`)

**What it does:**
- Runs STEP 1 → STEP 2 in sequence
- Handles errors and provides clear status reporting
- Supports testing with limited data sets
- Allows running steps independently

**Process Flow:**
```
🌐 STEP 1: SCRAPE FORUM CONTENT
├── Connect to Discourse API
├── Get topic lists (paginated)
├── Check each topic for changes (checksum)
├── Fetch full content for changed topics
└── Store raw content in database

🤖 STEP 2: ANALYZE FORUM CONTENT  
├── Read unanalyzed raw topics from database
├── Clean and prepare content for LLM
├── Send to OpenAI with analysis prompt
├── Parse structured JSON response
└── Store insights in analysis tables

📊 RESULTS AVAILABLE
└── Query insights with scripts/query_results.py
```

## Database Schema

### Raw Content Storage
- `forum_topics_raw` - Complete raw forum content from Discourse API

### Analysis Results  
- `forum_topics` - Topic metadata and analysis categories
- `forum_qa_pairs` - Extracted question/answer pairs
- `forum_voice_patterns` - User vs platform voice analysis
- `forum_insights` - Content opportunities and messaging insights

### Key Features
- **JSONB Storage**: Flexible schema for raw content
- **Foreign Key Relationships**: Analysis tables reference raw topics
- **Indexes**: Optimized for common queries
- **Incremental Processing**: Only analyze topics not yet processed

## Configuration

### Environment Variables Required
```env
# PostgreSQL Database
DB_HOST=your-postgres-host
DB_PORT=5432
DB_DATABASE=your-database
DB_USERNAME=your-username
DB_PASSWORD=your-password
DB_SSLMODE=require
DB_SSLROOTCERT=.postgres.crt

# Discourse Forum API
DISCOURSE_API_KEY=your-api-key
DISCOURSE_API_USERNAME=your-username

# OpenAI Analysis
OPENAI_API_KEY=your-openai-key
```

### API Requirements
- **Discourse API**: Read access to forum content
- **OpenAI API**: GPT-4 access for content analysis
- **PostgreSQL**: Database for raw content and analysis storage

## 📁 Project Structure

```
forum-scraper-trainerday/
├── run_forum_analysis.py          # 🎯 MAIN PRODUCTION PROCESS
├── discourse_to_database.py       # STEP 1: Scrape forum → database
├── session.md                     # Current session status & progress
├── scripts/                       # Production utilities
│   ├── analyze_forum_topics.py    # STEP 2: Raw content → LLM analysis
│   ├── fixed_parallel.py          # STEP 2B: High-speed parallel processing
│   ├── query_results.py           # Query and view analysis results
│   └── incremental_analysis.py    # Process only new/changed topics
├── utilities/                     # Maintenance tools
│   ├── clear_database.py          # Clear analysis tables
│   └── debug_failed_topic.py      # Debug analysis failures
├── script-testing/                # Development & monitoring tools
│   ├── check_db_status.py         # Monitor processing progress
│   ├── INCREMENTAL_WORKFLOW.md    # Development notes
│   ├── to_be_deleted/             # Obsolete parallel processing scripts
│   └── test_failure_reporting.py  # Test error handling
└── archived_scripts/              # Old file-based system (can be deleted)
    ├── get_forum_data.py          # Legacy: File-based scraper
    ├── consolidate_forum_data.py  # Legacy: File processor
    └── forum_data/                # Legacy: 2000+ JSON files
```

## Production Commands

### Daily Operations
```bash
# Default: incremental scraping + analysis
python run_forum_analysis.py

# Check current status
python scripts/query_results.py
```

### Initial Setup
```bash
# First time: scrape entire forum then analyze
python run_forum_analysis.py --mode full
```

### Individual Components
```bash
# STEP 1: Scrape forum data only
python discourse_to_database.py --mode incremental

# STEP 2: Analyze existing raw data only  
python scripts/analyze_forum_topics.py

# STEP 2B: High-speed parallel analysis (recommended for large datasets)
python scripts/fixed_parallel.py

# View analysis results
python scripts/query_results.py

# Check processing status and progress
python script-testing/check_db_status.py
```

### Monitoring & Status
```bash
# Check current processing status
python script-testing/check_db_status.py
# Shows: total topics, analyzed count, remaining, recent activity

# Monitor parallel processing in real-time
# (run in separate terminal while parallel processing runs)
watch python script-testing/check_db_status.py
```

### Maintenance
```bash
# Clear all analysis data (keeps raw forum data)
python utilities/clear_database.py

# Debug a specific failed topic
python utilities/debug_failed_topic.py --topic-id 1234
```

### Testing & Development
```bash
# Test with limited data
python run_forum_analysis.py --mode full --max-pages 5

# Test analysis only  
python run_forum_analysis.py --skip-scraping --max-topics 10
```

## Benefits of v2 System

### Performance & Efficiency
- **Smart Incremental Updates**: Only processes changed content
- **Database-First**: No file I/O bottlenecks
- **Change Detection**: MD5 checksums skip unchanged topics
- **Rate Limiting**: Respects API limits

### Reliability & Maintenance  
- **Enhanced Error Reporting**: Clear failure tracking with visual indicators
- **Structured Storage**: Normalized database schema
- **Independent Steps**: Can run scraping and analysis separately
- **Future-Proof**: Can re-analyze historical content with new strategies

### Production Ready
- **Complete Pipeline**: End-to-end automation
- **Monitoring**: Detailed statistics and progress reporting
- **Scalable**: Handles large forum datasets efficiently
- **Maintainable**: Clean separation of concerns

## Analysis Output

### Content Strategy Insights
- **Topic Categories**: Automatically classify forum discussions
- **Q&A Extraction**: User questions and platform responses
- **Content Opportunities**: Blog/video topics based on user needs
- **Messaging Gaps**: Where user language differs from platform communication

### Voice Pattern Analysis
- **User Voice**: How users describe problems and solutions
- **Platform Voice**: How support team explains features
- **Language Alignment**: Opportunities to match user terminology

### Actionable Intelligence
- **Recurring Issues**: Problems that come up frequently
- **Feature Demand**: What users are asking for
- **Success Indicators**: Signs of user satisfaction
- **Priority Scoring**: Recency, frequency, and impact analysis

## Migration Notes

### From File-Based v1 System
- ✅ **Migrated**: 2000+ JSON files → PostgreSQL database
- ✅ **Enhanced**: Added incremental processing with change detection
- ✅ **Improved**: Error reporting with detailed failure tracking
- ✅ **Cleaned**: Organized scripts into logical directories

### Legacy System (Archived)
- `archived_scripts/get_forum_data.py` - Old file-based scraper
- `archived_scripts/consolidate_forum_data.py` - Old file processor  
- `archived_scripts/forum_data/` - 2000+ JSON files (can be deleted)

The v2 system is production-ready and eliminates all file-based bottlenecks while providing comprehensive error reporting and smart incremental processing.