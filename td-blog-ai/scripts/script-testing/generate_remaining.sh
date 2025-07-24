#!/bin/bash

# Generate remaining feature articles F005-F070
echo "🎯 Generating remaining feature articles F005-F070..."

for i in {5..70}; do
    f_number=$(printf "F%03d" $i)
    echo "🔄 Generating article #$i as $f_number..."
    
    python generate_numbered_article.py $i "${f_number}-placeholder.md"
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully generated $f_number"
    else
        echo "❌ Failed to generate $f_number"
    fi
    
    # Small delay to avoid rate limiting
    sleep 3
done

echo "🎉 Batch generation complete!"