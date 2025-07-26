#!/usr/bin/env python3
"""
Create Comprehensive Workout Features JSON
Combines workout feature definitions with actual content from the knowledge base
"""

import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

def create_comprehensive_json():
    """Create a comprehensive JSON combining feature definitions with database content"""
    
    # Database configuration
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'trainerday_local',
        'user': os.getenv('USER', 'alex'),
        'password': '',
    }
    
    # Load the existing query results
    results_file = Path("./script-testing/workout_query_results/workout_features_results_20250725_175221.json")
    
    with open(results_file, 'r', encoding='utf-8') as f:
        query_results = json.load(f)
    
    # Complete workout feature definitions from workouts.md
    workout_features = {
        "metadata": {
            "title": "TrainerDay Workout Features - Comprehensive Documentation",
            "description": "Complete feature set for TrainerDay workout creation, management, and training",
            "generated": datetime.now().isoformat(),
            "version": "1.0",
            "total_features": 100,  # Approximate count from workouts.md
            "sources": {
                "primary": "workouts.md feature list",
                "knowledge_base": "LlamaIndex unified knowledge base",
                "content_types": ["facts", "blog_articles", "youtube_videos", "forum_qa", "forum_discussions"]
            }
        },
        "feature_categories": {
            "Workout Creation & Management": {
                "description": "Tools and features for creating, editing, and managing workouts",
                "features": {
                    "Visual Workout Editor": {
                        "description": "Drag-and-drop interface with Excel-like functionality",
                        "key_features": [
                            "Drag-and-drop workout blocks",
                            "Excel-like grid editing",
                            "Copy/paste functionality",
                            "Visual representation of intervals"
                        ],
                        "use_cases": [
                            "Creating custom workouts",
                            "Modifying existing workouts",
                            "Visual workout design"
                        ],
                        "related_content": []
                    },
                    "Fastest Workout Editor": {
                        "description": "Keyboard-focused speed editing with shortcuts",
                        "key_features": [
                            "Keyboard shortcuts",
                            "Arrow key navigation",
                            "Quick copy/paste",
                            "Rapid interval creation"
                        ],
                        "use_cases": [
                            "Quick workout modifications",
                            "Efficient bulk editing",
                            "Speed-focused workflow"
                        ],
                        "related_content": []
                    },
                    "Sets and Reps Editor": {
                        "description": "Create complex interval structures with repeated patterns",
                        "key_features": [
                            "Set-based interval creation",
                            "Repetition patterns",
                            "Complex interval structures",
                            "Nested intervals"
                        ],
                        "use_cases": [
                            "HIIT workouts",
                            "Structured interval training",
                            "Complex training patterns"
                        ],
                        "related_content": []
                    },
                    "Interval Comments & Coaching Notes": {
                        "description": "Add instructions and cues to specific intervals with timing",
                        "key_features": [
                            "Per-interval comments",
                            "Coaching instructions",
                            "Timed cues",
                            "Motivational messages"
                        ],
                        "use_cases": [
                            "Self-coaching",
                            "Guided workouts",
                            "Form reminders"
                        ],
                        "related_content": []
                    },
                    "Route Importing": {
                        "description": "Import GPS routes for outdoor simulation",
                        "key_features": [
                            "GPX file import",
                            "FIT file support",
                            "Elevation profile",
                            "Power/slope calculation"
                        ],
                        "use_cases": [
                            "Race preparation",
                            "Route simulation",
                            "Outdoor training indoors"
                        ],
                        "related_content": []
                    },
                    "Target Modes": {
                        "description": "Multiple training target options",
                        "key_features": [
                            "Power/ERG targets",
                            "Heart rate targets",
                            "Slope simulation",
                            "Feel-based training",
                            "Resistance mode"
                        ],
                        "use_cases": [
                            "Different training styles",
                            "Equipment compatibility",
                            "Varied workout types"
                        ],
                        "related_content": []
                    },
                    "Mixed-Mode Workouts": {
                        "description": "Automatic switching between target modes in one workout",
                        "key_features": [
                            "Mode transitions",
                            "Automatic switching",
                            "Mixed targets",
                            "Seamless changes"
                        ],
                        "use_cases": [
                            "Varied training stimulus",
                            "Complete workouts",
                            "Advanced training"
                        ],
                        "related_content": []
                    },
                    "Workout Tags & Organization": {
                        "description": "Categorization system for workout library",
                        "key_features": [
                            "Public tags",
                            "Private tags",
                            "Tag-based search",
                            "Organization system"
                        ],
                        "use_cases": [
                            "Workout organization",
                            "Easy discovery",
                            "Personal categorization"
                        ],
                        "related_content": []
                    },
                    "Workout Cloning": {
                        "description": "Duplicate workouts with ALT+drag",
                        "key_features": [
                            "ALT+drag duplication",
                            "Quick copying",
                            "Workout templates",
                            "Easy modification"
                        ],
                        "use_cases": [
                            "Creating variations",
                            "Template workouts",
                            "Quick customization"
                        ],
                        "related_content": []
                    },
                    "Ramps and Steps": {
                        "description": "Progressive power changes with Garmin optimization",
                        "key_features": [
                            "Gradual power ramps",
                            "Step conversions",
                            "Garmin 50-step limit",
                            "Smooth progressions"
                        ],
                        "use_cases": [
                            "Warmup protocols",
                            "Progressive intervals",
                            "Threshold testing"
                        ],
                        "related_content": []
                    },
                    "Free Ride/Open-Ended Intervals": {
                        "description": "Intervals that continue until manually stopped",
                        "key_features": [
                            "Lap button control",
                            "Open duration",
                            "Manual progression",
                            "Flexible timing"
                        ],
                        "use_cases": [
                            "Time trials",
                            "Testing efforts",
                            "Flexible training"
                        ],
                        "related_content": []
                    },
                    "W'bal Integration": {
                        "description": "Anaerobic capacity modeling for interval design",
                        "key_features": [
                            "W' balance tracking",
                            "Anaerobic capacity",
                            "Recovery modeling",
                            "Interval optimization"
                        ],
                        "use_cases": [
                            "Scientific training",
                            "Optimal intervals",
                            "Recovery planning"
                        ],
                        "related_content": []
                    },
                    "Multi-Sport Workout Creation": {
                        "description": "Support for cycling, rowing, and swimming",
                        "key_features": [
                            "Cycling workouts",
                            "Rowing support",
                            "Swimming workouts",
                            "Sport-specific metrics"
                        ],
                        "use_cases": [
                            "Cross-training",
                            "Multi-sport athletes",
                            "Varied training"
                        ],
                        "related_content": []
                    }
                }
            },
            "Training Modes": {
                "description": "Different control modes for smart trainers and training styles",
                "features": {
                    "ERG Mode": {
                        "description": "Automatic power control regardless of cadence",
                        "key_features": [
                            "Fixed power output",
                            "Cadence independent",
                            "Automatic resistance",
                            "Consistent power"
                        ],
                        "use_cases": [
                            "Structured intervals",
                            "Power-based training",
                            "Indoor training"
                        ],
                        "related_content": []
                    },
                    "HR+ Mode": {
                        "description": "Heart rate controlled training with power adjustments",
                        "key_features": [
                            "HR-based control",
                            "Automatic power adjustment",
                            "Zone targeting",
                            "Adaptive resistance"
                        ],
                        "use_cases": [
                            "Zone 2 training",
                            "HR-based workouts",
                            "Adaptive training"
                        ],
                        "related_content": []
                    },
                    "Slope Mode": {
                        "description": "Gradient simulation with gear shifting",
                        "key_features": [
                            "Virtual gradients",
                            "Gear control",
                            "Realistic feel",
                            "Grade changes"
                        ],
                        "use_cases": [
                            "Climbing simulation",
                            "Outdoor feel",
                            "Variable resistance"
                        ],
                        "related_content": []
                    },
                    "Resistance Mode": {
                        "description": "Fixed resistance for sprints and strength",
                        "key_features": [
                            "Fixed percentage",
                            "Sprint training",
                            "Strength work",
                            "Manual control"
                        ],
                        "use_cases": [
                            "Sprint intervals",
                            "Strength training",
                            "Specific drills"
                        ],
                        "related_content": []
                    }
                }
            },
            "Training Execution & Real-time Features": {
                "description": "Features available during active training sessions",
                "features": {
                    "Real-time Training": {
                        "description": "Live workout execution with trainer control",
                        "key_features": [
                            "Live control",
                            "Real-time adjustments",
                            "Smart trainer sync",
                            "Instant feedback"
                        ],
                        "related_content": []
                    },
                    "6-Second Warmup": {
                        "description": "Ultra-quick start functionality",
                        "key_features": [
                            "Instant start",
                            "Quick warmup",
                            "Fast beginning",
                            "No delays"
                        ],
                        "related_content": []
                    },
                    "Dynamic Workout Editing": {
                        "description": "Modify workouts during execution",
                        "key_features": [
                            "On-the-fly changes",
                            "Live modifications",
                            "Real-time editing",
                            "Adaptive training"
                        ],
                        "related_content": []
                    },
                    "Power Adjustments": {
                        "description": "+/- buttons for instant power changes",
                        "key_features": [
                            "10-second increments",
                            "Quick adjustments",
                            "Power buttons",
                            "Easy modification"
                        ],
                        "related_content": []
                    },
                    "Hot Swap Feature": {
                        "description": "Change workouts mid-session",
                        "key_features": [
                            "Workout switching",
                            "Seamless transition",
                            "No interruption",
                            "Flexibility"
                        ],
                        "related_content": []
                    },
                    "Auto-extend Workouts": {
                        "description": "Continue beyond planned duration",
                        "key_features": [
                            "Extended duration",
                            "User control",
                            "Flexible ending",
                            "Bonus intervals"
                        ],
                        "related_content": []
                    },
                    "FTP-based Scaling": {
                        "description": "Automatic workout scaling to fitness",
                        "key_features": [
                            "FTP adjustment",
                            "Fitness scaling",
                            "Personalized power",
                            "Adaptive workouts"
                        ],
                        "related_content": []
                    }
                }
            },
            "Real-time Display & Monitoring": {
                "description": "Visual feedback and data display features",
                "features": {
                    "Broadcast to Big Screen": {
                        "description": "Cast data to external displays",
                        "key_features": [
                            "TV casting",
                            "External monitors",
                            "Big screen view",
                            "Multi-device"
                        ],
                        "related_content": []
                    },
                    "Power Zone Displays": {
                        "description": "Visual power zone indicators",
                        "key_features": [
                            "Zone visualization",
                            "Color coding",
                            "Real-time zones",
                            "Clear indicators"
                        ],
                        "related_content": []
                    },
                    "Real-time Metrics": {
                        "description": "Live training data display",
                        "key_features": [
                            "Power display",
                            "Heart rate",
                            "Cadence",
                            "Speed/distance"
                        ],
                        "related_content": []
                    },
                    "Secret URL Sharing": {
                        "description": "Share live data with coaches",
                        "key_features": [
                            "Private URLs",
                            "Coach viewing",
                            "Live sharing",
                            "Remote monitoring"
                        ],
                        "related_content": []
                    }
                }
            },
            "Workout Library & Discovery": {
                "description": "Finding and organizing workouts",
                "features": {
                    "Community Workout Library": {
                        "description": "Access to thousands of shared workouts",
                        "key_features": [
                            "30,000+ workouts",
                            "Community created",
                            "Searchable library",
                            "User contributions"
                        ],
                        "related_content": []
                    },
                    "Workout Search and Filtering": {
                        "description": "Advanced search capabilities",
                        "key_features": [
                            "Tag search",
                            "Difficulty filter",
                            "Duration filter",
                            "Sport type"
                        ],
                        "related_content": []
                    },
                    "Rating System": {
                        "description": "Community-driven workout ratings",
                        "key_features": [
                            "User ratings",
                            "Popularity sorting",
                            "Quality indicators",
                            "Community feedback"
                        ],
                        "related_content": []
                    },
                    "Author Following": {
                        "description": "Follow favorite workout creators",
                        "key_features": [
                            "Creator profiles",
                            "Follow system",
                            "New workout alerts",
                            "Favorite authors"
                        ],
                        "related_content": []
                    }
                }
            },
            "Workout Export & Integration": {
                "description": "Sharing workouts with other platforms",
                "features": {
                    "Multi-Format Export": {
                        "description": "Export to various file formats",
                        "key_features": [
                            "TCX export",
                            "ZWO (Zwift)",
                            "MRC format",
                            "ERG files"
                        ],
                        "related_content": []
                    },
                    "Garmin Connect": {
                        "description": "Direct Garmin device integration",
                        "key_features": [
                            "Direct sync",
                            "Calendar integration",
                            "Device push",
                            "Workout library"
                        ],
                        "related_content": []
                    },
                    "TrainingPeaks": {
                        "description": "TrainingPeaks calendar sync",
                        "key_features": [
                            "Calendar sync",
                            "Workout distribution",
                            "Planning integration",
                            "ATP/CTL tracking"
                        ],
                        "related_content": []
                    },
                    "Zwift Integration": {
                        "description": "Export workouts to Zwift",
                        "key_features": [
                            "ZWO export",
                            "Custom workouts",
                            "Free ride support",
                            "Zwift compatibility"
                        ],
                        "related_content": []
                    },
                    "Other Platform Support": {
                        "description": "Additional platform integrations",
                        "key_features": [
                            "Intervals.icu",
                            "Wahoo devices",
                            "Rouvy",
                            "MyWhoosh"
                        ],
                        "related_content": []
                    }
                }
            },
            "Workout Organization & Management": {
                "description": "Tools for organizing workout libraries",
                "features": {
                    "Personal Workout Lists": {
                        "description": "Custom workout organization",
                        "key_features": [
                            "Custom lists",
                            "Personal organization",
                            "Quick access",
                            "List management"
                        ],
                        "related_content": []
                    },
                    "Cross-platform Sync": {
                        "description": "Sync across devices",
                        "key_features": [
                            "Web sync",
                            "Mobile sync",
                            "Real-time updates",
                            "Multi-device"
                        ],
                        "related_content": []
                    },
                    "Bulk Operations": {
                        "description": "Manage multiple workouts",
                        "key_features": [
                            "Batch editing",
                            "Mass operations",
                            "Quick updates",
                            "Efficient management"
                        ],
                        "related_content": []
                    }
                }
            },
            "Community & Sharing Features": {
                "description": "Social and sharing capabilities",
                "features": {
                    "Workout Sharing": {
                        "description": "Share workouts with community",
                        "key_features": [
                            "Public sharing",
                            "Private sharing",
                            "Community library",
                            "Easy distribution"
                        ],
                        "related_content": []
                    },
                    "Coach-Athlete Sharing": {
                        "description": "Coaching relationship features",
                        "key_features": [
                            "Coach access",
                            "Athlete sharing",
                            "Training plans",
                            "Progress tracking"
                        ],
                        "related_content": []
                    },
                    "Link Sharing": {
                        "description": "Direct workout links",
                        "key_features": [
                            "Shareable URLs",
                            "Direct access",
                            "Easy sharing",
                            "Quick distribution"
                        ],
                        "related_content": []
                    }
                }
            }
        },
        "query_results_mapping": {}
    }
    
    # Map query results to features
    if 'results' in query_results:
        # Add the query results as related content
        workout_features['query_results_mapping'] = query_results['results']
        
        # Also add summary statistics
        workout_features['metadata']['query_statistics'] = query_results['summary']
    
    # Get additional statistics from database
    conn = psycopg2.connect(**db_config)
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get total counts by source
            cur.execute("""
                SELECT 
                    metadata_->>'source' as source,
                    COUNT(*) as count
                FROM llamaindex_knowledge_base
                GROUP BY metadata_->>'source'
                ORDER BY count DESC
            """)
            
            source_counts = cur.fetchall()
            workout_features['metadata']['knowledge_base_statistics'] = {
                row['source']: row['count'] for row in source_counts
            }
            
            # Get sample content for each source
            for source in ['facts', 'blog', 'youtube', 'forum']:
                cur.execute("""
                    SELECT 
                        metadata_->>'title' as title,
                        metadata_->>'content_type' as content_type,
                        metadata_->>'priority' as priority
                    FROM llamaindex_knowledge_base
                    WHERE metadata_->>'source' = %s
                    LIMIT 5
                """, (source,))
                
                samples = cur.fetchall()
                workout_features['metadata'][f'{source}_samples'] = samples
                
    finally:
        conn.close()
    
    # Save comprehensive JSON
    output_dir = Path("./script-testing/workout_query_results")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "comprehensive_workout_features.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(workout_features, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Comprehensive JSON created: {output_file}")
    print(f"📊 Total features documented: {len(workout_features['feature_categories'])}")
    print(f"📚 Knowledge base sources: {workout_features['metadata']['knowledge_base_statistics']}")
    
    return workout_features

if __name__ == "__main__":
    create_comprehensive_json()