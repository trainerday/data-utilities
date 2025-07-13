put all test files with in the directory you are working in a script-testing folder and remember to ask me to put the final ones in the root of this individual folder/sub-project

## Project Structure

### Event Utilities
The `event-utilities/` folder contains the consolidated event tracking and email service functionality:
- **Event Tracking**: Handles webhooks, data warehousing, and integrations with Mautic/Telegram
- **Email Service**: Processes email-related webhooks and subscription events
- **Scripts**: Database migration and connection utilities
- **Testing**: All test files are located in `script-testing/` subfolder

### Manage Users
The `manage-users/` folder contains user management utilities with BigMailer integration.

## Deployment Instructions

### Event Utilities Dokku Deployment

To deploy the event-utilities subfolder to Dokku servers, use git subtree:

```bash
# Deploy to production
git subtree push --prefix=event-utilities dokku-events-tracker master

# Deploy to UAT
git subtree push --prefix=event-utilities dokku2-events-tracker master
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
- **Solution**: Run `npm install` in event-utilities directory and commit the updated package-lock.json

**4. Deployment Conflicts:**
If git subtree push fails with "non-fast-forward" error:
```bash
# Use force push with subtree split
git push dokku2-events-tracker $(git subtree split --prefix=event-utilities HEAD):master --force
git push dokku-events-tracker $(git subtree split --prefix=event-utilities HEAD):master --force
```

**5. Testing the API:**
- Health check: `curl https://events-tracker.uat.trainerday.com/health`
- Webhook test: `curl -X POST https://events-tracker.uat.trainerday.com/webhook -H "Content-Type: application/json" -d '{"userId":123,"name":"test","value":"test"}'`
- Email webhook test: `curl -X POST "https://events-tracker.uat.trainerday.com/email-webhook?type=subscription-active&userid=123&username=testuser&email=test@example.com&membership=premium&old_status=free" -H "Content-Type: application/json" -d '{"test":"data"}'`

**6. Checking Logs:**
```bash
dokku logs events-tracker --tail
```
