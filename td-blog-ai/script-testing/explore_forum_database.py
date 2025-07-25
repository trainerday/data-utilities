#!/usr/bin/env python3
"""
Explore TrainerDay Forum Database Structure
Understand the actual forum data available for better LlamaIndex integration
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Load environment variables
load_dotenv()

def connect_to_database():
    """Connect to PostgreSQL database"""
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 25060)),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('DB_SSLMODE', 'require')
    }
    
    print(f"Connecting to: {db_config['host']}:{db_config['port']} / {db_config['database']}")
    
    try:
        conn = psycopg2.connect(**db_config)
        print("✅ Database connection successful")
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def explore_database_schema(conn):
    """Explore database tables and their structure"""
    print("\n📊 DATABASE SCHEMA EXPLORATION")
    print("=" * 50)
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Find all tables with 'forum' in the name
        cur.execute("""
            SELECT table_name, table_schema 
            FROM information_schema.tables 
            WHERE table_name LIKE '%forum%' 
            AND table_schema NOT IN ('information_schema', 'pg_catalog')
            ORDER BY table_name
        """)
        
        forum_tables = cur.fetchall()
        
        if not forum_tables:
            print("❌ No forum tables found")
            
            # Look for any tables that might contain forum data
            print("\n🔍 Searching for related tables...")
            cur.execute("""
                SELECT table_name, table_schema 
                FROM information_schema.tables 
                WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
                ORDER BY table_name
            """)
            
            all_tables = cur.fetchall()
            print(f"Found {len(all_tables)} total tables:")
            for table in all_tables[:20]:  # Show first 20
                print(f"  - {table['table_name']}")
            
            if len(all_tables) > 20:
                print(f"  ... and {len(all_tables) - 20} more")
                
        else:
            print(f"Found {len(forum_tables)} forum-related tables:")
            
            for table in forum_tables:
                table_name = table['table_name']
                print(f"\n📋 Table: {table_name}")
                
                # Get table structure
                cur.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = %s
                    ORDER BY ordinal_position
                """, (table_name,))
                
                columns = cur.fetchall()
                print("   Columns:")
                for col in columns:
                    nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                    default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                    print(f"     {col['column_name']}: {col['data_type']} {nullable}{default}")
                
                # Get row count - quote table name for dashes
                cur.execute(f'SELECT COUNT(*) as count FROM "{table_name}"')
                count = cur.fetchone()['count']
                print(f"   Rows: {count:,}")
                
                # Show sample data if available
                if count > 0:
                    cur.execute(f'SELECT * FROM "{table_name}" LIMIT 3')
                    samples = cur.fetchall()
                    print("   Sample data:")
                    for i, sample in enumerate(samples):
                        print(f"     Row {i+1}: {dict(sample)}")

def check_existing_forum_analysis(conn):
    """Check for existing forum analysis data"""
    print("\n🔍 CHECKING EXISTING FORUM ANALYSIS")
    print("=" * 50)
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Check for forum_analysis table
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'forum_analysis'
            )
        """)
        
        has_forum_analysis = cur.fetchone()['exists']
        
        if has_forum_analysis:
            print("✅ Found forum_analysis table")
            
            # Get structure
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'forum_analysis'
                ORDER BY ordinal_position
            """)
            columns = cur.fetchall()
            print("Columns:", [col['column_name'] for col in columns])
            
            # Get counts
            cur.execute("SELECT COUNT(*) as total FROM forum_analysis")
            total = cur.fetchone()['total']
            
            cur.execute("SELECT COUNT(*) as with_qa FROM forum_analysis WHERE question IS NOT NULL AND answer IS NOT NULL")
            with_qa = cur.fetchone()['with_qa']
            
            print(f"Total rows: {total:,}")
            print(f"With Q&A pairs: {with_qa:,}")
            
            # Sample data
            if with_qa > 0:
                cur.execute("""
                    SELECT category, question, answer 
                    FROM forum_analysis 
                    WHERE question IS NOT NULL AND answer IS NOT NULL
                    LIMIT 2
                """)
                samples = cur.fetchall()
                
                print("\nSample Q&A pairs:")
                for i, sample in enumerate(samples):
                    print(f"  {i+1}. Category: {sample['category']}")
                    print(f"     Question: {sample['question'][:100]}...")
                    print(f"     Answer: {sample['answer'][:100]}...")
        else:
            print("❌ No forum_analysis table found")

