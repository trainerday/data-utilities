#!/usr/bin/env python3
"""
Export Facts to CSV for Google Sheets Import

Creates a CSV file with all facts from database that can be imported into Google Sheets.
Includes the proper structure for status management.
"""

import os
import sys
import csv
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from utils.db_connection import get_db_connection

def export_facts_to_csv():
    """Export all facts to CSV file"""
    
    print("🎯 EXPORTING FACTS TO CSV")
    print("=" * 40)
    
    # Get facts from database
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
            SELECT 
                id,
                fact_text,
                source_article,
                created_at
            FROM facts 
            ORDER BY id
            """
            
            cursor.execute(query)
            facts = cursor.fetchall()
        
        conn.close()
        
        print(f"✅ Retrieved {len(facts)} facts from database")
        
    except Exception as e:
        print(f"❌ Error retrieving facts: {e}")
        return None
    
    if not facts:
        print("⚠️  No facts found in database")
        return None
    
    # Create CSV file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = Path(__file__).parent / f'td-blog-facts_{timestamp}.csv'
    
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write headers (matching Google Sheets structure)
            headers = [
                'fact_id',
                'status',
                'original_fact',
                'replacement_text', 
                'notes',
                'source_article',
                'created_at'
            ]
            writer.writerow(headers)
            
            # Write data rows
            for fact in facts:
                row = [
                    fact['id'],                                       # fact_id
                    '',                                              # status (blank default)
                    fact['fact_text'],                               # original_fact
                    '',                                              # replacement_text (empty)
                    '',                                              # notes (empty)
                    fact['source_article'],                          # source_article
                    fact['created_at'].strftime('%Y-%m-%d %H:%M:%S') # created_at
                ]
                writer.writerow(row)
        
        print(f"✅ Exported {len(facts)} facts to CSV")
        print(f"📄 File: {csv_file}")
        
        # Show sample of data
        print(f"\n🔍 Sample of exported data:")
        print(f"Headers: {', '.join(headers)}")
        
        for i, fact in enumerate(facts[:3], 1):
            preview = fact['fact_text'][:50] + '...' if len(fact['fact_text']) > 50 else fact['fact_text']
            print(f"{i:2d}. ID:{fact['id']:3d} | {preview} | {fact['source_article']}")
        
        if len(facts) > 3:
            print(f"    ... and {len(facts) - 3} more facts")
        
        print(f"\n📋 MANUAL IMPORT INSTRUCTIONS:")
        print(f"=" * 40)
        print(f"1. Go to https://sheets.google.com")
        print(f"2. Create a new spreadsheet called 'td-blog-facts'")
        print(f"3. Go to File > Import > Upload")
        print(f"4. Upload the CSV file: {csv_file.name}")
        print(f"5. Choose 'Replace spreadsheet' and 'Detect automatically'")
        print(f"6. Click 'Import data'")
        print(f"\n📝 REVIEW PROCESS:")
        print(f"- Column C (status): Change from 'pending' to 'good', 'bad', or 'replace'")
        print(f"- Column D (replacement_text): Add improved text for 'replace' status")
        print(f"- Column E (notes): Add review comments as needed")
        
        return {
            'csv_file': str(csv_file),
            'total_facts': len(facts),
            'headers': headers
        }
        
    except Exception as e:
        print(f"❌ Error creating CSV file: {e}")
        return None

def main():
    """Main function"""
    
    try:
        result = export_facts_to_csv()
        
        if result:
            print(f"\n✅ CSV export completed successfully!")
            print(f"📊 {result['total_facts']} facts exported")
        else:
            print(f"\n❌ CSV export failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()