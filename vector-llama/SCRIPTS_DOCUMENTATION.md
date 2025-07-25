# Vector-Llama Scripts Documentation

## Overview
This document provides detailed documentation for all scripts in the vector-llama project, organized by their function and location.

## Table of Contents
1. [Main Scripts](#main-scripts)
2. [Production Data Loaders](#production-data-loaders)
3. [Facts System Scripts](#facts-system-scripts)
4. [Utility Scripts](#utility-scripts)
5. [Archive Scripts](#archive-scripts)

---

## Main Scripts

### `llamaindex_query_system.py`
**Purpose**: Main query interface for the TrainerDay knowledge base

**Key Classes**:
- `TrainerDayKnowledgeBase`: Main class for querying the knowledge base

**Key Methods**:
- `load_index()`: Loads the pre-built LlamaIndex from storage
- `setup_query_engines()`: Configures fact extraction and blog content engines
- `extract_facts(query)`: Extracts specific facts related to a query
- `generate_blog_content(topic)`: Generates blog content for a given topic
- `search(query, top_k)`: General search with customizable parameters

**Usage**:
```python
from llamaindex_query_system import TrainerDayKnowledgeBase

kb = TrainerDayKnowledgeBase()
facts = kb.extract_facts("How to use Coach Jack?")
content = kb.generate_blog_content("Zone 2 training benefits")
```

**Configuration**:
- Uses GPT-4-turbo for generation
- text-embedding-3-large for embeddings
- Similarity thresholds: 0.5-0.6 depending on query type

---

### `llamaindex_full_data_loader.py`
**Purpose**: Complete data loading pipeline for all content sources

**Key Features**:
- Progress tracking with JSON file
- Resumable loading (can continue after interruption)
- Cost estimation for embeddings
- Error logging and recovery

**Process Flow**:
1. Setup PostgreSQL vector store
2. Load blog articles from markdown files
3. Load YouTube transcripts from database
4. Load forum Q&A pairs and discussions
5. Load facts from Google Sheets
6. Create embeddings and build index

**Usage**:
```bash
python llamaindex_full_data_loader.py
```

**Progress Tracking**:
- Creates `llamaindex_load_progress.json`
- Tracks loaded/total/errors for each content type
- Estimates embedding costs

---

### `test_alt_key_query.py`
**Purpose**: Test query system with alternative configurations

**Features**:
- Tests different retrieval parameters
- Validates query results
- Benchmarks performance
- Tests edge cases

**Usage**:
```bash
python test_alt_key_query.py
```

---

## Production Data Loaders

### `production/data_loaders/blog_data_loader.py`
**Purpose**: Loads blog articles from markdown files into LlamaIndex

**Process**:
1. Scans blog articles directory
2. Parses frontmatter metadata
3. Extracts article content
4. Creates Document objects with metadata
5. Adds to LlamaIndex with "critical" priority

**Metadata Added**:
- `source`: "blog"
- `content_type`: "article"
- `priority`: "critical"
- `similarity_threshold`: 0.3
- `authority`: "official"
- `title`, `date`, `tags` from frontmatter

**Usage**:
```bash
python production/data_loaders/blog_data_loader.py
```

---

### `production/data_loaders/facts_data_loader.py`
**Purpose**: Loads facts from Google Sheets with validation status

**Key Features**:
- Google Sheets API integration
- Status-based content processing
- False fact warning system
- Duplicate detection

**Fact Processing**:
- **Valid Facts** (status: blank, validated, ADD): Normal loading
- **Wrong Facts** (status: WRONG): Prefixed with "DO NOT USE IN ARTICLES"

**Metadata Added**:
- `source`: "facts"
- `content_type`: "valid_fact" or "wrong_fact"
- `priority`: "highest"
- `similarity_threshold`: 0.2
- `authority`: "official" or "corrective"

**Usage**:
```bash
python production/data_loaders/facts_data_loader.py
```

---

### `production/data_loaders/forum_data_loader_step1.py`
**Purpose**: Implements dual document strategy for forum content

**Dual Strategy**:
1. **Structured Q&A Pairs**: Clean, processed answers (high priority)
2. **Raw Discussions**: Complete conversation threads (medium priority)

**Database Tables Used**:
- `forum_qa_pairs`: 3,513 AI-processed Q&A pairs
- `forum_topics_raw`: 1,536 complete discussion threads

**Metadata Added**:
- Q&A: `priority`: "high", `similarity_threshold`: 0.4
- Raw: `priority`: "medium", `similarity_threshold`: 0.6
- Both: `topic_id` for cross-reference

**Usage**:
```bash
python production/data_loaders/forum_data_loader_step1.py
```

---

### `production/data_loaders/youtube_data_loader.py`
**Purpose**: Loads YouTube video transcripts from database

**Process**:
1. Connects to production database
2. Queries `youtube_content` table
3. Extracts transcript text (excludes timing)
4. Creates Documents with video metadata

**Metadata Added**:
- `source`: "youtube"
- `content_type`: "video_transcript"
- `priority`: "critical"
- `similarity_threshold`: 0.3
- `authority`: "official"
- `video_id`, `title`, `channel`, `duration`

**Usage**:
```bash
python production/data_loaders/youtube_data_loader.py
```

---

### `production/data_loaders/merge_facts_tables.py`
**Purpose**: Utility to merge multiple fact tables in database

**Features**:
- Handles table consolidation
- Preserves unique facts
- Updates embeddings
- Maintains fact IDs

**Usage**:
```bash
python production/data_loaders/merge_facts_tables.py --source table1 --target table2
```

---

## Facts System Scripts

### `production/facts_system/create_facts_spreadsheet.py`
**Purpose**: Creates and configures Google Sheets for fact management

**Sheet Structure Created**:
- `fact_id`: Database ID
- `original_fact`: Extracted fact text
- `status`: Review status (pending/good/bad/replace)
- `replacement_text`: For "replace" status
- `notes`: Review comments

**Usage**:
```bash
python production/facts_system/create_facts_spreadsheet.py
```

---

### `production/facts_system/extract_facts_to_database.py`
**Purpose**: Extracts facts from articles and stores in database

**Process**:
1. Uses Claude Sonnet 4 for fact extraction
2. Generates embeddings for each fact
3. Checks for duplicates via vector similarity
4. Stores new facts in database
5. Syncs with Google Sheets

**Extraction Prompt**:
- Extracts specific, verifiable facts
- Focuses on features, instructions, technical details
- Avoids opinions and general statements

**Usage**:
```bash
python production/facts_system/extract_facts_to_database.py --article path/to/article.md
```

---

### `production/facts_system/enhance_all_articles.py`
**Purpose**: Enhances all articles with validated facts

**Process**:
1. Loads validated facts from database
2. For each article, finds relevant facts
3. Enhances article content with facts
4. Preserves article structure and style
5. Outputs enhanced versions

**Usage**:
```bash
python production/facts_system/enhance_all_articles.py
```

---

### `production/facts_system/enhance_articles_from_facts.py`
**Purpose**: Enhances specific articles using fact database

**Features**:
- Targeted article enhancement
- Fact relevance scoring
- Content integration
- Quality validation

**Usage**:
```bash
python production/facts_system/enhance_articles_from_facts.py --article path/to/article.md
```

---

### `production/facts_system/populate_existing_spreadsheet.py`
**Purpose**: Populates Google Sheets with existing database facts

**Features**:
- Batch upload to avoid rate limits
- Preserves existing statuses
- Adds new facts as "pending"
- Maintains fact ID mapping

**Usage**:
```bash
python production/facts_system/populate_existing_spreadsheet.py
```

---

### `production/facts_system/update_facts_preserve_status.py`
**Purpose**: Updates fact database while preserving Google Sheets statuses

**Process**:
1. Reads current statuses from Google Sheets
2. Updates fact text if changed
3. Preserves status and replacement text
4. Maintains bidirectional sync

**Usage**:
```bash
python production/facts_system/update_facts_preserve_status.py
```

---

## Utility Scripts

### `production/utilities/check_facts_status.py`
**Purpose**: Reports on fact validation status

**Output**:
- Total facts in database
- Status distribution (good/bad/replace/pending)
- Facts needing review
- Validation progress percentage

**Usage**:
```bash
python production/utilities/check_facts_status.py
```

---

### `production/utilities/check_processing_status.py`
**Purpose**: Checks overall data processing status

**Reports On**:
- Content source loading status
- Embedding generation progress
- Index building status
- Error summaries

**Usage**:
```bash
python production/utilities/check_processing_status.py
```

---

### `production/utilities/direct_query_zone2.py`
**Purpose**: Direct query testing for Zone 2 training content

**Features**:
- Tests specific Zone 2 queries
- Validates retrieval accuracy
- Checks content relevance
- Benchmarks performance

**Usage**:
```bash
python production/utilities/direct_query_zone2.py
```

---

### `production/utilities/explore_false_facts.py`
**Purpose**: Analyzes false facts in the system

**Analysis**:
- Lists all facts marked as "WRONG"
- Shows correction patterns
- Identifies common misconceptions
- Suggests improvements

**Usage**:
```bash
python production/utilities/explore_false_facts.py
```

---

### `production/utilities/export_facts_csv.py`
**Purpose**: Exports facts database to CSV format

**Export Options**:
- All facts
- Filtered by status
- With or without embeddings
- Custom field selection

**Usage**:
```bash
python production/utilities/export_facts_csv.py --output facts_export.csv --status good
```

---

### `production/utilities/list_drive_files.py`
**Purpose**: Lists Google Drive files for fact sheets

**Features**:
- Google Drive API integration
- File metadata display
- Permission checking
- Folder navigation

**Usage**:
```bash
python production/utilities/list_drive_files.py
```

---

### `production/utilities/monitor_progress.py`
**Purpose**: Real-time monitoring of data loading progress

**Displays**:
- Current phase
- Records processed/total
- Error counts
- Time estimates
- Cost estimates

**Usage**:
```bash
python production/utilities/monitor_progress.py
```

---

### `production/utilities/test_unified_knowledge_base.py`
**Purpose**: Comprehensive testing of the unified knowledge base

**Test Coverage**:
- All content sources
- Priority-based retrieval
- False fact prevention
- Query accuracy
- Performance benchmarks

**Usage**:
```bash
python production/utilities/test_unified_knowledge_base.py
```

---

## Archive Scripts

### Notable Archive Scripts

#### `archive/llamaindex_development/llamaindex_final_solution.py`
- Final working implementation before production refactor
- Contains proven query patterns
- Reference for optimization

#### `archive/llamaindex_development/llamaindex_comparison.py`
- Compares different LlamaIndex configurations
- Benchmarks retrieval strategies
- Optimization insights

#### `archive/pre_llamaindex_system/enhanced_forum_loader.py`
- Original forum loading approach
- Pre-LlamaIndex implementation
- Historical reference

---

## Script Organization Best Practices

### Development Workflow
1. New features start in `archive/llamaindex_development/`
2. Proven features move to `production/`
3. Deprecated code moves to `Old/`
4. All test scripts in respective `script-testing/` folders

### Naming Conventions
- Data loaders: `*_data_loader.py`
- Utilities: Descriptive action names
- Tests: `test_*.py`
- Monitoring: `monitor_*.py` or `check_*.py`

### Error Handling
- All scripts log to `.log` files
- Progress saved to `.json` files
- Graceful failure with clear error messages
- Resumable operations where possible

### Performance Considerations
- Batch operations for API calls
- Connection pooling for databases
- Progress tracking for long operations
- Cost estimation for API usage

---

**Last Updated**: July 25, 2025