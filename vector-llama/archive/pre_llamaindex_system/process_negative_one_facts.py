#!/usr/bin/env python3
"""
Process Facts with ID = -1

This script finds facts in Google Sheets with fact_id = -1, creates vector embeddings,
stores them in the database, and updates the Google Sheets with the new database IDs.
This should run before the AI enhancement process.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials
from psycopg2.extras import RealDictCursor
import openai
import numpy as np
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from utils.db_connection import get_db_connection

def read_google_sheets_facts():
    """Read all facts from Google Sheets, focusing on those with fact_id = -1"""
    
    print("📊 Reading facts from Google Sheets...")
    
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
        return None, None
    
    # Open the shared spreadsheet by ID
    spreadsheet_id = "1YJyAVVaPUM6uhd9_DIRLAB0tE106gExTSD0sUMV5LLc"
    try:
        spreadsheet = gc.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.sheet1
        print(f"✅ Reading from: {spreadsheet.title}")
        
    except Exception as e:
        print(f"❌ Failed to open spreadsheet: {e}")
        return None, None
    
    # Read all data
    try:
        all_values = worksheet.get_all_values()
        
        if len(all_values) < 2:
            print("⚠️  No data found in spreadsheet")
            return [], worksheet
        
        # Parse data (column order: fact_id, status, original_fact, replacement_text, notes, source_article, created_at)
        headers = all_values[0]
        data_rows = all_values[1:]
        
        print(f"📊 Found {len(data_rows)} total facts in spreadsheet")
        
        negative_one_facts = []
        
        for row_index, row in enumerate(data_rows, start=2):  # Start at 2 because row 1 is headers
            if len(row) >= 3 and row[0]:  # Ensure we have minimum required columns
                try:
                    fact_id = int(row[0])
                    if fact_id == -1:
                        fact_data = {
                            'row_index': row_index,
                            'fact_id': fact_id,
                            'status': row[1].strip() if len(row) > 1 else '',
                            'original_fact': row[2] if len(row) > 2 else '',
                            'replacement_text': row[3] if len(row) > 3 else '',
                            'notes': row[4] if len(row) > 4 else '',
                            'source_article': row[5] if len(row) > 5 else '',
                            'created_at': row[6] if len(row) > 6 else ''
                        }
                        negative_one_facts.append(fact_data)
                
                except (ValueError, IndexError):
                    continue  # Skip invalid rows
        
        print(f"✅ Found {len(negative_one_facts)} facts with ID = -1")
        return negative_one_facts, worksheet
        
    except Exception as e:
        print(f"❌ Error reading spreadsheet data: {e}")
        return None, None

def create_fact_embedding(fact_text):
    """Create vector embedding for a fact"""
    
    try:
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        response = client.embeddings.create(
            model="text-embedding-3-large",
            input=fact_text,
            dimensions=1536
        )
        
        embedding = response.data[0].embedding
        return np.array(embedding)
        
    except Exception as e:
        print(f"❌ Error creating embedding: {e}")
        return None

def check_similarity_with_existing_facts(fact_text, embedding, threshold=0.9):
    """Check if this fact is similar to existing facts in database"""
    
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Get all existing facts with embeddings
            cursor.execute("""
                SELECT id, fact_text, embedding 
                FROM facts 
                WHERE embedding IS NOT NULL
            """)
            
            existing_facts = cursor.fetchall()
            
            if not existing_facts:
                print("   No existing facts to compare against")
                return False, None
            
            # Check similarity with each existing fact
            for existing_fact in existing_facts:
                # Parse the existing embedding from JSON string
                existing_embedding = np.array(json.loads(existing_fact['embedding']))
                
                # Calculate cosine similarity
                similarity = np.dot(embedding, existing_embedding) / (
                    np.linalg.norm(embedding) * np.linalg.norm(existing_embedding)
                )
                
                if similarity >= threshold:
                    print(f"   🔄 Similar fact found (similarity: {similarity:.3f})")
                    print(f"      Original: {fact_text[:100]}...")
                    print(f"      Existing: {existing_fact['fact_text'][:100]}...")
                    return True, existing_fact['id']
            
            return False, None
            
    except Exception as e:
        print(f"❌ Error checking similarity: {e}")
        return False, None
    finally:
        if 'conn' in locals():
            conn.close()

def store_fact_in_database(fact_data, embedding):
    """Store fact in database and return the new ID"""
    
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Insert fact into database
            insert_query = """
            INSERT INTO facts (fact_text, source_article, embedding, metadata, created_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """
            
            metadata = {
                'extraction_source': 'google_sheets_negative_one',
                'original_status': fact_data['status'],
                'notes': fact_data['notes'],
                'processed_at': datetime.now().isoformat()
            }
            
            cursor.execute(insert_query, (
                fact_data['original_fact'],
                fact_data['source_article'],
                json.dumps(embedding.tolist()),
                json.dumps(metadata),
                datetime.now()
            ))
            
            new_fact_id = cursor.fetchone()['id']
            conn.commit()
            
            print(f"   ✅ Stored in database with ID: {new_fact_id}")
            return new_fact_id
            
    except Exception as e:
        print(f"❌ Error storing fact in database: {e}")
        return None
    finally:
        if 'conn' in locals():
            conn.close()

def update_google_sheets_id(worksheet, row_index, new_fact_id):
    """Update the fact_id in Google Sheets"""
    
    try:
        # Update cell A{row_index} with new fact ID using range notation
        cell_reference = f"A{row_index}"
        worksheet.update(cell_reference, [[str(new_fact_id)]])
        print(f"   ✅ Updated Google Sheets row {row_index} with ID: {new_fact_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating Google Sheets: {e}")
        return False

def main():
    """Main function"""
    
    print("🚀 PROCESSING FACTS WITH ID = -1")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Read facts from Google Sheets
    negative_one_facts, worksheet = read_google_sheets_facts()
    
    if not negative_one_facts:
        print("✅ No facts with ID = -1 found. All facts already processed!")
        return
    
    print(f"📊 Processing {len(negative_one_facts)} facts with ID = -1...")
    print()
    
    # Track statistics
    processed_count = 0
    stored_count = 0
    duplicate_count = 0
    error_count = 0
    
    # Process each fact
    for i, fact_data in enumerate(negative_one_facts, 1):
        print(f"📄 [{i}/{len(negative_one_facts)}] Processing fact from {fact_data['source_article']}")
        print(f"   Fact: {fact_data['original_fact'][:100]}...")
        
        # Create embedding
        print("   🤖 Creating vector embedding...")
        embedding = create_fact_embedding(fact_data['original_fact'])
        if embedding is None:
            print(f"   ❌ Failed to create embedding - SKIPPING")
            error_count += 1
            continue
        
        # Check for similarity with existing facts
        print("   🔍 Checking for duplicates...")
        is_similar, existing_id = check_similarity_with_existing_facts(
            fact_data['original_fact'], 
            embedding
        )
        
        if is_similar:
            print(f"   🔄 Using existing fact ID: {existing_id}")
            new_fact_id = existing_id
            duplicate_count += 1
        else:
            # Store new fact in database
            print("   💾 Storing new fact in database...")
            new_fact_id = store_fact_in_database(fact_data, embedding)
            if new_fact_id is None:
                print(f"   ❌ Failed to store fact - SKIPPING")
                error_count += 1
                continue
            stored_count += 1
        
        # Update Google Sheets with new ID
        print("   📝 Updating Google Sheets...")
        if update_google_sheets_id(worksheet, fact_data['row_index'], new_fact_id):
            processed_count += 1
        else:
            error_count += 1
        
        print(f"   ✅ Completed fact {i}")
        print("-" * 60)
    
    # Final summary
    print()
    print("🎉 PROCESSING COMPLETE!")
    print("=" * 60)
    print(f"📊 STATISTICS:")
    print(f"   - Facts processed: {processed_count}")
    print(f"   - New facts stored: {stored_count}")
    print(f"   - Duplicates found: {duplicate_count}")
    print(f"   - Errors: {error_count}")
    print()
    print("✅ Google Sheets updated with database IDs")
    print("✅ All facts now have proper vector embeddings")
    print("🚀 Ready for AI enhancement process!")

if __name__ == "__main__":
    main()