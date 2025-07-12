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

### Troubleshooting Common Deployment Issues

**1. SSL Certificate Error:**
```
Error: ENOENT: no such file or directory, open '/app/ca-certificate.crt'
```
- **Solution**: The certificate file is excluded by `.gitignore` for security
- The code now handles missing certificates gracefully with environment variable fallback

**2. AWS Credentials Error:**
```
Error [CredentialsError]: Missing credentials in config
```
- **Solution**: Set AWS environment variables on the Dokku server:
```bash
dokku config:set events-tracker AWS_ACCESS_KEY_ID=your_key_here
dokku config:set events-tracker AWS_SECRET_ACCESS_KEY=your_secret_here
dokku config:set events-tracker AWS_REGION=us-east-1
```
- **Check config**: `dokku config:show events-tracker`
- **Restart after setting**: `dokku ps:restart events-tracker`

**3. Package Lock File Issues:**
```
npm ci` can only install packages when your package.json and package-lock.json are in sync
```
- **Solution**: Run `npm install` in event-tracker directory and commit the updated package-lock.json

**4. Testing the API:**
- Health check: `curl https://events-tracker.uat.trainerday.com/health`
- Webhook test: `curl -X POST https://events-tracker.uat.trainerday.com/webhook -H "Content-Type: application/json" -d '{"userId":123,"name":"test","value":"test"}'`

**5. Checking Logs:**
```bash
dokku logs events-tracker --tail
```
