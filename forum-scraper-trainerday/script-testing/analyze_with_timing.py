#!/usr/bin/env python3
"""
Analyze a topic with detailed timing breakdown to identify bottlenecks
"""

import os
import sys
import time
import json
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.analyze_forum_topics import ForumTopicAnalyzerV2
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables
load_dotenv()

def analyze_with_detailed_timing(topic_id):
    """Analyze a topic with step-by-step timing"""
    
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('DB_SSLMODE', 'require')
    }
    
    if os.getenv('DB_SSLROOTCERT'):
        ssl_cert_filename = os.getenv('DB_SSLROOTCERT')
        ssl_cert_path = Path(__file__).parent.parent / ssl_cert_filename
        if ssl_cert_path.exists():
            db_config['sslrootcert'] = str(ssl_cert_path)
    
    print(f"🔍 Detailed Timing Analysis for Topic {topic_id}")
    print("=" * 50)
    
    total_start = time.time()
    
    try:
        # Step 1: Initialize analyzer
        step_start = time.time()
        analyzer = ForumTopicAnalyzerV2(db_config=db_config)
        step1_time = time.time() - step_start
        print(f"Step 1 - Initialize analyzer: {step1_time:.3f}s")
        
        # Step 2: Connect to database
        step_start = time.time()
        analyzer.connect_to_database()
        step2_time = time.time() - step_start
        print(f"Step 2 - Connect to database: {step2_time:.3f}s")
        
        # Step 3: Get raw content from database
        step_start = time.time()
        with analyzer.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT raw_content FROM forum_topics_raw WHERE topic_id = %s
            """, (topic_id,))
            
            result = cursor.fetchone()
            if not result:
                print(f"❌ Topic {topic_id} not found")
                return
            
            raw_content = result['raw_content']
        step3_time = time.time() - step_start
        print(f"Step 3 - Get raw content: {step3_time:.3f}s")
        
        # Step 4: Prepare data for analysis
        step_start = time.time()
        cleaned_data = analyzer.prepare_topic_for_analysis(raw_content)
        step4_time = time.time() - step_start
        print(f"Step 4 - Prepare data: {step4_time:.3f}s")
        
        # Step 5: Create prompt
        step_start = time.time()
        prompt = analyzer.get_analysis_prompt()
        topic_json = json.dumps(cleaned_data, indent=2)
        full_prompt = prompt + topic_json
        step5_time = time.time() - step_start
        print(f"Step 5 - Create prompt: {step5_time:.3f}s")
        print(f"         Prompt size: {len(full_prompt)} characters")
        print(f"         Topic JSON size: {len(topic_json)} characters")
        
        # Step 6: OpenAI API call (THIS IS LIKELY THE BOTTLENECK)
        step_start = time.time()
        print(f"Step 6 - Making OpenAI API call with gpt-4...")
        
        response = analyzer.openai_client.chat.completions.create(
            model="gpt-4",  # This is the slow model
            messages=[
                {"role": "system", "content": "You are an expert at analyzing forum discussions for content strategy insights."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.1
        )
        step6_time = time.time() - step_start
        print(f"Step 6 - OpenAI API call: {step6_time:.3f}s ⬅️ THIS IS THE BOTTLENECK!")
        
        # Step 7: Parse response
        step_start = time.time()
        analysis_text = response.choices[0].message.content.strip()
        
        # Extract JSON
        if "```json" in analysis_text:
            json_start = analysis_text.find("```json") + 7
            json_end = analysis_text.find("```", json_start)
            json_text = analysis_text[json_start:json_end].strip()
        else:
            json_text = analysis_text
        
        analysis = json.loads(json_text)
        step7_time = time.time() - step_start
        print(f"Step 7 - Parse response: {step7_time:.3f}s")
        
        total_time = time.time() - total_start
        print(f"\n📊 TIMING BREAKDOWN:")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  OpenAI API: {step6_time:.3f}s ({(step6_time/total_time)*100:.1f}% of total)")
        print(f"  Database ops: {(step2_time + step3_time):.3f}s ({((step2_time + step3_time)/total_time)*100:.1f}% of total)")
        print(f"  Data processing: {(step4_time + step5_time + step7_time):.3f}s ({((step4_time + step5_time + step7_time)/total_time)*100:.1f}% of total)")
        
        qa_count = len(analysis.get('qa_pairs', []))
        category = analysis.get('topic_summary', {}).get('analysis_category', 'Unknown')
        print(f"\n✅ Analysis successful: {qa_count} Q&A pairs, {category}")
        
        analyzer.close_database_connection()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key required")
        return
    
    # Get a topic to analyze
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('DB_SSLMODE', 'require')
    }
    
    if os.getenv('DB_SSLROOTCERT'):
        ssl_cert_filename = os.getenv('DB_SSLROOTCERT')
        ssl_cert_path = Path(__file__).parent.parent / ssl_cert_filename
        if ssl_cert_path.exists():
            db_config['sslrootcert'] = str(ssl_cert_path)
    
    try:
        connection = psycopg2.connect(**db_config)
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT r.topic_id, r.title, r.posts_count
                FROM forum_topics_raw r
                LEFT JOIN forum_topics t ON r.topic_id = t.topic_id
                WHERE t.topic_id IS NULL
                AND (jsonb_array_length(COALESCE(r.raw_content -> 'posts', '[]'::jsonb)) > 0
                     OR jsonb_array_length(COALESCE(r.raw_content -> 'post_stream' -> 'posts', '[]'::jsonb)) > 0)
                ORDER BY r.topic_id DESC
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            if result:
                topic_id = result['topic_id']
                title = result['title']
                posts_count = result['posts_count']
                
                print(f"Testing with: Topic {topic_id} - {title} ({posts_count} posts)")
                print()
                
                analyze_with_detailed_timing(topic_id)
            else:
                print("No unprocessed topics found")
                
        connection.close()
        
    except Exception as e:
        print(f"Error getting topic: {e}")

if __name__ == "__main__":
    main()