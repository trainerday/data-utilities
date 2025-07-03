#!/usr/bin/env python3
"""
Real-time monitoring of Clicky stats.
"""

import sys
sys.path.insert(0, '..')

import time
from datetime import datetime
from clicky_api import ClickyAPIClient, Config


def monitor_real_time(refresh_interval=60):
    """
    Monitor real-time statistics.
    
    Args:
        refresh_interval: Seconds between refreshes
    """
    config = Config()
    client = ClickyAPIClient(config.site_id, config.sitekey)
    
    print(f"Starting real-time monitoring (refreshing every {refresh_interval} seconds)")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            # Clear screen (works on Unix/Linux/Mac)
            print("\033[2J\033[H", end='')
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"=== CLICKY REAL-TIME MONITOR === {timestamp}")
            print("=" * 60)
            
            try:
                # Get current stats
                stats = client.get_multiple_stats(
                    ['visitors', 'actions', 'visitors-online'],
                    date_range='today'
                )
                
                # Parse the response
                if stats and len(stats) > 0:
                    for stat in stats[0]:
                        if isinstance(stat, dict):
                            title = stat.get('title', 'Unknown')
                            value = stat.get('value', 0)
                            print(f"{title}: {value}")
                
                print("\n--- TOP PAGES (Last Hour) ---")
                pages = client.get_pages(date_range='last-hour', limit=5)
                if isinstance(pages, list):
                    for i, page in enumerate(pages[:5], 1):
                        if isinstance(page, dict):
                            title = page.get('title', 'Unknown')[:50]
                            value = page.get('value', 0)
                            print(f"{i}. {title}: {value} views")
                
                print("\n--- RECENT VISITORS ---")
                visitors = client.get_stats(
                    'visitors-list',
                    date_range='last-hour',
                    limit=5
                )
                if isinstance(visitors, list):
                    for visitor in visitors[:5]:
                        if isinstance(visitor, dict):
                            ip = visitor.get('ip_address', 'Unknown')
                            country = visitor.get('country', 'Unknown')
                            time_str = visitor.get('time', 'Unknown')
                            print(f"- {ip} ({country}) at {time_str}")
                
            except Exception as e:
                print(f"Error fetching data: {e}")
            
            # Wait before next refresh
            time.sleep(refresh_interval)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Real-time Clicky stats monitor')
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Refresh interval in seconds (default: 60)'
    )
    
    args = parser.parse_args()
    monitor_real_time(args.interval)