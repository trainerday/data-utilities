#!/usr/bin/env python3
"""
Unified Content Processor for TrainerDay Vector Database
Processes forum Q&A, YouTube transcripts, and blog articles into unified embeddings table

EMBEDDING MODEL CONFIGURATION:
- Uses text-embedding-3-large for optimal understanding of cycling technical content
- Configured via OPENAI_EMBEDDING_MODEL environment variable
- Always use text-embedding-3-large for human content (discussions, tutorials, documentation)
- Different models may be used for source code analysis in other projects
"""

import os
import sys
import json
import time
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import re

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import openai
import frontmatter

# Load environment variables
load_dotenv()

@dataclass
class ContentChunk:
    """Standardized content chunk for all sources"""
    source: str          # 'forum', 'youtube', 'blog'
    source_id: str       # topic_id, video_id, article_filename
    title: str           # Question, video title, article title
    content: str         # The actual text content
    metadata: Dict       # Source-specific metadata
    chunk_index: int = 0 # For multi-chunk content

class UnifiedContentProcessor:
    def __init__(self, db_config: Dict, openai_api_key: Optional[str] = None):
        self.db_config = db_config
        self.db_connection = None
        
        # OpenAI setup
        self.openai_client = openai.OpenAI(
            api_key=openai_api_key or os.getenv('OPENAI_API_KEY')
        )
        
        # Rate limiting
        self.last_api_call = 0
        self.min_api_interval = 0.1  # 10 requests per second max
        
        # Processing statistics
        self.stats = {
            'forum': {'processed': 0, 'errors': 0},
            'youtube': {'processed': 0, 'errors': 0},
            'blog': {'processed': 0, 'errors': 0},
            'project_feature_map': {'processed': 0, 'errors': 0},
            'total_embeddings': 0
        }

    def connect_db(self):
        """Connect to PostgreSQL database"""
        try:
            self.db_connection = psycopg2.connect(**self.db_config)
            print("✓ Connected to database")
            self.setup_tables()
        except Exception as e:
            raise Exception(f"Failed to connect to database: {e}")

    def setup_tables(self):
        """Create required tables with pgvector support"""
        schema_sql = """
        -- Enable pgvector extension
        CREATE EXTENSION IF NOT EXISTS vector;
        
        -- Create unified content embeddings table
        -- NOTE: Vector dimensions must match OPENAI_EMBEDDING_DIMENSIONS environment variable
        CREATE TABLE IF NOT EXISTS content_embeddings (
            id SERIAL PRIMARY KEY,
            source VARCHAR(20) NOT NULL,        -- 'forum', 'blog', 'youtube', 'project_feature_map'
            source_id VARCHAR(100) NOT NULL,    -- topic_id, article_filename, video_id
            title TEXT NOT NULL,
            content TEXT NOT NULL,              -- The actual text content for retrieval
            embedding vector(1536) NOT NULL,    -- Configurable via OPENAI_EMBEDDING_DIMENSIONS (default: 1536)
            metadata JSONB,                     -- source-specific fields
            chunk_index INTEGER DEFAULT 0,     -- for multi-chunk content
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(source, source_id, chunk_index)
        );
        
        -- Create processing metadata table for change detection
        CREATE TABLE IF NOT EXISTS content_processing_metadata (
            id SERIAL PRIMARY KEY,
            source VARCHAR(20) NOT NULL,
            source_path TEXT,
            last_processed_timestamp TIMESTAMP,
            last_processed_id INTEGER,
            file_hash TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(source, source_path)
        );
        
        -- Create indexes for fast similarity search
        CREATE INDEX IF NOT EXISTS idx_content_embeddings_similarity 
        ON content_embeddings USING ivfflat (embedding vector_cosine_ops);
        
        CREATE INDEX IF NOT EXISTS idx_content_embeddings_source 
        ON content_embeddings(source, source_id);
        
        CREATE INDEX IF NOT EXISTS idx_content_embeddings_source_type 
        ON content_embeddings(source);
        """
        
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute(schema_sql)
                self.db_connection.commit()
                print("✓ Database tables and indexes ready")
        except Exception as e:
            self.db_connection.rollback()
            raise Exception(f"Failed to create tables: {e}")

    def create_embedding(self, text: str) -> Optional[List[float]]:
        """Create embedding using OpenAI API with rate limiting"""
        # Rate limiting
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        
        if time_since_last_call < self.min_api_interval:
            sleep_time = self.min_api_interval - time_since_last_call
            time.sleep(sleep_time)

        try:
            # Use environment variables for embedding model configuration
            embedding_model = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-large')
            embedding_dimensions = int(os.getenv('OPENAI_EMBEDDING_DIMENSIONS', '1536'))
            
            response = self.openai_client.embeddings.create(
                model=embedding_model,
                input=text,
                dimensions=embedding_dimensions
            )
            
            self.last_api_call = time.time()
            embedding = response.data[0].embedding
            return embedding
            
        except Exception as e:
            print(f"  ❌ OpenAI API error: {e}")
            return None

    def store_content_chunk(self, chunk: ContentChunk) -> bool:
        """Store content chunk with embedding in unified table"""
        if not self.db_connection:
            return False

        # Create embedding for the content
        embedding = self.create_embedding(chunk.content)
        if not embedding:
            return False

        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO content_embeddings 
                    (source, source_id, title, content, embedding, metadata, chunk_index)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (source, source_id, chunk_index) DO UPDATE SET
                        title = EXCLUDED.title,
                        content = EXCLUDED.content,
                        embedding = EXCLUDED.embedding,
                        metadata = EXCLUDED.metadata,
                        created_at = NOW()
                """, (
                    chunk.source,
                    chunk.source_id,
                    chunk.title,
                    chunk.content,
                    embedding,
                    json.dumps(chunk.metadata),
                    chunk.chunk_index
                ))
                
                self.db_connection.commit()
                self.stats['total_embeddings'] += 1
                return True
                
        except Exception as e:
            self.db_connection.rollback()
            print(f"  ❌ Database error storing chunk: {e}")
            return False

    # ===========================================
    # FORUM Q&A EXTRACTOR (PostgreSQL)
    # ===========================================
    
    def extract_forum_content(self) -> List[ContentChunk]:
        """Extract Q&A pairs from forum_analysis table"""
        chunks = []
        
        try:
            # Get last processed ID for incremental updates
            last_processed_id = self.get_last_processed_id('forum')
            
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id, question_content, response_content, topic_id, created_at
                    FROM forum_qa_pairs 
                    WHERE id > %s
                      AND question_content IS NOT NULL 
                      AND response_content IS NOT NULL
                      AND LENGTH(TRIM(question_content)) > 0
                      AND LENGTH(TRIM(response_content)) > 0
                    ORDER BY id
                """, (last_processed_id,))
                
                qa_pairs = cursor.fetchall()
                print(f"✓ Found {len(qa_pairs)} new forum Q&A pairs")
                
                for qa in qa_pairs:
                    # Format Q&A as single content chunk
                    content = f"Question: {qa['question_content'].strip()}\nAnswer: {qa['response_content'].strip()}"
                    
                    chunk = ContentChunk(
                        source='forum',
                        source_id=str(qa['id']),
                        title=qa['question_content'].strip(),
                        content=content,
                        metadata={
                            'topic_id': qa['topic_id'],
                            'question': qa['question_content'].strip(),
                            'answer': qa['response_content'].strip(),
                            'created_at': qa['created_at'].isoformat() if qa['created_at'] else None
                        }
                    )
                    chunks.append(chunk)
                
                # Update last processed ID
                if qa_pairs:
                    self.update_processing_metadata('forum', last_processed_id=qa_pairs[-1]['id'])
                    
        except Exception as e:
            print(f"❌ Error extracting forum content: {e}")
            self.stats['forum']['errors'] += 1
            
        self.stats['forum']['processed'] = len(chunks)
        return chunks

    # ===========================================
    # YOUTUBE EXTRACTOR (JSON Files)
    # ===========================================
    
    def extract_youtube_content(self, youtube_dir: str = "youtube_content") -> List[ContentChunk]:
        """Extract content from YouTube transcript JSON files"""
        chunks = []
        youtube_path = Path(youtube_dir)
        
        if not youtube_path.exists():
            print(f"⚠️ YouTube directory not found: {youtube_path}")
            return chunks
            
        json_files = list(youtube_path.glob("video_*.json"))
        print(f"✓ Found {len(json_files)} YouTube video files")
        
        for json_file in json_files:
            try:
                # Check if file has been processed
                if self.is_file_already_processed('youtube', str(json_file)):
                    continue
                    
                with open(json_file, 'r', encoding='utf-8') as f:
                    video_data = json.load(f)
                
                video_id = video_data.get('video_id', json_file.stem)
                video_title = video_data.get('title', 'Untitled Video')
                
                # Extract transcript text from the JSON structure
                transcript_data = video_data.get('transcript', {})
                if isinstance(transcript_data, dict):
                    transcript_text = transcript_data.get('full_text', '')
                else:
                    transcript_text = str(transcript_data) if transcript_data else ''
                
                if not transcript_text or not transcript_text.strip():
                    print(f"  ⚠️ No transcript text found for {video_id}")
                    continue
                
                # Chunk transcript into time-based segments (60-90 seconds worth of content)
                video_chunks = self.chunk_youtube_transcript(transcript_text, video_data)
                
                for i, chunk_data in enumerate(video_chunks):
                    chunk = ContentChunk(
                        source='youtube',
                        source_id=video_id,
                        title=f"{video_title} (Part {i+1})",
                        content=chunk_data['content'],
                        metadata={
                            'video_title': video_title,
                            'video_id': video_id,
                            'duration': video_data.get('duration'),
                            'start_time': chunk_data.get('start_time'),
                            'end_time': chunk_data.get('end_time'),
                            'topics': video_data.get('topics', []),
                            'description': video_data.get('description', ''),
                            'url': f"https://youtube.com/watch?v={video_id}"
                        },
                        chunk_index=i
                    )
                    chunks.append(chunk)
                
                # Mark file as processed
                self.update_processing_metadata('youtube', source_path=str(json_file), 
                                              file_hash=self.get_file_hash(json_file))
                
            except Exception as e:
                print(f"❌ Error processing YouTube file {json_file}: {e}")
                self.stats['youtube']['errors'] += 1
                continue
        
        self.stats['youtube']['processed'] = len(chunks)
        return chunks

    def chunk_youtube_transcript(self, transcript_text: str, video_data: Dict) -> List[Dict]:
        """Chunk YouTube transcript into time-based segments"""
        chunks = []
        
        # Check if we have segment data with timestamps
        transcript_data = video_data.get('transcript', {})
        if isinstance(transcript_data, dict) and 'segments' in transcript_data:
            # Use timestamp-based chunking if segments are available
            chunks = self.chunk_by_timestamps(transcript_data['segments'])
        else:
            # Fall back to simple text chunking
            chunks = self.chunk_by_text_length(transcript_text)
        
        return chunks

    def chunk_by_timestamps(self, segments: List[Dict]) -> List[Dict]:
        """Chunk transcript using timestamp segments for better context"""
        chunks = []
        current_chunk = []
        current_length = 0
        chunk_start_time = None
        target_chunk_size = 1200  # characters
        
        for segment in segments:
            segment_text = segment.get('text', '').strip()
            segment_start = segment.get('start', 0)
            
            if not segment_text:
                continue
                
            # Set start time for first segment in chunk
            if chunk_start_time is None:
                chunk_start_time = segment_start
            
            current_chunk.append(segment_text)
            current_length += len(segment_text) + 1  # +1 for space
            
            # Create chunk when we reach target size or have substantial content
            if current_length >= target_chunk_size and len(current_chunk) >= 3:
                chunk_content = ' '.join(current_chunk)
                chunks.append({
                    'content': chunk_content,
                    'start_time': chunk_start_time,
                    'end_time': segment.get('start', 0) + segment.get('duration', 0)
                })
                
                current_chunk = []
                current_length = 0
                chunk_start_time = None
        
        # Add remaining content
        if current_chunk:
            chunk_content = ' '.join(current_chunk)
            chunks.append({
                'content': chunk_content,
                'start_time': chunk_start_time,
                'end_time': segments[-1].get('start', 0) + segments[-1].get('duration', 0) if segments else None
            })
        
        return chunks

    def chunk_by_text_length(self, transcript_text: str) -> List[Dict]:
        """Simple text-based chunking when timestamps aren't available"""
        chunks = []
        chunk_size = 1500  # characters
        words = transcript_text.split()
        
        current_chunk = []
        current_length = 0
        
        for word in words:
            current_chunk.append(word)
            current_length += len(word) + 1  # +1 for space
            
            if current_length >= chunk_size:
                chunk_content = ' '.join(current_chunk)
                chunks.append({
                    'content': chunk_content,
                    'start_time': None,
                    'end_time': None
                })
                current_chunk = []
                current_length = 0
        
        # Add remaining content
        if current_chunk:
            chunk_content = ' '.join(current_chunk)
            chunks.append({
                'content': chunk_content,
                'start_time': None,
                'end_time': None
            })
        
        return chunks

    # ===========================================
    # BLOG EXTRACTOR (Markdown Files)
    # ===========================================
    
    def extract_blog_content(self, blog_dir: str = "source-data/blog_articles") -> List[ContentChunk]:
        """Extract content from blog Markdown files"""
        chunks = []
        blog_path = Path(blog_dir)
        
        if not blog_path.exists():
            print(f"⚠️ Blog directory not found: {blog_path}")
            return chunks
            
        md_files = list(blog_path.glob("*.md"))
        print(f"✓ Found {len(md_files)} blog articles")
        
        for md_file in md_files:
            try:
                # Check if file has been processed
                if self.is_file_already_processed('blog', str(md_file)):
                    print(f"  ⏭️ Skipping already processed: {md_file.name}")
                    continue
                    
                print(f"  📄 Processing new file: {md_file.name}")
                    
                # Parse frontmatter and content
                with open(md_file, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)
                
                title = post.metadata.get('title', md_file.stem)
                content = post.content
                
                if not content.strip():
                    continue
                
                # Chunk by sections (headers)
                blog_chunks = self.chunk_blog_content(content, post.metadata)
                
                for i, chunk_content in enumerate(blog_chunks):
                    # Truncate source_id to fit database constraint (100 chars)
                    source_id = md_file.stem[:95] if len(md_file.stem) > 95 else md_file.stem
                    
                    chunk = ContentChunk(
                        source='blog',
                        source_id=source_id,
                        title=f"{title} (Section {i+1})" if len(blog_chunks) > 1 else title,
                        content=chunk_content,
                        metadata={
                            'article_title': title,
                            'filename': md_file.name,
                            'category': post.metadata.get('category', 'general'),
                            'tags': post.metadata.get('tags', []),
                            'engagement': post.metadata.get('engagement', 'unknown'),
                            'date': str(post.metadata.get('date', '')),
                            'description': post.metadata.get('description', ''),
                            'section_index': i
                        },
                        chunk_index=i
                    )
                    chunks.append(chunk)
                
                # Mark file as processed
                self.update_processing_metadata('blog', source_path=str(md_file), 
                                              file_hash=self.get_file_hash(md_file))
                
            except Exception as e:
                print(f"❌ Error processing blog file {md_file}: {e}")
                self.stats['blog']['errors'] += 1
                continue
        
        self.stats['blog']['processed'] = len(chunks)
        return chunks

    def chunk_blog_content(self, content: str, metadata: Dict) -> List[str]:
        """Chunk blog content by sections (headers)"""
        # Split by markdown headers
        sections = re.split(r'\n#{1,6}\s+', content)
        
        chunks = []
        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            # If section is too long, split further
            if len(section) > 2000:
                # Split by paragraphs
                paragraphs = section.split('\n\n')
                current_chunk = []
                current_length = 0
                
                for para in paragraphs:
                    if current_length + len(para) > 1500 and current_chunk:
                        chunks.append('\n\n'.join(current_chunk))
                        current_chunk = [para]
                        current_length = len(para)
                    else:
                        current_chunk.append(para)
                        current_length += len(para) + 2  # +2 for \n\n
                
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
            else:
                chunks.append(section)
        
        return chunks

    # ===========================================
    # PROJECT FEATURE MAP EXTRACTOR (Markdown Files)
    # ===========================================
    
    def extract_project_feature_map_content(self, feature_dir: str = "source-data/project_feature_map") -> List[ContentChunk]:
        """Extract content from project feature map Markdown files"""
        chunks = []
        feature_path = Path(feature_dir)
        
        if not feature_path.exists():
            print(f"⚠️ Feature map directory not found: {feature_path}")
            return chunks
            
        md_files = list(feature_path.glob("*.md"))
        print(f"✓ Found {len(md_files)} feature map files")
        
        for md_file in md_files:
            try:
                # Check if file has been processed
                if self.is_file_already_processed('project_feature_map', str(md_file)):
                    continue
                    
                # Parse frontmatter and content
                with open(md_file, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)
                
                title = post.metadata.get('title', md_file.stem)
                content = post.content
                
                if not content.strip():
                    continue
                
                # Chunk by feature sections (headers)
                feature_chunks = self.chunk_feature_map_content(content, post.metadata)
                
                for i, chunk_data in enumerate(feature_chunks):
                    chunk = ContentChunk(
                        source='project_feature_map',
                        source_id=md_file.stem,
                        title=f"{chunk_data['section_title']}" if chunk_data['section_title'] else title,
                        content=chunk_data['content'],
                        metadata={
                            'document_title': title,
                            'filename': md_file.name,
                            'section_title': chunk_data['section_title'],
                            'category': chunk_data['category'],
                            'feature_type': chunk_data.get('feature_type', 'general'),
                            'platform': chunk_data.get('platform', 'general'),
                            'type': post.metadata.get('type', 'note'),
                            'permalink': post.metadata.get('permalink', ''),
                            'section_level': chunk_data['section_level'],
                            'section_index': i
                        },
                        chunk_index=i
                    )
                    chunks.append(chunk)
                
                # Mark file as processed
                self.update_processing_metadata('project_feature_map', source_path=str(md_file), 
                                              file_hash=self.get_file_hash(md_file))
                
            except Exception as e:
                print(f"❌ Error processing feature map file {md_file}: {e}")
                self.stats['project_feature_map']['errors'] += 1
                continue
        
        self.stats['project_feature_map']['processed'] = len(chunks)
        return chunks

    def chunk_feature_map_content(self, content: str, metadata: Dict) -> List[Dict]:
        """Chunk feature map content by sections and features"""
        chunks = []
        
        # Split by markdown headers
        lines = content.split('\n')
        current_section = []
        current_header = None
        current_level = 0
        section_category = "General"
        
        for line in lines:
            # Check if this is a header line
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            
            if header_match:
                # Process previous section if it exists
                if current_section:
                    section_content = '\n'.join(current_section).strip()
                    if section_content and len(section_content) > 50:  # Only process substantial content
                        
                        # Determine feature type and platform from content
                        feature_type = self.determine_feature_type(section_content)
                        platform = self.determine_platform(section_content)
                        
                        chunks.append({
                            'content': section_content,
                            'section_title': current_header,
                            'category': section_category,
                            'feature_type': feature_type,
                            'platform': platform,
                            'section_level': current_level
                        })
                        
                        # If section is too long, split it further
                        if len(section_content) > 2000:
                            sub_chunks = self.split_long_feature_section(section_content, current_header, section_category)
                            chunks.extend(sub_chunks)
                
                # Start new section
                header_level = len(header_match.group(1))
                header_text = header_match.group(2).strip()
                
                current_header = header_text
                current_level = header_level
                current_section = []
                
                # Update category based on main headers (level 2)
                if header_level == 2:
                    section_category = header_text
                    
            else:
                # Add line to current section
                current_section.append(line)
        
        # Process final section
        if current_section:
            section_content = '\n'.join(current_section).strip()
            if section_content and len(section_content) > 50:
                feature_type = self.determine_feature_type(section_content)
                platform = self.determine_platform(section_content)
                
                chunks.append({
                    'content': section_content,
                    'section_title': current_header,
                    'category': section_category,
                    'feature_type': feature_type,
                    'platform': platform,
                    'section_level': current_level
                })
        
        return chunks

    def determine_feature_type(self, content: str) -> str:
        """Determine if feature is premium, free, or general based on content"""
        content_lower = content.lower()
        
        if any(keyword in content_lower for keyword in ['premium', 'subscription', 'paid', 'unlimited', 'advanced']):
            return 'premium'
        elif any(keyword in content_lower for keyword in ['free', 'basic', 'limited']):
            return 'free'
        else:
            return 'general'

    def determine_platform(self, content: str) -> str:
        """Determine platform (web, mobile, api) based on content"""
        content_lower = content.lower()
        
        if any(keyword in content_lower for keyword in ['ios', 'android', 'mobile app', 'iphone', 'ipad']):
            return 'mobile'
        elif any(keyword in content_lower for keyword in ['api', 'webhook', 'developer']):
            return 'api'
        elif any(keyword in content_lower for keyword in ['web', 'browser', 'trainerday.com']):
            return 'web'
        else:
            return 'general'

    def split_long_feature_section(self, content: str, header: str, category: str) -> List[Dict]:
        """Split long feature sections into smaller chunks"""
        chunks = []
        
        # Split by feature items (lines starting with "- **")
        feature_items = re.split(r'\n- \*\*', content)
        
        current_chunk = []
        current_length = 0
        
        for i, item in enumerate(feature_items):
            if i > 0:  # Add back the bullet point marker for non-first items
                item = '- **' + item
                
            item_length = len(item)
            
            if current_length + item_length > 1500 and current_chunk:
                # Create chunk from current items
                chunk_content = '\n'.join(current_chunk)
                chunks.append({
                    'content': chunk_content,
                    'section_title': f"{header} (Part {len(chunks) + 1})",
                    'category': category,
                    'feature_type': self.determine_feature_type(chunk_content),
                    'platform': self.determine_platform(chunk_content),
                    'section_level': 3
                })
                
                current_chunk = [item]
                current_length = item_length
            else:
                current_chunk.append(item)
                current_length += item_length
        
        # Add remaining items
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            chunks.append({
                'content': chunk_content,
                'section_title': f"{header} (Part {len(chunks) + 1})" if chunks else header,
                'category': category,
                'feature_type': self.determine_feature_type(chunk_content),
                'platform': self.determine_platform(chunk_content),
                'section_level': 3
            })
        
        return chunks

    # ===========================================
    # CHANGE DETECTION & METADATA
    # ===========================================
    
    def get_last_processed_id(self, source: str) -> int:
        """Get last processed ID for incremental updates"""
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    SELECT last_processed_id 
                    FROM content_processing_metadata 
                    WHERE source = %s AND source_path IS NULL
                """, (source,))
                
                result = cursor.fetchone()
                return result[0] if result and result[0] else 0
                
        except Exception:
            return 0

    def is_file_already_processed(self, source: str, file_path: str) -> bool:
        """Check if file has been processed and hasn't changed"""
        try:
            current_hash = self.get_file_hash(Path(file_path))
            
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    SELECT file_hash 
                    FROM content_processing_metadata 
                    WHERE source = %s AND source_path = %s
                """, (source, file_path))
                
                result = cursor.fetchone()
                return result and result[0] == current_hash
                
        except Exception:
            return False

    def get_file_hash(self, file_path: Path) -> str:
        """Get SHA256 hash of file content"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""

    def update_processing_metadata(self, source: str, source_path: str = None, 
                                 last_processed_id: int = None, file_hash: str = None):
        """Update processing metadata for change detection"""
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO content_processing_metadata 
                    (source, source_path, last_processed_id, file_hash, updated_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    ON CONFLICT (source, source_path) DO UPDATE SET
                        last_processed_id = COALESCE(EXCLUDED.last_processed_id, content_processing_metadata.last_processed_id),
                        file_hash = COALESCE(EXCLUDED.file_hash, content_processing_metadata.file_hash),
                        updated_at = NOW()
                """, (source, source_path, last_processed_id, file_hash))
                
                self.db_connection.commit()
                
        except Exception as e:
            print(f"⚠️ Failed to update processing metadata: {e}")
            self.db_connection.rollback()

    # ===========================================
    # MAIN PROCESSING PIPELINE
    # ===========================================
    
    def process_all_content(self, youtube_dir: str = None, blog_dir: str = None, feature_dir: str = None):
        """Main processing pipeline for all content sources"""
        print("🚀 Starting unified content processing...")
        start_time = time.time()
        
        all_chunks = []
        
        # 1. Extract Forum Q&A (PostgreSQL)
        print("\n📊 Processing Forum Q&A...")
        forum_chunks = self.extract_forum_content()
        all_chunks.extend(forum_chunks)
        
        # 2. Extract YouTube Content (JSON files)
        print("\n🎥 Processing YouTube Content...")
        youtube_chunks = self.extract_youtube_content(youtube_dir or "source-data/youtube_content")
        all_chunks.extend(youtube_chunks)
        
        # 3. Extract Blog Content (Markdown files)
        print("\n📝 Processing Blog Articles...")
        blog_chunks = self.extract_blog_content(blog_dir or "source-data/blog_articles")
        all_chunks.extend(blog_chunks)
        
        # 4. Extract Project Feature Map (Markdown files)
        print("\n🗺️ Processing Project Feature Map...")
        feature_chunks = self.extract_project_feature_map_content(feature_dir or "source-data/project_feature_map")
        all_chunks.extend(feature_chunks)
        
        print(f"\n🔄 Processing {len(all_chunks)} total content chunks...")
        
        # 4. Store all chunks with embeddings
        processed_count = 0
        for i, chunk in enumerate(all_chunks, 1):
            print(f"[{i}/{len(all_chunks)}] Processing {chunk.source}: {chunk.title[:50]}...")
            
            if self.store_content_chunk(chunk):
                processed_count += 1
                print(f"  ✅ Stored successfully")
            else:
                print(f"  ❌ Failed to store")
            
            # Progress update every 10 items
            if i % 10 == 0:
                elapsed = time.time() - start_time
                rate = i / elapsed if elapsed > 0 else 0
                print(f"\n📊 Progress: {i}/{len(all_chunks)} ({(i/len(all_chunks))*100:.1f}%) - {rate:.1f} items/sec")

        # Final statistics
        elapsed_time = time.time() - start_time
        print(f"\n🎯 UNIFIED CONTENT PROCESSING COMPLETE")
        print(f"=" * 50)
        print(f"Forum Q&A: {self.stats['forum']['processed']} processed, {self.stats['forum']['errors']} errors")
        print(f"YouTube: {self.stats['youtube']['processed']} processed, {self.stats['youtube']['errors']} errors")
        print(f"Blog: {self.stats['blog']['processed']} processed, {self.stats['blog']['errors']} errors")
        print(f"Feature Map: {self.stats['project_feature_map']['processed']} processed, {self.stats['project_feature_map']['errors']} errors")
        print(f"Total embeddings created: {self.stats['total_embeddings']}")
        print(f"Time elapsed: {elapsed_time:.1f} seconds")
        
        if processed_count > 0:
            rate = processed_count / elapsed_time
            print(f"Processing rate: {rate:.2f} chunks/second")
            
            # Estimate OpenAI cost
            estimated_cost = self.stats['total_embeddings'] * 0.0001
            print(f"Estimated OpenAI cost: ${estimated_cost:.4f}")

    def similarity_search(self, query_text: str, source_filter: str = None, limit: int = 10):
        """Search across all content sources"""
        print(f"\n🔍 Searching for: '{query_text}'")
        if source_filter:
            print(f"Filtered to source: {source_filter}")
        
        # Create embedding for query
        query_embedding = self.create_embedding(query_text)
        if not query_embedding:
            print("❌ Could not create query embedding")
            return []

        try:
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                where_clause = "WHERE 1=1"
                params = []
                
                # Add similarity calculation parameters
                params.append(query_embedding)  # For similarity score
                params.append(query_embedding)  # For ORDER BY
                
                if source_filter:
                    where_clause += " AND source = %s"
                    params.append(source_filter)
                
                params.append(limit)
                
                cursor.execute(f"""
                    SELECT 
                        source, source_id, title, content, metadata, chunk_index,
                        1 - (embedding <=> %s::vector) AS similarity_score
                    FROM content_embeddings
                    {where_clause}
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                """, params)
                
                results = cursor.fetchall()
                
                print(f"\n📊 Found {len(results)} similar results:")
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. [{result['source'].upper()}] {result['title']}")
                    print(f"   Similarity: {result['similarity_score']:.3f}")
                    print(f"   Content: {result['content'][:150]}...")
                    
                return results
                    
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified content processor for TrainerDay vector database")
    parser.add_argument("--youtube-dir", help="YouTube content directory (default: source-data/youtube_content)")
    parser.add_argument("--blog-dir", help="Blog articles directory (default: source-data/blog_articles)")
    parser.add_argument("--feature-dir", help="Feature map directory (default: source-data/project_feature_map)")
    parser.add_argument("--search", help="Test search query")
    parser.add_argument("--source-filter", choices=["forum", "youtube", "blog", "project_feature_map"], help="Filter search by source")
    
    args = parser.parse_args()
    
    # Database configuration from environment
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('DB_SSLMODE', 'require')
    }
    
    # Validate configuration
    if not all([db_config['host'], db_config['database'], db_config['user'], db_config['password']]):
        print("❌ Database configuration incomplete. Please set environment variables:")
        print("   Required: DB_HOST, DB_DATABASE, DB_USERNAME, DB_PASSWORD")
        sys.exit(1)
        
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key required. Please set OPENAI_API_KEY environment variable.")
        sys.exit(1)

    try:
        processor = UnifiedContentProcessor(db_config=db_config)
        processor.connect_db()
        
        if args.search:
            # Test search functionality
            processor.similarity_search(args.search, source_filter=args.source_filter)
        else:
            # Process all content
            processor.process_all_content(
                youtube_dir=args.youtube_dir,
                blog_dir=args.blog_dir,
                feature_dir=args.feature_dir
            )
        
        print("✅ Process completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# USAGE EXAMPLES:
#
# Process all content sources:
# python unified_content_processor.py
#
# Process with custom directories:
# python unified_content_processor.py --youtube-dir /path/to/youtube --blog-dir /path/to/blog
#
# Test search across all sources:
# python unified_content_processor.py --search "How to sync with Garmin?"
#
# Test search in specific source:
# python unified_content_processor.py --search "power zones" --source-filter youtube
#
# Search TrainerDay features:
# python unified_content_processor.py --search "premium features" --source-filter project_feature_map