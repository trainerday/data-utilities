#!/usr/bin/env python3
"""Test script to check bad facts retrieval"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.google_sheets_client import GoogleSheetsClient

def main():
    print("Testing bad facts retrieval...")
    
    try:
        client = GoogleSheetsClient()
        bad_facts = client.get_bad_facts()
        
        print(f"\nFound {len(bad_facts)} bad facts total")
        print("\nBad facts list:")
        print("-" * 80)
        
        for i, fact_info in enumerate(bad_facts, 1):
            print(f"{i}. [{fact_info['status']}] {fact_info['fact'][:100]}...")
            if "visual workout editor" in fact_info['fact'].lower():
                print("   ⚠️  Contains 'visual workout editor'")
        
        # Check formatted output
        formatted = client.format_bad_facts_for_prompt(bad_facts)
        print("\n\nFormatted bad facts section:")
        print("-" * 80)
        print(formatted)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()