# Dokku Deployment Setup for Data Utilities

This document outlines how to deploy subfolders to different Dokku containers from the parent project.

## Current Event Tracker Remotes
The event-tracker subfolder has these existing remotes:

```bash
dokku	dokku@prod.trainerday.com:events-tracker (fetch/push)
dokku2	dokku@uat.trainerday.com:events-tracker (fetch/push)  
origin	https://github.com/trainerday/event-tracker.git (fetch/push)
```

## Setup Instructions for Parent Directory
From `/Users/alex/Documents/Projects/data-utilities` root, add these remotes:

```bash
# Add remotes for event-tracker deployments
git remote add dokku-events-tracker dokku@prod.trainerday.com:events-tracker
git remote add dokku2-events-tracker dokku@uat.trainerday.com:events-tracker

# Add remotes for other services as needed
# git remote add dokku-other-service dokku@prod.trainerday.com:other-service
```

## Deployment Commands
Deploy specific subfolders to their respective containers:

```bash
# Deploy event-tracker to production
git subtree push --prefix=event-tracker dokku-events-tracker master

# Deploy event-tracker to UAT
git subtree push --prefix=event-tracker dokku2-events-tracker master

# Deploy other services (example)
# git subtree push --prefix=other-service dokku-other-service master
```

## Notes
- Each subfolder can be deployed independently to its own Dokku container
- Use meaningful remote names like `dokku-[service-name]` for clarity
- The `--prefix` should match the subfolder path relative to the git root