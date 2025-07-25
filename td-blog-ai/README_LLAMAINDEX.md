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

### Phase 4: Process Review Results
10. **Read Google Sheets updates** - Get reviewed facts
11. **Update LlamaIndex knowledge base**:
    - Add NEW facts to knowledge base
    - Add WRONG facts with warning prefix
    - Add USELESS facts with exclusion prefix
    - Update status to CORRECT after adding
12. **Re-generate article** - Generate again with updated knowledge base

### Phase 5: Article Finalization
13. **Manual review/edit** - Review regenerated article
14. **Split into sub-articles** - Break into 5-10 focused pieces (500-800 words each)
15. **Review sub-articles** - Check coherence and flow

### Phase 6: Prepare for Publishing
16. **Add media** - Screenshots, diagrams, videos (AUTOMATE THIS... with vector media match...)
17. **Final formatting** - Ensure consistency
18. **Update status** - Mark as edit-complete
19. **Move to articles directory** - Ready for separate publish process

---

## Key Scripts

### Article Generation
```bash
# Generate comprehensive article
python generate_comprehensive_article_llamaindex.py "workout-features"

# Process batch of 3 articles
python batch_process_articles.py 1 2 3
```

### Fact Processing
```bash
# Extract new facts from article
python extract_new_facts.py output/workout-features-comprehensive.md

# Update knowledge base from Google Sheets
python update_facts_from_sheets.py

# Re-generate article with updated facts
python regenerate_article.py output/workout-features-comprehensive.md
```

### Article Splitting
```bash
# Split comprehensive article into sub-articles
python split_comprehensive_article.py output/workout-features-comprehensive.md

# Review and organize sub-articles
python organize_subarticles.py output/workout-features/
```

## Important Information

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
- **Re-generation**: ~5 minutes per article
- **Splitting & review**: 20-30 minutes per comprehensive article
- **Total**: ~2 hours for 3 comprehensive articles → 15-30 sub-articles

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