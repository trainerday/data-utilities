#!/usr/bin/env python3
"""
Check what facts are actually in the database
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def check_facts_in_database():
    """Check what facts are in the knowledge base"""
    
    print("🔍 CHECKING FACTS IN DATABASE")
    print("=" * 50)
    
    # Connect to database
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='trainerday_local',
        user=os.getenv('USER', 'alex'),
        password=''
    )
    
    try:
        with conn.cursor() as cur:
            # Check total facts count
            cur.execute("""
                SELECT COUNT(*) 
                FROM llamaindex_knowledge_base 
                WHERE metadata_->>'source' = 'facts'
            """)
            total_facts = cur.fetchone()[0]
            print(f"📊 Total facts in database: {total_facts}")
            
            # Check fact types
            cur.execute("""
                SELECT 
                    metadata_->>'content_type' as content_type,
                    COUNT(*) as count
                FROM llamaindex_knowledge_base 
                WHERE metadata_->>'source' = 'facts'
                GROUP BY metadata_->>'content_type'
                ORDER BY count DESC
            """)
            fact_types = cur.fetchall()
            
            print("\n📋 Facts by type:")
            for content_type, count in fact_types:
                print(f"  {content_type}: {count}")
            
            # Check for ALT/duplication related facts
            cur.execute("""
                SELECT 
                    text,
                    metadata_->>'content_type' as content_type,
                    metadata_->>'fact_status' as fact_status
                FROM llamaindex_knowledge_base 
                WHERE metadata_->>'source' = 'facts'
                AND (LOWER(text) LIKE '%alt%' OR LOWER(text) LIKE '%drag%' OR LOWER(text) LIKE '%duplicat%')
                LIMIT 10
            """)
            alt_facts = cur.fetchall()
            
            print(f"\n🔍 ALT/Drag/Duplication related facts: {len(alt_facts)}")
            for i, (text, content_type, fact_status) in enumerate(alt_facts, 1):
                print(f"\n{i}. Type: {content_type}, Status: {fact_status}")
                print(f"   Text: {text}")
            
            # Check for any "DO NOT USE" facts
            cur.execute("""
                SELECT 
                    text,
                    metadata_->>'content_type' as content_type,
                    metadata_->>'fact_status' as fact_status
                FROM llamaindex_knowledge_base 
                WHERE metadata_->>'source' = 'facts'
                AND UPPER(text) LIKE '%DO NOT USE%'
                LIMIT 10
            """)
            wrong_facts = cur.fetchall()
            
            print(f"\n🚨 'DO NOT USE' facts found: {len(wrong_facts)}")
            for i, (text, content_type, fact_status) in enumerate(wrong_facts, 1):
                print(f"\n{i}. Type: {content_type}, Status: {fact_status}")
                print(f"   Text: {text[:200]}...")
            
            # Sample some random facts
            cur.execute("""
                SELECT 
                    text,
                    metadata_->>'content_type' as content_type,
                    metadata_->>'fact_status' as fact_status
                FROM llamaindex_knowledge_base 
                WHERE metadata_->>'source' = 'facts'
                ORDER BY RANDOM()
                LIMIT 5
            """)
            sample_facts = cur.fetchall()
            
            print(f"\n📝 Sample facts:")
            for i, (text, content_type, fact_status) in enumerate(sample_facts, 1):
                print(f"\n{i}. Type: {content_type}, Status: {fact_status}")
                print(f"   Text: {text[:150]}...")
        
    finally:
        conn.close()

if __name__ == "__main__":
    check_facts_in_database()