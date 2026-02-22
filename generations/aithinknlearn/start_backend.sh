#!/bin/bash

# Start backend server for Multi-Agent Orchestration System

echo "Starting Multi-Agent Orchestration Backend..."
echo ""

# Activate virtual environment and start server
cd "$(dirname "$0")"

# Set mock mode if no API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Note: OPENAI_API_KEY not set. System will run in structure-test mode."
    echo "For full LLM functionality, set OPENAI_API_KEY in .env file"
    echo ""
fi

# Start FastAPI server
/Users/jordanmason/WOC/2026/opal_site/generations/aithinknlearn/venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
