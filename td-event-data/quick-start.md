# Quick Start Guide

## 1. Test the HTML Page Locally
1. Open `test-posthog.html` in your browser
2. The page is configured with your PostHog project token: `phc_pXPWqFoZfzwVuEtCx5uZ76QfpfXJcWYNlqrXits9JHP`
3. Click the event buttons to send test events

## 2. What PostHog Adds Automatically
When you send a simple event like:
```javascript
posthog.capture('workout_completed', {
  duration_minutes: 45
})
```

PostHog automatically adds:
- User/device identifiers
- Browser and OS information
- Screen dimensions
- Geographic data (city, country)
- Timestamp
- Session information
- And much more

## 3. Connect PostHog to Your Worker
1. Log into PostHog (https://app.posthog.com)
2. Go to Settings → Webhooks
3. Create new webhook:
   - URL: `https://posthog-to-r2.av-958.workers.dev`
   - Add header: `X-Webhook-Secret` = `cfb92e462c727f6487149c3a7c0337dc24787e904fd438da54fcf665d613f8bd`
   - Select which events to forward (or all events)

## 4. View Your Data
Check R2 bucket for stored events:
```bash
export CLOUDFLARE_API_TOKEN="GpsaJK5hiDA2z51Lrn0VIzzi8gfumkTLPVGqWgCq"
npx wrangler r2 object get posthog-events/[path-to-file] --pipe
```

## 5. Direct API Testing
Test without PostHog:
```bash
curl -X POST https://posthog-to-r2.av-958.workers.dev \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: cfb92e462c727f6487149c3a7c0337dc24787e904fd438da54fcf665d613f8bd" \
  -d '{"event": "test", "properties": {"source": "direct"}}'
```