#!/usr/bin/env python3
"""
Advanced Content Chunking Strategy for Vector Embeddings
Optimized for different content types: Forum Q&A, Blog Articles, YouTube Transcripts
"""

import re
import json
from typing import List, Dict, Tuple
from pathlib import Path

class ContentChunker:
    def __init__(self):
        self.chunk_sizes = {
            'forum_qa': (200, 800),      # Min, Max characters
            'blog_section': (500, 1500),
            'youtube_segment': (800, 2000)
        }
    
    def chunk_forum_qa(self, question: str, answer: str, metadata: Dict) -> List[Dict]:
        """
        Forum Q&A: Question + Answer as single semantic unit
        """
        qa_text = f"Question: {question.strip()}\nAnswer: {answer.strip()}"
        
        # If too long, consider splitting
        if len(qa_text) > self.chunk_sizes['forum_qa'][1]:
            # Try to split long answers at natural breakpoints
            return self._split_long_qa(question, answer, metadata)
        
        return [{
            'text': qa_text,
            'type': 'forum_qa',
            'question': question,
            'answer': answer,
            'metadata': metadata,
            'chunk_index': 0
        }]
    
    def chunk_blog_article(self, content: str, frontmatter: Dict) -> List[Dict]:
        """
        Blog Articles: Section-based chunking with title context
        """
        chunks = []
        
        # Extract title and metadata for context
        title_context = f"Article: {frontmatter.get('title', '')}\n"
        title_context += f"Category: {frontmatter.get('category', '')}\n"
        title_context += f"Tags: {', '.join(frontmatter.get('tags', []))}\n\n"
        
        # Split by headers (H1, H2, H3)
        sections = self._split_by_headers(content)
        
        # Handle introduction (usually before first header)
        if sections and not sections[0].get('header'):
            intro_text = title_context + sections[0]['content']
            if len(intro_text) >= self.chunk_sizes['blog_section'][0]:
                chunks.append({
                    'text': intro_text,
                    'type': 'blog_intro',
                    'title': frontmatter.get('title', ''),
                    'section': 'introduction',
                    'metadata': frontmatter,
                    'chunk_index': 0
                })
            sections = sections[1:]  # Remove intro from sections
        
        # Process each section
        for i, section in enumerate(sections):
            section_text = f"{title_context}Section: {section['header']}\n\n{section['content']}"
            
            # Skip very short sections
            if len(section_text) < self.chunk_sizes['blog_section'][0]:
                continue
            
            # If section is too long, split it
            if len(section_text) > self.chunk_sizes['blog_section'][1]:
                sub_chunks = self._split_long_section(section_text, section['header'], frontmatter)
                chunks.extend(sub_chunks)
            else:
                chunks.append({
                    'text': section_text,
                    'type': 'blog_section',
                    'title': frontmatter.get('title', ''),
                    'section': section['header'],
                    'metadata': frontmatter,
                    'chunk_index': len(chunks)
                })
        
        return chunks
    
    def chunk_youtube_transcript(self, transcript_data: Dict, segment_duration: int = 90, 
                                include_timestamps: bool = False) -> List[Dict]:
        """
        YouTube: Time-based segments with natural breakpoints
        
        Args:
            transcript_data: Video transcript data
            segment_duration: Target duration per chunk in seconds
            include_timestamps: Whether to include timestamp markers in chunks
        """
        chunks = []
        
        # Video context
        video_context = f"Video: {transcript_data.get('title', '')}\n"
        video_context += f"Topics: {', '.join(transcript_data.get('topics', []))}\n"
        
        # Get transcript segments
        segments = transcript_data.get('transcript', {}).get('segments', [])
        
        if not segments:
            # Fallback: use full text and split by time estimates
            full_text = transcript_data.get('transcript', {}).get('full_text', '')
            return self._chunk_by_estimated_time(full_text, video_context, transcript_data)
        
        # Group segments by time duration
        current_chunk = []
        current_duration = 0
        chunk_start_time = 0
        
        for segment in segments:
            start_time = segment.get('start', 0)
            duration = segment.get('duration', 3)
            text = segment.get('text', '').strip()
            
            current_chunk.append(segment)
            current_duration = (start_time + duration) - chunk_start_time
            
            # Create chunk when we hit target duration or natural breakpoint
            if (current_duration >= segment_duration or 
                self._is_natural_breakpoint(text)):
                
                # Format chunk content
                chunk_text = self._format_youtube_chunk(
                    current_chunk, video_context, chunk_start_time, 
                    chunk_start_time + current_duration, include_timestamps
                )
                
                chunks.append({
                    'text': chunk_text,
                    'type': 'youtube_segment',
                    'video_title': transcript_data.get('title', ''),
                    'start_time': chunk_start_time,
                    'end_time': chunk_start_time + current_duration,
                    'duration': current_duration,
                    'url_with_timestamp': f"{transcript_data.get('url', '')}?t={int(chunk_start_time)}",
                    'metadata': transcript_data,
                    'chunk_index': len(chunks)
                })
                
                # Reset for next chunk
                chunk_start_time = chunk_start_time + current_duration
                current_chunk = []
                current_duration = 0
        
        # Handle remaining content
        if current_chunk:
            chunk_text = self._format_youtube_chunk(
                current_chunk, video_context, chunk_start_time, 
                chunk_start_time + current_duration, include_timestamps
            )
            chunks.append({
                'text': chunk_text,
                'type': 'youtube_segment',
                'video_title': transcript_data.get('title', ''),
                'start_time': chunk_start_time,
                'end_time': chunk_start_time + current_duration,
                'duration': current_duration,
                'url_with_timestamp': f"{transcript_data.get('url', '')}?t={int(chunk_start_time)}",
                'metadata': transcript_data,
                'chunk_index': len(chunks)
            })
        
        return chunks
    
    def _format_youtube_chunk(self, segments: List[Dict], context: str, 
                             start_time: float, end_time: float, include_timestamps: bool) -> str:
        """Format YouTube chunk with or without timestamps"""
        
        # Add timing context to header
        time_context = f"Time: {self._seconds_to_mmss(start_time)} - {self._seconds_to_mmss(end_time)}\n\n"
        chunk_header = context + time_context
        
        if include_timestamps:
            # Include individual timestamps for precise reference
            timestamped_text = ""
            for segment in segments:
                segment_time = self._seconds_to_mmss(segment.get('start', 0))
                text = segment.get('text', '').strip()
                if text:
                    timestamped_text += f"[{segment_time}] {text} "
            
            return chunk_header + timestamped_text.strip()
        else:
            # Clean text without individual timestamps (better for embedding)
            clean_text = ' '.join([segment.get('text', '').strip() 
                                 for segment in segments 
                                 if segment.get('text', '').strip()])
            
            return chunk_header + clean_text
    
    def _seconds_to_mmss(self, seconds: float) -> str:
        """Convert seconds to MM:SS format"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def _split_by_headers(self, content: str) -> List[Dict]:
        """Split content by markdown headers"""
        sections = []
        
        # Regex to find headers (# ## ###)
        header_pattern = r'^(#{1,3})\s+(.+)$'
        lines = content.split('\n')
        
        current_section = {'header': None, 'content': ''}
        
        for line in lines:
            header_match = re.match(header_pattern, line.strip())
            
            if header_match:
                # Save previous section
                if current_section.get('header') is not None or current_section['content'].strip():
                    sections.append(current_section)
                
                # Start new section
                current_section = {
                    'header': header_match.group(2).strip(),
                    'level': len(header_match.group(1)),
                    'content': ''
                }
            else:
                current_section['content'] += line + '\n'
        
        # Add final section
        if current_section['content'].strip():
            sections.append(current_section)
        
        return sections
    
    def _is_natural_breakpoint(self, text: str) -> bool:
        """Identify natural breakpoints in speech/text"""
        # Look for sentence endings, long pauses, topic transitions
        breakpoint_indicators = [
            r'[.!?]\s*$',  # Sentence endings
            r'\.\s*So\s',   # Transition words
            r'\.\s*Now\s',
            r'\.\s*Next\s',
            r'\.\s*Okay\s',
            r'[.!?]\s*\d+\.',  # Numbered lists
        ]
        
        for pattern in breakpoint_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _split_long_qa(self, question: str, answer: str, metadata: Dict) -> List[Dict]:
        """Split long Q&A pairs while preserving context"""
        chunks = []
        
        # First chunk: Question + beginning of answer
        first_chunk = f"Question: {question.strip()}\nAnswer: "
        
        # Split answer at natural breakpoints
        answer_parts = re.split(r'[.!?]\s+', answer)
        current_answer = ""
        
        for i, part in enumerate(answer_parts):
            test_chunk = first_chunk + current_answer + part + ". "
            
            if len(test_chunk) > self.chunk_sizes['forum_qa'][1]:
                # Save current chunk
                chunks.append({
                    'text': first_chunk + current_answer.strip(),
                    'type': 'forum_qa',
                    'question': question,
                    'answer_part': current_answer.strip(),
                    'metadata': metadata,
                    'chunk_index': len(chunks),
                    'is_continuation': len(chunks) > 0
                })
                
                # Start new chunk with continuation
                current_answer = part + ". "
                first_chunk = f"Question: {question.strip()}\nAnswer (continued): "
            else:
                current_answer += part + ". "
        
        # Add final chunk
        if current_answer.strip():
            chunks.append({
                'text': first_chunk + current_answer.strip(),
                'type': 'forum_qa',
                'question': question,
                'answer_part': current_answer.strip(),
                'metadata': metadata,
                'chunk_index': len(chunks),
                'is_continuation': len(chunks) > 0
            })
        
        return chunks
    
    def _split_long_section(self, section_text: str, header: str, metadata: Dict) -> List[Dict]:
        """Split long blog sections while preserving context"""
        chunks = []
        
        # Split by paragraphs
        paragraphs = section_text.split('\n\n')
        current_chunk = f"Section: {header}\n\n"
        base_length = len(current_chunk)
        
        for para in paragraphs:
            test_chunk = current_chunk + para + '\n\n'
            
            if len(test_chunk) > self.chunk_sizes['blog_section'][1]:
                # Save current chunk
                if len(current_chunk) > base_length + 100:  # Ensure minimum content
                    chunks.append({
                        'text': current_chunk.strip(),
                        'type': 'blog_section',
                        'title': metadata.get('title', ''),
                        'section': header,
                        'metadata': metadata,
                        'chunk_index': len(chunks),
                        'is_continuation': len(chunks) > 0
                    })
                
                # Start new chunk
                current_chunk = f"Section: {header} (continued)\n\n{para}\n\n"
            else:
                current_chunk = test_chunk
        
        # Add final chunk
        if len(current_chunk) > base_length + 100:
            chunks.append({
                'text': current_chunk.strip(),
                'type': 'blog_section',
                'title': metadata.get('title', ''),
                'section': header,
                'metadata': metadata,
                'chunk_index': len(chunks),
                'is_continuation': len(chunks) > 0
            })
        
        return chunks
    
    def _chunk_by_estimated_time(self, full_text: str, context: str, metadata: Dict) -> List[Dict]:
        """Fallback chunking when transcript segments unavailable"""
        # Estimate ~150 words per minute, ~5 chars per word = ~750 chars per minute
        chars_per_minute = 750
        target_duration = 90  # seconds
        chars_per_chunk = int((target_duration / 60) * chars_per_minute)  # ~1125 chars
        
        chunks = []
        words = full_text.split()
        current_chunk_words = []
        
        for word in words:
            current_chunk_words.append(word)
            current_text = ' '.join(current_chunk_words)
            
            if len(current_text) >= chars_per_chunk:
                chunk_text = context + current_text
                chunks.append({
                    'text': chunk_text,
                    'type': 'youtube_segment',
                    'video_title': metadata.get('title', ''),
                    'estimated_start_time': len(chunks) * target_duration,
                    'estimated_duration': target_duration,
                    'metadata': metadata,
                    'chunk_index': len(chunks),
                    'is_estimated_timing': True
                })
                current_chunk_words = []
        
        # Handle remaining words
        if current_chunk_words:
            chunk_text = context + ' '.join(current_chunk_words)
            chunks.append({
                'text': chunk_text,
                'type': 'youtube_segment',
                'video_title': metadata.get('title', ''),
                'estimated_start_time': len(chunks) * target_duration,
                'metadata': metadata,
                'chunk_index': len(chunks),
                'is_estimated_timing': True
            })
        
        return chunks


def test_chunking_strategies():
    """Test different chunking approaches"""
    chunker = ContentChunker()
    
    # Test forum Q&A
    print("🔍 Testing Forum Q&A Chunking:")
    qa_chunks = chunker.chunk_forum_qa(
        "How do I sync my workouts to Garmin?",
        "To sync workouts to Garmin, go to Settings > Connections > Garmin Connect. Enter your credentials and enable auto-sync. Your completed workouts will automatically appear in Garmin Connect within 5 minutes.",
        {'category': 'sync', 'topic_id': 1234}
    )
    
    for chunk in qa_chunks:
        print(f"  • {len(chunk['text'])} chars: {chunk['text'][:100]}...")
    
    # Test blog article (mock data)
    print("\n📖 Testing Blog Article Chunking:")
    blog_content = """
