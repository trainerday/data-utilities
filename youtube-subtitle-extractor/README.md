# YouTube Subtitle Extractor

Extracts transcripts from YouTube videos using the official YouTube Data API, optimized for TrainerDay channel content analysis.

## 📁 Contents

- `extract_youtube_with_api.py` - Main extraction script using YouTube Data API
- `analyze_youtube_content.py` - Analyze extracted content statistics and topics
- `youtube_content/` - Directory with 54 extracted video transcripts
- `.env` - YouTube API key configuration

## 🚀 Usage

### Extract All Videos
```bash
python extract_youtube_with_api.py
```
- Automatically detects existing extractions and only processes new videos
- Uses official YouTube API (no IP blocking issues)
- Fast extraction with proper rate limiting
- Handles multiple languages and transcript types

### Analyze Extracted Content
```bash
python analyze_youtube_content.py
```
- Shows content statistics and topic coverage
- Identifies video lengths and segment counts
- Provides content samples for quality verification

## 📊 Current Extraction Results

- **54 videos successfully extracted** (93% success rate)
- **241,810 total characters** of transcript content
- **6,576 transcript segments** with precise timestamps
- **14 topic categories** automatically classified

### Content Distribution by Topic:
- **General**: 16 videos (tutorials, explanations)
- **Workout Creator**: 10 videos (feature guides)
- **Coach Jack**: 9 videos (training plans, AI coaching)
- **Trainer**: 8 videos (hardware setup, connectivity)
- **Mobile App**: 6 videos (iOS/Android app features)
- **Zwift Integration**: 5 videos (third-party connections)
- **Garmin Sync**: 4 videos (device synchronization)
- **Power Zones**: 3 videos (FTP, training zones)
- **And more...**

### Content Quality Highlights:
- **Deep Technical Content**: 29K character deep-dive tutorials
- **Product Comparisons**: TrainerDay vs TrainerRoad, Zwift analysis
- **Feature Walkthroughs**: Comprehensive app and web platform guides
- **User Workflows**: Step-by-step setup and sync procedures

## 🔧 Configuration

### Environment Variables
Create a `.env` file with:
```env
YOUTUBE_API_KEY=your_youtube_api_key_here
```

### Getting a YouTube API Key
1. Go to [Google Cloud Console](https://console.developers.google.com/)
2. Create a project or select existing one
3. Enable "YouTube Data API v3" 
4. Create credentials → API Key
5. Copy the API key to your `.env` file

## 📂 Output Format

### Individual Video Files (`video_*.json`)
```json
{
  "video_id": "abc123",
  "title": "Video Title Here",
  "url": "https://www.youtube.com/watch?v=abc123",
  "upload_date": "2024-01-01T00:00:00Z",
  "topics": ["mobile-app", "tutorial"],
  "transcript": {
    "type": "auto",
    "full_text": "Complete transcript text...",
    "segment_count": 156,
    "segments": [
      {
        "start": 12.5,
        "duration": 3.2,
        "text": "Individual segment text"
      }
    ]
  },
  "processed_at": "2025-07-23T07:39:00.000000"
}
```

### Content Analysis Output
- Video statistics (character counts, segment counts)
- Topic distribution and coverage analysis
- Content samples for quality verification
- Processing success/failure rates

## 🎯 Topic Classification

Videos are automatically tagged based on title content:

| Topic | Keywords | Example Videos |
|-------|----------|----------------|
| `mobile-app` | app, mobile, ios, android | "TrainerDay Mobile Training App - Deep-Dive" |
| `coach-jack` | coach jack, training plan, ai | "100% Custom Cycling Training Plans" |
| `trainer` | trainer, smart trainer, hardware | "Automatic Slope, ERG and HR mode switching" |
| `zwift` | zwift | "Getting your TrainerDay workouts in Zwift" |
| `garmin` | garmin | "Sent full Training Plan to Garmin" |
| `sync` | sync, strava, trainingpeaks | "TrainerDay + Intervals.Icu integration" |
| `power-zones` | power, ftp, zones, threshold | "The Ultimate Way to do Zone 2 Training" |
| `workout-creator` | workout, create, editor | "W Prime Deep-Dive using Workout Creator" |
| `review` | vs, comparison, review | "TrainerDay vs TrainerRoad: Which Is Right?" |
| `general` | (default for uncategorized) | General tutorials and explanations |

## ⚠️ Limitations & Notes

### Failed Extractions (4 videos)
- **1 video**: Subtitles disabled by creator
- **2 videos**: Spanish language content (would need translation)
- **1 video**: Vietnamese language content (would need translation)

### Content Scope
- Focuses specifically on @trainerday YouTube channel
- English language transcripts only (auto-generated)
- Requires YouTube Data API quota (10,000 requests/day default)

## 🔗 Integration

This extractor is designed to work with:

- **Vector Processing System**: For content chunking and semantic search
  - Location: `/Users/alex/Documents/Projects/data-utilities/vector-processor/`
- **Forum Analysis System**: For cross-content analysis and gap identification
  - Location: `/Users/alex/Documents/Projects/data-utilities/forum-scraper-trainerday/`
- **Content Strategy Pipeline**: For automated content generation and enhancement
  - Location: TD-Business Basic Memory project

## 📈 Performance

- **Extraction Speed**: ~1-2 seconds per video (API-based)
- **Success Rate**: 93% (54/58 videos successfully processed)
- **Content Volume**: Average 4,477 characters per video
- **API Efficiency**: No IP blocking, official rate limits respected

## 🎬 Content Samples

**Longest Video**: TrainerDay Mobile Training App - Deep-Dive (29,155 characters)
**Most Technical**: W Prime Deep-Dive using the TrainerDay Workout Creator (5,869 characters)  
**Best Comparisons**: Zwift vs TrainerRoad analysis (3,551 characters)

*This extraction system provides the foundation for TrainerDay's educational content analysis, enabling cross-platform content strategy and user-driven content enhancement.*