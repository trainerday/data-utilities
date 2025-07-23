# Vector Processor Scripts

Production scripts for the TrainerDay YouTube content vector database.

## Main Scripts

### `youtube_only_processor.py` 
**Primary processing script** - Processes YouTube content into vector embeddings
- Creates embeddings for all YouTube video transcripts 
- Stores in PostgreSQL with pgvector
- Supports incremental processing (only new/changed files)
- Uses 1536-dimension embeddings for optimal performance

```bash
# Process all YouTube content
python scripts/youtube_only_processor.py

# Search YouTube content 
python scripts/youtube_only_processor.py --search "power zones"
```

### `search_youtube.py`
**Dedicated search tool** - Fast semantic search across YouTube content
- High-quality semantic search with similarity scores
- Direct video links with timestamps
- Clean, focused search interface

```bash
# Search examples
python scripts/search_youtube.py "training plans"
python scripts/search_youtube.py "how to use Coach Jack" --limit 10
```

## Utility Scripts

### `check_db_status.py`
Monitor database status and content overview
```bash
python scripts/check_db_status.py
```

### `check_completion_status.py` 
Verify processing completion and identify missing content
```bash
python scripts/check_completion_status.py
```

## Current Status

- ✅ **Complete**: All 54 YouTube videos processed (219 chunks)
- ✅ **Database**: PostgreSQL + pgvector with 1536-dimension embeddings  
- ✅ **Search**: High-quality semantic search with video timestamps
- ✅ **Performance**: ~1.1 chunks/second processing, fast search queries

## Configuration

Requires `.env` file with:
```env
OPENAI_API_KEY=your_key_here
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
OPENAI_EMBEDDING_DIMENSIONS=1536

DB_HOST=your_host
DB_PORT=25060
DB_DATABASE=defaultdb
DB_USERNAME=your_username
DB_PASSWORD=your_password
DB_SSLMODE=require
```

## Legacy Scripts

Old/experimental scripts moved to `script-testing/` folder:
- ChromaDB-based approaches
- Forum-only processors  
- Debugging utilities
- Development tools