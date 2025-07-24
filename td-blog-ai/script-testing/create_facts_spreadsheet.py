#!/usr/bin/env python3
"""
Google Sheets Integration for Facts

Creates 'td-blog-facts' spreadsheet and inserts all facts from database.
Uses service account credentials for authentication.
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

class FactsSpreadsheetManager:
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

    def create_or_get_spreadsheet(self, title="td-blog-facts"):
        """Create spreadsheet or get existing one"""
        
        try:
            # Try to open existing spreadsheet first
            spreadsheet = self.gc.open(title)
            print(f"✅ Found existing spreadsheet: {title}")
            return spreadsheet
            
        except gspread.SpreadsheetNotFound:
            # Create new spreadsheet
            print(f"📄 Creating new spreadsheet: {title}")
            try:
                spreadsheet = self.gc.create(title)
                print(f"✅ Created spreadsheet: {title}")
                print(f"🔗 URL: https://docs.google.com/spreadsheets/d/{spreadsheet.id}")
                return spreadsheet
            except Exception as create_error:
                print(f"❌ Failed to create spreadsheet: {create_error}")
                # Try creating with a unique name
                unique_title = f"{title}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                print(f"🔄 Trying with unique name: {unique_title}")
                spreadsheet = self.gc.create(unique_title)
                print(f"✅ Created spreadsheet: {unique_title}")
                print(f"🔗 URL: https://docs.google.com/spreadsheets/d/{spreadsheet.id}")
                return spreadsheet
            
        except Exception as e:
            print(f"❌ Unexpected error with spreadsheet: {e}")
            raise

    def setup_spreadsheet_headers(self, worksheet):
        """Setup the header row for the facts spreadsheet"""
        
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
        worksheet.update('A1:G1', [headers])
        
        # Format headers (bold)
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

    def insert_facts_to_sheet(self, worksheet, facts):
        """Insert facts into spreadsheet"""
        
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
        if not data_rows:
            print("⚠️  No facts to insert")
            return
        
        end_row = len(data_rows) + 1  # +1 because we start from row 2 (after headers)
        range_name = f'A2:G{end_row}'
        
        # Batch update
        try:
            worksheet.update(range_name, data_rows)
            print(f"✅ Inserted {len(data_rows)} facts into spreadsheet")
            
            # Set up some basic formatting
            # Format fact_id column as numbers
            worksheet.format('A:A', {'numberFormat': {'type': 'NUMBER'}})
            
            # Set column widths for better readability
            worksheet.update_dimension_properties('COLUMNS', {
                'range': {'dimension': 'COLUMNS', 'startIndex': 0, 'endIndex': 1},  # fact_id
                'properties': {'pixelSize': 80}
            })
            
            worksheet.update_dimension_properties('COLUMNS', {
                'range': {'dimension': 'COLUMNS', 'startIndex': 1, 'endIndex': 2},  # original_fact
                'properties': {'pixelSize': 400}
            })
            
            worksheet.update_dimension_properties('COLUMNS', {
                'range': {'dimension': 'COLUMNS', 'startIndex': 2, 'endIndex': 3},  # status
                'properties': {'pixelSize': 100}
            })
            
            worksheet.update_dimension_properties('COLUMNS', {
                'range': {'dimension': 'COLUMNS', 'startIndex': 3, 'endIndex': 4},  # replacement_text
                'properties': {'pixelSize': 400}
            })
            
            print(f"✅ Applied formatting to spreadsheet")
            
        except Exception as e:
            print(f"❌ Error inserting facts: {e}")
            raise

    def check_existing_facts(self, worksheet):
        """Check if facts already exist in spreadsheet"""
        
        try:
            # Get all values from fact_id column (column A)
            existing_ids = worksheet.col_values(1)[1:]  # Skip header row
            
            # Convert to integers, filtering out empty cells
            existing_ids = [int(id_val) for id_val in existing_ids if id_val.strip()]
            
            print(f"📊 Found {len(existing_ids)} existing facts in spreadsheet")
            return set(existing_ids)
            
        except Exception as e:
            print(f"⚠️  Could not check existing facts: {e}")
            return set()

    def create_facts_spreadsheet(self):
        """Main function to create and populate the facts spreadsheet"""
        
        print("🎯 CREATING TD-BLOG-FACTS SPREADSHEET")
        print("=" * 50)
        
        # Create or get spreadsheet
        spreadsheet = self.create_or_get_spreadsheet("td-blog-facts")
        
        # Get the first worksheet (or create if needed)
        try:
            worksheet = spreadsheet.sheet1
        except:
            worksheet = spreadsheet.add_worksheet(title="Facts", rows=1000, cols=10)
        
        # Check if spreadsheet already has facts
        existing_fact_ids = self.check_existing_facts(worksheet)
        
        # Get facts from database
        all_facts = self.get_facts_from_database()
        
        if existing_fact_ids:
            # Filter out facts that already exist
            new_facts = [f for f in all_facts if f['id'] not in existing_fact_ids]
            print(f"📊 {len(new_facts)} new facts to add (skipping {len(existing_fact_ids)} existing)")
        else:
            # Setup headers for new spreadsheet
            self.setup_spreadsheet_headers(worksheet)
            new_facts = all_facts
            print(f"📊 Adding all {len(new_facts)} facts to new spreadsheet")
        
        # Insert facts
        if new_facts:
            if existing_fact_ids:
                # Append to existing data
                next_row = len(existing_fact_ids) + 2  # +2 for header and 1-based indexing
                
                data_rows = []
                for fact in new_facts:
                    row = [
                        fact['id'],
                        fact['fact_text'],
                        'pending',
                        '',
                        '',
                        fact['source_article'],
                        fact['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                    ]
                    data_rows.append(row)
                
                # Calculate range for append
                end_row = next_row + len(data_rows) - 1
                range_name = f'A{next_row}:G{end_row}'
                
                worksheet.update(range_name, data_rows)
                print(f"✅ Appended {len(new_facts)} new facts")
            else:
                # Insert all facts to new spreadsheet
                self.insert_facts_to_sheet(worksheet, new_facts)
        else:
            print("✅ No new facts to add - spreadsheet is up to date")
        
        # Print summary
        print()
        print("📊 SPREADSHEET SUMMARY:")
        print(f"   - Spreadsheet: td-blog-facts")
        print(f"   - URL: https://docs.google.com/spreadsheets/d/{spreadsheet.id}")
        print(f"   - Total facts in database: {len(all_facts)}")
        print(f"   - Facts in spreadsheet: {len(existing_fact_ids) + len(new_facts if new_facts else [])}")
        print()
        print("📝 NEXT STEPS:")
        print("   1. Open the spreadsheet URL above")
        print("   2. Review facts and set status: pending → good/bad/replace")
        print("   3. For 'replace' status, add improved text in replacement_text column")
        print("   4. Add notes for context as needed")
        
        return {
            'spreadsheet_id': spreadsheet.id,
            'url': f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}",
            'total_facts': len(all_facts),
            'new_facts_added': len(new_facts) if new_facts else 0
        }

def main():
    """Main function"""
    
    # Path to credentials file
    credentials_path = Path.home() / "td-drive-credentials.json"
    
    if not credentials_path.exists():
        print(f"❌ Credentials file not found: {credentials_path}")
        print("Please ensure ~/td-drive-credentials.json exists")
        return
    
    try:
        manager = FactsSpreadsheetManager(str(credentials_path))
        result = manager.create_facts_spreadsheet()
        
        if result:
            print(f"\n✅ Spreadsheet creation completed!")
            print(f"🔗 Access your spreadsheet: {result['url']}")
        else:
            print(f"\n❌ Spreadsheet creation failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()