# Getting Started with TrainerDay

TrainerDay is a comprehensive training platform that helps cyclists improve their performance through structured workouts.

## Setting Up Your Profile

First, you'll need to create your profile and set your FTP (Functional Threshold Power). This is crucial for accurate workout targeting.

### FTP Testing
We recommend doing an FTP test every 6-8 weeks to ensure your training zones remain accurate.

## Connecting Devices

TrainerDay supports a wide range of devices including smart trainers, power meters, and heart rate monitors.
"""
    
    blog_chunks = chunker.chunk_blog_article(blog_content, {
        'title': 'Getting Started with TrainerDay',
        'category': 'Training',
        'tags': ['beginner', 'setup']
    })
    
    for i, chunk in enumerate(blog_chunks):
        print(f"  • Chunk {i+1} ({chunk.get('section', 'N/A')}): {len(chunk['text'])} chars")
    
    # Test YouTube transcript (mock data)
    print("\n🎥 Testing YouTube Transcript Chunking:")
    youtube_data = {
        'title': 'How to Set Up Your First Workout',
        'topics': ['beginner', 'setup'],
        'url': 'https://youtube.com/watch?v=example',
        'transcript': {
            'segments': [
                {'start': 12, 'duration': 4, 'text': 'Welcome to TrainerDay setup guide.'},
                {'start': 16, 'duration': 5, 'text': 'Today we\'ll show you how to create your first workout.'},
                {'start': 21, 'duration': 6, 'text': 'First, navigate to the workout library in the main menu.'},
                {'start': 27, 'duration': 4, 'text': 'You\'ll see thousands of workouts here.'},
                {'start': 31, 'duration': 7, 'text': 'For beginners, I recommend starting with our basic endurance workouts.'}
            ]
        }
    }
    
    # Test both clean and timestamped versions
    youtube_chunks_clean = chunker.chunk_youtube_transcript(youtube_data, segment_duration=20, include_timestamps=False)
    youtube_chunks_timed = chunker.chunk_youtube_transcript(youtube_data, segment_duration=20, include_timestamps=True)
    
    print(f"  Clean chunks: {len(youtube_chunks_clean)}")
    for i, chunk in enumerate(youtube_chunks_clean):
        print(f"    • Chunk {i+1}: {len(chunk['text'])} chars | {chunk['start_time']:.0f}-{chunk['end_time']:.0f}s")
    
    print(f"  Timestamped chunks: {len(youtube_chunks_timed)}")
    print(f"    • Sample timestamped content:")
    if youtube_chunks_timed:
        sample = youtube_chunks_timed[0]['text'][:200] + "..." if len(youtube_chunks_timed[0]['text']) > 200 else youtube_chunks_timed[0]['text']
        print(f"      {sample}")
    
    print(f"\n✅ Generated {len(qa_chunks)} Q&A chunks, {len(blog_chunks)} blog chunks, and {len(youtube_chunks_clean)} YouTube chunks")


if __name__ == "__main__":
    test_chunking_strategies()