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
from app.core.analytics import analytics_manager, QueryMetrics
from app.core.cache import cache_manager
import time

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
    """Main chat endpoint for the chatbot with analytics tracking."""
    start_time = time.time()
    
    try:
        data = await request.json()
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    chat_request = ChatRequest(**data)
    query = chat_request.text
    session_id = chat_request.session_id
    logger.info(f"Received /chat request: {query} (session: {session_id})")
    
    # Start analytics tracking
    analytics_manager.start_session(session_id)
    
    try:
        # Process query with agent
        agent_result = chatbot_agent.process_query(query, session_id)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Record analytics
        metrics = QueryMetrics(
            query=query,
            session_id=session_id,
            agent_type=agent_result.get("agent_type", "unknown"),
            response_time=response_time,
            products_found=len(agent_result.get("products", [])),
            cache_hit=agent_result.get("cached", False),
            success=agent_result.get("success", False),
            error_message=agent_result.get("error", None)
        )
        analytics_manager.record_query(metrics)
        
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
        response_time = time.time() - start_time
        logger.error(f"Error processing chat request: {e}")
        
        # Record error analytics
        metrics = QueryMetrics(
            query=query,
            session_id=session_id,
            agent_type="error",
            response_time=response_time,
            products_found=0,
            cache_hit=False,
            success=False,
            error_message=str(e)
        )
        analytics_manager.record_query(metrics)
        
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

@app.get("/analytics/health")
async def analytics_health():
    """Get system health analytics."""
    return analytics_manager.get_system_health()

@app.get("/analytics/user/{session_id}")
async def user_analytics(session_id: str):
    """Get analytics for a specific user session."""
    analytics = analytics_manager.get_user_analytics(session_id)
    if analytics:
        return analytics
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@app.get("/analytics/popular-queries")
async def popular_queries(limit: int = 10):
    """Get most popular queries."""
    return analytics_manager.get_popular_queries(limit)

@app.get("/analytics/trends")
async def performance_trends(hours: int = 24):
    """Get performance trends over time."""
    return analytics_manager.get_performance_trends(hours)

@app.get("/cache/stats")
async def cache_stats():
    """Get cache statistics."""
    return cache_manager.get_cache_stats()

@app.post("/cache/clear")
async def clear_cache():
    """Clear expired cache entries."""
    cache_manager.clear_expired_entries()
    return {"message": "Expired cache entries cleared"}

@app.post("/session/end/{session_id}")
async def end_session(session_id: str):
    """End a user session."""
    analytics_manager.end_session(session_id)
    return {"message": f"Session {session_id} ended"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)