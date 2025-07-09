# PostHog Webhook Setup Instructions

## Setting up the Webhook in PostHog

1. **Log into PostHog** at https://app.posthog.com

2. **Navigate to Data Pipeline**:
   - Click on "Data pipeline" in the left sidebar
   - Click on "Destinations" tab

3. **Create New Webhook**:
   - Click "New destination"
   - Select "Webhook" from the list

4. **Configure the Webhook**:
   - **URL**: `https://posthog-to-r2.av-958.workers.dev`
   - **Method**: POST
   - **Headers**: Add custom header:
     - Key: `X-Webhook-Secret`
     - Value: `cfb92e462c727f6487149c3a7c0337dc24787e904fd438da54fcf665d613f8bd`

5. **Select Events**:
   - Choose which events to send (or select "All events")
   - For testing, you might want to start with specific events like "Pageview" or custom events

6. **Test the Connection**:
   - PostHog will send a test event
   - Check your Cloudflare Worker logs to verify it's receiving data

## Alternative: Using PostHog Apps/Plugins

If you're using PostHog Cloud (not self-hosted), you might need to use the "Apps" feature:

1. Go to "Apps" in the left sidebar
2. Search for "Webhook" or "HTTP"
3. Install and configure with the same URL and headers

## Debugging

### Check if events are being sent:
1. In PostHog, go to "Activity" or "Live events"
2. Verify your events are showing up in PostHog first

### Check Cloudflare Worker logs:
```bash
npx wrangler tail
```

### Test the webhook manually:
```bash
curl -X POST https://posthog-to-r2.av-958.workers.dev \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: cfb92e462c727f6487149c3a7c0337dc24787e904fd438da54fcf665d613f8bd" \
  -d '{"event": "test_webhook", "properties": {"test": true}}'
```

## Note on PostHog Versions

- **PostHog Cloud**: Uses the Data Pipeline → Destinations approach
- **Self-hosted PostHog**: May have different webhook options
- Some features require specific PostHog plans (check your plan limitations)