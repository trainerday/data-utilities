# TrainerDay Project Management with Basic Memory & GitHub Integration

This directory contains scripts for managing the TrainerDay project's Basic Memory structure and GitHub integration.

## Overview

The TrainerDay project uses Basic Memory for documentation and specs, with automatic GitHub issue creation and link management. This folder contains tools to maintain consistency between Basic Memory permalinks and GitHub repository links.

## Key Components

### Project Structure
- **Basic Memory Project**: `TrainerDay` (switched with `mcp__basic-memory__switch_project TrainerDay`)
- **Root Folder**: `product-development/` (renamed from `trainer-day/` to avoid naming confusion)
- **GitHub Organization**: `trainerday`
- **Main Repositories**: 
  - `Development-Process` (contains specs and documentation)
  - `main-app-web` (web application)
  - `mobile-app-rn` (mobile application)

### Automated Scripts

1. **fix_title_filename_consistency.py** - Ensures titles match filenames and permalinks are correct
2. **fix_trainer_day_to_product_development.py** - Handles folder rename operations
3. **fix_github_issue_links.py** - Updates GitHub issue links after permalink changes

## Workflow: Creating GitHub Issues from Basic Memory Specs

### Step 1: Create GitHub Issue from Spec
```bash
# 1. Read the spec from Basic Memory
mcp__basic-memory__read_note <spec-permalink>

# 2. Create GitHub issue with proper assignment
gh issue create --repo trainerday/<repository> \
  --title "<descriptive title>" \
  --assignee <username> \
  --body "<description with link to spec>"

# 3. Add issue to project board
gh project item-add 1 --owner trainerday --url <issue-url>

# 4. Update the spec with GitHub issue reference
mcp__basic-memory__edit_note <spec-permalink> --operation prepend \
  --content "**GitHub Issue:** [#<number> - <title>](<issue-url>)"
```

### Step 2: Verify Links Work
Always test that the GitHub issue links to the correct spec file in the Development-Process repository.

## Workflow: Maintaining Project Consistency

### When Making Structural Changes

1. **Run Consistency Checks**
   ```bash
   cd /Users/alex/Documents/Projects/data-utilities/basic-memory-functions/script-testing
   python fix_title_filename_consistency.py
   ```

2. **Apply Fixes if Needed**
   ```bash
   python fix_title_filename_consistency.py --apply
   ```

3. **Push Changes to GitHub**
   ```bash
   # From the TrainerDay Basic Memory project directory
   git add .
   git commit -m "Fix permalink and title consistency"
   git push
   ```

4. **Check for Broken GitHub Links**
   ```bash
   gh project item-list 1 --owner trainerday --format json
   # Review any links that reference Development-Process repository
   ```

5. **Fix Any Broken Links**
   Use the appropriate fix script or manually update GitHub issues with broken links.

## Workflow: Major Folder Restructuring

### When Renaming Root Folders or Major Reorganization

1. **Create Specific Fix Script**
   - Model after `fix_trainer_day_to_product_development.py`
   - Handle both permalink updates and reference fixes

2. **Test with Dry Run**
   ```bash
   python <fix-script>.py
   ```

3. **Apply Changes**
   ```bash
   python <fix-script>.py --apply
   ```

4. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Restructure: <description of changes>"
   git push
   ```

5. **Scan and Fix GitHub Links**
   ```bash
   # Check project board for broken links
   gh project item-list 1 --owner trainerday --format json
   
   # Fix any broken issue links
   gh issue edit <issue-number> --repo <repository> --body "<updated-body>"
   ```

## Best Practices

### File Naming Convention
- **Files**: Use kebab-case (e.g., `cj-update-questions-interface-spec.md`)
- **Titles**: Match filename with proper capitalization (e.g., "CJ Update Questions Interface - Spec")
- **Permalinks**: Auto-generate from file path structure

### GitHub Issue Creation
- Always include link to the full specification
- Assign to appropriate team member
- Add to the main TrainerDay project board
- Include brief description and key requirements
- Link back to the GitHub issue in the Basic Memory spec

### Preventing Link Breakage
- Run consistency checks before major changes
- Test GitHub links after pushing changes
- Keep naming conventions consistent
- Use the automated scripts for bulk operations

## Common Commands

### Basic Memory Operations
```bash
# Switch to TrainerDay project
mcp__basic-memory__switch_project TrainerDay

# List directory contents
mcp__basic-memory__list_directory <path>

# Read a spec
mcp__basic-memory__read_note <permalink>

# Edit a spec
mcp__basic-memory__edit_note <permalink> --operation <operation> --content "<content>"
```

### GitHub Operations
```bash
# List project board items
gh project item-list 1 --owner trainerday

# Create issue
gh issue create --repo trainerday/<repo> --title "<title>" --assignee <user> --body "<body>"

# Add to project board
gh project item-add 1 --owner trainerday --url <issue-url>

# Edit existing issue
gh issue edit <number> --repo trainerday/<repo> --body "<new-body>"
```

### Maintenance Operations
```bash
# Check for broken links after changes
gh search issues --owner trainerday --match body "<old-path>"

# Run consistency fixes
python fix_title_filename_consistency.py --apply

# Fix specific folder renames
python fix_<specific-rename>.py --apply
```

## Emergency Recovery

If major link breakage occurs:

1. **Identify the scope** - Use GitHub search to find affected issues
2. **Create a fix script** - Model after existing scripts in this directory
3. **Test thoroughly** - Always run dry runs first
4. **Apply systematically** - Fix Basic Memory first, then GitHub links
5. **Verify completeness** - Check project board and test random links

## File Locations

- **Scripts**: `/Users/alex/Documents/Projects/data-utilities/basic-memory-functions/script-testing/`
- **Basic Memory Project**: Switch to TrainerDay project in Basic Memory
- **GitHub Project Board**: https://github.com/orgs/trainerday/projects/1

## Notes

- All scripts include dry-run functionality for safety
- Summary JSON files are generated for each major operation
- The TrainerDay Basic Memory project must be active when running operations
- Always test GitHub links after making permalink changes
- Keep this documentation updated as workflows evolve