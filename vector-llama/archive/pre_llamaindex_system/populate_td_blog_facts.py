#!/usr/bin/env python3
"""
Populate TD-Blog-Facts Spreadsheet

Populates the shared "TD-Blog-Facts" spreadsheet with facts from database.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials
from psycopg2.extras import RealDictCursor

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from utils.db_connection import get_db_connection

def populate_shared_spreadsheet():
    """Populate the shared TD-Blog-Facts spreadsheet"""
    
    print("🎯 POPULATING TD-BLOG-FACTS SPREADSHEET")
    print("=" * 50)
    
    # Initialize Google Sheets client
    credentials_path = Path.home() / "td-drive-credentials.json"
    
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    try:
        credentials = Credentials.from_service_account_file(
            str(credentials_path), 
            scopes=scopes
        )
        
        gc = gspread.authorize(credentials)
        print(f"✅ Google Sheets client initialized")
        
    except Exception as e:
        print(f"❌ Failed to initialize Google Sheets client: {e}")
        return None
    
    # Open the shared spreadsheet by ID
    spreadsheet_id = "1YJyAVVaPUM6uhd9_DIRLAB0tE106gExTSD0sUMV5LLc"
    try:
        spreadsheet = gc.open_by_key(spreadsheet_id)
        print(f"✅ Opened spreadsheet: {spreadsheet.title}")
        print(f"🔗 URL: https://docs.google.com/spreadsheets/d/{spreadsheet.id}")
        
    except Exception as e:
        print(f"❌ Failed to open spreadsheet: {e}")
        print(f"💡 The Google Sheets API may need to be enabled for the service account project.")
        print(f"💡 Or check if the spreadsheet is properly shared with: td-drive-service@td-drive-1753304812.iam.gserviceaccount.com")
        return None
    
    # Get the first worksheet
    try:
        worksheet = spreadsheet.sheet1
        print(f"✅ Using worksheet: {worksheet.title}")
    except:
        print(f"❌ Could not access first worksheet")
        return None
    
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
        print(f"❌ Error retrieving facts from database: {e}")
        return None
    
    if not facts:
        print("⚠️  No facts found in database")
        return None
    
    # Clear existing content and setup headers
    print("🔄 Setting up spreadsheet...")
    worksheet.clear()
    
    # Setup headers
    headers = [
        'fact_id',
        'original_fact', 
        'status',
        'replacement_text',
        'notes',
        'source_article',
        'created_at'
    ]
    
    # Set headers in first row
    worksheet.update('A1:G1', [headers])
    
    # Format headers (bold, background color)
    try:
        worksheet.format('A1:G1', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
        })
        print(f"✅ Headers configured: {', '.join(headers)}")
    except Exception as e:
        print(f"⚠️  Could not format headers: {e}")
    
    # Prepare data for batch insert
    data_rows = []
    
    for fact in facts:
        row = [
            fact['id'],                                       # fact_id
            fact['fact_text'],                               # original_fact
            'pending',                                       # status (default)
            '',                                              # replacement_text (empty)
            '',                                              # notes (empty)
            fact['source_article'],                          # source_article
            fact['created_at'].strftime('%Y-%m-%d %H:%M:%S') # created_at
        ]
        data_rows.append(row)
    
    # Calculate range for batch update
    end_row = len(data_rows) + 1  # +1 because we start from row 2 (after headers)
    range_name = f'A2:G{end_row}'
    
    # Batch update
    try:
        print(f"📊 Inserting {len(data_rows)} facts...")
        worksheet.update(range_name, data_rows)
        print(f"✅ Successfully inserted {len(data_rows)} facts")
        
    except Exception as e:
        print(f"❌ Error inserting facts: {e}")
        return None
    
    # Apply formatting
    try:
        # Format fact_id column as numbers
        worksheet.format('A:A', {'numberFormat': {'type': 'NUMBER'}})
        
        # Set column widths for better readability
        requests = []
        
        # fact_id column (80px)
        requests.append({
            'updateDimensionProperties': {
                'range': {
                    'dimension': 'COLUMNS',
                    'startIndex': 0,
                    'endIndex': 1
                },
                'properties': {'pixelSize': 80},
                'fields': 'pixelSize'
            }
        })
        
        # original_fact column (500px)
        requests.append({
            'updateDimensionProperties': {
                'range': {
                    'dimension': 'COLUMNS',
                    'startIndex': 1,
                    'endIndex': 2
                },
                'properties': {'pixelSize': 500},
                'fields': 'pixelSize'
            }
        })
        
        # status column (100px)
        requests.append({
            'updateDimensionProperties': {
                'range': {
                    'dimension': 'COLUMNS',
                    'startIndex': 2,
                    'endIndex': 3
                },
                'properties': {'pixelSize': 100},
                'fields': 'pixelSize'
            }
        })
        
        # replacement_text column (500px)
        requests.append({
            'updateDimensionProperties': {
                'range': {
                    'dimension': 'COLUMNS',
                    'startIndex': 3,
                    'endIndex': 4
                },
                'properties': {'pixelSize': 500},
                'fields': 'pixelSize'
            }
        })
        
        # Apply all formatting requests
        spreadsheet.batch_update({'requests': requests})
        print(f"✅ Applied column formatting")
        
    except Exception as format_error:
        print(f"⚠️  Could not apply formatting: {format_error}")
    
    # Print final summary
    print()
    print("🎉 SPREADSHEET POPULATION COMPLETED!")
    print("=" * 50)
    print(f"   - Spreadsheet: {spreadsheet.title}")
    print(f"   - URL: https://docs.google.com/spreadsheets/d/{spreadsheet.id}")
    print(f"   - Facts inserted: {len(data_rows)}")
    print()
    print("📝 NEXT STEPS:")
    print("   1. Open the spreadsheet URL above")
    print("   2. Review facts in column B (original_fact)")
    print("   3. Set status in column C:")
    print("      • good = use fact as-is")
    print("      • bad = skip/ignore fact")
    print("      • replace = use replacement_text instead")
    print("      • pending = still needs review")
    print("   4. For 'replace' status, add improved text in column D (replacement_text)")
    print("   5. Add notes in column E as needed")
    
    return {
        'spreadsheet_id': spreadsheet.id,
        'url': f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}",
        'total_facts': len(data_rows),
        'title': spreadsheet.title
    }

def main():
    """Main function"""
    
    try:
        result = populate_shared_spreadsheet()
        
        if result:
            print(f"\n✅ Success! Your spreadsheet is ready for review.")
            print(f"🔗 {result['url']}")
        else:
            print(f"\n❌ Failed to populate spreadsheet")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()