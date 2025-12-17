#!/bin/bash
# Startup script for the RAG Chatbot Backend

echo "Starting RAG Chatbot Backend for Physical AI and Humanoid Robotics Textbook..."

# Activate virtual environment
source .venv/bin/activate

# Run the application
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

echo "Server started on http://localhost:8000"