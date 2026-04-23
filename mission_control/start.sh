#!/bin/bash
# Mission Control Startup Script
# Usage: ./start.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PYTHON="/home/thecarter34/.openclaw/workspace/development/GolfLeague/scorecard_automation/.venv/bin/python3.12"
LOG_FILE="/tmp/mission_control.log"

cd "$SCRIPT_DIR"

echo "🚀 Starting Mission Control..."
nohup "$VENV_PYTHON" mission_control.py > "$LOG_FILE" 2>&1 &
echo "   PID: $!"
echo "   Logs: tail -f $LOG_FILE"
echo "   Dashboard: http://localhost:5050"
