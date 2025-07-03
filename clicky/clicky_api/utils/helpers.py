from datetime import datetime, timedelta
from typing import List, Dict, Any
import csv
import json


def format_date_range(days_back: int) -> str:
    """
    Format a date range string for the API.
    
    Args:
        days_back: Number of days to go back
        
    Returns:
        Formatted date range string
    """
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days_back)
    return f"{start_date},{end_date}"


def save_to_csv(data: List[Dict[str, Any]], filename: str, fieldnames: List[str] = None):
    """
    Save data to CSV file.
    
    Args:
        data: List of dictionaries to save
        filename: Output filename
        fieldnames: List of field names (auto-detected if not provided)
    """
    if not data:
        print(f"No data to save to {filename}")
        return
    
    if not fieldnames:
        fieldnames = list(data[0].keys())
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"Data saved to {filename}")


def save_to_json(data: Any, filename: str, indent: int = 2):
    """
    Save data to JSON file.
    
    Args:
        data: Data to save
        filename: Output filename
        indent: JSON indentation level
    """
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=indent, ensure_ascii=False)
    
    print(f"Data saved to {filename}")


def flatten_stats(stats_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Flatten nested statistics data for easier processing.
    
    Args:
        stats_data: Raw statistics data from API
        
    Returns:
        Flattened list of statistics
    """
    flattened = []
    
    for date_key, date_data in stats_data.items():
        if isinstance(date_data, list):
            for item in date_data:
                if isinstance(item, dict):
                    item['date'] = date_key
                    flattened.append(item)
        elif isinstance(date_data, dict):
            for stat_type, stat_data in date_data.items():
                if isinstance(stat_data, list):
                    for item in stat_data:
                        if isinstance(item, dict):
                            item['date'] = date_key
                            item['type'] = stat_type
                            flattened.append(item)
    
    return flattened


def print_stats_summary(stats: Dict[str, Any], stat_type: str):
    """
    Print a formatted summary of statistics.
    
    Args:
        stats: Statistics data
        stat_type: Type of statistics being displayed
    """
    print(f"\n=== {stat_type.upper()} STATISTICS ===")
    
    if isinstance(stats, list):
        for item in stats[:10]:  # Show top 10
            if isinstance(item, dict):
                title = item.get('title', 'N/A')
                value = item.get('value', 0)
                value_percent = item.get('value_percent', 0)
                print(f"{title}: {value} ({value_percent}%)")
    elif isinstance(stats, dict):
        for key, value in stats.items():
            if isinstance(value, list) and value:
                print(f"\n{key}:")
                for item in value[:5]:  # Show top 5 per category
                    if isinstance(item, dict):
                        title = item.get('title', 'N/A')
                        val = item.get('value', 0)
                        print(f"  - {title}: {val}")
            else:
                print(f"{key}: {value}")