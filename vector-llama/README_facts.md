# Fact Extraction and Processing System

## Overview

This system extracts factual statements from generated blog articles, manages them through a database with vector similarity checking, and provides a Google Sheets interface for fact quality control and replacement management.

## Architecture

### Components

1. **Fact Extraction**: Uses Claude Sonnet 4 to extract factual statements from articles
2. **Vector Database**: PostgreSQL with pgvector for similarity checking and deduplication
3. **Google Sheets Interface**: Manual review and status management for extracted facts
4. **Status Processing**: Handles good/bad/replace logic based on Sheet status

### Database Schema

```sql
CREATE TABLE facts (
    id SERIAL PRIMARY KEY,              -- Used as Google Sheet key
    fact_text TEXT NOT NULL,            -- Original extracted fact
    source_article VARCHAR(200),        -- Source article filename
    embedding vector(1536),             -- OpenAI text-embedding-3-large
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Google Sheet Structure

| Column | Description | Values |
|--------|-------------|---------|
| fact_id | Database ID | Auto-populated |
| original_fact | Extracted fact text | From Claude extraction |
| status | Review status | pending, good, bad, replace |
| replacement_text | Improved fact text | Only for "replace" status |
| notes | Review comments | Optional |

## Workflow

### 1. Article Processing
```
Article (Markdown) → Fact Extraction (Claude) → Individual Facts
```

### 2. Fact Verification
```
For each fact:
├── Generate embedding (OpenAI)
├── Check similarity in facts table
├── If new fact:
│   ├── Insert into database (get ID)
│   └── Add to Google Sheet (status: pending)
└── If existing fact:
    └── Read status from Google Sheet
```

### 3. Status Actions
- **good**: Use fact as extracted
- **bad**: Skip/ignore fact
- **replace**: Use replacement_text from Google Sheet
- **pending**: Awaiting manual review

## File Structure

```
td-blog-ai/
├── scripts/
│   └── extract_and_process_facts.py    # Main fact processor
├── utils/
│   ├── db_connection.py                 # Database utilities (existing)
│   ├── claude_client.py                 # Claude API client (existing)
│   └── google_sheets_client.py          # Google Sheets integration (new)
└── README_facts.md                      # This documentation
```

## Implementation Scripts

### Main Processor: `extract_and_process_facts.py`
```python
def process_article_facts(article_path):
    """Main function to extract and process facts from an article"""
    
def extract_facts_from_article(article_content):
    """Use Claude Sonnet 4 to extract factual statements"""
    
def check_fact_exists(fact_text):
    """Check if similar fact exists using vector similarity"""
    
def get_fact_status(fact_id):
    """Get status from Google Sheet using fact ID"""
    
def apply_fact_status(fact, status, replacement_text=None):
    """Handle fact based on status (good/bad/replace)"""
```

### Google Sheets Client: `google_sheets_client.py`
```python
def add_fact_to_sheet(fact_id, fact_text):
    """Add new fact to Google Sheet with pending status"""
    
def get_fact_status_from_sheet(fact_id):
    """Get status and replacement text for a fact ID"""
    
def batch_update_sheet(facts_data):
    """Batch insert multiple facts to avoid rate limits"""
```

## Configuration

### Environment Variables
```bash
# Existing database config (from td-blog-ai)
DB_HOST=your_postgres_host
DB_DATABASE=your_database
DB_USERNAME=your_username
DB_PASSWORD=your_password

# Existing API keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Google Sheets API
GOOGLE_SHEETS_CREDENTIALS_FILE=path/to/service-account.json
GOOGLE_SHEETS_ID=your_sheet_id
```

### Dependencies
Add to `requirements.txt`:
```
gspread>=5.0.0
google-auth>=2.0.0
```

## Usage

### Extract Facts from Single Article
```bash
python scripts/extract_and_process_facts.py --article articles-ai/article-name.md
```

### Process All Articles in Directory
```bash
python scripts/extract_and_process_facts.py --directory articles-ai/
```

### Reprocess Facts with Updated Status
```bash
python scripts/extract_and_process_facts.py --reprocess-existing
```

## Google Sheets Management

### Review Process
1. New facts appear with status="pending"
2. Review original_fact text
3. Set status:
   - **good**: Fact is accurate as-is
   - **bad**: Fact is incorrect/unwanted
   - **replace**: Fact needs improvement (add replacement_text)
4. Save sheet - system will use updated status on next run

### Batch Operations
- Filter by status to focus on pending items
- Use notes column for review context
- Sort by fact_id to process chronologically

## Vector Similarity

### Deduplication Logic
- Uses cosine similarity on OpenAI embeddings
- Threshold: 0.85-0.90 (configurable)
- Prevents near-duplicate facts from being added
- Existing fact takes precedence (keeps original ID)

### Performance Considerations
- Batch embedding generation for efficiency
- Index on embedding column for fast similarity queries
- Connection pooling for database operations

## Integration Points

### With Existing td-blog-ai
- Reuses database connection patterns from `utils/db_connection.py`
- Leverages Claude API client from `utils/claude_client.py`
- Processes articles from existing output directory

### With vector-processor Project
- Uses same PostgreSQL database and pgvector extension
- Compatible with existing content_embeddings table structure
- Can share vector similarity utility functions if needed

## Error Handling

### API Failures
- Retry logic for Claude and OpenAI API calls
- Rate limiting respect for Google Sheets API
- Graceful degradation when services unavailable

### Data Integrity
- Transaction handling for database operations
- Verification of Google Sheets sync status
- Logging of all fact processing decisions

## Monitoring and Logging

### Metrics to Track
- Facts extracted per article
- Deduplication hit rate
- Google Sheets sync success rate
- Processing time per article

### Log Files
- `fact_extraction.log`: Claude API responses and extracted facts
- `similarity_checks.log`: Vector similarity decisions
- `sheets_sync.log`: Google Sheets API operations