# Scripts Directory

This directory contains the main script for querying article features from the LlamaIndex knowledge base.

## Main Script

### query_all_article_features.py
**Comprehensive article features query script**
- Queries LlamaIndex for features based on markdown query files
- Loads queries from `article-queries/` directory
- Uses priority-based retrieval with different similarity thresholds for each content type
- Generates comprehensive JSON results for article generation

#### Usage

```bash
python scripts/query_all_article_features.py <query-file-name>
```

Example:
```bash
python scripts/query_all_article_features.py workout-queries
```

This will load queries from `article-queries/workout-queries.md`.

#### Query File Format

Query files should be markdown files in the `article-queries/` directory with the following structure:

```markdown
# Query Title

## Category Name

### Feature Name
- "query string 1"
- "query string 2"
- "query string 3"

### Another Feature
- "another query"
- "more queries"
```

#### Output

Results are saved to `article-temp-files/article_features.json`

## Environment Requirements

Make sure you have the required environment variables set in your `.env` file:
- `OPENAI_API_KEY` - Required for embeddings
- Database connection details (defaults to localhost/trainerday_local)
- Other API keys as needed

## Dependencies

The script requires:
- Python 3.x
- psycopg2
- llama-index
- python-dotenv
- OpenAI API access

Install dependencies with:
```bash
pip install -r requirements.txt
```