def check_raw_forum_data(conn):
    """Check for raw forum data tables"""
    print("\n🔍 CHECKING RAW FORUM DATA")
    print("=" * 50)
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Check for forum_topics_raw table (from the analyzer script)
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'forum_topics_raw'
            )
        """)
        
        has_raw_topics = cur.fetchone()['exists']
        
        if has_raw_topics:
            print("✅ Found forum_topics_raw table")
            
            # Get counts
            cur.execute("SELECT COUNT(*) as total FROM forum_topics_raw")
            total = cur.fetchone()['total']
            print(f"Total raw topics: {total:,}")
            
            if total > 0:
                # Sample raw data structure
                cur.execute("""
                    SELECT topic_id, title, posts_count, 
                           jsonb_array_length(COALESCE(raw_content->'posts', '[]'::jsonb)) as actual_posts
                    FROM forum_topics_raw 
                    LIMIT 5
                """)
                samples = cur.fetchall()
                
                print("\nSample topics:")
                for sample in samples:
                    print(f"  Topic {sample['topic_id']}: {sample['title']}")
                    print(f"    Recorded posts: {sample['posts_count']}, Actual posts: {sample['actual_posts']}")
                
                # Check for processed analysis
                cur.execute("""
                    SELECT COUNT(*) as analyzed
                    FROM forum_topics_raw r
                    JOIN forum_topics t ON r.topic_id = t.topic_id
                """)
                analyzed = cur.fetchone()['analyzed']
                print(f"\nTopics with analysis: {analyzed:,}")
                
        else:
            print("❌ No forum_topics_raw table found")

def analyze_forum_data_richness(conn):
    """Analyze the richness of available forum data"""
    print("\n📈 FORUM DATA RICHNESS ANALYSIS")
    print("=" * 50)
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        try:
            # Check if we have the full forum analysis tables
            tables_to_check = [
                'forum_topics_raw', 'forum_topics', 'forum_qa_pairs', 
                'forum_voice_patterns', 'forum_insights'
            ]
            
            existing_tables = []
            for table in tables_to_check:
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = %s
                    )
                """, (table,))
                
                if cur.fetchone()['exists']:
                    existing_tables.append(table)
            
            print(f"Available tables: {existing_tables}")
            
            if 'forum_topics_raw' in existing_tables:
                # Analyze raw content richness
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_topics,
                        AVG(posts_count) as avg_posts_per_topic,
                        MAX(posts_count) as max_posts_per_topic,
                        SUM(posts_count) as total_posts
                    FROM forum_topics_raw
                """)
                
                stats = cur.fetchone()
                print(f"\nRaw Content Stats:")
                print(f"  Total topics: {stats['total_topics']:,}")
                print(f"  Total posts: {stats['total_posts']:,}")
                print(f"  Avg posts per topic: {stats['avg_posts_per_topic']:.1f}")
                print(f"  Max posts in a topic: {stats['max_posts_per_topic']}")
                
                # Check for complete conversations (more than just Q&A)
                cur.execute("""
                    SELECT COUNT(*) as rich_discussions
                    FROM forum_topics_raw
                    WHERE posts_count >= 3
                """)
                
                rich = cur.fetchone()['rich_discussions']
                print(f"  Topics with 3+ posts (discussions): {rich:,}")
                
            if 'forum_qa_pairs' in existing_tables:
                # Analyze processed Q&A pairs
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_qa_pairs,
                        COUNT(DISTINCT topic_id) as topics_with_qa,
                        AVG(LENGTH(question_content)) as avg_question_length,
                        AVG(LENGTH(response_content)) as avg_answer_length
                    FROM forum_qa_pairs
                """)
                
                qa_stats = cur.fetchone()
                print(f"\nProcessed Q&A Stats:")
                print(f"  Total Q&A pairs: {qa_stats['total_qa_pairs']:,}")
                print(f"  Topics with Q&A: {qa_stats['topics_with_qa']:,}")
                print(f"  Avg question length: {qa_stats['avg_question_length']:.0f} chars")
                print(f"  Avg answer length: {qa_stats['avg_answer_length']:.0f} chars")
                
        except Exception as e:
            print(f"Error in richness analysis: {e}")

