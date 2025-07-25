# TrainerDay LlamaIndex Article Generation Process

## Process Steps

### Phase 1: Article Generation
1. **Load article config** from priority list (obsidian  blog/articles-ai/category-sub-categories/workouts....)
2. **LlamaIndex retrieval** - Query knowledge base with automatic relevance scoring
3. **Generate comprehensive article** (~2000-3000 words)
4. **Save draft article** with status: draft

### Phase 2: Fact Extraction & Review
5. **Extract facts** from generated article
6. **Vector search existing facts** - Check against LlamaIndex knowledge base
7. **Identify new facts** - Not found in knowledge base (similarity < 0.8)
8. **Insert to Google Sheets** - Add NEW facts with status: REVIEW

### Phase 3: Human Fact Review
9. **Review facts in Google Sheets** - Change status from REVIEW to:
   - **NEW** - Good fact to add to knowledge base
   - **WRONG** - Incorrect information
   - **USELESS** - True but not valuable

### Phase 4: Process Review Results (vector-loader project)
10. **Run fact update in vector-loader** - `cd ../vector-loader && python production/facts_system/update_facts_preserve_status.py`
11. **Reload facts to LlamaIndex** - `python production/data_loaders/facts_data_loader.py`
    - Adds NEW facts to knowledge base
    - Adds WRONG facts with warning prefix
    - Adds USELESS facts with exclusion prefix
    - Updates status to CORRECT after adding

### Phase 5: Article Re-generation
12. **Re-generate article** - Generate again with updated knowledge base

### Phase 6: Article Finalization
13. **Manual review/edit** - Review regenerated article
14. **Split into sub-articles** - Break into 5-10 focused pieces (500-800 words each)
15. **Review sub-articles** - Check coherence and flow

### Phase 7: Prepare for Publishing
16. **Add media** - Screenshots, diagrams, videos (AUTOMATE THIS... with vector media match...)
17. **Final formatting** - Ensure consistency
18. **Update status** - Mark as edit-complete
19. **Move to articles directory** - Ready for separate publish process

---

## Key Scripts

### Article Generation (td-blog-ai)
```bash
# Generate comprehensive article
python generate_comprehensive_article_llamaindex.py "workout-features"

# Process batch of 3 articles
python batch_process_articles.py 1 2 3
```

### Fact Processing (td-blog-ai)
```bash
# Extract new facts from article
python extract_new_facts.py output/workout-features-comprehensive.md
```

### Fact Updates (vector-loader)
```bash
# Switch to vector-loader project
cd ../vector-loader

# Update facts from Google Sheets review
python production/facts_system/update_facts_preserve_status.py

# Reload facts to LlamaIndex knowledge base
python production/data_loaders/facts_data_loader.py
```

### Article Re-generation (td-blog-ai)
```bash
# Back to td-blog-ai
cd ../td-blog-ai

# Re-generate article with updated facts
python regenerate_article.py output/workout-features-comprehensive.md

# Split comprehensive article into sub-articles
python split_comprehensive_article.py output/workout-features-comprehensive.md
```

## Important Information

### Project Responsibilities

**td-blog-ai project:**
- Article generation and content creation
- Fact extraction from generated articles
- Article splitting and formatting
- Final article output

**vector-loader project:**
- Knowledge base management
- Fact loading and updates
- Google Sheets synchronization
- LlamaIndex vector store maintenance

### Fact Status Lifecycle

**REVIEW** → Human Review → **NEW/WRONG/USELESS** → Process → **CORRECT**

- **REVIEW**: Awaiting human review (automatically set)
- **NEW**: Validated fact to be added
- **WRONG**: Incorrect information to be blocked
- **USELESS**: True but not valuable to include
- **CORRECT**: Final status after processing

### Global Fact System

Facts are **global across all articles**:
- Once marked WRONG or USELESS, prevents use in ALL future articles
- NEW facts become available to all articles after adding to knowledge base
- No need to review the same facts multiple times

### Knowledge Base Prefixes

- **Normal facts**: "Fact: [fact text]"
- **Wrong facts**: "DO NOT USE IN ARTICLES: This is incorrect information - [fact text]"
- **Useless facts**: "USELESS FACT - DO NOT INCLUDE: [fact text]"

### Fact Update Process Detail

1. **td-blog-ai** extracts facts and adds to Google Sheets
2. **Human** reviews in Google Sheets
3. **vector-loader/production/facts_system/update_facts_preserve_status.py**:
   - Reads Google Sheets with status updates
   - Preserves existing user modifications
   - Identifies new facts to add
4. **vector-loader/production/data_loaders/facts_data_loader.py**:
   - Loads facts with appropriate prefixes based on status
   - Updates LlamaIndex knowledge base
   - Makes facts available for all future queries

### Article Output Structure

```
output/
├── comprehensive/          # Initial comprehensive articles
│   ├── workout-features-comprehensive.md
│   └── calendar-sync-comprehensive.md
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

- **Automatic deduplication** - LlamaIndex prevents duplicate content
- **Fact validation** - Global fact review prevents misinformation
- **Similarity thresholds** - Intelligent retrieval without manual tuning
- **Re-generation** - Articles updated after fact review

### Expected Timeline

- **Article generation**: ~5 minutes per comprehensive article
- **Fact extraction**: ~2 minutes per article
- **Human fact review**: 15-30 minutes for batch of new facts
- **Fact update & reload**: ~5 minutes in vector-loader
- **Re-generation**: ~5 minutes per article
- **Splitting & review**: 20-30 minutes per comprehensive article
- **Total**: ~2.5 hours for 3 comprehensive articles → 15-30 sub-articles

### Migration from Old System

This system replaces:
- Manual vector search with similarity thresholds
- Complex fact extraction and enhancement phases
- Multiple review cycles
- Separate enhancement scripts

Benefits:
- Single source of truth for facts
- Faster end-to-end process
- Simpler codebase
- Better quality control
- Clear separation of concerns between projects