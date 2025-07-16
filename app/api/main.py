"""
FastAPI Chatbot with Agentic Workflow
"""
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime

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

# Enhanced in-memory chat history storage with conversation context
chat_history: Dict[str, Dict[str, Any]] = {}

class ChatRequest(BaseModel):
    text: str
    session_id: Optional[str] = "default"
    user_name: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    reply: str
    session_id: str
    products: List[Dict[str, Any]] = []
    workflow_steps: List[str] = []
    success: bool = True
    conversation_context: Optional[Dict[str, Any]] = None

class ScrapePricesRequest(BaseModel):
    query: str

def _initialize_session(session_id: str, user_name: str = None):
    """Initialize a new chat session with enhanced context."""
    if session_id not in chat_history:
        chat_history[session_id] = {
            "messages": [],
            "user_preferences": {},
            "mentioned_products": [],
            "conversation_stage": "greeting",
            "session_start": datetime.now().isoformat(),
            "user_name": user_name,
            "total_interactions": 0
        }

def _update_session_context(session_id: str, user_message: str, bot_response: str, products: List[Dict]):
    """Update session context with rich conversation information."""
    session = chat_history[session_id]
    
    # Add to message history
    session["messages"].append({
        "timestamp": datetime.now().isoformat(),
        "user": user_message,
        "bot": bot_response,
        "products_shown": len(products)
    })
    
    # Update conversation metrics
    session["total_interactions"] += 1
    
    # Keep only last 20 messages for memory efficiency
    if len(session["messages"]) > 20:
        session["messages"] = session["messages"][-20:]
    
    # Track products mentioned in this session
    for product in products[:3]:  # Track top 3 products
        if product not in session["mentioned_products"]:
            session["mentioned_products"].append(product)
    
    # Keep only last 10 mentioned products
    if len(session["mentioned_products"]) > 10:
        session["mentioned_products"] = session["mentioned_products"][-10:]

def _get_conversation_context(session_id: str) -> str:
    """Generate conversation context for the LLM."""
    if session_id not in chat_history:
        return "This is the start of a new conversation."
    
    session = chat_history[session_id]
    context_parts = []
    
    # Add user info if available
    if session.get("user_name"):
        context_parts.append(f"Customer name: {session['user_name']}")
    
    # Add interaction count
    context_parts.append(f"This is interaction #{session['total_interactions'] + 1} in this session")
    
    # Add recent conversation history (last 3 exchanges)
    recent_messages = session["messages"][-3:] if session["messages"] else []
    if recent_messages:
        context_parts.append("Recent conversation:")
        for msg in recent_messages:
            context_parts.append(f"User: {msg['user']}")
            context_parts.append(f"Assistant: {msg['bot'][:100]}...")  # Truncate for brevity
    
    # Add mentioned products context
    if session["mentioned_products"]:
        context_parts.append(f"Previously discussed products: {[p.get('name', 'Unknown') for p in session['mentioned_products'][:3]]}")
    
    return "\n".join(context_parts)

@app.get("/")
async def root():
    """Health check endpoint with friendly message"""
    return {
        "message": "🌟 Welcome to Al Essa Kuwait Virtual Assistant! I'm here to help you find amazing medical equipment and appliances!", 
        "status": "running",
        "version": "1.0.0"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint using agentic workflow with enhanced conversation handling"""
    query = request.text
    session_id = request.session_id
    user_name = request.user_name
    
    logger.info(f"Received /chat request: {query} (session: {session_id}, user: {user_name})")
    
    try:
        # Initialize session if needed
        _initialize_session(session_id, user_name)
        
        # Update user name if provided
        if user_name and session_id in chat_history:
            chat_history[session_id]["user_name"] = user_name
        
        # Get conversation context
        conversation_context = _get_conversation_context(session_id)
        
        # Process query with agent
        agent_result = chatbot_agent.process_query(query, session_id)
        
        if agent_result.get("success"):
            response_text = agent_result["response"]
            products = agent_result.get("products", [])
            
            # Personalize response if we have user name
            if user_name and not any(greeting in query.lower() for greeting in ["hello", "hi", "hey"]):
                # Don't add name to greetings since agent handles that
                if not response_text.startswith(user_name):
                    # Add name naturally to some responses
                    if "!" in response_text[:50]:  # If response starts enthusiastically
                        response_text = response_text.replace("!", f", {user_name}!", 1)
            
            # Update session context
            _update_session_context(session_id, query, response_text, products)
            
            return ChatResponse(
                response=response_text,
                reply=response_text,
                session_id=session_id,
                products=products,
                workflow_steps=agent_result.get("workflow_steps", []),
                success=True,
                conversation_context={
                    "total_interactions": chat_history[session_id]["total_interactions"],
                    "mentioned_products_count": len(chat_history[session_id]["mentioned_products"]),
                    "conversation_stage": chat_history[session_id].get("conversation_stage", "ongoing")
                }
            )
        else:
            logger.warning("Agent failed, returning error response")
            error_response = agent_result.get("response", "I'm so sorry, but I'm having a technical moment. Could you please try again? I'm here to help!")
            
            return ChatResponse(
                response=error_response,
                reply=error_response,
                session_id=session_id,
                products=[],
                workflow_steps=["agent_error"],
                success=False
            )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        friendly_error = "Oh no! I encountered a little hiccup. Don't worry though - I'm still here to help! Could you try asking me again? 😊"
        raise HTTPException(status_code=500, detail=friendly_error)

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
    """Get enhanced chat history for a session"""
    if session_id not in chat_history:
        return {
            "session_id": session_id,
            "history": [],
            "message": "No conversation history found for this session yet! Start chatting to build our conversation history. 😊"
        }
    
    session = chat_history[session_id]
    return {
        "session_id": session_id,
        "history": session["messages"],
        "context": {
            "user_name": session.get("user_name"),
            "total_interactions": session["total_interactions"],
            "session_start": session["session_start"],
            "mentioned_products": session["mentioned_products"],
            "conversation_stage": session.get("conversation_stage", "ongoing")
        },
        "summary": f"We've had {session['total_interactions']} great interactions and discussed {len(session['mentioned_products'])} products together!"
    }

@app.delete("/chat-history/{session_id}")
async def clear_chat_history(session_id: str):
    """Clear chat history for a session with friendly confirmation"""
    if session_id in chat_history:
        user_name = chat_history[session_id].get("user_name", "friend")
        del chat_history[session_id]
        return {
            "message": f"All set! I've cleared our conversation history, {user_name}. Ready for a fresh start whenever you are! 😊"
        }
    else:
        return {
            "message": f"No worries! There wasn't any history to clear for session {session_id}. Feel free to start a new conversation anytime!"
        }

@app.get("/health")
async def health_check():
    """Health check endpoint with personality"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "agent_available": True,
        "message": "I'm running perfectly and ready to help you find amazing products! 🌟",
        "active_sessions": len(chat_history)
    }

@app.get("/sessions")
async def get_active_sessions():
    """Get information about active sessions"""
    sessions_info = []
    for session_id, session_data in chat_history.items():
        sessions_info.append({
            "session_id": session_id,
            "user_name": session_data.get("user_name", "Anonymous"),
            "total_interactions": session_data["total_interactions"],
            "session_start": session_data["session_start"],
            "last_activity": session_data["messages"][-1]["timestamp"] if session_data["messages"] else session_data["session_start"]
        })
    
    return {
        "active_sessions": len(chat_history),
        "sessions": sessions_info,
        "message": f"Currently managing {len(chat_history)} active conversation{'s' if len(chat_history) != 1 else ''}!"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)