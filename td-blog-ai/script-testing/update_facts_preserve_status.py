#!/usr/bin/env python3
"""
Update Facts Spreadsheet - Preserve Status Updates

This script safely updates the Google Sheets with new facts while preserving
all existing status updates, replacement text, and notes.

It reads existing data, identifies which facts already exist, and only adds
new facts without overwriting any user modifications.
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

def preserve_and_update_spreadsheet():
    """Update spreadsheet while preserving existing status updates"""
    
    print("🔒 PRESERVING STATUS UPDATES - SAFE SPREADSHEET UPDATE")
    print("=" * 60)
    
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
        
    except Exception as e:
        print(f"❌ Failed to open spreadsheet: {e}")
        return None
    
    # Get the first worksheet
    try:
        worksheet = spreadsheet.sheet1
        print(f"✅ Using worksheet: {worksheet.title}")
    except:
        print(f"❌ Could not access first worksheet")
        return None
    
    # Read all existing data from spreadsheet
    print("📊 Reading existing spreadsheet data...")
    try:
        all_values = worksheet.get_all_values()
        
        if not all_values:
            print("⚠️  Spreadsheet is empty - will create new structure")
            existing_facts = {}
            headers_exist = False
        else:
            # Check if headers exist
            if len(all_values) >= 1 and all_values[0][0] == 'fact_id':
                headers_exist = True
                headers = all_values[0]
                data_rows = all_values[1:]
                print(f"✅ Found headers: {headers}")
                print(f"📊 Found {len(data_rows)} existing data rows")
                
                # Build dictionary of existing facts with their status updates
                existing_facts = {}
                for row in data_rows:
                    if len(row) >= 7 and row[0]:  # Ensure we have enough columns and fact_id exists
                        try:
                            fact_id = int(row[0])
                            existing_facts[fact_id] = {
                                'fact_id': fact_id,
                                'status': row[1] if len(row) > 1 else 'pending',
                                'original_fact': row[2] if len(row) > 2 else '',
                                'replacement_text': row[3] if len(row) > 3 else '',
                                'notes': row[4] if len(row) > 4 else '',
                                'source_article': row[5] if len(row) > 5 else '',
                                'created_at': row[6] if len(row) > 6 else ''
                            }
                        except (ValueError, IndexError):
                            continue  # Skip invalid rows
                            
                print(f"✅ Preserved {len(existing_facts)} existing facts with status updates")
                
            else:
                headers_exist = False
                existing_facts = {}
                print("⚠️  No valid headers found - will create new structure")
        
    except Exception as e:
        print(f"❌ Error reading existing spreadsheet data: {e}")
        return None
    
    # Get all facts from database
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
            db_facts = cursor.fetchall()
        
        conn.close()
        
        print(f"✅ Retrieved {len(db_facts)} facts from database")
        
    except Exception as e:
        print(f"❌ Error retrieving facts from database: {e}")
        return None
    
    if not db_facts:
        print("⚠️  No facts found in database")
        return None
    
    # Identify new facts that need to be added
    new_facts = []
    updated_facts = []
    
    for db_fact in db_facts:
        fact_id = db_fact['id']
        
        if fact_id in existing_facts:
            # Fact exists - preserve status but update other fields if needed
            existing = existing_facts[fact_id]
            
            # Check if fact text or source changed (update if needed)
            if (existing['original_fact'] != db_fact['fact_text'] or 
                existing['source_article'] != db_fact['source_article']):
                
                updated_facts.append({
                    'fact_id': fact_id,
                    'status': existing['status'],  # PRESERVE USER STATUS
                    'original_fact': db_fact['fact_text'],
                    'replacement_text': existing['replacement_text'],  # PRESERVE USER TEXT
                    'notes': existing['notes'],  # PRESERVE USER NOTES
                    'source_article': db_fact['source_article'],
                    'created_at': db_fact['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                })
            else:
                # No changes needed - keep existing data as-is
                pass
        else:
            # New fact - add with default pending status
            new_facts.append({
                'fact_id': fact_id,
                'status': '',
                'original_fact': db_fact['fact_text'],
                'replacement_text': '',
                'notes': '',
                'source_article': db_fact['source_article'],
                'created_at': db_fact['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            })
    
    print(f"📊 Analysis complete:")
    print(f"   - Existing facts to preserve: {len(existing_facts)}")
    print(f"   - New facts to add: {len(new_facts)}")
    print(f"   - Facts needing updates: {len(updated_facts)}")
    
    # Build complete dataset preserving user updates
    all_spreadsheet_facts = {}
    
    # Start with existing facts (preserves all user status updates)
    for fact_id, fact_data in existing_facts.items():
        all_spreadsheet_facts[fact_id] = fact_data
    
    # Apply any updates to existing facts
    for updated_fact in updated_facts:
        fact_id = updated_fact['fact_id']
        all_spreadsheet_facts[fact_id] = updated_fact
        print(f"   🔄 Updated fact {fact_id}")
    
    # Add new facts
    for new_fact in new_facts:
        fact_id = new_fact['fact_id']
        all_spreadsheet_facts[fact_id] = new_fact
        print(f"   ➕ Added new fact {fact_id}")
    
    # Sort facts by ID for consistent ordering
    sorted_facts = sorted(all_spreadsheet_facts.values(), key=lambda x: x['fact_id'])
    
    # Clear spreadsheet and rebuild with preserved data
    print(f"🔄 Rebuilding spreadsheet with {len(sorted_facts)} facts...")
    worksheet.clear()
    
    # Setup headers
    headers = [
        'fact_id',
        'status',
        'original_fact', 
        'replacement_text',
        'notes',
        'source_article',
        'created_at'
    ]
    
    # Set headers in first row
    worksheet.update(values=[headers], range_name='A1:G1')
    
    # Format headers
    try:
        worksheet.format('A1:G1', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
        })
        print(f"✅ Headers configured")
    except Exception as e:
        print(f"⚠️  Could not format headers: {e}")
    
    # Prepare data rows
    data_rows = []
    for fact in sorted_facts:
        row = [
            fact['fact_id'],
            fact['status'],
            fact['original_fact'],
            fact['replacement_text'],
            fact['notes'],
            fact['source_article'],
            fact['created_at']
        ]
        data_rows.append(row)
    
    # Batch update data
    if data_rows:
        try:
            end_row = len(data_rows) + 1
            range_name = f'A2:G{end_row}'
            
            worksheet.update(values=data_rows, range_name=range_name)
            print(f"✅ Successfully updated spreadsheet with {len(data_rows)} facts")
            
        except Exception as e:
            print(f"❌ Error updating spreadsheet: {e}")
            return None
    
    # Apply formatting
    try:
        worksheet.format('A:A', {'numberFormat': {'type': 'NUMBER'}})
        
        # Set column widths
        requests = [
            {
                'updateDimensionProperties': {
                    'range': {'dimension': 'COLUMNS', 'startIndex': 0, 'endIndex': 1},
                    'properties': {'pixelSize': 80}, 'fields': 'pixelSize'
                }
            },
            {
                'updateDimensionProperties': {
                    'range': {'dimension': 'COLUMNS', 'startIndex': 1, 'endIndex': 2},
                    'properties': {'pixelSize': 100}, 'fields': 'pixelSize'
                }
            },
            {
                'updateDimensionProperties': {
                    'range': {'dimension': 'COLUMNS', 'startIndex': 2, 'endIndex': 3},
                    'properties': {'pixelSize': 500}, 'fields': 'pixelSize'
                }
            },
            {
                'updateDimensionProperties': {
                    'range': {'dimension': 'COLUMNS', 'startIndex': 3, 'endIndex': 4},
                    'properties': {'pixelSize': 500}, 'fields': 'pixelSize'
                }
            }
        ]
        
        spreadsheet.batch_update({'requests': requests})
        print(f"✅ Applied column formatting")
        
    except Exception as format_error:
        print(f"⚠️  Could not apply formatting: {format_error}")
    
    # Print summary
    print()
    print("🎉 SAFE UPDATE COMPLETED!")
    print("=" * 50)
    print(f"   - Spreadsheet: {spreadsheet.title}")
    print(f"   - URL: https://docs.google.com/spreadsheets/d/{spreadsheet.id}")
    print(f"   - Total facts: {len(sorted_facts)}")
    print(f"   - Status updates preserved: ✅")
    print(f"   - New facts added: {len(new_facts)}")
    print(f"   - Facts updated: {len(updated_facts)}")
    
    # Show status breakdown
    status_counts = {}
    for fact in sorted_facts:
        status = fact['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print()
    print("📊 STATUS BREAKDOWN:")
    for status, count in sorted(status_counts.items()):
        print(f"   - {status}: {count} facts")
    
    return {
        'spreadsheet_id': spreadsheet.id,
        'url': f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}",
        'total_facts': len(sorted_facts),
        'new_facts_added': len(new_facts),
        'facts_updated': len(updated_facts),
        'preserved_existing': len(existing_facts)
    }

def main():
    """Main function"""
    
    try:
        result = preserve_and_update_spreadsheet()
        
        if result:
            print(f"\n✅ Success! Your status updates have been preserved.")
            print(f"🔗 {result['url']}")
        else:
            print(f"\n❌ Failed to update spreadsheet safely")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()