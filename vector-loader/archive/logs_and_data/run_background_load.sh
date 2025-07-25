#!/bin/bash
# Background loader script with monitoring

echo "🚀 Starting LlamaIndex full data loading in background..."

# Run the loader in background
nohup python llamaindex_full_data_loader.py > llamaindex_load_output.log 2>&1 &
LOADER_PID=$!

echo "✅ Background process started with PID: $LOADER_PID"
echo "📁 Logs: llamaindex_load_output.log"
echo "📊 Progress: python llamaindex_full_data_loader.py monitor"
echo ""
echo "Monitor commands:"
echo "  Check progress: python llamaindex_full_data_loader.py monitor"
echo "  View logs: tail -f llamaindex_load_output.log" 
echo "  Check process: ps aux | grep $LOADER_PID"
echo ""

# Show initial progress
sleep 2
echo "Initial status:"
python llamaindex_full_data_loader.py monitor