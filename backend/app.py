"""
Hugging Face Spaces entry point for the RAG Chatbot Backend
This file serves as the main entry point for Hugging Face Spaces deployment
"""

import os
import asyncio
from src.main import app

# Set environment variables for Hugging Face Spaces
os.environ.setdefault('DEBUG', 'False')

# Ensure startup events run when the app is loaded
@app.on_event("startup")
async def startup_event_wrapper():
    """Wrapper to ensure startup events run properly in Hugging Face Spaces"""
    from src.main import startup_event
    await startup_event()

# Hugging Face Spaces will automatically serve this FastAPI app
# The variable 'app' is what Hugging Face will look for
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 7860)),  # Hugging Face uses PORT environment variable
        reload=False
    )