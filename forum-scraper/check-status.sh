#!/bin/bash

echo "=== Forum Scraper Service Status ==="
echo

# Check if the service is loaded
echo "1. Service Status:"
if launchctl list | grep -q "com.forum-scraper.refresh"; then
    echo "✅ Service is LOADED"
    
    # Get detailed status
    status=$(launchctl list com.forum-scraper.refresh 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "📊 Service Details:"
        echo "$status" | while read line; do
            echo "   $line"
        done
        
        # Check if it's running right now
        pid=$(echo "$status" | grep "PID" | awk '{print $3}')
        if [ "$pid" != "-" ] && [ -n "$pid" ]; then
            echo "🟢 Currently RUNNING (PID: $pid)"
        else
            echo "🟡 Loaded but not currently executing"
        fi
    fi
else
    echo "❌ Service is NOT loaded"
    echo "   Run: launchctl load ~/Library/LaunchAgents/com.forum-scraper.refresh.plist"
fi

echo
echo "2. Recent Activity (last 20 lines):"
if [ -f "logs/refresh.log" ]; then
    echo "📝 Last refresh log entries:"
    tail -20 logs/refresh.log | sed 's/^/   /'
else
    echo "   No log file found (logs/refresh.log)"
fi

echo
echo "3. Recent Errors (last 10 lines):"
if [ -f "logs/refresh-error.log" ]; then
    if [ -s "logs/refresh-error.log" ]; then
        echo "⚠️  Recent errors:"
        tail -10 logs/refresh-error.log | sed 's/^/   /'
    else
        echo "✅ No errors logged"
    fi
else
    echo "   No error log file found"
fi

echo
echo "4. Next Run Time:"
# Calculate next run based on last execution
if [ -f "logs/refresh.log" ]; then
    last_run=$(tail -1 logs/refresh.log | grep -o '\[.*\]' | head -1 | tr -d '[]')
    if [ -n "$last_run" ]; then
        echo "   Last run: $last_run"
        # Note: Calculating exact next run time is complex with launchctl
        echo "   Next run: Within 30 minutes of last run"
    else
        echo "   Cannot determine last run time"
    fi
else
    echo "   No log file to check last run time"
fi

echo
echo "5. Quick Commands:"
echo "   Check logs:     tail -f logs/refresh.log"
echo "   Run manually:   node standalone-refresh.js"
echo "   Stop service:   launchctl stop com.forum-scraper.refresh"
echo "   Restart:        launchctl stop com.forum-scraper.refresh && launchctl start com.forum-scraper.refresh"