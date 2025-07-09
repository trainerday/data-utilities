# Direct Event Tracking (Without PostHog)

## Overview
This solution sends events directly to your Cloudflare Worker, which stores them in R2. No PostHog account or integration needed.

## Files Created

### 1. `trainerday-tracker.js`
A lightweight JavaScript library that:
- Sends events directly to your Cloudflare Worker
- Automatically enriches events with device/browser info
- Manages user identification and sessions
- Handles device IDs persistently

### 2. `test-direct-tracking.html`
Test page to verify everything works

## Usage

### Basic Setup
```html
<script src="trainerday-tracker.js"></script>
<script>
  const tracker = new TrainerDayTracker({
    endpoint: 'https://posthog-to-r2.av-958.workers.dev',
    webhookSecret: 'cfb92e462c727f6487149c3a7c0337dc24787e904fd438da54fcf665d613f8bd',
    capturePageview: true
  });
</script>
```

### Identify Users
```javascript
tracker.identify('user123', {
  email: 'user@example.com',
  name: 'John Doe',
  plan: 'premium'
});
```

### Track Events
```javascript
// Simple event
tracker.capture('workout_started');

// Event with properties
tracker.capture('workout_completed', {
  duration_minutes: 45,
  distance_km: 25.5,
  avg_power_watts: 185
});
```

## Data Automatically Collected
- Device ID (persistent)
- Session ID
- Screen dimensions
- Browser and OS
- Page URL and title
- Timestamp
- User agent

## Benefits Over PostHog
- No third-party dependencies
- Data goes directly to your R2 storage
- Full control over data collection
- No usage limits or pricing tiers
- Simpler setup

## Testing
1. Open `test-direct-tracking.html` in your browser
2. Enable console debugging to see events
3. Click buttons to send test events
4. Check R2 bucket for stored data

## Viewing Stored Data
```bash
export CLOUDFLARE_API_TOKEN="GpsaJK5hiDA2z51Lrn0VIzzi8gfumkTLPVGqWgCq"
npx wrangler r2 object get posthog-events/[date]/[filename] --pipe
```