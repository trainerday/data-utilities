#!/usr/bin/env python3
"""
Quick status check for facts in unified knowledge base
"""

import os
import sys
import sqlalchemy
from dotenv import load_dotenv

load_dotenv()

def check_facts_status():
    """Check current facts status in knowledge base"""
    
    # Local PostgreSQL configuration
    local_db_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'trainerday_local',
        'user': os.getenv('USER', 'alex'),
        'password': '',
    }
    
    try:
        connection_string = f"postgresql://{local_db_config['user']}@{local_db_config['host']}:{local_db_config['port']}/{local_db_config['database']}"
        engine = sqlalchemy.create_engine(connection_string)
        
        with engine.connect() as conn:
            # Total documents
            result = conn.execute(sqlalchemy.text(
                "SELECT COUNT(*) as total FROM llamaindex_knowledge_base"
            ))
            total_docs = result.fetchone()[0]
            
            # By source
            result = conn.execute(sqlalchemy.text(
                "SELECT metadata_->>'source' as source, COUNT(*) as count FROM llamaindex_knowledge_base GROUP BY metadata_->>'source'"
            ))
            sources = result.fetchall()
            
            # Facts breakdown if any exist
            result = conn.execute(sqlalchemy.text(
                "SELECT metadata_->>'content_type' as fact_type, COUNT(*) as count FROM llamaindex_knowledge_base WHERE metadata_->>'source' = 'facts' GROUP BY metadata_->>'content_type'"
            ))
            fact_types = result.fetchall()
            
            print("📊 UNIFIED KNOWLEDGE BASE STATUS")
            print("=" * 50)
            print(f"Total documents: {total_docs:,}")
            print()
            
            print("By source:")
            for source, count in sources:
                print(f"  • {source}: {count:,}")
            print()
            
            if fact_types:
                print("Facts breakdown:")
                for fact_type, count in fact_types:
                    print(f"  • {fact_type}: {count:,}")
            else:
                print("No facts found in knowledge base")
                
    except Exception as e:
        print(f"Error checking status: {e}")

if __name__ == "__main__":
    check_facts_status()