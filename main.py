#!/usr/bin/env python3
"""
Main entry point for the chatbot application.
"""

import os
from dotenv import load_dotenv
from chatbot.core import Chatbot

def main():
    """Main function to run the chatbot."""
    # Load environment variables
    load_dotenv()
    
    # Initialize the chatbot
    chatbot = Chatbot()
    
    print("🤖 Welcome to the Chatbot!")
    print("Type 'quit' or 'exit' to end the conversation.")
    print("-" * 50)
    
    # Main conversation loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("🤖 Goodbye! Have a great day!")
                break
            
            # Skip empty input
            if not user_input:
                continue
            
            # Get chatbot response
            response = chatbot.get_response(user_input)
            print(f"🤖 {response}")
            
        except KeyboardInterrupt:
            print("\n🤖 Goodbye! Have a great day!")
            break
        except Exception as e:
            print(f"🤖 Sorry, I encountered an error: {e}")

if __name__ == "__main__":
    main() 