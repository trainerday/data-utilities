# Dokku Deployment Setup for Data Utilities

This document outlines how to deploy the data-utilities project components to different Dokku containers.

## Project Structure
The data-utilities project consists of multiple deployable components:

1. **forum-scraper** - Forum data scraping service

## Current Data Utilities Remotes
The data-utilities project has these deployment remotes:

```bash
# Forum Scraper
forum-scraper    dokku@uat.trainerday.com:forum-scraper (fetch/push)

# Additional remotes to be added as needed:
# reddit-scraper    dokku@uat.trainerday.com:reddit-scraper (fetch/push)
# other-utilities   dokku@uat.trainerday.com:other-utilities (fetch/push)
```

## Setup Instructions for Parent Directory
From `/Users/alex/Documents/Projects/data-utilities` root, add these remotes:

```bash
# Add remotes for data-utilities deployments (note: must use dokku@ user)
git remote add forum-scraper dokku@uat.trainerday.com:forum-scraper

# For production deployment (when ready)
# git remote add forum-scraper-prod dokku@prod.trainerday.com:forum-scraper
```

## Deployment Commands
Deploy specific subfolders to their respective containers:

```bash
# Deploy forum-scraper to UAT
git subtree push --prefix=forum-scraper forum-scraper master

# For production deployment (when ready)
# git subtree push --prefix=forum-scraper forum-scraper-prod master
```

## Service Descriptions

### forum-scraper
- **Technology**: Node.js application for forum data extraction
- **Features**: Forum data scraping, data processing, storage integration
- **Dependencies**: Database connections, external forum APIs
- **Port**: Configurable, typically 3000

## Notes
- Each service can be deployed independently to its own Dokku container
- Services communicate via configured endpoints and database connections
- Environment variables should be configured per service in Dokku
- The `--prefix` should match the subfolder path relative to the git root

## Environment Configuration
Each service will need appropriate environment variables configured in Dokku:

### Required for forum-scraper:
```bash
# Set environment for stage configuration
ssh dokku@uat.trainerday.com config:set forum-scraper APP_ENV=stage
ssh dokku@uat.trainerday.com config:set forum-scraper DATABASE_URL=your_database_url_here
ssh dokku@uat.trainerday.com config:set forum-scraper API_KEY=your_api_key_here
```

## Important Notes
- **Always use `dokku@` user** in remote URLs, not `alex@`
- **Build from git root** - must run subtree push from `/Users/alex/Documents/Projects/data-utilities`
- **Deployment creates the app** - first push will create the Dokku app automatically
- **Check deployment logs** if build fails - most issues are environment related

## Successful Deployment Example
```bash
# From /Users/alex/Documents/Projects/data-utilities
git subtree push --prefix=forum-scraper forum-scraper master

# Result: https://forum-scraper.uat.trainerday.com
```

## Troubleshooting Common Deployment Issues

**1. Package Lock File Issues:**
```
npm ci` can only install packages when your package.json and package-lock.json are in sync
```
- **Solution**: Run `npm install` in forum-scraper directory and commit the updated package-lock.json

**2. Deployment Conflicts:**
If git subtree push fails with "non-fast-forward" error:
```bash
# Use force push with subtree split
git push forum-scraper $(git subtree split --prefix=forum-scraper HEAD):master --force
```

**3. Testing the API:**
- Health check: `curl https://forum-scraper.uat.trainerday.com/health`
- API test: `curl -X GET https://forum-scraper.uat.trainerday.com/api/status`

**4. Checking Logs:**
```bash
ssh dokku@uat.trainerday.com logs forum-scraper --tail
```

## Staging Environment URLs

- **Forum Scraper**: https://forum-scraper.uat.trainerday.com