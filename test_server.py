#!/usr/bin/env python3
"""
Simple test server to verify FastAPI setup works before running the full chatbot.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

# Create FastAPI app
app = FastAPI(
    title="Al Essa Kuwait Chatbot - Test Server",
    description="Test server to verify setup",
    version="1.0.0-test"
)

class ChatRequest(BaseModel):
    text: str
    session_id: str = "test_session"

class ChatResponse(BaseModel):
    reply: str
    success: bool
    agent_type: str
    products: list = []
    workflow_steps: list = []

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Al Essa Kuwait Chatbot Test Server is running!"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "Test server is running",
        "version": "1.0.0-test"
    }

@app.post("/chat", response_model=ChatResponse)
async def test_chat(request: ChatRequest):
    """Test chat endpoint without OpenAI integration."""
    
    # Simple rule-based responses for testing
    text_lower = request.text.lower()
    
    if "wheelchair" in text_lower:
        return ChatResponse(
            reply="I found some wheelchairs for you! (This is a test response - OpenAI integration needed for full functionality)",
            success=True,
            agent_type="sales",
            products=[
                {"name": "Test Wheelchair", "price": "100 KWD", "url": "test-url"}
            ],
            workflow_steps=["test_routing", "mock_product_search"]
        )
    elif "medical" in text_lower or "doctor" in text_lower:
        return ChatResponse(
            reply="I can help with medical advice! (This is a test response - OpenAI integration needed for full functionality)",
            success=True,
            agent_type="doctor",
            products=[],
            workflow_steps=["test_routing", "mock_medical_advice"]
        )
    else:
        return ChatResponse(
            reply=f"You said: '{request.text}'. This is a test server response. Please add your OpenAI API key to enable full functionality!",
            success=True,
            agent_type="test",
            products=[],
            workflow_steps=["test_response"]
        )

@app.get("/test-info")
async def test_info():
    """Information about this test server."""
    return {
        "message": "This is a test server to verify your FastAPI setup works",
        "next_steps": [
            "1. Add your OpenAI API key to the .env file",
            "2. Install remaining dependencies: pip3 install openai langchain langchain-openai --break-system-packages",
            "3. Run the full chatbot: python3 app/api/main.py"
        ],
        "test_endpoints": {
            "health": "/health",
            "chat": "/chat (POST)",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🧪 Starting Al Essa Kuwait Chatbot Test Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    print("💡 This is a test server - add OpenAI API key for full functionality")
    uvicorn.run(app, host="0.0.0.0", port=8000)