# Forum Data Structure Analysis Report

## Executive Summary

This analysis examined the TrainerDay forum database to understand date storage patterns, recent activity trends, and content prioritization opportunities. The focus was on identifying questions from the last year and developing strategies to prioritize content creation based on recent user activity rather than just topic age.

## Database Schema Overview

### Primary Tables and Date Fields

#### 1. `forum_topics_raw` - Raw Forum Content Storage
- **topic_id**: INTEGER PRIMARY KEY
- **raw_content**: JSONB (complete topic + posts data from Discourse API)
- **checksum**: VARCHAR(32) (MD5 hash for change detection)
- **scraped_at**: TIMESTAMP (when scraped)
- **last_updated**: TIMESTAMP DEFAULT NOW() (when last changed)
- **title**: TEXT (extracted for easy querying)
- **posts_count**: INTEGER (topic metadata)
- **created_at_original**: TIMESTAMP (topic creation date from Discourse)

#### 2. `forum_qa_pairs` - Extracted Question/Answer Pairs
- **topic_id**: INTEGER (references forum_topics_raw)
- **date_posted**: DATE (when the Q&A interaction occurred)
- **question_content**: TEXT
- **response_content**: TEXT
- **pain_point**: TEXT (extracted user pain points)
- **user_language**: TEXT (how users describe issues)

#### 3. Additional Analysis Tables
- `forum_topics` - Topic metadata and categories
- `forum_voice_patterns` - User vs platform communication patterns
- `forum_insights` - Content opportunities and messaging insights

## Key Date Storage Patterns

### 1. Multiple Date Sources
- **Topic Creation**: `created_at_original` from Discourse API (ISO 8601 format: "2025-07-19T04:41:55.753Z")
- **Last Activity**: `last_posted_at` and `bumped_at` in raw_content JSONB
- **Q&A Dates**: `date_posted` in forum_qa_pairs table
- **Processing Dates**: `scraped_at`, `last_updated`, `analyzed_at`

### 2. Date Range Coverage
- **Total Q&A pairs with dates**: 3,513
- **Date range**: 2020-11-19 to 2025-07-20 (4.7 years)
- **Last year activity**: 1,267 Q&A pairs (36.1% of total)
- **Last 90 days**: 224 pairs (6.4%)
- **Last 30 days**: 54 pairs (1.5%)

## Recent Activity Analysis

### Monthly Forum Activity (Last 12 Months)
```
2025-07: 16 topics
2025-06: 31 topics  
2025-05: 43 topics
2025-04: 39 topics
2025-03: 55 topics (peak activity)
2025-02: 71 topics (highest)
2025-01: 63 topics
2024-12: 39 topics
2024-11: 36 topics
2024-10: 46 topics
2024-09: 39 topics
2024-08: 37 topics
```

### Category Distribution by Recent Activity
1. **Technical Issues**: 658 questions (largest category)
2. **Training Execution**: 271 questions
3. **Feature Requests**: 236 questions
4. **Integrations & Export**: 64 questions
5. **Getting Started**: 14 questions
6. **Success Stories**: 12 questions
7. **Training Theory**: 12 questions

## Content Prioritization Insights

### 1. Recent Questions in Old Topics
- Found many active discussions in topics created months/years ago
- Example: Topic 1577 (created 2022-05-11) had recent questions in 2025-07-20
- This indicates ongoing relevance of older topics

### 2. Most Active Recent Topics
Top topics by question frequency in the last year:
- **Topic 56715**: "Can I filter the searched workouts by sport?" (27 questions)
- **Topic 46863**: "Activity title edit" (9 questions)  
- **Topic 56727**: "Training VO2max when tired?" (8 questions)

### 3. Common Pain Points (Last Year)
1. **Sync Issues**: "Finished ride not syncing to intervals or Strava" (5 occurrences)
2. **Speed/Distance Recording**: "Speed and distance still not recorded after recalculation" (3 occurrences)
3. **Heart Rate Monitor Issues**: "The heart rate monitor won't reconnect after working perfectly" (3 occurrences)
4. **FTP Calculation**: "Lack of clarity on FTP calculation" (3 occurrences)

## Recommendations for Content Strategy

### 1. Prioritization Algorithm
Developed a scoring system based on:
- **Recency Score** (10 = last 30 days, 8 = last 90 days, etc.)
- **Frequency Score** (based on number of questions)
- **Engagement Score** (based on view counts)

### 2. Top Priority Topics for Content Creation
1. **Error on convert to HR** (Score: 24) - Technical Issues
2. **Training VO2max when tired** (Score: 22) - Training Execution  
3. **App shows different plan workout than Website** (Score: 20) - Technical Issues
4. **Concept2 ERG power not showing** (Score: 20) - Technical Issues
5. **How to edit a CJ Plan** (Score: 20) - Training Execution

### 3. Content Format Recommendations
- **Blog Articles**: For complex training execution topics
- **Video Tutorials**: For technical setup and troubleshooting
- **FAQ Updates**: For recurring pain points
- **Integration Guides**: For sync and export issues

## Database Query Strategies

### Identifying Recent Activity
```sql
-- Find topics with recent questions vs old creation dates
SELECT ftr.topic_id, ftr.title, ftr.created_at_original, 
       qa.date_posted, (qa.date_posted - ftr.created_at_original::date) as days_diff
FROM forum_topics_raw ftr
JOIN forum_qa_pairs qa ON ftr.topic_id = qa.topic_id
WHERE qa.date_posted >= CURRENT_DATE - INTERVAL '365 days'
AND (qa.date_posted - ftr.created_at_original::date) > 30
ORDER BY qa.date_posted DESC;
```

### Prioritization Scoring
```sql
-- Content prioritization query
WITH topic_scores AS (
    SELECT topic_id, title, analysis_category,
           -- Recency, frequency, and engagement scoring logic
           CASE WHEN MAX(qa.date_posted) >= CURRENT_DATE - INTERVAL '30 days' THEN 10
                WHEN MAX(qa.date_posted) >= CURRENT_DATE - INTERVAL '90 days' THEN 8
                -- etc.
           END as recency_score,
           LEAST(COUNT(qa.id) * 2, 10) as frequency_score,
           -- View-based engagement score
    FROM forum_topics_raw ftr
    JOIN forum_qa_pairs qa ON ftr.topic_id = qa.topic_id
    WHERE qa.date_posted >= CURRENT_DATE - INTERVAL '365 days'
    GROUP BY topic_id, title, analysis_category, raw_content
)
SELECT * FROM topic_scores ORDER BY total_score DESC;
```

## Implementation Recommendations

### 1. Focus on Recent User Activity
- Prioritize content creation based on recent questions, not topic age
- Monitor topics with continued engagement over time
- Track pain points that persist across multiple time periods

### 2. Content Calendar Planning
- Review monthly activity trends to time content releases
- Focus on technical issues (largest category) for immediate impact
- Balance technical solutions with training guidance content

### 3. Success Metrics
- Track reduction in repeat questions for covered topics
- Monitor engagement on content addressing identified pain points
- Measure forum activity changes after content publication

## Technical Notes

### Date Format Handling
- Discourse API returns ISO 8601 timestamps with 'Z' suffix
- Database stores as PostgreSQL TIMESTAMP type
- Q&A extraction uses DATE type for simpler querying

### Data Freshness
- Raw content updated via incremental scraping (checksum-based)
- Analysis runs on unprocessed topics automatically
- Current database contains 1,536 topics with 97.5% analyzed

This analysis provides a comprehensive foundation for data-driven content strategy decisions based on actual user needs and activity patterns rather than assumptions about topic importance.