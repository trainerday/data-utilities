put all test files with in the directory you are working in a script-testing folder and remember to ask me to put the final ones in the root of this individual folder/sub-project

## Deployment Instructions

### Event Tracker Dokku Deployment

To deploy the event-tracker subfolder to Dokku servers, use git subtree:

```bash
# Deploy to production
git subtree push --prefix=event-tracker dokku-events-tracker master

# Deploy to UAT
git subtree push --prefix=event-tracker dokku2-events-tracker master
```

Remotes are already configured:
- `dokku-events-tracker`: dokku@prod.trainerday.com:events-tracker (production)
- `dokku2-events-tracker`: dokku@uat.trainerday.com:events-tracker (UAT)
