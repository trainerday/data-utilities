# TrainerDay Blog Article Generation System

This system generates instructional blog articles for TrainerDay features using a multi-step workflow with LLM calls and human review integration.

## The 3 Big Steps

### 1. Generate Everything

```bash
python run-all-steps-to-generate-articles.py workout-queries
```

Runs the complete 5-step pipeline to generate styled articles.

### 2. Alex Edits

Review and manually edit articles in `output/articles-ai/`

### 3. Finalize and Move

```bash
python scripts/finalize_edits.py
```

Captures your edits and copies articles to blog system.

## Complete Workflow Steps

### Step 1: Query Vector Database

**Script:** `scripts/step1-query-vector-database.py`

- Queries the LlamaIndex vector database using queries from markdown files
- Retrieves relevant facts, blog quotes, forum discussions, and video content
- Saves results to `article-temp-files/article_features.json`
- No LLM calls - just database queries

### Step 2: Generate Article Content (LLM Call)

**Script:** `scripts/step2-generate-article-content.py`

- Cleans existing articles and _originals directories
- Generates comprehensive content (1000-1500 words) for each section
- Uses OpenAI GPT-4o (falls back to Claude if needed)
- Focuses purely on content - no style considerations
- Saves articles to `output/articles-ai/`
- Saves section info to `article-temp-files/generated_sections.json`

### Step 3: Generate YAML Metadata (LLM Call)

**Script:** `scripts/step3-generate-yaml-metadata.py`

- Adds YAML front matter to each article
- Uses GPT-4o to generate appropriate:
  - Title
  - Tags (from hierarchy rules)
  - Engagement type (quick-post, complete-post, geek-post)
  - Excerpt
  - Permalink
- Core features → quick-post, Secondary features → LLM decides

### Step 4: Apply Style and Edits (LLM Call)

**Script:** `scripts/step4-apply-style-and-edits.py`

- Creates backup in `output/_originals/`
- Uses Claude to apply:
  - Alex's writing style (direct, instructional, no marketing fluff)
  - User edits from `article-queries/edits/workout-edits.json`
  - Global style instructions
  - Article-specific edits
- Maintains technical accuracy while improving readability

### Step 5: Generate Overview (LLM Call)

**Script:** `scripts/step5-generate-overview.py`

- Creates overview article linking to all sections
- Extracts summaries from generated articles
- Organizes by Core Features and Additional Features
- Saves as `output/articles-ai/s00-overview.md`

## Edit Tracking System

### Making Edits

1. Edit articles directly in `output/articles-ai/`
2. Run `python scripts/finalize_edits.py` to:
   - Compare edited versions with originals
   - Extract edit instructions using GPT-4o
   - Save to `article-queries/edits/workout-edits.json`
   - Copy articles to blog system

### Edit Storage Format

```json
{
  "last_updated": "2025-07-26T19:49:11.000Z",
  "global_instructions": {
    "style": ["Always use 'Workout Editor' not 'Visual Workout Editor'"],
    "facts_to_avoid": ["Drag and drop functionality"]
  },
  "articles": {
    "s01-Workout_Editor_Basics": {
      "edit_instructions": ["Focus on Excel-like functionality"],
      "facts_to_add": ["Copy paste works like Excel"],
      "facts_to_remove": ["Visual drag and drop"],
      "custom_sections": []
    }
  }
}
```

## Query File Format

Query files in `article-queries/` use this markdown format:

```markdown
# Query Document Title

## Core Features
### Feature Name
- "exact query phrase 1"
- "query phrase with multiple words"
- "another search query"

## Additional Features  
### Another Feature
- "search query"
```

## Bad Facts System

Bad facts are managed in Google Sheets and prevent incorrect information from appearing in articles:

1. **During Generation**: Bad facts are loaded and passed to LLM with "DO NOT USE" instructions
2. **Examples**:
   - "Visual Workout Editor" → Use "Workout Editor" instead
   - "Drag and drop functionality" → Does not exist
3. **Management**: Review and update in Google Sheets

## Directory Structure

```
td-blog-ai/
├── scripts/
│   ├── step1-query-vector-database.py
│   ├── step2-generate-article-content.py
│   ├── step3-generate-yaml-metadata.py
│   ├── step4-apply-style-and-edits.py
│   ├── step5-generate-overview.py
│   ├── finalize_edits.py
│   └── ...
├── templates/
│   ├── section-generation-template.txt
│   ├── overview-template.txt
│   └── apply-style-template.txt
├── article-queries/
│   ├── workout-queries.md
│   └── edits/
│       └── workout-edits.json
├── article-temp-files/
│   ├── article_features.json
│   └── generated_sections.json
├── output/
│   ├── articles-ai/
│   │   ├── s00-overview.md
│   │   ├── s01-Workout_Editor_Basics.md
│   │   └── ...
│   └── _originals/
│       └── (backup of articles before style application)
└── run-all-steps-to-generate-articles.py
```

## Configuration

Set these environment variables in `.env`:

- `OPENAI_API_KEY` - For GPT-4o calls
- `ANTHROPIC_API_KEY` - For Claude style application
- `CONTENT_OUTPUT_PATH` - Output directory (default: "output")

## Manual Workflow

If you prefer to run steps individually:

```bash
# Step 1: Query database
python scripts/step1-query-vector-database.py workout-queries

# Step 2: Generate content
python scripts/step2-generate-article-content.py

# Step 3: Add metadata
python scripts/step3-generate-yaml-metadata.py

# Step 4: Apply style
python scripts/step4-apply-style-and-edits.py

# Step 5: Generate overview
python scripts/step5-generate-overview.py
```

## Complete Workflow Overview

### Phase 1: Initial Generation

Run the complete pipeline:

```bash
python run-all-steps-to-generate-articles.py workout-queries
```

This generates articles with:

- Comprehensive content
- YAML metadata
- Alex's writing style applied
- Any previously saved edits applied
- Overview article

### Phase 2: Manual Review and Editing

1. **Review styled articles** in `output/articles-ai/`
2. **Make manual edits** directly to the files
3. **Save your changes**

### Phase 3: Finalize and Track Edits

```bash
python scripts/finalize_edits.py
```

This script:

- Compares your edited versions with _originals
- Extracts edit instructions using GPT-4o
- Saves edits to `article-queries/edits/workout-edits.json`
- Copies final articles to blog system

### Future Regenerations

When you run the generation pipeline again:

- Step 4 will automatically apply your saved edits
- Your manual improvements are preserved
- No need to make the same edits twice

## LLM Usage Summary

- **4 LLM calls per article**:

  1. Content generation (GPT-4o)
  2. YAML metadata (GPT-4o)
  3. Style application (Claude)
  4. Overview generation (GPT-4o)
- **Token estimates**:

  - Content: ~4000 tokens per article
  - Metadata: ~500 tokens per article
  - Style: ~8000 tokens per article
  - Overview: ~2000 tokens total

## Tips

- **Query optimization**: More specific queries yield better results
- **Bad facts**: Review generated articles for incorrect terminology
- **Style consistency**: Claude ensures consistent voice across articles
- **Edit tracking**: Always run finalize_edits.py after manual changes
