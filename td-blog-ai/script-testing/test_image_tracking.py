#!/usr/bin/env python3
"""
Test script to demonstrate image tracking functionality
"""

import json
from pathlib import Path

# Example of what the workout-edits.json will look like with images
example_edits_data = {
    "last_updated": "2025-07-26T20:30:00.000Z",
    "global_instructions": {
        "style": ["Always use 'Workout Editor' not 'Visual Workout Editor'"],
        "facts_to_avoid": ["Drag and drop functionality"]
    },
    "articles": {
        "s01-Workout_Editor_Basics": {
            "title": "Workout Editor Basics",
            "edit_instructions": [
                {
                    "section": "Introduction",
                    "instruction": "Emphasize Excel-like functionality",
                    "type": "enhancement"
                }
            ],
            "facts_to_add": ["Copy paste works like Excel"],
            "facts_to_remove": ["Visual drag and drop"],
            "custom_sections": []
        }
    },
    "images": {
        "s01-Workout_Editor_Basics": {
            "title": "Workout Editor Basics",
            "images": [
                {
                    "url": "https://i.ibb.co/abcd123/workout-editor-interface.png",
                    "alt_text": "Workout Editor main interface",
                    "type": "article_level",
                    "line_number": 5,
                    "context": "article_header",
                    "metadata": {
                        "keywords": ["workout", "editor", "main", "interface"],
                        "topics": [],
                        "feature": "workout editor"
                    }
                },
                {
                    "url": "https://i.ibb.co/xyz789/copy-paste-example.png",
                    "alt_text": "Copy and paste functionality in action",
                    "type": "inline",
                    "line_number": 35,
                    "context": "section: Excel-Like Features",
                    "metadata": {
                        "keywords": ["copy", "paste", "functionality", "action"],
                        "topics": [],
                        "feature": "workout editor"
                    }
                }
            ],
            "count": 2
        },
        "s02-Control_Modes_ERG_Slope_Resistance_HR": {
            "title": "Training Control Modes",
            "images": [
                {
                    "url": "https://i.ibb.co/def456/erg-mode-display.png",
                    "alt_text": "ERG mode power display",
                    "type": "inline",
                    "line_number": 22,
                    "context": "ERG mode maintains constant power output regardless of cadence...",
                    "metadata": {
                        "keywords": ["mode", "power", "display"],
                        "topics": [],
                        "feature": "erg mode"
                    }
                }
            ],
            "count": 1
        }
    }
}

# Save example to show structure
output_file = Path("script-testing/example_workout-edits-with-images.json")
output_file.parent.mkdir(exist_ok=True)

with open(output_file, 'w') as f:
    json.dump(example_edits_data, f, indent=2)

print(f"✅ Created example edit file with image tracking at: {output_file}")
print(f"\n📊 Summary:")
print(f"   - Articles with edits: {len(example_edits_data['articles'])}")
print(f"   - Articles with images: {len(example_edits_data['images'])}")
print(f"   - Total images tracked: {sum(article['count'] for article in example_edits_data['images'].values())}")

# Show what images would be reinserted
print(f"\n🖼️  Image reinsertion preview:")
for article_key, article_data in example_edits_data['images'].items():
    print(f"\n   {article_key}:")
    for img in article_data['images']:
        print(f"      - {img['type']}: {img['alt_text']}")
        print(f"        URL: {img['url'][:50]}...")
        print(f"        Context: {img['context']}")