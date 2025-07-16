"""
Conversation Memory System - Manages chat history and context persistence.
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class ChatMessage:
    """Represents a single chat message."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: str
    agent_type: Optional[str] = None
    products: List[Dict] = None
    workflow_steps: List[str] = None
    
    def __post_init__(self):
        if self.products is None:
            self.products = []
        if self.workflow_steps is None:
            self.workflow_steps = []

@dataclass
class ConversationSession:
    """Represents a conversation session with memory."""
    session_id: str
    messages: List[ChatMessage]
    created_at: str
    last_updated: str
    agent_type: Optional[str] = None
    user_context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.user_context is None:
            self.user_context = {}

class ConversationMemory:
    """Manages conversation memory and persistence."""
    
    def __init__(self, storage_dir: str = "conversation_data"):
        """Initialize conversation memory."""
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.active_sessions: Dict[str, ConversationSession] = {}
        
    def get_session(self, session_id: str) -> ConversationSession:
        """Get or create a conversation session."""
        if session_id not in self.active_sessions:
            # Try to load from storage
            session = self._load_session(session_id)
            if session is None:
                # Create new session
                session = ConversationSession(
                    session_id=session_id,
                    messages=[],
                    created_at=datetime.now().isoformat(),
                    last_updated=datetime.now().isoformat()
                )
            self.active_sessions[session_id] = session
        return self.active_sessions[session_id]
    
    def add_message(self, session_id: str, role: str, content: str, 
                   agent_type: Optional[str] = None, products: List[Dict] = None,
                   workflow_steps: List[str] = None) -> None:
        """Add a message to the conversation."""
        session = self.get_session(session_id)
        
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            agent_type=agent_type,
            products=products or [],
            workflow_steps=workflow_steps or []
        )
        
        session.messages.append(message)
        session.last_updated = datetime.now().isoformat()
        
        # Update session context
        if agent_type:
            session.agent_type = agent_type
        
        # Save to storage
        self._save_session(session)
    
    def get_conversation_history(self, session_id: str, max_messages: int = 10) -> List[Dict[str, Any]]:
        """Get conversation history for context."""
        session = self.get_session(session_id)
        
        # Get recent messages
        recent_messages = session.messages[-max_messages:] if len(session.messages) > max_messages else session.messages
        
        # Format for LLM context
        history = []
        for msg in recent_messages:
            history.append({
                "role": msg.role,
                "content": msg.content,
                "agent_type": msg.agent_type,
                "timestamp": msg.timestamp
            })
        
        return history
    
    def get_user_context(self, session_id: str) -> Dict[str, Any]:
        """Get user context from the session."""
        session = self.get_session(session_id)
        return session.user_context
    
    def update_user_context(self, session_id: str, context_updates: Dict[str, Any]) -> None:
        """Update user context."""
        session = self.get_session(session_id)
        session.user_context.update(context_updates)
        session.last_updated = datetime.now().isoformat()
        self._save_session(session)
    
    def _save_session(self, session: ConversationSession) -> None:
        """Save session to storage."""
        file_path = self.storage_dir / f"{session.session_id}.json"
        
        # Convert to dict for JSON serialization
        session_dict = asdict(session)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(session_dict, f, indent=2, ensure_ascii=False)
    
    def _load_session(self, session_id: str) -> Optional[ConversationSession]:
        """Load session from storage."""
        file_path = self.storage_dir / f"{session_id}.json"
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                session_dict = json.load(f)
            
            # Reconstruct session
            messages = []
            for msg_dict in session_dict.get("messages", []):
                message = ChatMessage(**msg_dict)
                messages.append(message)
            
            session = ConversationSession(
                session_id=session_dict["session_id"],
                messages=messages,
                created_at=session_dict["created_at"],
                last_updated=session_dict["last_updated"],
                agent_type=session_dict.get("agent_type"),
                user_context=session_dict.get("user_context", {})
            )
            
            return session
        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None
    
    def clear_session(self, session_id: str) -> None:
        """Clear a session."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        
        # Remove from storage
        file_path = self.storage_dir / f"{session_id}.json"
        if file_path.exists():
            file_path.unlink()
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of the session."""
        session = self.get_session(session_id)
        
        return {
            "session_id": session.session_id,
            "message_count": len(session.messages),
            "created_at": session.created_at,
            "last_updated": session.last_updated,
            "agent_type": session.agent_type,
            "user_context": session.user_context
        }

# Global conversation memory instance
conversation_memory = ConversationMemory()