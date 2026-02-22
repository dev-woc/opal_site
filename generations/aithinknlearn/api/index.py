"""
Vercel serverless entry point for the Agentic Literacy Pipeline API.
Wraps the FastAPI app for deployment on Vercel.
"""

import sys
import os

# Add the project root to the path so backend imports resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app
