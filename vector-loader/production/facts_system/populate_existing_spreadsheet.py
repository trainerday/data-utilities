#!/usr/bin/env python3
"""
Populate Existing Google Spreadsheet with Facts

Works with an existing Google Sheet that you've created and shared
with the service account: td-drive-service@td-drive-1753304812.iam.gserviceaccount.com
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

class ExistingSpreadsheetManager:
    def __init__(self, credentials_path):
        """Initialize Google Sheets client"""
        
        # Define the scopes needed for Google Sheets and Drive
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Load service account credentials
        try:
            credentials = Credentials.from_service_account_file(
                credentials_path, 
                scopes=scopes
            )
            
            # Initialize gspread client
            self.gc = gspread.authorize(credentials)
            
            print(f"✅ Google Sheets client initialized")
            
        except Exception as e:
            print(f"❌ Failed to initialize Google Sheets client: {e}")
            raise

    def open_spreadsheet_by_id(self, spreadsheet_id):
        """Open spreadsheet by ID"""
        try:
            spreadsheet = self.gc.open_by_key(spreadsheet_id)
            print(f"✅ Opened spreadsheet: {spreadsheet.title}")
            return spreadsheet
        except Exception as e:
            print(f"❌ Failed to open spreadsheet: {e}")
            raise

    def open_spreadsheet_by_name(self, name):
        """Open spreadsheet by name"""
        try:
            spreadsheet = self.gc.open(name)
            print(f"✅ Opened spreadsheet: {name}")
            return spreadsheet
        except Exception as e:
            print(f"❌ Failed to open spreadsheet '{name}': {e}")
            print(f"💡 Make sure the spreadsheet exists and is shared with:")
            print(f"   td-drive-service@td-drive-1753304812.iam.gserviceaccount.com")
            raise

    def setup_spreadsheet_headers(self, worksheet):
        """Setup the header row for the facts spreadsheet"""
        
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
        worksheet.format('A1:G1', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
        })
        
        print(f"✅ Headers configured: {', '.join(headers)}")

    def get_facts_from_database(self):
        """Retrieve all facts from database"""
        
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
                results = cursor.fetchall()
            
            conn.close()
            
            print(f"✅ Retrieved {len(results)} facts from database")
            return results
            
        except Exception as e:
            print(f"❌ Error retrieving facts from database: {e}")
            raise

    def populate_spreadsheet(self, spreadsheet_identifier, by_id=False):
        """Populate spreadsheet with facts data"""
        
        print("🎯 POPULATING EXISTING SPREADSHEET WITH FACTS")
        print("=" * 50)
        
        # Open spreadsheet
        if by_id:
            spreadsheet = self.open_spreadsheet_by_id(spreadsheet_identifier)
        else:
            spreadsheet = self.open_spreadsheet_by_name(spreadsheet_identifier)
        
        # Get the first worksheet
        try:
            worksheet = spreadsheet.sheet1
            print(f"✅ Using worksheet: {worksheet.title}")
        except:
            print(f"❌ Could not access first worksheet")
            return None
        
        # Check if worksheet has data
        existing_data = worksheet.get_all_values()
        if len(existing_data) > 1:  # More than just headers
            print(f"⚠️  Worksheet has {len(existing_data)} rows of data")
            print(f"💡 This will overwrite existing data. Continue? (y/n)")
            response = input().lower().strip()
            if response != 'y':
                print("❌ Operation cancelled")
                return None
        
        # Get facts from database
        facts = self.get_facts_from_database()
        
        if not facts:
            print("⚠️  No facts found in database")
            return None
        
        # Clear existing content
        worksheet.clear()
        
        # Setup headers
        self.setup_spreadsheet_headers(worksheet)
        
        # Prepare data for batch insert
        data_rows = []
        
        for fact in facts:
            row = [
                fact['id'],                                    # fact_id
                fact['fact_text'],                            # original_fact
                'pending',                                    # status (default)
                '',                                           # replacement_text (empty)
                '',                                           # notes (empty)
                fact['source_article'],                       # source_article
                fact['created_at'].strftime('%Y-%m-%d %H:%M:%S')  # created_at
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
            
            # Apply formatting
            # Format fact_id column as numbers
            worksheet.format('A:A', {'numberFormat': {'type': 'NUMBER'}})
            
            # Set column widths for better readability
            try:
                # fact_id column
                worksheet.update_dimension_properties('COLUMNS', {
                    'range': {'dimension': 'COLUMNS', 'startIndex': 0, 'endIndex': 1},
                    'properties': {'pixelSize': 80}
                })
                
                # original_fact column
                worksheet.update_dimension_properties('COLUMNS', {
                    'range': {'dimension': 'COLUMNS', 'startIndex': 1, 'endIndex': 2},
                    'properties': {'pixelSize': 500}
                })
                
                # status column
                worksheet.update_dimension_properties('COLUMNS', {
                    'range': {'dimension': 'COLUMNS', 'startIndex': 2, 'endIndex': 3},
                    'properties': {'pixelSize': 100}
                })
                
                # replacement_text column
                worksheet.update_dimension_properties('COLUMNS', {
                    'range': {'dimension': 'COLUMNS', 'startIndex': 3, 'endIndex': 4},
                    'properties': {'pixelSize': 500}
                })
                
                print(f"✅ Applied formatting to spreadsheet")
                
            except Exception as format_error:
                print(f"⚠️  Could not apply formatting: {format_error}")
            
        except Exception as e:
            print(f"❌ Error inserting facts: {e}")
            raise
        
        # Print summary
        print()
        print("📊 SPREADSHEET SUMMARY:")
        print(f"   - Spreadsheet: {spreadsheet.title}")
        print(f"   - URL: https://docs.google.com/spreadsheets/d/{spreadsheet.id}")
        print(f"   - Facts inserted: {len(data_rows)}")
        print()
        print("📝 NEXT STEPS:")
        print("   1. Open the spreadsheet URL above")
        print("   2. Review facts and set status: pending → good/bad/replace")
        print("   3. For 'replace' status, add improved text in replacement_text column")
        print("   4. Add notes for context as needed")
        print()
        print("📋 STATUS OPTIONS:")
        print("   - good: Use fact as-is")
        print("   - bad: Skip/ignore fact")
        print("   - replace: Use replacement_text instead")
        print("   - pending: Still needs review")
        
        return {
            'spreadsheet_id': spreadsheet.id,
            'url': f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}",
            'total_facts': len(data_rows),
            'title': spreadsheet.title
        }

def main():
    """Main function"""
    
    # Path to credentials file
    credentials_path = Path.home() / "td-drive-credentials.json"
    
    if not credentials_path.exists():
        print(f"❌ Credentials file not found: {credentials_path}")
        print("Please ensure ~/td-drive-credentials.json exists")
        return
    
    print("🔧 SPREADSHEET SETUP OPTIONS:")
    print("=" * 40)
    print("1. Use spreadsheet name (e.g., 'td-blog-facts')")
    print("2. Use spreadsheet ID (from URL)")
    print()
    
    choice = input("Enter 1 for name or 2 for ID: ").strip()
    
    if choice == "1":
        name = input("Enter spreadsheet name: ").strip()
        if not name:
            print("❌ No name provided")
            return
        
        try:
            manager = ExistingSpreadsheetManager(str(credentials_path))
            result = manager.populate_spreadsheet(name, by_id=False)
            
            if result:
                print(f"\n✅ Spreadsheet population completed!")
                print(f"🔗 Access your spreadsheet: {result['url']}")
            else:
                print(f"\n❌ Spreadsheet population failed")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    elif choice == "2":
        spreadsheet_id = input("Enter spreadsheet ID: ").strip()
        if not spreadsheet_id:
            print("❌ No ID provided")
            return
        
        try:
            manager = ExistingSpreadsheetManager(str(credentials_path))
            result = manager.populate_spreadsheet(spreadsheet_id, by_id=True)
            
            if result:
                print(f"\n✅ Spreadsheet population completed!")
                print(f"🔗 Access your spreadsheet: {result['url']}")
            else:
                print(f"\n❌ Spreadsheet population failed")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()