def recommend_forum_integration_strategy(conn):
    """Recommend the best strategy for forum data integration"""
    print("\n💡 FORUM INTEGRATION RECOMMENDATIONS")
    print("=" * 50)
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Check what data is available
        has_raw = False
        has_processed = False
        has_analysis = False
        
        try:
            cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'forum_topics_raw')")
            has_raw = cur.fetchone()['exists']
            
            cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'forum_qa_pairs')")
            has_processed = cur.fetchone()['exists']
            
            cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'forum_analysis')")
            has_analysis = cur.fetchone()['exists']
            
        except Exception as e:
            print(f"Error checking tables: {e}")
        
        print(f"Data availability:")
        print(f"  ✅ Raw forum topics: {'Yes' if has_raw else 'No'}")
        print(f"  ✅ Processed Q&A pairs: {'Yes' if has_processed else 'No'}")
        print(f"  ✅ Legacy analysis: {'Yes' if has_analysis else 'No'}")
        
        print(f"\n🎯 RECOMMENDED APPROACH:")
        
        if has_raw:
            print("1. 🏆 OPTIMAL: Use raw forum data for rich context")
            print("   - Load complete topic discussions (not just Q&A)")
            print("   - Include user conversations and follow-ups") 
            print("   - Preserve thread context and relationships")
            print("   - Create documents per topic with full conversation")
            
        elif has_processed:
            print("1. 🥈 GOOD: Use processed Q&A pairs")
            print("   - More structured than raw data")
            print("   - Clear question-answer relationships")
            print("   - Good for targeted responses")
            
        elif has_analysis:
            print("1. 🥉 BASIC: Use legacy analysis table")
            print("   - Simple Q&A format")
            print("   - Limited context")
            print("   - Better than nothing")
            
        else:
            print("1. ❌ NO FORUM DATA AVAILABLE")
            print("   - Need to run forum scraper first")
            print("   - Check forum-scraper-trainerday project")
        
        print(f"\n📋 IMPLEMENTATION STEPS:")
        if has_raw:
            print("1. Create forum document loader for raw topics")
            print("2. Structure documents as complete conversations")
            print("3. Include metadata: participants, topic categories, dates")
            print("4. Chunk long discussions appropriately")
            print("5. Test retrieval quality vs. simple Q&A")
        else:
            print("1. Run forum data collection first")
            print("2. Use forum-scraper-trainerday to get raw data")
            print("3. Process with forum analysis tools")
            print("4. Then integrate with LlamaIndex")

def main():
    """Main exploration function"""
    print("🔍 EXPLORING TRAINERDAY FORUM DATABASE")
    print("=" * 60)
    
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        explore_database_schema(conn)
        check_existing_forum_analysis(conn)
        check_raw_forum_data(conn)
        analyze_forum_data_richness(conn)
        recommend_forum_integration_strategy(conn)
        
    except Exception as e:
        print(f"❌ Exploration failed: {e}")
    finally:
        conn.close()
        print(f"\n✅ Database exploration complete")

if __name__ == "__main__":
    main()