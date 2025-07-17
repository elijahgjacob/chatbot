#!/usr/bin/env python3
"""
Simple CLI for interacting with the Al Essa Kuwait Virtual Sales Representative chatbot.
"""

import sys
import json
import requests
from typing import Dict, Any
import os
import argparse

def chat_with_bot(message: str, session_id: str = "cli_session") -> Dict[str, Any]:
    """
    Send a message to the chatbot via the API.
    """
    try:
        response = requests.post(
            "http://localhost:8000/chat",
            json={"text": message, "session_id": session_id},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to connect to chatbot: {e}"}

def get_session_history(session_id: str = "cli_session") -> Dict[str, Any]:
    """
    Get session history from the API.
    """
    try:
        response = requests.get(
            f"http://localhost:8000/chat-history/{session_id}",
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"history": []}
    except:
        return {"history": []}

def evaluate_response(user_query: str, response_data: Dict[str, Any]) -> None:
    """Evaluate a chatbot response using the LLM evaluator."""
    try:
        # Import evaluator (local import to avoid dependency issues)
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from app.core.response_evaluator import response_evaluator
        
        # Extract response components
        bot_response = response_data.get("reply", "")
        products = response_data.get("products", [])
        agent_type = response_data.get("agent_type", "unknown")
        workflow_steps = response_data.get("workflow_steps", [])
        
        # Evaluate the response
        evaluation = response_evaluator.evaluate_response(
            user_query=user_query,
            bot_response=bot_response,
            products=products,
            agent_type=agent_type,
            workflow_steps=workflow_steps
        )
        
        # Format and display evaluation
        eval_summary = response_evaluator.format_evaluation_summary(evaluation)
        print(eval_summary)
        
    except Exception as e:
        print(f"\n❌ Response evaluation failed: {e}")

def main():
    """
    Main CLI loop for chatting with the bot.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Al Essa Kuwait Chatbot CLI")
    parser.add_argument("--evaluate", action="store_true", 
                       help="Enable response evaluation for each message")
    args = parser.parse_args()
    
    print("🤖 Welcome to Al Essa Kuwait Virtual Sales Representative!")
    print("💬 I can help you with medical equipment, home appliances, and general health questions.")
    print("📝 Type 'quit' or 'exit' to end the conversation.")
    print("📋 Type 'history' to see conversation history.")
    print("🔄 Type 'new' to start a new session.")
    if args.evaluate:
        print("📊 Response evaluation is ENABLED")
    print("=" * 60)
    
    session_id = "cli_session"
    
    # Show recent history if available
    history_data = get_session_history(session_id)
    if history_data.get("history"):
        print("\n📚 Recent conversation history:")
        for msg in history_data["history"][-3:]:  # Show last 3 messages
            role_emoji = "👤" if msg.get("role") == "user" else "🤖"
            print(f"{role_emoji} {msg.get('content', '')[:100]}...")
        print()
    
    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            # Check for special commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n🤖 Bot: Goodbye! Have a great day!")
                break
            
            if user_input.lower() == 'history':
                history_data = get_session_history(session_id)
                if history_data.get("history"):
                    print("\n📚 Full conversation history:")
                    for i, msg in enumerate(history_data["history"], 1):
                        role_emoji = "👤" if msg.get("role") == "user" else "🤖"
                        agent_type = msg.get("agent_type", "")
                        agent_emoji = "🩺" if agent_type == "doctor" else "💼" if agent_type == "sales" else ""
                        print(f"{i}. {role_emoji} {msg.get('content', '')}")
                        if agent_emoji:
                            print(f"   {agent_emoji} {agent_type.title()} Agent")
                else:
                    print("\n📚 No conversation history found.")
                continue
            
            if user_input.lower() == 'new':
                session_id = f"cli_session_{len(session_id)}"
                print(f"\n🔄 Started new session: {session_id}")
                continue
            
            if not user_input:
                continue
            
            # Send to bot
            print("🤖 Bot: Thinking...")
            result = chat_with_bot(user_input, session_id)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
                continue
            
            # Display bot response
            reply = result.get("reply", "I'm sorry, I didn't understand that.")
            print(f"🤖 Bot: {reply}")
            
            # Display agent type and routing decision
            agent_type = result.get("agent_type", "unknown")
            routing_decision = result.get("routing_decision", "unknown")
            if agent_type != "unknown":
                agent_emoji = "🩺" if agent_type == "doctor" else "💼"
                print(f"{agent_emoji} Agent: {agent_type.title()} Agent")
                print(f"🎯 Routing: {routing_decision}")
            
            # Display products if any
            products = result.get("products", [])
            if products:
                print("\n🛍️ Products found:")
                for i, product in enumerate(products[:3], 1):  # Show max 3 products
                    name = product.get("name", "Unknown Product")
                    price = product.get("price", "Price not available")
                    print(f"   {i}. {name} - {price}")
                if len(products) > 3:
                    print(f"   ... and {len(products) - 3} more products")
            
            # Display workflow steps
            workflow = result.get("workflow_steps", [])
            if workflow:
                print(f"\n🔧 Workflow: {' → '.join(workflow)}")
            
            # Evaluate response if enabled
            if args.evaluate:
                print("\n" + "="*50)
                print("🔍 EVALUATING RESPONSE...")
                evaluate_response(user_input, result)
                print("="*50)
            
        except KeyboardInterrupt:
            print("\n\n🤖 Bot: Goodbye! Have a great day!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()