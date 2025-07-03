#!/usr/bin/env python3
"""
Basic usage example for Clicky API client.
"""

import sys
sys.path.insert(0, '..')

from clicky_api import ClickyAPIClient, Config
from clicky_api.utils.helpers import print_stats_summary, save_to_json, save_to_csv


def main():
    # Load configuration from .env file
    try:
        config = Config()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("\nPlease create a .env file with your Clicky credentials:")
        print("CLICKY_SITE_ID=101125465")
        print("CLICKY_SITEKEY=your_sitekey_here")
        return
    
    # Create API client
    client = ClickyAPIClient(config.site_id, config.sitekey)
    
    print("Fetching today's statistics...")
    
    try:
        # Get today's visitors and actions
        visitors_actions = client.get_multiple_stats(
            ['visitors', 'actions'],
            date_range='today'
        )
        print("\nVisitors and Actions:")
        print(visitors_actions)
        
        # Get top pages
        pages = client.get_pages(date_range='today', limit=10)
        print_stats_summary(pages, "Top Pages")
        
        # Get referrers
        referrers = client.get_referrers(date_range='today', limit=10)
        print_stats_summary(referrers, "Top Referrers")
        
        # Get countries
        countries = client.get_countries(date_range='today', limit=10)
        print_stats_summary(countries, "Top Countries")
        
        # Save some data to files
        if isinstance(pages, list):
            save_to_json(pages, 'output/pages_today.json')
            save_to_csv(pages, 'output/pages_today.csv')
        
    except Exception as e:
        print(f"Error fetching data: {e}")


if __name__ == "__main__":
    main()