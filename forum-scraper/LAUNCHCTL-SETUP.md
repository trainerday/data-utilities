# Forum Scraper Automated Refresh Setup

This guide shows how to set up automated forum scraping that runs every 30 minutes using macOS launchctl.

## Files Created

1. **`standalone-refresh.js`** - Standalone Node.js script that performs the forum scraping without needing the web server
2. **`com.forum-scraper.refresh.plist`** - LaunchAgent configuration file for macOS
3. **`logs/`** - Directory for log files

## Installation Steps

### 1. Copy the plist file to LaunchAgents directory

```bash
cp com.forum-scraper.refresh.plist ~/Library/LaunchAgents/
```

### 2. Load the launch agent

```bash
launchctl load ~/Library/LaunchAgents/com.forum-scraper.refresh.plist
```

### 3. Start the service immediately (optional)

```bash
launchctl start com.forum-scraper.refresh
```

## How It Works

- **Frequency**: Runs every 30 minutes (1800 seconds)
- **Auto-start**: Yes, automatically starts when you turn on your computer (`RunAtLoad: true`)
- **What it does**: 
  - Fetches new posts from r/cycling, r/Velo, and TrainerRoad forum
  - Fetches comments for posts that are 1+ hours old
  - Prioritizes "hot" posts (15+ comments, recent) for early comment fetching
  - Logs all activity to `logs/refresh.log` and `logs/refresh-error.log`

## Management Commands

### Check if the service is loaded and running
```bash
launchctl list | grep forum-scraper
```

### View recent logs
```bash
tail -f logs/refresh.log
tail -f logs/refresh-error.log
```

### Stop the service
```bash
launchctl stop com.forum-scraper.refresh
```

### Unload the service (disable)
```bash
launchctl unload ~/Library/LaunchAgents/com.forum-scraper.refresh.plist
```

### Reload after making changes
```bash
launchctl unload ~/Library/LaunchAgents/com.forum-scraper.refresh.plist
cp com.forum-scraper.refresh.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.forum-scraper.refresh.plist
```

## Manual Testing

You can test the script manually anytime:

```bash
node standalone-refresh.js
```

## Configuration Details

- **Label**: `com.forum-scraper.refresh`
- **Interval**: 1800 seconds (30 minutes)
- **Working Directory**: `/Users/alex/Documents/Projects/data-utilities/forum-scraper`
- **Logs**: 
  - Standard output: `logs/refresh.log`
  - Errors: `logs/refresh-error.log`

## Important Notes

1. **Database connection**: The script uses the `.env` file in the forum-scraper directory for database credentials
2. **No web server required**: This runs completely independently of the web interface
3. **Error handling**: Failed requests (like 404s for deleted Reddit posts) are logged but don't stop the process
4. **Rate limiting**: Built-in delays between requests to be respectful to Reddit and TrainerRoad APIs

## Troubleshooting

If the service isn't working:

1. Check if it's loaded: `launchctl list | grep forum-scraper`
2. Check the error logs: `cat logs/refresh-error.log`
3. Test manually: `node standalone-refresh.js`
4. Verify Node.js path: `which node` (should match the path in the plist file)
5. Check file permissions: `ls -la standalone-refresh.js`