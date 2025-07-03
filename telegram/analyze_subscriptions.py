#!/usr/bin/env python3
import os
import re
from datetime import datetime
from collections import defaultdict
from bs4 import BeautifulSoup
import json

def parse_subscription_data(html_content):
    """Extract subscription data from HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    subscriptions = []
    
    # Find all message divs
    messages = soup.find_all('div', class_='message')
    
    for message in messages:
        # Get date
        date_elem = message.find('div', class_='date')
        if not date_elem:
            continue
            
        date_str = date_elem.get('title', '')
        if not date_str:
            continue
            
        # Parse date
        try:
            # Format: "01.01.2021 12:00:00 UTC+01:00"
            date_part = date_str.split(' UTC')[0]
            dt = datetime.strptime(date_part, '%d.%m.%Y %H:%M:%S')
        except:
            continue
            
        # Get message text
        text_elem = message.find('div', class_='text')
        if not text_elem:
            continue
            
        text = text_elem.get_text(strip=True)
        
        # Parse subscription info
        # Pattern: "username: status->active (subscription_type) user_id"
        pattern = r'([^:]+):\s*(\w+)->active\s*\(([^)]+)\)\s*(\d+)'
        match = re.search(pattern, text)
        
        if match:
            username = match.group(1).strip()
            previous_status = match.group(2).strip()
            subscription_type = match.group(3).strip()
            user_id = match.group(4).strip()
            
            subscriptions.append({
                'date': dt,
                'month_year': dt.strftime('%Y-%m'),
                'username': username,
                'previous_status': previous_status,
                'subscription_type': subscription_type,
                'user_id': user_id
            })
    
    return subscriptions

def analyze_subscriptions():
    """Analyze all HTML files and generate statistics."""
    all_subscriptions = []
    
    # Get all HTML files
    html_files = []
    for file in os.listdir('.'):
        if file.startswith('messages') and file.endswith('.html'):
            html_files.append(file)
    
    html_files.sort(key=lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 0)
    
    print(f"Found {len(html_files)} HTML files to process...")
    
    # Process each file
    for file in html_files:
        print(f"Processing {file}...")
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            subscriptions = parse_subscription_data(content)
            all_subscriptions.extend(subscriptions)
    
    print(f"\nTotal subscriptions found: {len(all_subscriptions)}")
    
    # Group by month and subscription type
    monthly_stats = defaultdict(lambda: defaultdict(int))
    
    for sub in all_subscriptions:
        month_year = sub['month_year']
        sub_type = sub['subscription_type']
        monthly_stats[month_year][sub_type] += 1
    
    # Sort months chronologically
    sorted_months = sorted(monthly_stats.keys())
    
    # Generate report
    print("\n" + "="*80)
    print("MONTHLY SUBSCRIPTION STATISTICS BY TYPE")
    print("="*80)
    
    # Collect all subscription types
    all_types = set()
    for month_data in monthly_stats.values():
        all_types.update(month_data.keys())
    
    # Sort subscription types by total count
    type_totals = defaultdict(int)
    for month_data in monthly_stats.values():
        for sub_type, count in month_data.items():
            type_totals[sub_type] += count
    
    sorted_types = sorted(all_types, key=lambda x: type_totals[x], reverse=True)
    
    # Print monthly breakdown
    for month in sorted_months:
        month_dt = datetime.strptime(month, '%Y-%m')
        print(f"\n{month_dt.strftime('%B %Y')}:")
        print("-" * 40)
        
        month_data = monthly_stats[month]
        month_total = sum(month_data.values())
        
        for sub_type in sorted_types:
            if sub_type in month_data:
                count = month_data[sub_type]
                percentage = (count / month_total) * 100
                print(f"  {sub_type:<30} {count:>4} ({percentage:>5.1f}%)")
        
        print(f"  {'TOTAL':<30} {month_total:>4}")
    
    # Print summary statistics
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    
    print("\nTotal Activations by Subscription Type:")
    print("-" * 40)
    
    grand_total = sum(type_totals.values())
    for sub_type in sorted_types:
        count = type_totals[sub_type]
        percentage = (count / grand_total) * 100
        print(f"  {sub_type:<30} {count:>5} ({percentage:>5.1f}%)")
    
    print(f"  {'GRAND TOTAL':<30} {grand_total:>5}")
    
    # Save to JSON for further analysis
    output_data = {
        'monthly_stats': {month: dict(data) for month, data in monthly_stats.items()},
        'type_totals': dict(type_totals),
        'total_activations': grand_total,
        'date_range': {
            'start': sorted_months[0] if sorted_months else None,
            'end': sorted_months[-1] if sorted_months else None
        }
    }
    
    with open('subscription_stats.json', 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nDetailed statistics saved to subscription_stats.json")

if __name__ == "__main__":
    analyze_subscriptions()