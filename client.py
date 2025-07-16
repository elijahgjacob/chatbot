import requests
import json

API_URL = "http://localhost:8000/chat"

def display_welcome():
    """Display a welcoming message to demonstrate the conversational nature."""
    print("🌟 Welcome to Al Essa Kuwait Virtual Assistant! 🌟")
    print("=" * 50)
    print("I'm your friendly AI assistant, ready to have a great conversation!")
    print("I can help you with:")
    print("• Finding medical equipment and appliances")
    print("• Answering general questions")
    print("• Having a friendly chat")
    print("• Providing personalized recommendations")
    print()
    print("💡 Try asking me things like:")
    print("• 'Hello, my name is Sarah'")
    print("• 'I'm looking for wheelchairs'")
    print("• 'Tell me a joke'")
    print("• 'How are you doing today?'")
    print("• 'What's the best medical equipment you have?'")
    print()
    print("Type 'exit' or 'quit' to end our conversation.")
    print("=" * 50)
    print()

def send_message(message, session_id="default", user_name=None):
    """Send a message to the chatbot and return the response."""
    try:
        payload = {"text": message, "session_id": session_id}
        if user_name:
            payload["user_name"] = user_name
            
        response = requests.post(API_URL, json=payload, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "reply": f"Sorry, I encountered an error (HTTP {response.status_code}). Let me try to help you anyway! 😊",
                "success": False
            }
    except requests.exceptions.RequestException as e:
        return {
            "reply": "I'm having trouble connecting right now. Please make sure the server is running! 🔧",
            "success": False
        }

def extract_user_name(message):
    """Simple extraction of user name from common patterns."""
    message_lower = message.lower()
    
    # Look for common name introduction patterns
    patterns = [
        "my name is ",
        "i'm ",
        "i am ",
        "call me ",
        "this is "
    ]
    
    for pattern in patterns:
        if pattern in message_lower:
            start_idx = message_lower.find(pattern) + len(pattern)
            remaining = message[start_idx:].strip()
            # Get first word as name (simple approach)
            name_parts = remaining.split()
            if name_parts and len(name_parts[0]) > 1:
                return name_parts[0].title()
    
    return None

def display_response(response_data):
    """Display the chatbot response in a friendly format."""
    reply = response_data.get("reply", "I'm not sure how to respond to that.")
    products = response_data.get("products", [])
    
    print("🤖 Assistant:", reply)
    
    # Show products if any were found
    if products and len(products) > 0:
        print("\n📋 Product Details:")
        for i, product in enumerate(products[:3], 1):
            name = product.get('name', f'Product {i}')
            price = product.get('price', 'Price available upon request')
            link = product.get('link', product.get('url', ''))
            
            print(f"   {i}. {name} - {price}")
            if link:
                print(f"      🔗 {link}")
        
        if len(products) > 3:
            print(f"   ... and {len(products) - 3} more options available!")
    
    print()

def main():
    """Main conversation loop with enhanced user experience."""
    display_welcome()
    
    session_id = "demo_session"
    user_name = None
    conversation_count = 0
    
    while True:
        try:
            # Get user input
            if conversation_count == 0:
                user_input = input("👤 You: ")
            else:
                user_input = input("👤 You: ")
            
            # Check for exit conditions
            if user_input.lower().strip() in ("exit", "quit", "bye", "goodbye"):
                print("🤖 Assistant: It's been wonderful chatting with you! Have an amazing day! 🌟")
                break
            
            if not user_input.strip():
                print("🤖 Assistant: I'm here whenever you're ready to chat! 😊")
                continue
            
            # Try to extract user name if not already known
            if not user_name:
                extracted_name = extract_user_name(user_input)
                if extracted_name:
                    user_name = extracted_name
                    print(f"🌟 Nice to meet you, {user_name}!")
            
            # Send message to chatbot
            response_data = send_message(user_input, session_id, user_name)
            
            # Display response
            display_response(response_data)
            
            conversation_count += 1
            
            # Show conversation context occasionally
            if conversation_count % 5 == 0:
                context = response_data.get("conversation_context", {})
                if context:
                    interactions = context.get("total_interactions", conversation_count)
                    print(f"💭 We've had {interactions} great exchanges in this conversation!")
                    print()
            
        except KeyboardInterrupt:
            print("\n\n🤖 Assistant: Thanks for the chat! Come back anytime! 👋")
            break
        except Exception as e:
            print(f"😅 Oops! Something unexpected happened: {e}")
            print("Let's keep chatting though!")
            print()

if __name__ == "__main__":
    main() 