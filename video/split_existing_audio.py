#!/usr/bin/env python3
"""
Split existing audio file into chunks for OpenAI API
"""

from pydub import AudioSegment
from pathlib import Path
import os

# Load the existing audio file
audio_path = Path("video_processing/FullTrainerDayForAI_audio.mp3")
output_dir = Path("video_processing/transcription_output")
output_dir.mkdir(exist_ok=True)

print(f"Loading audio file: {audio_path}")
print(f"File size: {audio_path.stat().st_size / (1024 * 1024):.1f} MB")

# Load audio with pydub
audio = AudioSegment.from_mp3(str(audio_path))
duration_minutes = len(audio) / 60000  # Convert ms to minutes

print(f"Audio duration: {duration_minutes:.1f} minutes")

# Split into ~20MB chunks (roughly 20-25 minutes each at current bitrate)
# Since 48MB = ~52 minutes, we'll split into 3 chunks of ~17 minutes each
chunk_duration_ms = len(audio) // 3  # Split into 3 parts

segments = []
for i in range(3):
    start_ms = i * chunk_duration_ms
    end_ms = min((i + 1) * chunk_duration_ms, len(audio))
    
    chunk = audio[start_ms:end_ms]
    chunk_path = output_dir / f"audio_chunk_{i+1}.mp3"
    
    print(f"Exporting chunk {i+1}: {start_ms/60000:.1f}-{end_ms/60000:.1f} minutes")
    chunk.export(str(chunk_path), format="mp3", bitrate="32k")
    
    file_size = chunk_path.stat().st_size / (1024 * 1024)
    print(f"  Chunk {i+1} size: {file_size:.1f} MB")
    
    segments.append({
        'path': chunk_path,
        'start_time': start_ms / 1000,
        'end_time': end_ms / 1000,
        'size_mb': file_size
    })

print(f"\n✅ Created {len(segments)} audio chunks:")
for i, seg in enumerate(segments):
    print(f"  Chunk {i+1}: {seg['start_time']/60:.1f}-{seg['end_time']/60:.1f} min ({seg['size_mb']:.1f}MB)")