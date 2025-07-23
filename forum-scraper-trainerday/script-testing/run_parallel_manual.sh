#!/bin/bash

echo "🚀 Running 4 parallel processors manually"
echo "Each will process topics independently with database preventing conflicts"
echo "Press Ctrl+C to stop"
echo

# Run 4 processes in parallel in the background
python3 process_next_latest.py &
PID1=$!
echo "Started processor 1 (PID: $PID1)"

sleep 2  # Stagger starts slightly

python3 process_next_latest.py &
PID2=$!
echo "Started processor 2 (PID: $PID2)"

sleep 2

python3 process_next_latest.py &
PID3=$!
echo "Started processor 3 (PID: $PID3)"

sleep 2

python3 process_next_latest.py &
PID4=$!
echo "Started processor 4 (PID: $PID4)"

echo
echo "All 4 processors running in parallel..."
echo "PIDs: $PID1, $PID2, $PID3, $PID4"
echo

# Wait for all processes to complete
wait $PID1 $PID2 $PID3 $PID4

echo "All processors completed!"