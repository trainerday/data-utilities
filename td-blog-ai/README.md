# TrainerDay LlamaIndex Article Generation Process

## Process Steps

### Phase 1: Initial Article Generation
1. **Load article config** from priority list (obsidian blog/articles-ai/category-sub-categories/workouts....)
2. **LlamaIndex retrieval** - Query knowledge base with automatic relevance scoring
3. **Generate comprehensive article** (~2000-3000 words)
4. **Save draft article** with status: draft

### Phase 2: Fact Extraction & Deduplication
5. **Extract facts** from generated article
6. **Generate embeddings** for each extracted fact
7. **Vector search existing facts** - Check each fact against LlamaIndex knowledge base
8. **Filter duplicates** - Skip facts with similarity ≥ 0.8 to existing facts
9. **Insert to Google Sheets** - Add ONLY truly new facts with status: REVIEW

### Phase 3: Human Fact Review
10. **Review facts in Google Sheets** - Change status from REVIEW to:
    - **NEW** - Good fact to add to knowledge base
    - **WRONG** - Incorrect information
    - **USELESS** - True but not valuable

### Phase 4: Article Re-generation with Review Feedback
11. **Query Google Sheets for bad facts** - Get all WRONG and USELESS facts
12. **Re-generate article** with explicit exclusions:
    - Pass bad facts list as "DO NOT INCLUDE THESE FACTS"
    - LLM avoids these specific facts during generation
13. **Save updated article** - Replaces initial draft

### Phase 5: Article Finalization
14. **Manual review/edit** - Review regenerated article
15. **Split into sub-articles** - Break into 5-10 focused pieces (500-800 words each)
16. **Review sub-articles** - Check coherence and flow

### Phase 6: Prepare for Publishing
17. **Add media** - Screenshots, diagrams, videos (AUTOMATE THIS... with vector media match...)
18. **Final formatting** - Ensure consistency
19. **Update status** - Mark as edit-complete
20. **Move to articles directory** - Ready for separate publish process

### Phase 7: Knowledge Base Update (Async)
21. **Run fact refresh in vector-loader** - Updates knowledge base for future articles
    - `cd ../vector-loader`
    - `python production/facts_system/update_facts_preserve_status.py`
    - `python production/data_loaders/facts_data_loader.py`

---

## Key Scripts

### Article Generation (td-blog-ai)
```bash
# Initial generation
python generate_comprehensive_article_llamaindex.py "workout-features"

# Process batch of 3 articles
python batch_process_articles.py 1 2 3
```

### Fact Processing (td-blog-ai)
```bash
# Extract new facts with vector deduplication
python extract_new_facts_vector.py output/workout-features-comprehensive.md

# Query bad facts from Google Sheets
python get_bad_facts_from_sheets.py

# Re-generate with exclusions
python regenerate_with_exclusions.py output/workout-features-comprehensive.md
```

### Article Splitting (td-blog-ai)
```bash
# Split comprehensive article into sub-articles
python split_comprehensive_article.py output/workout-features-comprehensive.md

# Review and organize sub-articles
python organize_subarticles.py output/workout-features/
```

### Knowledge Base Update (vector-loader)
```bash
# Update facts from Google Sheets (can be done async)
cd ../vector-loader
python production/facts_system/update_facts_preserve_status.py
python production/data_loaders/facts_data_loader.py
```

## Important Information

### Two-Stage Generation Approach

**Stage 1: Initial Generation**
- Uses existing LlamaIndex knowledge base
- May include some incorrect facts not yet marked

**Stage 2: Re-generation with Exclusions**
- Queries Google Sheets directly for WRONG/USELESS facts
- Explicitly tells LLM what facts to avoid
- Immediate use of human review feedback
- No need to wait for knowledge base update

### Fact Deduplication Process

1. **Extract facts** from generated article
2. **Generate embeddings** using text-embedding-3-large
3. **Vector search** against existing facts in LlamaIndex
4. **Similarity threshold**: 0.8 (configurable)
   - ≥ 0.8: Duplicate (skip)
   - < 0.8: New fact (add to sheets)
5. **Google Sheets columns**:
   - Fact text
   - Source article
   - Closest match similarity
   - Closest match text (for reference)
   - Status: REVIEW

### Project Responsibilities

**td-blog-ai project:**
- Article generation and re-generation
- Fact extraction with vector deduplication
- Google Sheets fact insertion
- Query bad facts from Sheets for re-generation
- Article splitting and formatting

**vector-loader project:**
- Knowledge base management
- Google Sheets synchronization for future articles
- LlamaIndex vector store maintenance
- Long-term fact storage

### Fact Status Lifecycle

**REVIEW** → Human Review → **NEW/WRONG/USELESS** → Immediate Use → Later KB Update

- **REVIEW**: Awaiting human review (automatically set)
- **NEW**: Validated fact to be added
- **WRONG**: Incorrect information to exclude
- **USELESS**: True but not valuable to exclude
- **CORRECT**: Final status after KB update

### Global Fact System

Facts are **global across all articles**:
- Immediate exclusion via Google Sheets query
- Permanent exclusion after vector-loader update
- No duplicate fact reviews due to vector matching

### Article Output Structure

```
output/
├── comprehensive/          # Initial comprehensive articles
│   ├── workout-features-comprehensive.md
│   └── calendar-sync-comprehensive.md
├── regenerated/           # Articles after fact review
│   ├── workout-features-comprehensive-v2.md
│   └── calendar-sync-comprehensive-v2.md
├── subarticles/           # Split articles (5-10 per comprehensive)
│   ├── workout-features/
│   │   ├── F001-creating-workouts.md
│   │   ├── F002-workout-editor.md
│   │   └── ...
│   └── calendar-sync/
│       ├── F010-google-calendar.md
│       └── ...
└── final/                 # Ready for articles directory
    ├── F001-creating-workouts.md
    └── ...
```

### Quality Controls

- **Vector deduplication** - Only review truly new facts
- **Immediate feedback** - Re-generation uses review results instantly
- **Explicit exclusions** - LLM knows exactly what to avoid
- **Async KB updates** - Knowledge base updated for future articles

### Expected Timeline

- **Initial generation**: ~5 minutes per comprehensive article
- **Fact extraction & dedup**: ~3 minutes per article
- **Human fact review**: 10-15 minutes (only new facts)
- **Re-generation**: ~5 minutes per article
- **Splitting & review**: 20-30 minutes per comprehensive article
- **Total**: ~2 hours for 3 comprehensive articles → 15-30 sub-articles
- **KB update**: Can happen anytime later

### Benefits Over Previous System

1. **Fewer facts to review** - Vector deduplication eliminates duplicates
2. **Immediate feedback** - No waiting for KB updates
3. **Explicit guidance** - LLM knows what to avoid
4. **Flexible timing** - KB updates can happen async
5. **Better quality** - Two-pass generation with human input