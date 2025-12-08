#!/bin/bash
# View backend performance logs

LOG_FILE="logs/backend.log"

if [ ! -f "$LOG_FILE" ]; then
    echo "📝 No log file found yet."
    echo "   Logs will be created after the next API request."
    echo ""
    echo "💡 To generate logs, make a search request from the frontend"
    echo "   or use: curl -X POST http://localhost:8000/api/v1/search ..."
    exit 0
fi

echo "📊 Recent Backend Performance Logs"
echo "===================================="
echo ""

# Show last 50 lines with timing information
echo "⏱️  Performance Timing Logs:"
echo "----------------------------"
grep -E "(⏱️|Search completed|Total time|Search time|Generation time)" "$LOG_FILE" | tail -20

echo ""
echo "📋 Full Recent Logs (last 30 lines):"
echo "-------------------------------------"
tail -30 "$LOG_FILE"

echo ""
echo "💡 To follow logs in real-time: tail -f $LOG_FILE"

