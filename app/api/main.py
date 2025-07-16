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
    description="A conversational chatbot that helps users find medical equipment using agentic workflows",
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
    conversation_context: Optional[Dict[str, Any]] = None

@dataclass
class ScrapePricesRequest:
    query: str

@app.get("/")
async def root():
    """Health check endpoint with friendly message"""
    return {
        "message": "🌟 Welcome to Al Essa Kuwait Virtual Assistant! I'm here to help you find amazing medical equipment and appliances!", 
        "status": "running",
        "version": "1.0.0"
    }

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    chat_request = ChatRequest(**data)
    query = chat_request.text
    session_id = chat_request.session_id
    logger.info(f"Received /chat request: {query} (session: {session_id})")
    
    try:
        # Process query with agent
        agent_result = chatbot_agent.process_query(query, session_id)
        
        if agent_result.get("success"):
            response_text = agent_result["reply"]
            products = agent_result.get("products", [])
            
            return ChatResponse(
                response=response_text,
                reply=response_text,
                session_id=session_id,
                products=products,
                workflow_steps=agent_result.get("workflow_steps", []),
                success=True
            )
        else:
            return ChatResponse(
                response=agent_result.get("reply", "I'm sorry, I encountered an error."),
                reply=agent_result.get("reply", "I'm sorry, I encountered an error."),
                session_id=session_id,
                products=[],
                workflow_steps=agent_result.get("workflow_steps", ["error"]),
                success=False
            )
            
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        return ChatResponse(
            response=f"I'm sorry, I encountered an error: {str(e)}",
            reply=f"I'm sorry, I encountered an error: {str(e)}",
            session_id=session_id,
            products=[],
            workflow_steps=["error"],
            success=False
        )

@app.post("/scrape-prices")
async def scrape_prices(request: ScrapePricesRequest):
    """Direct product search endpoint for testing and external use."""
    try:
        result = get_product_prices_from_search(request.query)
        return {
            "success": True,
            "query": request.query,
            "products": result.get("products", []),
            "formatted_reply": result.get("formatted_reply", ""),
            "count": len(result.get("products", []))
        }
    except Exception as e:
        logger.error(f"Error scraping prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Al Essa Kuwait Virtual Assistant is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)