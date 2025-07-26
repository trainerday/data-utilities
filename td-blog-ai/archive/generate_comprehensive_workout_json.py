#!/usr/bin/env python3
"""
Generate Comprehensive Workout Features JSON
Combines direct database queries with LlamaIndex retrieval
"""

import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from collections import defaultdict

from llama_index.embeddings.openai import OpenAIEmbedding

load_dotenv()

class ComprehensiveWorkoutData:
    def __init__(self):
        self.embedding_model = OpenAIEmbedding(
            model="text-embedding-3-large",
            dimensions=1536
        )
        
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'trainerday_local',
            'user': os.getenv('USER', 'alex'),
            'password': '',
        }
        
        # Complete workout feature structure from workouts.md
        self.workout_features = {
            "Workout Creation & Management": {
                "Visual Workout Editor": {
                    "description": "Drag-and-drop interface with Excel-like functionality",
                    "features": ["visual interface", "drag and drop", "Excel-like grid", "intuitive design"],
                    "queries": ['"workout editor" OR "visual workout builder"', '"drag-and-drop" OR "drag and drop"']
                },
                "Fastest Workout Editor": {
                    "description": "Copy/paste, arrow keys, speed-focused design",
                    "features": ["copy paste", "arrow keys", "keyboard shortcuts", "speed editing"],
                    "queries": ['"fastest workout editor"', '"copy paste" AND workout', '"keyboard shortcuts"']
                },
                "Sets and Reps Editor": {
                    "description": "Create complex interval structures with repeated patterns",
                    "features": ["sets and reps", "interval patterns", "repetitions", "structured workouts"],
                    "queries": ['"sets and reps"', '"interval structure"', '"complex intervals"']
                },
                "Interval Comments": {
                    "description": "Add instructions and cues to specific intervals with offset timing",
                    "features": ["coaching notes", "interval instructions", "timed cues", "workout guidance"],
                    "queries": ['"interval comments"', '"coaching notes"', '"workout instructions"']
                },
                "Route Importing": {
                    "description": "GPS routes for outdoor simulation with power/slope data",
                    "features": ["GPS import", "route files", "outdoor simulation", "elevation data"],
                    "queries": ['"route importing"', '"GPS routes"', '"outdoor simulation"']
                },
                "Target Modes": {
                    "description": "Power/ERG, Heart Rate, Slope, Feel-based, Resistance targets",
                    "features": ["power targets", "heart rate targets", "slope mode", "resistance mode"],
                    "queries": ['"target modes"', '"power targets"', '"heart rate targets"', '"slope targets"']
                },
                "Mixed-Mode Workouts": {
                    "description": "Automatically switch between different target modes within single workout",
                    "features": ["mode switching", "automatic transitions", "mixed targets"],
                    "queries": ['"mixed-mode workouts"', '"automatic mode switching"']
                },
                "Workout Tags": {
                    "description": "Public and private tags for categorization",
                    "features": ["tagging system", "organization", "public tags", "private tags"],
                    "queries": ['"workout tags"', '"workout organization"', '"public private"']
                },
                "Workout Cloning": {
                    "description": "ALT+drag to duplicate workouts",
                    "features": ["duplicate workouts", "ALT drag", "cloning", "copy workouts"],
                    "queries": ['"workout cloning"', '"duplicate workouts"', '"ALT drag"']
                },
                "Auto-Mode Switching": {
                    "description": "Automatically switch from Slope to ERG or HR modes",
                    "features": ["automatic switching", "mode transitions", "smart switching"],
                    "queries": ['"auto-mode switching"', '"automatic mode"']
                },
                "Ramps and Steps": {
                    "description": "Gradual power increases/decreases, automatic conversion to steps for Garmin",
                    "features": ["power ramps", "gradual changes", "Garmin steps", "progressive intervals"],
                    "queries": ['"ramps and steps"', '"gradual power"', '"progressive intervals"']
                },
                "Free Ride Intervals": {
                    "description": "Intervals that continue until manual stop via lap button",
                    "features": ["open-ended", "lap button control", "manual stop", "free ride"],
                    "queries": ['"free ride intervals"', '"open-ended intervals"', '"lap button"']
                },
                "W'bal Integration": {
                    "description": "Anaerobic capacity calculations for precise interval design",
                    "features": ["W prime balance", "anaerobic capacity", "interval optimization"],
                    "queries": ['"W\'bal"', '"anaerobic capacity"', '"interval design"']
                },
                "Multi-Sport Support": {
                    "description": "Cycling, rowing, swimming with sport-specific targeting",
                    "features": ["cycling", "rowing", "swimming", "multi-sport"],
                    "queries": ['"multi-sport"', '"cycling rowing swimming"']
                }
            },
            "Training Modes": {
                "ERG Mode": {
                    "description": "Automatic power control regardless of cadence/gear",
                    "features": ["automatic power", "cadence independent", "power control"],
                    "queries": ['"ERG mode"', '"automatic power control"', '"power targeting"']
                },
                "HR+ Mode": {
                    "description": "Heart rate-controlled with automatic power adjustment",
                    "features": ["heart rate control", "power adjustment", "HR targeting"],
                    "queries": ['"HR+ mode"', '"heart rate controlled"', '"automatic power adjustment"']
                },
                "Slope Mode": {
                    "description": "Gradient simulation with gear control, automatic slope changes",
                    "features": ["gradient simulation", "gear control", "slope changes"],
                    "queries": ['"slope mode"', '"gradient simulation"', '"gear control"']
                },
                "Resistance Mode": {
                    "description": "Fixed resistance percentage, ideal for sprints/strength work",
                    "features": ["fixed resistance", "sprint training", "strength work"],
                    "queries": ['"resistance mode"', '"fixed resistance"', '"sprint training"']
                },
                "Power Target Adjustment": {
                    "description": "Based on heart rate feedback",
                    "features": ["dynamic adjustment", "HR feedback", "adaptive power"],
                    "queries": ['"power target adjustment"', '"heart rate feedback"']
                },
                "Dynamic Power Scaling": {
                    "description": "Real-time adjustments during training",
                    "features": ["real-time scaling", "dynamic adjustments", "adaptive training"],
                    "queries": ['"dynamic power scaling"', '"real-time adjustments"']
                },
                "Trainer Difficulty": {
                    "description": "20-50% settings for optimal gear usage",
                    "features": ["difficulty adjustment", "gear optimization", "resistance settings"],
                    "queries": ['"trainer difficulty"', '"gear usage"', '"resistance settings"']
                }
            },
            "Training Execution & Real-time Features": {
                "Real-time Training": {
                    "description": "Live workout execution with smart trainer control",
                    "features": ["live execution", "smart trainer", "real-time control"],
                    "queries": ['"real-time training"', '"live workout"', '"smart trainer control"']
                },
                "6-Second Warmup": {
                    "description": "Ultra-quick start functionality",
                    "features": ["quick start", "fast warmup", "instant begin"],
                    "queries": ['"6-second warmup"', '"quick start"', '"ultra-fast start"']
                },
                "Dynamic Workout Editing": {
                    "description": "On-the-fly modifications during training",
                    "features": ["live editing", "mid-workout changes", "dynamic modifications"],
                    "queries": ['"dynamic workout editing"', '"on-the-fly"', '"mid-workout changes"']
                },
                "Power Adjustments": {
                    "description": "10-second increments/decrements during sessions",
                    "features": ["power buttons", "intensity controls", "+/- adjustments"],
                    "queries": ['"power adjustments"', '"intensity controls"', '"+/- buttons"']
                },
                "Hot Swap": {
                    "description": "Change entire workouts mid-session",
                    "features": ["workout switching", "mid-session change", "hot swap"],
                    "queries": ['"hot swap"', '"change workouts mid-session"', '"workout switching"']
                },
                "Auto-extend Workouts": {
                    "description": "Continue beyond planned duration until user stops",
                    "features": ["extended training", "continue beyond", "auto-extend"],
                    "queries": ['"auto-extend"', '"continue beyond duration"', '"extended training"']
                },
                "Training Effect Integration": {
                    "description": "Garmin training effect monitoring for intensity adjustment",
                    "features": ["Garmin integration", "training effect", "intensity monitoring"],
                    "queries": ['"training effect"', '"Garmin training effect"']
                },
                "ERG Spiral Recovery": {
                    "description": "Easy reset from low-cadence resistance buildup",
                    "features": ["spiral recovery", "cadence recovery", "ERG reset"],
                    "queries": ['"ERG spiral"', '"low-cadence resistance"', '"spiral recovery"']
                },
                "Ride Feel Adjustment": {
                    "description": "Modify workout intensity without changing main adaptations",
                    "features": ["ride feel", "intensity modification", "feel adjustment"],
                    "queries": ['"ride feel"', '"intensity modification"', '"feel adjustment"']
                },
                "FTP-based Scaling": {
                    "description": "Automatic workout adjustment based on current fitness",
                    "features": ["FTP scaling", "fitness adjustment", "automatic scaling"],
                    "queries": ['"FTP-based scaling"', '"fitness-based adjustment"', '"FTP adjustment"']
                },
                "Power Match": {
                    "description": "Work with external power meters",
                    "features": ["power match", "external power meter", "power meter compatibility"],
                    "queries": ['"power match"', '"external power meters"', '"power meter compatibility"']
                },
                "Heart Rate Testing": {
                    "description": "Maximum heart rate and Zone 2 testing",
                    "features": ["HR testing", "max heart rate", "zone 2 test"],
                    "queries": ['"heart rate testing"', '"zone 2 testing"', '"maximum heart rate"']
                }
            },
            "Real-time Display & Monitoring": {
                "Broadcast to Big Screen": {
                    "description": "Cast training data to Mac/PC/tablet displays",
                    "features": ["screen casting", "big screen", "external display"],
                    "queries": ['"broadcast to big screen"', '"cast training data"', '"external displays"']
                },
                "Live Training Display": {
                    "description": "Real-time workout viewing on external devices",
                    "features": ["live display", "real-time viewing", "workout monitoring"],
                    "queries": ['"live training display"', '"real-time viewing"', '"workout monitoring"']
                },
                "Power Zone Displays": {
                    "description": "Visual power zone indicators during training",
                    "features": ["zone display", "visual indicators", "power zones"],
                    "queries": ['"power zone displays"', '"visual zone indicators"', '"zone display"']
                },
                "Speed and Distance": {
                    "description": "Indoor approximation with drag coefficient adjustment",
                    "features": ["speed calculation", "distance tracking", "drag coefficient"],
                    "queries": ['"speed distance calculation"', '"indoor approximation"', '"drag coefficient"']
                },
                "Real-time Metrics": {
                    "description": "Power, HR, cadence, speed, distance during training",
                    "features": ["live metrics", "real-time data", "training metrics"],
                    "queries": ['"real-time metrics"', '"power HR cadence"', '"live data"']
                },
                "YouTube Integration": {
                    "description": "Embedded video during big screen display",
                    "features": ["YouTube player", "video integration", "entertainment"],
                    "queries": ['"YouTube integration"', '"embedded video"', '"entertainment"']
                },
                "Secret URL Sharing": {
                    "description": "Share live training data with coaches/friends",
                    "features": ["URL sharing", "coach viewing", "live sharing"],
                    "queries": ['"secret URL"', '"live data sharing"', '"coach viewing"']
                },
                "Data Visualization": {
                    "description": "Power curves, zone time, interval analysis",
                    "features": ["power curves", "zone analysis", "data visualization"],
                    "queries": ['"training data visualization"', '"power curves"', '"interval analysis"']
                }
            },
            "Workout Library & Discovery": {
                "Community Library": {
                    "description": "Thousands of user-created workouts",
                    "features": ["community workouts", "shared library", "user contributions"],
                    "queries": ['"community workout library"', '"user-created workouts"', '"shared workouts"']
                },
                "Open Source Workouts": {
                    "description": "30,000+ open source workouts",
                    "features": ["open source", "ERGdb", "free workouts"],
                    "queries": ['"open source workouts"', '"ERGdb"', '"free workouts"']
                },
                "Search and Filtering": {
                    "description": "By tags, difficulty, type, sport, duration, stress level",
                    "features": ["workout search", "filtering", "advanced search"],
                    "queries": ['"workout search"', '"filtering"', '"tags difficulty type"']
                },
                "Rating System": {
                    "description": "Community-driven popularity rankings",
                    "features": ["workout ratings", "popularity", "community rankings"],
                    "queries": ['"workout rating"', '"popularity rankings"', '"community ratings"']
                },
                "Author Following": {
                    "description": "Follow favorite workout creators",
                    "features": ["follow authors", "favorite creators", "author system"],
                    "queries": ['"author following"', '"favorite creators"', '"workout creators"']
                },
                "Search by Popularity": {
                    "description": "Discover highly-rated community content",
                    "features": ["popular workouts", "highly rated", "discover content"],
                    "queries": ['"search by popularity"', '"highly-rated workouts"', '"discover content"']
                },
                "Sport-Specific Filtering": {
                    "description": "Cycling, rowing, swimming workout separation",
                    "features": ["sport filtering", "cycling rowing swimming", "sport specific"],
                    "queries": ['"sport-specific filtering"', '"cycling rowing swimming"']
                },
                "Tag-based Search": {
                    "description": "# symbol for tag-based workout discovery",
                    "features": ["hashtag search", "tag search", "workout discovery"],
                    "queries": ['"tag-based search"', '"hashtag search"', '"workout discovery"']
                },
                "Advanced Search": {
                    "description": "Detailed filtering capabilities",
                    "features": ["advanced filters", "detailed search", "search capabilities"],
                    "queries": ['"advanced search"', '"detailed filtering"', '"search capabilities"']
                },
                "Personal Lists": {
                    "description": "Custom organization beyond tags",
                    "features": ["personal lists", "custom organization", "workout collections"],
                    "queries": ['"personal workout lists"', '"custom organization"', '"workout collections"']
                },
                "Favorites System": {
                    "description": "Quick access to preferred workouts",
                    "features": ["favorites", "quick access", "preferred workouts"],
                    "queries": ['"favorites system"', '"preferred workouts"', '"quick access"']
                }
            },
            "Workout Export & Integration": {
                "Multi-Format Export": {
                    "description": "TCX, ZWO, MRC, ERG file formats",
                    "features": ["TCX export", "ZWO files", "MRC format", "ERG files"],
                    "queries": ['"multi-format export"', '"TCX ZWO MRC ERG"', '"workout formats"']
                },
                "Platform Integrations": {
                    "description": "Send To functionality for multiple platforms",
                    "features": ["send to", "platform sync", "integrations"],
                    "queries": ['"platform integrations"', '"send to functionality"', '"device sync"']
                },
                "Garmin Connect": {
                    "description": "Direct device sync and calendar integration",
                    "features": ["Garmin sync", "Garmin calendar", "device integration"],
                    "queries": ['"Garmin Connect"', '"Garmin sync"', '"Garmin calendar"']
                },
                "TrainingPeaks": {
                    "description": "Workout distribution and calendar sync",
                    "features": ["TrainingPeaks sync", "TP calendar", "workout distribution"],
                    "queries": ['"TrainingPeaks"', '"workout distribution"', '"TP sync"']
                },
                "Zwift Integration": {
                    "description": "Structured workout export with free-ride mode support",
                    "features": ["Zwift export", "ZWO files", "free-ride mode"],
                    "queries": ['"Zwift integration"', '"structured workout export"', '"ZWO"']
                },
                "Intervals.icu": {
                    "description": "Workout and calendar sync, WOD integration",
                    "features": ["intervals.icu", "WOD", "calendar sync"],
                    "queries": ['"Intervals.icu"', '"WOD integration"', '"intervals icu"']
                },
                "Other Platforms": {
                    "description": "Rouvy, MyWhoosh, Wahoo compatibility",
                    "features": ["Rouvy", "MyWhoosh", "Wahoo", "virtual training"],
                    "queries": ['"Rouvy MyWhoosh Wahoo"', '"virtual training"', '"device compatibility"']
                },
                "Outdoor Conversion": {
                    "description": "Convert indoor workouts to outdoor versions",
                    "features": ["outdoor conversion", "indoor to outdoor", "format conversion"],
                    "queries": ['"outdoor workout conversion"', '"indoor to outdoor"', '"format conversion"']
                },
                "HR Zone Conversion": {
                    "description": "Power zone to HR zone translation for outdoor training",
                    "features": ["HR zones", "power to HR", "zone conversion"],
                    "queries": ['"heart rate zone conversion"', '"power to HR zones"', '"zone conversion"']
                },
                "Calendar Distribution": {
                    "description": "Single creation, multiple platform delivery",
                    "features": ["calendar sync", "multi-platform", "distribution"],
                    "queries": ['"automatic calendar distribution"', '"multiple platform delivery"']
                }
            },
            "Workout Organization & Management": {
                "Personal Lists": {
                    "description": "Custom organization beyond tags",
                    "features": ["personal organization", "custom lists", "workout management"],
                    "queries": ['"personal workout lists"', '"custom organization"']
                },
                "Training App Shortcuts": {
                    "description": "Quick access to frequently used workout lists",
                    "features": ["shortcuts", "quick access", "app navigation"],
                    "queries": ['"training app shortcuts"', '"quick access"', '"frequently used"']
                },
                "Tag System": {
                    "description": "Public/private tag system for organization",
                    "features": ["tag system", "public tags", "private tags"],
                    "queries": ['"public private tag"', '"tag system"', '"organization"']
                },
                "Auto-complete Tags": {
                    "description": "Streamlined tagging process",
                    "features": ["auto-complete", "tag suggestions", "streamlined tagging"],
                    "queries": ['"auto-complete tag"', '"tag suggestions"', '"streamlined tagging"']
                },
                "Cross-platform Sync": {
                    "description": "Workout library accessible across web and mobile",
                    "features": ["cross-platform", "web mobile sync", "library sync"],
                    "queries": ['"cross-platform sync"', '"web mobile sync"', '"library access"']
                },
                "Bulk Operations": {
                    "description": "Batch editing and management",
                    "features": ["bulk edit", "batch operations", "mass management"],
                    "queries": ['"bulk workout operations"', '"batch editing"', '"mass management"']
                },
                "History Tracking": {
                    "description": "Completed workout records and progression",
                    "features": ["workout history", "completed workouts", "progression tracking"],
                    "queries": ['"workout history"', '"completed workouts"', '"progression tracking"']
                },
                "List Sharing": {
                    "description": "Private URLs for sharing workout collections",
                    "features": ["list sharing", "private URLs", "collection sharing"],
                    "queries": ['"list sharing"', '"private URLs"', '"workout collection sharing"']
                },
                "Hierarchical Tags": {
                    "description": "Organized category systems for export platforms",
                    "features": ["hierarchical tags", "category systems", "organized structure"],
                    "queries": ['"hierarchical tag"', '"organized categories"', '"export platforms"']
                }
            },
            "Community & Sharing Features": {
                "Workout Sharing": {
                    "description": "Public/private sharing with community",
                    "features": ["public sharing", "private sharing", "community sharing"],
                    "queries": ['"workout sharing"', '"public private sharing"', '"community sharing"']
                },
                "List Sharing": {
                    "description": "Private URLs for sharing workout collections",
                    "features": ["URL sharing", "collection sharing", "private links"],
                    "queries": ['"list sharing"', '"private URLs"', '"collection sharing"']
                },
                "Community Contributions": {
                    "description": "Public workouts become part of community library",
                    "features": ["community library", "public contributions", "shared content"],
                    "queries": ['"community contributions"', '"public workout library"', '"shared content"']
                },
                "Coach-Athlete Sharing": {
                    "description": "Dedicated features for coaching relationships",
                    "features": ["coach sharing", "athlete sharing", "coaching features"],
                    "queries": ['"coach-athlete"', '"coaching relationships"', '"training partnerships"']
                },
                "Link Sharing": {
                    "description": "Direct workout links for easy sharing",
                    "features": ["workout links", "direct sharing", "easy sharing"],
                    "queries": ['"link sharing"', '"direct workout links"', '"easy sharing"']
                }
            }
        }
        
    def get_all_content_by_keyword(self, keywords: list):
        """Get all content mentioning specific keywords"""
        conn = psycopg2.connect(**self.db_config)
        results = []
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                for keyword in keywords:
                    # Search for exact keyword matches
                    cur.execute("""
                        SELECT 
                            text,
                            metadata_->>'title' as title,
                            metadata_->>'source' as source,
                            metadata_->>'priority' as priority,
                            metadata_->>'content_type' as content_type,
                            metadata_->>'category' as category,
                            metadata_->>'url' as url,
                            metadata_->>'video_id' as video_id,
                            metadata_->>'fact_status' as fact_status
                        FROM llamaindex_knowledge_base 
                        WHERE LOWER(text) LIKE LOWER(%s)
                        ORDER BY 
                            CASE metadata_->>'source'
                                WHEN 'facts' THEN 1
                                WHEN 'blog' THEN 2
                                WHEN 'youtube' THEN 3
                                WHEN 'forum' THEN 4
                            END
                    """, (f'%{keyword}%',))
                    
                    keyword_results = cur.fetchall()
                    if keyword_results:
                        results.extend(keyword_results)
                        
        finally:
            conn.close()
            
        return results
    
    def query_by_embedding(self, query_text: str):
        """Query using embeddings with priority thresholds"""
        query_embedding = self.embedding_model.get_text_embedding(query_text)
        
        conn = psycopg2.connect(**self.db_config)
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    WITH ranked_results AS (
                        SELECT 
                            text,
                            metadata_->>'title' as title,
                            metadata_->>'source' as source,
                            metadata_->>'priority' as priority,
                            metadata_->>'content_type' as content_type,
                            metadata_->>'category' as category,
                            metadata_->>'url' as url,
                            metadata_->>'video_id' as video_id,
                            metadata_->>'fact_status' as fact_status,
                            metadata_->>'similarity_threshold' as threshold,
                            embedding <=> %s::vector as distance
                        FROM llamaindex_knowledge_base 
                        WHERE embedding IS NOT NULL
                    )
                    SELECT * FROM ranked_results
                    WHERE 
                        (source = 'facts' AND distance <= 0.2) OR
                        (source IN ('blog', 'youtube') AND distance <= 0.3) OR
                        (source = 'forum' AND content_type LIKE '%%qa%%' AND distance <= 0.4) OR
                        (source = 'forum' AND content_type NOT LIKE '%%qa%%' AND distance <= 0.6)
                    ORDER BY distance
                    LIMIT 50
                """, (query_embedding,))
                
                return cur.fetchall()
                
        finally:
            conn.close()
    
    def generate_comprehensive_json(self):
        """Generate comprehensive JSON with all workout features"""
        
        print("🏗️ GENERATING COMPREHENSIVE WORKOUT FEATURES JSON")
        print("=" * 80)
        
        comprehensive_data = {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "source": "TrainerDay LlamaIndex Knowledge Base",
                "total_features": 0,
                "total_content_items": 0,
                "content_sources": {
                    "facts": 0,
                    "blog": 0,
                    "youtube": 0,
                    "forum_qa": 0,
                    "forum_raw": 0
                }
            },
            "workout_features": {}
        }
        
        all_content = []
        feature_count = 0
        
        # Process each category
        for category_name, features in self.workout_features.items():
            print(f"\n📂 Processing: {category_name}")
            print("-" * 60)
            
            category_data = {
                "description": f"TrainerDay {category_name} capabilities",
                "features": {}
            }
            
            for feature_name, feature_info in features.items():
                feature_count += 1
                print(f"  🔍 {feature_name}...")
                
                feature_data = {
                    "description": feature_info["description"],
                    "capabilities": feature_info["features"],
                    "content": {
                        "facts": [],
                        "blog_articles": [],
                        "youtube_videos": [],
                        "forum_qa": [],
                        "forum_discussions": [],
                        "related_keywords": []
                    }
                }
                
                # Search using multiple methods
                all_results = []
                
                # 1. Query embeddings for each search query
                for query in feature_info["queries"]:
                    results = self.query_by_embedding(query)
                    all_results.extend(results)
                
                # 2. Direct keyword search for feature terms
                for keyword in feature_info["features"]:
                    keyword_results = self.get_all_content_by_keyword([keyword])
                    all_results.extend(keyword_results)
                
                # Deduplicate and organize by source
                seen = set()
                for result in all_results:
                    # Create unique key
                    key = f"{result['source']}:{result['title']}:{result['text'][:100]}"
                    if key in seen:
                        continue
                    seen.add(key)
                    
                    content_item = {
                        "title": result['title'],
                        "text": result['text'],
                        "content_type": result['content_type'],
                        "priority": result['priority']
                    }
                    
                    # Add source-specific metadata
                    if result['source'] == 'facts':
                        content_item['fact_status'] = result.get('fact_status', '')
                        feature_data['content']['facts'].append(content_item)
                        comprehensive_data['metadata']['content_sources']['facts'] += 1
                        
                    elif result['source'] == 'blog':
                        content_item['url'] = result.get('url', '')
                        content_item['category'] = result.get('category', '')
                        feature_data['content']['blog_articles'].append(content_item)
                        comprehensive_data['metadata']['content_sources']['blog'] += 1
                        
                    elif result['source'] == 'youtube':
                        content_item['video_id'] = result.get('video_id', '')
                        content_item['url'] = result.get('url', '')
                        feature_data['content']['youtube_videos'].append(content_item)
                        comprehensive_data['metadata']['content_sources']['youtube'] += 1
                        
                    elif result['source'] == 'forum':
                        if 'qa' in result['content_type']:
                            feature_data['content']['forum_qa'].append(content_item)
                            comprehensive_data['metadata']['content_sources']['forum_qa'] += 1
                        else:
                            feature_data['content']['forum_discussions'].append(content_item)
                            comprehensive_data['metadata']['content_sources']['forum_raw'] += 1
                
                # Extract related keywords from content
                all_text = ' '.join([r['text'] for r in all_results[:10]])  # First 10 results
                keywords = set()
                for feature in feature_info["features"]:
                    if feature.lower() in all_text.lower():
                        keywords.add(feature)
                feature_data['content']['related_keywords'] = list(keywords)
                
                # Add to category
                category_data['features'][feature_name] = feature_data
                
                # Summary for this feature
                total_content = sum([
                    len(feature_data['content']['facts']),
                    len(feature_data['content']['blog_articles']),
                    len(feature_data['content']['youtube_videos']),
                    len(feature_data['content']['forum_qa']),
                    len(feature_data['content']['forum_discussions'])
                ])
                
                print(f"    ✓ Found {total_content} content items")
                comprehensive_data['metadata']['total_content_items'] += total_content
            
            comprehensive_data['workout_features'][category_name] = category_data
        
        comprehensive_data['metadata']['total_features'] = feature_count
        
        # Save to file
        output_dir = Path("./script-testing/workout_query_results")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / "comprehensive_workout_features.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_data, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 GENERATION COMPLETE")
        print("=" * 80)
        print(f"Total Features Documented: {feature_count}")
        print(f"Total Content Items: {comprehensive_data['metadata']['total_content_items']}")
        print("\nContent Distribution:")
        for source, count in comprehensive_data['metadata']['content_sources'].items():
            print(f"  • {source}: {count}")
        print(f"\n💾 Saved to: {output_file}")
        
        # Generate summary report
        self.generate_summary_report(comprehensive_data, output_dir / "workout_features_summary.md")
        
        return comprehensive_data
    
    def generate_summary_report(self, data: dict, output_file: Path):
        """Generate a markdown summary report"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# TrainerDay Workout Features - Comprehensive Summary\n\n")
            f.write(f"*Generated: {data['metadata']['generated']}*\n\n")
            f.write(f"**Total Features**: {data['metadata']['total_features']}  \n")
            f.write(f"**Total Content Items**: {data['metadata']['total_content_items']}\n\n")
            
            f.write("## Content Source Distribution\n\n")
            for source, count in data['metadata']['content_sources'].items():
                f.write(f"- **{source}**: {count} items\n")
            
            f.write("\n## Feature Categories\n\n")
            
            for category_name, category_data in data['workout_features'].items():
                f.write(f"### {category_name}\n\n")
                
                for feature_name, feature_data in category_data['features'].items():
                    content_count = sum([
                        len(feature_data['content']['facts']),
                        len(feature_data['content']['blog_articles']),
                        len(feature_data['content']['youtube_videos']),
                        len(feature_data['content']['forum_qa']),
                        len(feature_data['content']['forum_discussions'])
                    ])
                    
                    f.write(f"**{feature_name}** ({content_count} items)\n")
                    f.write(f"- {feature_data['description']}\n")
                    
                    # Show content distribution
                    if content_count > 0:
                        sources = []
                        if feature_data['content']['facts']:
                            sources.append(f"Facts: {len(feature_data['content']['facts'])}")
                        if feature_data['content']['blog_articles']:
                            sources.append(f"Blog: {len(feature_data['content']['blog_articles'])}")
                        if feature_data['content']['youtube_videos']:
                            sources.append(f"YouTube: {len(feature_data['content']['youtube_videos'])}")
                        if feature_data['content']['forum_qa']:
                            sources.append(f"Forum Q&A: {len(feature_data['content']['forum_qa'])}")
                        if feature_data['content']['forum_discussions']:
                            sources.append(f"Forum: {len(feature_data['content']['forum_discussions'])}")
                        
                        f.write(f"- Content: {', '.join(sources)}\n")
                    
                    f.write("\n")
        
        print(f"📄 Summary report saved to: {output_file}")

def main():
    """Generate comprehensive workout features JSON"""
    generator = ComprehensiveWorkoutData()
    comprehensive_data = generator.generate_comprehensive_json()
    
    print("\n✅ Generation complete!")

if __name__ == "__main__":
    main()