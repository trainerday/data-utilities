# Project Feature Map Data Source

Comprehensive TrainerDay feature documentation for semantic discovery of platform capabilities and functionality.

## 📊 Data Source Overview

**Primary Content**: Complete TrainerDay feature list and functionality descriptions
**Processing Focus**: Feature descriptions, capabilities, and use cases for semantic feature discovery
**Content Type**: Product documentation, feature specifications, technical capabilities

## 🚀 Data Processing

### **Feature Map Processing** (`unified_content_processor.py`)
- **Input**: Structured Markdown files with frontmatter containing feature descriptions
- **Processing**: Feature categories and descriptions as searchable semantic units
- **Chunk Size**: 300-800 characters per feature section
- **Metadata**: `{"category": "Training Features", "feature_type": "premium", "platform": "web"}`

### **Data Source Details**
- **Format**: Markdown files with frontmatter metadata
- **Structure**: Hierarchical feature organization by category and platform
- **Content Types**: Feature descriptions, technical specs, integration details
- **Update Method**: File-based change detection using content hashes

## 📋 Usage

### **Search TrainerDay Features**
```bash
# Find features related to specific functionality
python unified_content_processor.py --search "heart rate training" --source-filter project_feature_map

# Discover integration capabilities
python unified_content_processor.py --search "Garmin sync" --source-filter project_feature_map
```

### **Feature Discovery Examples**
```bash
# Natural language feature queries
"How do I create custom workouts?"
"What premium features are available?"
"Can I sync with TrainingPeaks?"
"Does TrainerDay work with smart trainers?"
```

## 🎯 Content Strategy Benefits

### **Feature Discovery**
- **Natural Language Queries**: Users can ask about features in their own words
- **Cross-Feature Relationships**: Find related features across different platform areas
- **Capability Mapping**: Understand what TrainerDay can do for specific use cases

### **User Support Enhancement**
- **Self-Service Discovery**: Users find features without contacting support
- **Feature Education**: Learn about features they didn't know existed
- **Integration Guidance**: Understand how to connect with other platforms

### **Product Development Insights**
- **Feature Usage Patterns**: Understand which features users search for most
- **Gap Identification**: Discover missing features users are looking for
- **Documentation Improvement**: Identify areas needing better explanation

## 🏗️ Vectorization Value

**High Value for Vectorization:**
- ✅ **Rich Semantic Content**: Detailed feature descriptions with context
- ✅ **User-Centric Language**: Features described in terms users understand
- ✅ **Cross-Reference Potential**: Features relate to forum questions and blog content
- ✅ **Discovery Enhancement**: Helps users find capabilities they need
- ✅ **Support Deflection**: Reduces support requests through self-service discovery

**Processing Strategy:**
- **Section-Based Chunking**: Each feature section becomes a searchable unit
- **Category Metadata**: Preserve feature categories for filtered search
- **Platform Tagging**: Distinguish web vs mobile vs API features
- **Integration Mapping**: Highlight third-party platform connections

## 🔍 Search Capabilities

### **Feature-Specific Queries**
```sql
-- Find premium features
WHERE source = 'project_feature_map' AND metadata->>'feature_type' = 'premium'

-- Search by platform
WHERE source = 'project_feature_map' AND metadata->>'platform' = 'mobile'

-- Find integration features
WHERE source = 'project_feature_map' AND content ILIKE '%sync%'
```

### **Cross-Content Discovery**
```sql
-- Find features related to forum discussions
SELECT ce1.title as feature, ce2.title as forum_question
FROM content_embeddings ce1, content_embeddings ce2
WHERE ce1.source = 'project_feature_map' 
  AND ce2.source = 'forum'
  AND ce1.embedding <-> ce2.embedding < 0.3
```

## 📈 Processing Impact

**Expected Outcomes:**
- **Improved Feature Discovery**: Users find relevant features faster
- **Reduced Support Load**: Self-service feature discovery
- **Better User Onboarding**: New users discover platform capabilities
- **Enhanced Documentation**: Cross-reference features with tutorials

**Content Volume**: 200+ features across multiple categories and platforms
**Update Frequency**: Updated when new features are released or documented
**Integration**: Links to forum discussions and blog tutorials about features

---

*Feature map vectorization enables intelligent feature discovery, helping users understand TrainerDay's full capabilities through natural language queries and semantic relationships with support content.*