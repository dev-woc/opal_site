#!/bin/bash

echo "Starting Agentic Literacy Pipeline..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Python is installed
echo -e "${BLUE}Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi
echo -e "${GREEN}Python 3 found: $(python3 --version)${NC}"
echo ""

# Check if Node.js is installed
echo -e "${BLUE}Checking Node.js installation...${NC}"
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi
echo -e "${GREEN}Node.js found: $(node --version)${NC}"
echo ""

# Check if npm is installed
echo -e "${BLUE}Checking npm installation...${NC}"
if ! command -v npm &> /dev/null; then
    echo "npm is not installed. Please install npm."
    exit 1
fi
echo -e "${GREEN}npm found: $(npm --version)${NC}"
echo ""

# Create virtual environment for Python
echo -e "${BLUE}Setting up Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}Virtual environment created${NC}"
else
    echo -e "${GREEN}Virtual environment already exists${NC}"
fi
echo ""

# Activate virtual environment
source venv/bin/activate
echo -e "${GREEN}Virtual environment activated${NC}"
echo ""

# Install Python dependencies
if [ -f "backend/requirements.txt" ]; then
    echo -e "${BLUE}Installing Python dependencies...${NC}"
    pip install -r backend/requirements.txt
    echo -e "${GREEN}Python dependencies installed${NC}"
else
    echo -e "${BLUE}backend/requirements.txt not found. Skipping Python dependency installation.${NC}"
fi
echo ""

# Install Node.js dependencies
if [ -f "frontend/package.json" ]; then
    echo -e "${BLUE}Installing Node.js dependencies...${NC}"
    npm install --prefix frontend
    echo -e "${GREEN}Node.js dependencies installed${NC}"
else
    echo -e "${BLUE}frontend/package.json not found. Skipping Node.js dependency installation.${NC}"
fi
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${BLUE}Note: .env file not found. Please create a .env file with your configuration.${NC}"
    echo -e "${BLUE}You can copy from .env.example if it exists.${NC}"
    echo ""
fi

echo -e "${GREEN}Agentic Literacy Pipeline is ready!${NC}"
echo ""
echo "To start the development server:"
echo "1. Backend: cd backend && python app.py"
echo "2. Frontend: cd frontend && npm start"
echo ""
echo "Or if you have concurrently installed:"
echo "npm run dev"
echo ""
