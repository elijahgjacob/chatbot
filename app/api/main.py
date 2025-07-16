"""
FastAPI Chatbot with LangChain Agentic Workflow
"""
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional

from app.core.logging_config import setup_logging
from app.agents.sales_agent import process_sales_query
from app.tools.tools import get_product_prices_from_search

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Al Essa Kuwait Virtual Sales Assistant",
    description="An intelligent sales agent that helps customers find and purchase medical equipment, home appliances, and technology products from Al Essa Kuwait using advanced LangChain agentic workflows",
    version="2.0.0"
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

class ChatRequest(BaseModel):
    text: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str
    reply: str
    session_id: str
    products: List[Dict[str, Any]] = []
    workflow_steps: List[str] = []
    success: bool = True

class ScrapePricesRequest(BaseModel):
    query: str

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Al Essa Kuwait Virtual Sales Assistant API", 
        "status": "running",
        "version": "2.0.0",
        "features": [
            "Sales Agent with LangChain",
            "Al Essa Kuwait Product Search",
            "Price Comparison & Recommendations",
            "Customer Qualification & Upselling"
        ]
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint using Al Essa Kuwait Sales Agent"""
    query = request.text
    session_id = request.session_id
    logger.info(f"Received /chat request: {query} (session: {session_id})")
    
    try:
        # Process query with the new sales agent
        sales_result = process_sales_query(query, session_id)
        
        if sales_result.get("success"):
            # Store chat history
            if session_id not in chat_history:
                chat_history[session_id] = []
            chat_history[session_id].append({
                "user": query,
                "bot": sales_result["response"],
                "sales_stage": sales_result.get("sales_stage", "discovery"),
                "customer_profile": sales_result.get("customer_profile", {})
            })
            # Keep only last 10 messages
            if len(chat_history[session_id]) > 10:
                chat_history[session_id] = chat_history[session_id][-10:]
            
            return ChatResponse(
                response=sales_result["response"],
                reply=sales_result["response"],
                session_id=session_id,
                products=sales_result.get("products", []),
                workflow_steps=sales_result.get("recommended_actions", []),
                success=True
            )
        else:
            logger.warning("Sales agent failed, returning error response")
            return ChatResponse(
                response=sales_result.get("response", "I apologize for the technical issue. Let me connect you with a human sales representative."),
                reply=sales_result.get("response", "I apologize for the technical issue. Let me connect you with a human sales representative."),
                session_id=session_id,
                products=[],
                workflow_steps=["sales_agent_error"],
                success=False
            )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="I'm experiencing technical difficulties. Please contact our sales team directly at 1800080.")

@app.get("/scrape-prices")
async def scrape_prices_get(category_url: str):
    """Scrape product prices based on a category_url (GET for test compatibility)"""
    result = get_product_prices_from_search(category_url)
    print(f"[DEBUG] /scrape-prices GET called with category_url={category_url}, result={result}")
    return {"products": result.get("products", [])}

@app.post("/scrape-prices")
async def scrape_prices(request: ScrapePricesRequest):
    """Scrape product prices based on a query"""
    result = get_product_prices_from_search(request.query)
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