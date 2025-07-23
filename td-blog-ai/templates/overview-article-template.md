# Article Generation Templates

This directory contains templates for generating TrainerDay blog articles.

## Template Files:

### YAML Frontmatter
- **`obsidian-frontmatter-template.yaml`** - YAML structure for Obsidian compatibility (used by both scripts)

### Prompt Templates (What gets sent to Claude 4.0)
- **`individual-article-prompt-template.txt`** - For specific feature/solution articles
- **`overview-article-prompt-template.txt`** - For comprehensive hub articles

### Documentation
- **`overview-article-template.md`** - This documentation file

## How It Works:

1. **Scripts gather data** via vector search across blog/YouTube/forum content
2. **Load prompt template** from appropriate `.txt` file
3. **Populate template** with real content and user questions  
4. **Send to Claude 4.0** to generate educational content
5. **Apply YAML frontmatter** from `obsidian-frontmatter-template.yaml`
6. **Save article** with `status: new-article`

## Article Structure:
Both prompt templates follow educational approach:
- Concept overview and proper usage
- Common confusion points (not temporary bugs)
- Step-by-step workflows
- Best practices and integration tips
- Conceptual understanding

## Editorial Workflow:
- Generated articles: `status: new-article`  
- After your review/editing: `status: edit-complete`

## Key Guidelines:
- No colons (:) in YAML frontmatter values (breaks Obsidian parsing)
- Focus on education and proper usage, not temporary technical issues
- Address conceptual confusion from real user questions
- Maintain evergreen content that won't become outdated