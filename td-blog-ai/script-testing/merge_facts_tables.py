#!/usr/bin/env python3
"""
Merge facts from data_llamaindex_knowledge_base into unified llamaindex_knowledge_base
"""

import os
import sys
import sqlalchemy
from dotenv import load_dotenv

load_dotenv()

def merge_facts_to_unified_table():
    """Merge facts from separate table into unified knowledge base"""
    
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
            # Start transaction
            trans = conn.begin()
            
            try:
                # First, check what we have
                result = conn.execute(sqlalchemy.text(
                    "SELECT COUNT(*) FROM data_llamaindex_knowledge_base WHERE metadata_->>'source' = 'facts'"
                ))
                facts_count = result.fetchone()[0]
                print(f"📊 Found {facts_count} facts to merge")
                
                # Check facts breakdown
                result = conn.execute(sqlalchemy.text(
                    "SELECT metadata_->>'content_type' as fact_type, COUNT(*) as count FROM data_llamaindex_knowledge_base WHERE metadata_->>'source' = 'facts' GROUP BY metadata_->>'content_type'"
                ))
                fact_types = result.fetchall()
                print("Facts breakdown:")
                for fact_type, count in fact_types:
                    print(f"  • {fact_type}: {count}")
                print()
                
                # Remove any existing facts from unified table
                result = conn.execute(sqlalchemy.text(
                    "DELETE FROM llamaindex_knowledge_base WHERE metadata_->>'source' = 'facts'"
                ))
                deleted_count = result.rowcount
                print(f"🗑️ Removed {deleted_count} existing facts from unified table")
                
                # Copy facts from data table to unified table
                result = conn.execute(sqlalchemy.text("""
                    INSERT INTO llamaindex_knowledge_base (node_id, text, metadata_, embedding)
                    SELECT node_id, text, metadata_, embedding 
                    FROM data_llamaindex_knowledge_base 
                    WHERE metadata_->>'source' = 'facts'
                """))
                
                # Get updated counts
                result = conn.execute(sqlalchemy.text(
                    "SELECT COUNT(*) FROM llamaindex_knowledge_base WHERE metadata_->>'source' = 'facts'"
                ))
                new_facts_count = result.fetchone()[0]
                
                result = conn.execute(sqlalchemy.text(
                    "SELECT COUNT(*) FROM llamaindex_knowledge_base"
                ))
                total_count = result.fetchone()[0]
                
                # Commit transaction
                trans.commit()
                
                print(f"✅ Successfully merged {new_facts_count} facts")
                print(f"📊 Total documents in unified table: {total_count:,}")
                
                # Show final breakdown
                result = conn.execute(sqlalchemy.text(
                    "SELECT metadata_->>'source' as source, COUNT(*) as count FROM llamaindex_knowledge_base GROUP BY metadata_->>'source'"
                ))
                sources = result.fetchall()
                print("\n📊 FINAL UNIFIED KNOWLEDGE BASE:")
                print("=" * 40)
                for source, count in sources:
                    print(f"  • {source}: {count:,}")
                
                # Show facts breakdown
                result = conn.execute(sqlalchemy.text(
                    "SELECT metadata_->>'content_type' as fact_type, COUNT(*) as count FROM llamaindex_knowledge_base WHERE metadata_->>'source' = 'facts' GROUP BY metadata_->>'content_type'"
                ))
                fact_types = result.fetchall()
                if fact_types:
                    print("\n📋 Facts breakdown:")
                    for fact_type, count in fact_types:
                        print(f"  • {fact_type}: {count:,}")
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Error during merge: {e}")
                raise
                
    except Exception as e:
        print(f"Error merging facts: {e}")
        raise

if __name__ == "__main__":
    merge_facts_to_unified_table()