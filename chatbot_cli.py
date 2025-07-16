#!/usr/bin/env python3
"""
Simple CLI for interacting with the Al Essa Kuwait Virtual Sales Representative chatbot.
"""

import sys
import json
import requests
from typing import Dict, Any

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

def main():
    """
    Main CLI loop for chatting with the bot.
    """
    print("🤖 Welcome to Al Essa Kuwait Virtual Sales Representative!")
    print("💬 I can help you with medical equipment, home appliances, and general health questions.")
    print("📝 Type 'quit' or 'exit' to end the conversation.")
    print("=" * 60)
    
    session_id = "cli_session"
    
    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n🤖 Bot: Thank you for chatting with me! Have a great day!")
                break
            
            if not user_input:
                continue
            
            # Send message to bot
            print("🤖 Bot: Thinking...")
            result = chat_with_bot(user_input, session_id)
            
            # Display response
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"🤖 Bot: {result.get('reply', result.get('response', 'No response'))}")
                
                # Show products if any
                products = result.get('products', [])
                if products:
                    print(f"\n📦 Found {len(products)} products:")
                    for i, product in enumerate(products[:3], 1):  # Show first 3
                        print(f"   {i}. {product.get('name', 'Unknown')} - {product.get('price', 'N/A')}")
                    if len(products) > 3:
                        print(f"   ... and {len(products) - 3} more")
                
                # Show workflow steps if any
                workflow_steps = result.get('workflow_steps', [])
                if workflow_steps:
                    print(f"\n🔧 Workflow: {' → '.join(workflow_steps)}")
                
        except KeyboardInterrupt:
            print("\n\n🤖 Bot: Goodbye! Thanks for chatting!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()