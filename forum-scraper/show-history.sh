#!/bin/bash

echo "=== Forum Scraper Run History ==="
echo

if [ ! -f "logs/refresh.log" ]; then
    echo "❌ No log file found. Service may not have run yet."
    echo "   Expected location: logs/refresh.log"
    exit 1
fi

echo "📅 Recent Run History:"
echo

# Extract start and completion times with summary
grep -E "(Starting automated scrape|Scrape completed successfully)" logs/refresh.log | \
while IFS= read -r line; do
    timestamp=$(echo "$line" | grep -o '\[.*\]' | tr -d '[]')
    
    if echo "$line" | grep -q "Starting automated scrape"; then
        echo "🚀 Started:  $timestamp"
    elif echo "$line" | grep -q "Scrape completed successfully"; then
        # Extract the summary stats
        posts=$(echo "$line" | grep -o "New posts found: [0-9]*" | grep -o "[0-9]*")
        hot=$(echo "$line" | grep -o "Hot posts found: [0-9]*" | grep -o "[0-9]*")
        comments=$(echo "$line" | grep -o "Comments processed: [0-9]*" | grep -o "[0-9]*")
        
        echo "✅ Finished: $timestamp"
        echo "   📊 Stats: $posts new posts, $hot hot posts, $comments comments processed"
        echo
    fi
done

echo
echo "📈 Summary Statistics:"

# Count total runs
total_runs=$(grep -c "Starting automated scrape" logs/refresh.log)
echo "   Total runs: $total_runs"

# Last run time
last_run=$(grep "Starting automated scrape" logs/refresh.log | tail -1 | grep -o '\[.*\]' | tr -d '[]')
if [ -n "$last_run" ]; then
    echo "   Last run: $last_run"
    
    # Calculate time since last run
    last_timestamp=$(date -j -f "%Y-%m-%dT%H:%M:%S" "${last_run%.*}" "+%s" 2>/dev/null)
    current_timestamp=$(date "+%s")
    
    if [ -n "$last_timestamp" ]; then
        diff_minutes=$(( (current_timestamp - last_timestamp) / 60 ))
        echo "   Time since last run: ${diff_minutes} minutes ago"
        
        # Next run estimation (every 30 minutes)
        next_run_minutes=$(( 30 - (diff_minutes % 30) ))
        echo "   Estimated next run: in ${next_run_minutes} minutes"
    fi
fi

# Count errors
error_count=$(grep -c "ERROR" logs/refresh.log)
echo "   Total errors logged: $error_count"

# Recent activity summary
echo
echo "🔍 Quick Status Check:"

# Check if service is loaded
if launchctl list | grep -q "com.forum-scraper.refresh"; then
    echo "   ✅ Service is loaded and scheduled"
else
    echo "   ❌ Service is NOT loaded"
fi

# Check recent errors
if [ -f "logs/refresh-error.log" ] && [ -s "logs/refresh-error.log" ]; then
    recent_errors=$(tail -5 logs/refresh-error.log | wc -l)
    echo "   ⚠️  Recent errors in error log: $recent_errors"
else
    echo "   ✅ No recent errors"
fi

echo
echo "💡 Useful commands:"
echo "   Real-time logs:     tail -f logs/refresh.log"
echo "   Run manually:       node standalone-refresh.js"
echo "   Check service:      launchctl list com.forum-scraper.refresh"