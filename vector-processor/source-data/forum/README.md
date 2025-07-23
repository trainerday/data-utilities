# Forum Q&A Data Source

Forum discussions processed into semantic Q&A units for vector search across TrainerDay community support content.

## 📊 Data Source Overview

**Primary Content**: Extracted question/answer pairs from PostgreSQL forum database (15,000+ topics)
**Processing Focus**: Question-Answer Pairs processed into semantic Q&A units
**Content Type**: User support content, community discussions, technical support, feature requests

## 🚀 Data Processing

### **Forum Q&A Processing** (`unified_content_processor.py`)
- **Input**: PostgreSQL forum database with raw topics and analysis
- **Processing**: Extract question + answer pairs as single semantic units
- **Chunk Size**: 200-800 characters per Q&A pair
- **Metadata**: `{"category": "technical", "question": "...", "answer": "...", "topic_id": 1234}`

### **Database Source**
- **Table**: `forum_analysis` - Contains processed Q&A pairs from forum topics
- **Format**: PostgreSQL table with structured question/answer data
- **Update Method**: Incremental processing based on `created_at`/`updated_at` timestamps
- **Change Detection**: Tracks `last_processed_id` for efficient incremental updates

## 📋 Usage

### **Extract Forum Q&A Pairs**
```bash
# Process forum Q&A pairs into vector embeddings
python unified_content_processor.py

# Test similarity search on forum content
python unified_content_processor.py --search "How do I sync to Garmin?" --source-filter forum
```

### **Database Query Example**
```sql
-- Find similar forum content
SELECT 
    source, title, content, metadata,
    1 - (embedding <=> %s) AS similarity_score
FROM content_embeddings
WHERE source = 'forum'
ORDER BY embedding <=> %s
LIMIT 10;
```

## 🎯 Content Strategy Benefits

### **Cross-Content Analysis**
- **Gap Identification**: Find forum questions without corresponding blog articles
- **Content Enhancement**: Use forum language to improve existing documentation
- **Topic Prioritization**: Rank content opportunities by user engagement frequency

### **Voice Pattern Matching**
- **User Language**: How users actually describe problems ("my trainer won't connect")
- **Platform Language**: How official docs explain features ("Bluetooth pairing process")
- **Content Bridge**: Generate content using user terminology with technical accuracy

## 🏗️ Integration Points

- **Forum Analysis System**: External forum-scraper-trainerday project (data stored in PostgreSQL)
- **Content Strategy Pipeline**: TD-Business Basic Memory project (THE-PLAN.md)
- **PostgreSQL Integration**: Uses existing TrainerDay data warehouse infrastructure

## 🔍 Search Capabilities

### **Forum-Specific Search Examples**
```bash
# Natural language queries work across forum content
"How do I connect my power meter to TrainerDay?"
"Troubleshooting Garmin sync issues"
"Setting up Zwift integration"
"Creating custom workouts"
```

### **Advanced Forum Filtering**
```sql
-- Search within specific forum categories
WHERE source = 'forum' AND metadata->>'category' = 'technical'

-- Search by topic engagement
WHERE source = 'forum' AND metadata->>'posts_count' > '5'
```

## 📈 Processing Statistics

- **Content Volume**: 15,000+ forum topics processed into Q&A pairs
- **Processing Method**: Incremental updates based on database timestamps
- **Storage Format**: Unified `content_embeddings` table with pgvector similarity search
- **Update Frequency**: On-demand processing of new forum discussions

---

*Forum Q&A processing enables TrainerDay's comprehensive content strategy by providing semantic search across community discussions, facilitating content gap analysis and user-driven content enhancement.*