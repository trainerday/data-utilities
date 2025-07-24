#!/usr/bin/env python3
"""
List Google Drive files to see what's available
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials

# Load environment variables
load_dotenv()

def list_drive_files():
    """List files in Google Drive"""
    
    credentials_path = Path.home() / "td-drive-credentials.json"
    
    # Define the scopes needed
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    try:
        # Load service account credentials
        credentials = Credentials.from_service_account_file(
            str(credentials_path), 
            scopes=scopes
        )
        
        # Initialize gspread client
        gc = gspread.authorize(credentials)
        
        print("📁 GOOGLE DRIVE FILES:")
        print("=" * 40)
        
        # List all spreadsheets
        spreadsheets = gc.list_spreadsheet_files()
        
        if not spreadsheets:
            print("No spreadsheets found")
            return
        
        for i, sheet in enumerate(spreadsheets, 1):
            print(f"{i:2d}. {sheet['name']}")
            print(f"    ID: {sheet['id']}")
            print(f"    URL: https://docs.google.com/spreadsheets/d/{sheet['id']}")
            print()
        
        return spreadsheets
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    list_drive_files()