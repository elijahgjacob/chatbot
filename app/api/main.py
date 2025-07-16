"""
FastAPI Chatbot with Agentic Workflow
"""
import logging
from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.agents.agent import chatbot_agent
from app.tools.tools import get_product_prices_from_search

# Initialize FastAPI app
app = FastAPI(
    title="Alessa Med Virtual Health & Sales Assistant",
    description="A chatbot that helps users find medical equipment using agentic workflows",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory chat history storage (replace with database in production)
chat_history: Dict[str, List[Dict[str, str]]] = {}

@dataclass
class ChatRequest:
    text: str
    session_id: str = "default"

@dataclass
class ChatResponse:
    response: str
    reply: str
    session_id: str
    products: list = field(default_factory=list)
    workflow_steps: list = field(default_factory=list)
    success: bool = True

@dataclass
class ScrapePricesRequest:
    query: str

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Medical Equipment Chatbot API", "status": "running"}

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    chat_request = ChatRequest(**data)
    query = chat_request.text
    session_id = chat_request.session_id
    logger.info(f"Received /chat request: {query} (session: {session_id})")
    try:
        agent_result = chatbot_agent.process_query(query, session_id)
        if agent_result.get("success"):
            # Store chat history
            if session_id not in chat_history:
                chat_history[session_id] = []
            chat_history[session_id].append({
                "user": query,
                "bot": agent_result.get("reply", ""),
                "agent_type": agent_result.get("agent_type", "unknown"),
                "routing_decision": agent_result.get("routing_decision", "unknown")
            })
            
            # Return response
            response_data = {
                "response": agent_result.get("reply", ""),
                "reply": agent_result.get("reply", ""),
                "session_id": session_id,
                "products": agent_result.get("products", []),
                "workflow_steps": agent_result.get("workflow_steps", []),
                "success": True,
                "agent_type": agent_result.get("agent_type", "unknown"),
                "routing_decision": agent_result.get("routing_decision", "unknown")
            }
            return response_data
        else:
            return {
                "response": agent_result.get("reply", "I'm sorry, I encountered an error."),
                "reply": agent_result.get("reply", "I'm sorry, I encountered an error."),
                "session_id": session_id,
                "products": [],
                "workflow_steps": agent_result.get("workflow_steps", []),
                "success": False,
                "agent_type": agent_result.get("agent_type", "unknown"),
                "routing_decision": agent_result.get("routing_decision", "error")
            }
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        return {
            "response": "I'm sorry, I encountered an error processing your request.",
            "reply": "I'm sorry, I encountered an error processing your request.",
            "session_id": session_id,
            "products": [],
            "workflow_steps": ["error"],
            "success": False,
            "agent_type": "unknown",
            "routing_decision": "error"
        }

@app.get("/scrape-prices")
async def scrape_prices_get(category_url: str):
    """Scrape product prices based on a category_url (GET for test compatibility)"""
    result = get_product_prices_from_search(category_url)
    print(f"[DEBUG] /scrape-prices GET called with category_url={category_url}, result={result}")
    return {"products": result.get("products", [])}

@app.post("/scrape-prices")
async def scrape_prices(request: Request):
    data = await request.json()
    scrape_request = ScrapePricesRequest(**data)
    result = get_product_prices_from_search(scrape_request.query)
    return {"products": result.get("products", [])}

@app.get("/chat-history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    return {
        "session_id": session_id,
        "history": chat_history.get(session_id, [])
    }

@app.delete("/chat-history/{session_id}")
async def clear_chat_history(session_id: str):
    """Clear chat history for a session"""
    if session_id in chat_history:
        del chat_history[session_id]
    return {"message": f"Chat history cleared for session {session_id}"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "agent_available": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)