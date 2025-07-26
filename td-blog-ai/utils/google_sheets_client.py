#!/usr/bin/env python3
"""
Google Sheets client for retrieving bad facts
"""

import os
import logging
from typing import List, Dict
from dotenv import load_dotenv

# Google Sheets imports
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()

logger = logging.getLogger(__name__)

class GoogleSheetsClient:
    def __init__(self):
        """Initialize Google Sheets client"""
        
        # Google Sheets configuration
        self.spreadsheet_id = "1YJyAVVaPUM6uhd9_DIRLAB0tE106gExTSD0sUMV5LLc"
        self.credentials_path = os.path.expanduser("~/td-drive-credentials.json")
        
        self.client = None
        self.spreadsheet = None
        self.worksheet = None
        
    def connect(self):
        """Connect to Google Sheets"""
        try:
            # Setup Google Sheets credentials
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            creds = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=scope
            )
            
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            self.worksheet = self.spreadsheet.sheet1
            
            logger.info("✅ Connected to Google Sheets")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Google Sheets: {str(e)}")
            raise
    
    def get_bad_facts(self) -> List[Dict[str, str]]:
        """Get all facts marked as WRONG, USELESS, or UPDATED"""
        
        if not self.worksheet:
            self.connect()
        
        try:
            # Get all records from the sheet
            records = self.worksheet.get_all_records()
            
            bad_facts = []
            
            for record in records:
                status = record.get('status', '').strip().upper()
                
                if status in ['WRONG', 'USELESS', 'UPDATED']:
                    fact_text = record.get('original_fact', '').strip()
                    
                    if fact_text:
                        reason = {
                            'WRONG': 'WRONG - Incorrect information',
                            'USELESS': 'USELESS - Not valuable information',
                            'UPDATED': 'UPDATED - Information has changed and needs updating'
                        }.get(status, status)
                        
                        bad_facts.append({
                            'fact': fact_text,
                            'status': status,
                            'reason': reason
                        })
            
            logger.info(f"📋 Found {len(bad_facts)} bad facts (WRONG/USELESS/UPDATED)")
            return bad_facts
            
        except Exception as e:
            logger.error(f"❌ Error retrieving bad facts: {str(e)}")
            return []
    
    def format_bad_facts_for_prompt(self, bad_facts: List[Dict[str, str]]) -> str:
        """Format bad facts for inclusion in prompt"""
        
        if not bad_facts:
            return "No facts have been marked as incorrect or useless yet."
        
        formatted_facts = []
        
        for i, fact_info in enumerate(bad_facts, 1):
            formatted_facts.append(
                f"{i}. [{fact_info['status']}] {fact_info['fact']}\n"
                f"   Reason: {fact_info['reason']}"
            )
        
        return "\n\n".join(formatted_facts)


# Convenience function for scripts
def get_bad_facts_for_article_generation() -> str:
    """Get formatted bad facts for article generation"""
    
    try:
        client = GoogleSheetsClient()
        bad_facts = client.get_bad_facts()
        return client.format_bad_facts_for_prompt(bad_facts)
    except Exception as e:
        logger.warning(f"Could not retrieve bad facts: {str(e)}")
        return "Could not retrieve bad facts from Google Sheets. Proceeding without exclusions."