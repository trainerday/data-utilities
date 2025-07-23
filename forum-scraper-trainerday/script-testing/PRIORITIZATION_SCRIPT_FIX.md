# Forum Content Prioritization Script - Database Schema Fix

## Problem Summary

The original prioritization script failed because it was written to work with an incorrect database schema. The script expected SQLite tables but the actual forum-scraper project uses PostgreSQL with a different schema structure.

## Schema Issues Identified

### Expected vs Actual Schema

**Original (Incorrect) Assumptions:**
- SQLite database with simple column names
- Tables like `forum_topics` with direct columns like `created_at`, `title`, etc.
- Simple date fields

**Actual PostgreSQL Schema:**
- `forum_topics_raw` - Contains raw forum data as JSONB
- `forum_topics` - Contains analyzed topics with categories  
- `forum_qa_pairs` - Contains extracted Q&A pairs with date information
- Complex JSONB data structure requiring JSON path extraction

### Key Schema Differences

1. **Topic Data Storage:**
   - **Expected:** Direct columns like `title`, `views`, `posts_count`
   - **Actual:** JSONB field `raw_content` containing nested data structure

2. **Date Fields:**
   - **Expected:** Simple `created_at` column
   - **Actual:** Multiple date fields: `created_at_original`, `scraped_at`, `last_updated`

3. **Q&A Data:**
   - **Expected:** Questions embedded in topic table
   - **Actual:** Separate `forum_qa_pairs` table with `date_posted` field

## Solution Implemented

### 1. Database Connection
Fixed to use PostgreSQL with proper environment variable configuration:
```python
db_config = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_DATABASE'),
    'user': os.getenv('DB_USERNAME'),
    'password': os.getenv('DB_PASSWORD'),
    'sslmode': os.getenv('DB_SSLMODE', 'require')
}
```

### 2. Correct Table Joins
Updated query to properly join the three main tables:
```sql
FROM forum_topics_raw ftr
LEFT JOIN forum_topics ft ON ftr.topic_id = ft.topic_id
JOIN forum_qa_pairs qa ON ftr.topic_id = qa.topic_id
```

### 3. JSONB Data Extraction
Fixed data extraction from the JSONB `raw_content` field:
```sql
-- Extract views from JSONB
COALESCE(
    (jsonb_extract_path_text(ftr.raw_content, 'topic', 'views'))::int, 
    0
) as views

-- Extract post count from JSONB  
COALESCE(
    (jsonb_extract_path_text(ftr.raw_content, 'topic', 'posts_count'))::int, 
    0
) as posts_count
```

### 4. Proper Date Handling
Used correct date fields for recent activity analysis:
```sql
WHERE qa.date_posted >= CURRENT_DATE - INTERVAL '%s days'
```

### 5. JSON Serialization Fix
Fixed Decimal type serialization for JSON export:
```python
for key, value in result.items():
    if hasattr(value, 'isoformat'):  # datetime objects
        json_result[key] = value.isoformat()
    elif hasattr(value, '__float__'):  # Decimal objects
        json_result[key] = float(value)
    else:
        json_result[key] = value
```

## Script Features

### Core Functionality
- **Multi-factor Scoring:** Combines recency, frequency, engagement, and discussion metrics
- **Flexible Time Ranges:** Configurable lookback periods (default: 365 days)
- **Category Analysis:** Groups topics by analysis category
- **JSON Export:** Machine-readable results with metadata

### Scoring Algorithm
```
Priority Score = (recency_score * 0.3) + 
                (frequency_score * 0.25) + 
                (engagement_score * 0.25) + 
                (discussion_score * 0.2)
```

**Score Components:**
- **Recency Score (0-10):** Based on most recent question date
- **Frequency Score (0-10):** Number of questions × 2, capped at 10
- **Engagement Score (0-10):** Based on view count tiers
- **Discussion Score (0-10):** Based on post count tiers

## Usage Examples

### Basic Usage
```bash
python prioritize_recent_content.py
```

### Advanced Usage
```bash
# Look back 180 days, minimum 2 questions, top 20 results
python prioritize_recent_content.py --days-back 180 --min-questions 2 --limit 20

# Include category analysis and export results
python prioritize_recent_content.py --category-analysis --export my_results.json

# Focus on very recent activity
python prioritize_recent_content.py --days-back 90 --min-questions 3 --limit 15
```

### Command Line Options
- `--days-back N`: Look back N days for recent activity (default: 365)
- `--min-questions N`: Minimum questions required (default: 1)  
- `--limit N`: Maximum topics to return (default: 25)
- `--export FILE`: Export results to JSON file
- `--category-analysis`: Include category distribution analysis

## Output Example

```
TOP PRIORITY TOPICS FOR BLOG ARTICLES:
--------------------------------------------------
Rank Score Topic ID Views  Questions Title
--------------------------------------------------
1    7.8   53810    653    8         Error on convert to HR?
2    6.8   55971    292    4         [SOLVED] - Coach Jack not working
3    6.8   54703    1185   2         Removing Ant+ from TrainerDay
```

## File Location

The fixed script is located at:
`/Users/alex/Documents/Projects/data-utilities/forum-scraper-trainerday/script-testing/prioritize_recent_content.py`

## Dependencies

- Python 3.6+
- psycopg2-binary (PostgreSQL adapter)
- python-dotenv (environment variables)

## Environment Variables Required

```
DB_HOST=your_postgres_host
DB_PORT=5432
DB_DATABASE=your_database_name
DB_USERNAME=your_username
DB_PASSWORD=your_password
DB_SSLMODE=require
DB_SSLROOTCERT=ca-certificate.crt  # Optional
```

The script now works correctly with the actual PostgreSQL database schema and provides comprehensive prioritization of forum topics for blog article creation.