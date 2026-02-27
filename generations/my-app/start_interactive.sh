#!/bin/bash

# Start Interactive Blending Board Interface - ALPA-4
# This script starts the gamification API backend and serves the interactive interface

set -e

echo "Starting ALPA-4 Interactive Interface..."

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found. Please run init.sh first."
    exit 1
fi

# Check if dependencies are installed
echo "Checking dependencies..."
pip list | grep -q flask || pip install -r requirements.txt

# Start Flask API in background
echo "Starting Gamification API on port 5001..."
python3 app/gamification_api.py &
API_PID=$!
echo "API started with PID $API_PID"

# Wait for API to be ready
sleep 2

# Start simple HTTP server for the interface
echo "Starting Interactive Interface on port 8000..."
python3 -m http.server 8000 &
SERVER_PID=$!
echo "Server started with PID $SERVER_PID"

echo ""
echo "======================================================================"
echo "  ALPA-4 Interactive Interface is now running!"
echo "======================================================================"
echo ""
echo "  Interactive Interface: http://localhost:8000/interactive_interface.html"
echo "  API Endpoint: http://localhost:5001"
echo ""
echo "  Press Ctrl+C to stop all services"
echo ""
echo "======================================================================"

# Trap Ctrl+C to kill all background processes
trap "echo 'Stopping services...'; kill $API_PID $SERVER_PID 2>/dev/null; exit" INT

# Wait for background processes
wait
