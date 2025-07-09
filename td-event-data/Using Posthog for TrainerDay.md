# Using PostHog for TrainerDay

## Overview
This setup captures PostHog events and stores them in Cloudflare R2 storage for analysis.

## Endpoints

### Production Worker URL
```
https://posthog-to-r2.av-958.workers.dev
```

### Authentication
**Webhook Secret**: `cfb92e462c727f6487149c3a7c0337dc24787e904fd438da54fcf665d613f8bd`

Include in header: `X-Webhook-Secret: cfb92e462c727f6487149c3a7c0337dc24787e904fd438da54fcf665d613f8bd`

## Sending Events

### Minimal Event Structure
When using PostHog SDK, you only need to send:
```javascript
posthog.capture('user_signed_up', {
  user_id: '12345',
  plan_type: 'premium',
  source: 'mobile_app'
})
```

PostHog automatically adds:
- `distinct_id` - User identifier
- `$device_id` - Device UUID
- `$os` - Operating system
- `$browser` - Browser info
- `$current_url` - Current page
- `$host` - Domain
- `$pathname` - Page path
- `$screen_height`/`$screen_width` - Screen dimensions
- `$lib` - Library name
- `$lib_version` - Library version
- Timestamps and other metadata

### Direct API Call Example
```bash
curl -X POST https://posthog-to-r2.av-958.workers.dev \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: cfb92e462c727f6487149c3a7c0337dc24787e904fd438da54fcf665d613f8bd" \
  -d '{
    "event": "workout_completed",
    "properties": {
      "workout_type": "cycling",
      "duration_minutes": 45,
      "distance_km": 25.5,
      "avg_power_watts": 185
    }
  }'
```

## PostHog Configuration

### Setting up PostHog Webhook
1. Go to PostHog → Settings → Webhooks
2. Create new webhook with:
   - URL: `https://posthog-to-r2.av-958.workers.dev`
   - Add custom header: `X-Webhook-Secret` = `cfb92e462c727f6487149c3a7c0337dc24787e904fd438da54fcf665d613f8bd`
   - Select events to forward

### PostHog Project Token (for SDK)
Your PostHog project token: `phc_pXPWqFoZfzwVuEtCx5uZ76QfpfXJcWYNlqrXits9JHP`

## Data Storage
Events are stored in R2 at:
```
posthog-events/YYYY-MM-DD/timestamp-uuid.json
```

## TrainerDay Specific Events
Recommended event names:
- `workout_started`
- `workout_completed`
- `workout_paused`
- `plan_created`
- `plan_updated`
- `user_signed_up`
- `subscription_started`
- `subscription_cancelled`

## Testing
Use the included `test-posthog.html` file to test PostHog integration locally.