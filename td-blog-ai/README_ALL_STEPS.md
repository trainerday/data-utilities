# TrainerDay AI Article Enhancement Workflow - Complete Process

End-to-end workflow for generating, fact-checking, and enhancing TrainerDay blog articles using AI and human review.

## Prerequisites
- PostgreSQL with pgvector extension
- OpenAI API key (embeddings)
- Anthropic API key (Claude)
- Google Sheets API credentials
- Environment variables in `.env`

## Phase 1: Article Generation

### Human Tasks
1. **Plan article priorities** - Curate priority lists in `/Users/alex/Documents/bm-projects/TD-Business/blog/in-progress/`
2. **Review article lists** - Ensure topics marked as "yes" for generation

### Automated Process
3. **Generate individual articles** - `python scripts/generate_individual_article.py 1`
4. **Create vector embeddings** - System searches existing content for context
5. **Apply templates** - Uses `templates/individual-article-prompt-template.txt`
6. **Save to articles-ai** - Creates F001-F068 files with status "new-article"

### Outputs
- 68 articles in `/Users/alex/Documents/bm-projects/TD-Business/blog/articles-ai/ai-created/`
- YAML frontmatter with metadata
- 500-800 word articles in Alex's founder voice

## Phase 2: Fact Extraction

### Automated Process
7. **Extract facts from articles** - `python script-testing/extract_facts_to_database.py`
8. **Generate fact embeddings** - OpenAI embeddings for similarity detection
9. **Store in database** - Facts saved to PostgreSQL with vector similarity
10. **Detect duplicates** - 90% similarity threshold prevents duplicate facts

### Outputs
- ~1000+ facts in database with embeddings
- Fact metadata including source article references

## Phase 3: Google Sheets Review Setup

### Automated Process
11. **Create review spreadsheet** - `python script-testing/create_facts_spreadsheet.py`
12. **Populate facts** - `python script-testing/populate_td_blog_facts.py`
13. **Format for review** - Column structure: fact_id, status, original_fact, replacement_text, notes, source_article, created_at

### Human Tasks
14. **Review facts in Google Sheets** - Mark status as WRONG, REMOVE, ADD, or REPLACE
15. **Add replacement text** - Provide improved versions for facts marked "REPLACE" 
16. **Add review notes** - Context for fact corrections

### Outputs
- Shared Google Sheets with human fact review results
- Status markings for each extracted fact

## Phase 4: Targeted Article Enhancement

### Automated Process
17. **Read fact review results** - `python script-testing/enhance_articles_from_facts.py`
18. **Group facts by article** - Articles with WRONG/REMOVE/ADD markings
19. **Send to Claude for enhancement** - Apply fact corrections using templates
20. **Compare original vs enhanced** - Only save articles with real changes
21. **Update article status** - Change from "new-article" to "edit-complete"

### Outputs
- Enhanced articles in `ai-updated/` subdirectory
- Only articles with actual improvements saved

## Phase 5: Comprehensive Article Enhancement

### Automated Process
22. **Process all 67 articles** - `python script-testing/enhance_all_articles.py`
23. **General quality enhancement** - Claude reviews for accuracy, clarity, completeness
24. **Monitor progress** - `python script-testing/monitor_progress.py`
25. **Apply quality controls** - Only save articles with detected improvements

### Human Tasks
26. **Monitor enhancement progress** - Check logs and progress reports
27. **Review enhanced articles** - Final quality check in UPDATED directory

### Outputs
- All 67 articles processed through enhancement pipeline
- Enhanced versions saved to ai-updated directory with same filenames
- Progress tracking and statistics

## Phase 6: Final Review and Publishing

### Human Tasks
28. **Review all enhanced articles** - Editorial review of articles in ai-updated directory
29. **Review unenhanced articles** - Check articles remaining in ai-created for quality
30. **Final content editing** - Polish language, fix any issues, ensure consistency
31. **Add images and media** - Insert screenshots, diagrams, and visual content
32. **Move approved articles** - Transfer finalized articles to FINAL directory
33. **Run blog creation process** - Execute blog generation in the main blog project

### Outputs
- Finalized articles ready for publication in FINAL directory
- Enhanced articles with images, proper formatting, and editorial polish
- Complete set of high-quality blog content ready for main blog project workflow

## Key Files and Locations

### Scripts
- `scripts/generate_individual_article.py` - Generate specific articles
- `script-testing/extract_facts_to_database.py` - Extract facts from articles  
- `script-testing/populate_td_blog_facts.py` - Populate Google Sheets
- `script-testing/enhance_articles_from_facts.py` - Apply fact corrections
- `script-testing/enhance_all_articles.py` - Enhance all articles
- `script-testing/monitor_progress.py` - Track progress

### Templates
- `templates/individual-article-prompt-template.txt` - Article generation prompts
- `templates/article-enhancement-prompt-template.txt` - Enhancement prompts

### Data Locations
- **Original articles**: `/Users/alex/Documents/bm-projects/TD-Business/blog/articles-ai/ai-created/`
- **Enhanced articles**: `/Users/alex/Documents/bm-projects/TD-Business/blog/articles-ai/ai-updated/`
- **Later processing**: `/Users/alex/Documents/bm-projects/TD-Business/blog/articles-ai/ai-created-later/`
- **Final ready articles**: `/Users/alex/Documents/bm-projects/TD-Business/blog/articles-ai/FINAL/`
- **Priority lists**: `/Users/alex/Documents/bm-projects/TD-Business/blog/in-progress/`
- **Database**: PostgreSQL with pgvector extension
- **Google Sheets**: Shared spreadsheet for fact review

## Monitoring Commands

```bash
# Check fact extraction progress
python script-testing/check_processing_status.py

# Monitor article enhancement progress  
python script-testing/monitor_progress.py

# View Google Sheets integration status
python script-testing/populate_td_blog_facts.py
```

## Quality Controls

- **Vector similarity** prevents duplicate facts
- **Human fact review** ensures accuracy
- **Content comparison** only saves real improvements
- **Status tracking** maintains workflow state
- **Template consistency** ensures voice and format
- **Progress monitoring** tracks completion

## Expected Timeline
- **Article generation**: ~2 hours for 68 articles
- **Fact extraction**: ~1 hour for all articles
- **Human fact review**: 2-4 hours depending on complexity
- **Article enhancement**: ~2 hours for all articles (automated)
- **Final review and editing**: 3-4 hours for comprehensive review
- **Image addition and formatting**: 2-3 hours depending on complexity
- **Blog creation process**: 1-2 hours in main blog project

## Success Metrics
- 68 articles generated with consistent voice and format
- ~1000+ facts extracted and reviewed for accuracy
- Enhanced articles saved only when improvements detected
- Complete audit trail from generation to publication
- Final articles polished with images and proper formatting
- High-quality, factually accurate content ready for blog publication
- Seamless handoff to main blog creation workflow