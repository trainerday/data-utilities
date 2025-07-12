# Dokku Deployment Options

This document outlines different approaches for deploying just a subfolder of a larger project to Dokku.

## Multiple Subfolders to Different Containers

Set up different git remotes for each subfolder you want to deploy:

```bash
# From your main project root, add remotes for each service
git remote add dokku-events-tracker dokku@prod.trainerday.com:events-tracker
git remote add dokku-mautic-api dokku@prod.trainerday.com:mautic-api
git remote add dokku-other-service dokku@prod.trainerday.com:other-service

# Deploy specific subfolders to their respective containers
git subtree push --prefix=data-utilities/event-tracker dokku-events-tracker master
git subtree push --prefix=data-utilities/mautic-api dokku-mautic-api master
git subtree push --prefix=data-utilities/other-service dokku-other-service master
```

## Option 1: Git Subtree (Recommended for Multi-Service)
Push only the event-tracker folder as a separate branch:

```bash
# From your main project root
git subtree push --prefix=data-utilities/event-tracker dokku-events-tracker master
```

## Option 2: Dokku dockerfile with BUILD_DIR
Create a `.dokku/config` file in your repo root:
```
BUILD_DIR=data-utilities/event-tracker
```

## Option 3: Pre-build Hook Script
Create `.dokku/pre-build` in repo root:
```bash
#!/bin/bash
cd data-utilities/event-tracker
# Copy files to build root or set working directory
```

## Option 4: Separate Git Remote
Make the event-tracker folder its own git repository:
```bash
cd data-utilities/event-tracker
git init
git remote add dokku dokku@prod.trainerday.com:events-tracker
git push dokku master
```

## Current Setup - Event Tracker Remotes
The event-tracker directory has these existing remotes:

```bash
dokku	dokku@prod.trainerday.com:events-tracker (fetch/push)
dokku2	dokku@uat.trainerday.com:events-tracker (fetch/push)  
origin	https://github.com/trainerday/event-tracker.git (fetch/push)
```

## Instructions for Higher Root Setup
To set up subtree deployment from the parent directory (`/Users/alex/Documents/Projects/data-utilities`), add these remotes:

```bash
# From /Users/alex/Documents/Projects/data-utilities root
git remote add dokku-events-tracker dokku@prod.trainerday.com:events-tracker
git remote add dokku2-events-tracker dokku@uat.trainerday.com:events-tracker

# Then deploy with:
git subtree push --prefix=event-tracker dokku-events-tracker master
git subtree push --prefix=event-tracker dokku2-events-tracker master
```

Since the event-tracker directory already has its own git repository, **Option 4** is the simplest approach - you can push directly from this folder to dokku without needing to deploy the entire parent project.