#!/usr/bin/env python3
"""
Generate a weekly report using Clicky API.
"""

import sys
sys.path.insert(0, '..')

from datetime import datetime, timedelta
from clicky_api import ClickyAPIClient, Config
from clicky_api.utils.helpers import save_to_json, save_to_csv, format_date_range
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def generate_weekly_report():
    # Load configuration
    config = Config()
    client = ClickyAPIClient(config.site_id, config.sitekey)
    
    print("Generating weekly report...")
    
    # Get last 7 days of data
    stats = client.get_multiple_stats(
        ['visitors', 'actions', 'bounce_rate', 'time_average'],
        date_range='last-7-days'
    )
    
    # Get detailed daily stats
    daily_stats = []
    for i in range(7):
        date = datetime.now().date() - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        
        day_stats = client.get_multiple_stats(
            ['visitors', 'actions'],
            date_range=date_str
        )
        
        daily_stats.append({
            'date': date_str,
            'visitors': day_stats[0][0]['value'] if day_stats else 0,
            'actions': day_stats[0][1]['value'] if day_stats else 0
        })
    
    # Save raw data
    save_to_json(daily_stats, 'output/weekly_stats.json')
    save_to_csv(daily_stats, 'output/weekly_stats.csv')
    
    # Create visualizations
    df = pd.DataFrame(daily_stats)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Plot visitors and actions
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Visitors plot
    ax1.plot(df['date'], df['visitors'], marker='o', linewidth=2)
    ax1.set_title('Daily Visitors - Last 7 Days')
    ax1.set_ylabel('Visitors')
    ax1.grid(True, alpha=0.3)
    
    # Actions plot
    ax2.plot(df['date'], df['actions'], marker='o', linewidth=2, color='orange')
    ax2.set_title('Daily Actions - Last 7 Days')
    ax2.set_ylabel('Actions')
    ax2.set_xlabel('Date')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('output/weekly_trends.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Get top content for the week
    pages = client.get_pages(date_range='last-7-days', limit=20)
    referrers = client.get_referrers(date_range='last-7-days', limit=20)
    searches = client.get_searches(date_range='last-7-days', limit=20)
    
    # Save top content
    if isinstance(pages, list):
        save_to_csv(pages, 'output/top_pages_weekly.csv')
    if isinstance(referrers, list):
        save_to_csv(referrers, 'output/top_referrers_weekly.csv')
    if isinstance(searches, list):
        save_to_csv(searches, 'output/top_searches_weekly.csv')
    
    print("\nWeekly report generated!")
    print("Files created:")
    print("- output/weekly_stats.json")
    print("- output/weekly_stats.csv")
    print("- output/weekly_trends.png")
    print("- output/top_pages_weekly.csv")
    print("- output/top_referrers_weekly.csv")
    print("- output/top_searches_weekly.csv")


if __name__ == "__main__":
    # Create output directory
    import os
    os.makedirs('output', exist_ok=True)
    
    generate_weekly_report()