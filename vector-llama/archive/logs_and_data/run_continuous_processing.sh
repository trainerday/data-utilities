#!/bin/bash

# Continuous processing script for remaining articles
# Processes articles in small batches with progress tracking

echo "🎯 CONTINUOUS ARTICLE PROCESSING"
echo "================================="

# Get current status
python -c "
from utils.db_connection import get_db_connection
from psycopg2.extras import RealDictCursor
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

conn = get_db_connection()
with conn.cursor(cursor_factory=RealDictCursor) as cursor:
    cursor.execute('SELECT COUNT(DISTINCT source_article) as articles FROM facts')
    articles = cursor.fetchone()['articles']
    print(f'✅ Currently processed: {articles} articles')
    
    # Count total articles
    from pathlib import Path
    import os
    content_output_path = os.getenv('CONTENT_OUTPUT_PATH', '.')
    articles_dir = Path(content_output_path) / 'articles-ai'
    total_articles = len(list(articles_dir.glob('*.md')))
    remaining = total_articles - articles
    print(f'📄 Total articles: {total_articles}')
    print(f'🔄 Remaining: {remaining}')

conn.close()
"

echo ""
echo "🔄 Starting batch processing..."

# Process in batches of 2 articles each
start_idx=16
batch_size=2

while true; do
    echo "📊 Processing batch starting at article $((start_idx + 1))..."
    
    # Run batch processing
    python script-testing/extract_facts_batch.py --start $start_idx --batch-size $batch_size
    
    # Check if we processed any articles in this batch
    if [ $? -ne 0 ]; then
        echo "❌ Batch processing failed, trying smaller batch..."
        batch_size=1
    fi
    
    # Check if we're done
    processed=$(python -c "
from utils.db_connection import get_db_connection
from psycopg2.extras import RealDictCursor
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

conn = get_db_connection()
with conn.cursor(cursor_factory=RealDictCursor) as cursor:
    cursor.execute('SELECT COUNT(DISTINCT source_article) as articles FROM facts')
    articles = cursor.fetchone()['articles']
    print(articles)
conn.close()
")
    
    if [ "$processed" -ge 67 ]; then
        echo "🎉 All articles processed!"
        break
    fi
    
    # Increment start index
    start_idx=$((start_idx + batch_size))
    
    echo "⏸️  Waiting 10 seconds before next batch..."
    sleep 10
done

echo ""
echo "✅ Processing complete! Final summary:"
python -c "
from utils.db_connection import get_db_connection
from psycopg2.extras import RealDictCursor
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

conn = get_db_connection()
with conn.cursor(cursor_factory=RealDictCursor) as cursor:
    cursor.execute('SELECT COUNT(*) as count FROM facts')
    total = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(DISTINCT source_article) as articles FROM facts')
    articles = cursor.fetchone()['articles']
    
    print(f'📊 Total facts: {total}')
    print(f'📄 Articles processed: {articles}')

conn.close()
"