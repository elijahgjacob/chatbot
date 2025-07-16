#!/usr/bin/env python3
"""
Example Client for Al Essa Kuwait Sales Agent API
Demonstrates how to interact with the sales agent for different customer scenarios.
"""
import requests
import json
import time
from typing import Dict, Any

class AlEssaSalesClient:
    """Client for interacting with Al Essa Kuwait Sales Agent API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session_id = f"demo_session_{int(time.time())}"
    
    def chat(self, message: str) -> Dict[str, Any]:
        """Send a message to the sales agent"""
        url = f"{self.base_url}/chat"
        payload = {
            "text": message,
            "session_id": self.session_id
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {
                "error": f"Request failed: {e}",
                "success": False
            }
    
    def get_api_info(self) -> Dict[str, Any]:
        """Get API information and health status"""
        try:
            response = requests.get(f"{self.base_url}/")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {
                "error": f"Request failed: {e}",
                "success": False
            }
    
    def search_products(self, query: str) -> Dict[str, Any]:
        """Search for products directly"""
        url = f"{self.base_url}/scrape-prices"
        payload = {"query": query}
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {
                "error": f"Request failed: {e}",
                "success": False
            }

def print_response(response: Dict[str, Any], query: str):
    """Pretty print the sales agent response"""
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"{'='*60}")
    
    if not response.get('success', True):
        print(f"❌ Error: {response.get('error', 'Unknown error')}")
        return
    
    # Main response
    print(f"🤖 Sales Agent Response:")
    print(f"{response.get('response', response.get('reply', 'No response'))}")
    
    # Products found
    products = response.get('products', [])
    if products:
        print(f"\n🛍️ Products Found ({len(products)}):")
        for i, product in enumerate(products[:3], 1):  # Show first 3
            print(f"{i}. {product.get('name', 'Unknown')} - {product.get('price', 'N/A')} KWD")
            if product.get('url'):
                print(f"   🔗 {product['url']}")
    
    # Workflow steps
    steps = response.get('workflow_steps', [])
    if steps:
        print(f"\n📋 Recommended Actions:")
        for step in steps:
            print(f"• {step}")
    
    print(f"\n📊 Session ID: {response.get('session_id', 'Unknown')}")

def demo_scenarios():
    """Demonstrate different customer scenarios"""
    client = AlEssaSalesClient()
    
    # Check API status
    print("🏪 Al Essa Kuwait Sales Agent - Demo Client")
    print("=" * 60)
    
    api_info = client.get_api_info()
    if api_info.get('error'):
        print(f"❌ Cannot connect to API: {api_info['error']}")
        print("   Make sure the sales agent server is running:")
        print("   python3 start_sales_agent.py")
        return
    
    print(f"✅ Connected to: {api_info.get('message', 'Al Essa Kuwait API')}")
    print(f"📍 Version: {api_info.get('version', 'Unknown')}")
    
    # Demo scenarios
    scenarios = [
        {
            "title": "🏥 Medical Equipment Customer",
            "queries": [
                "Hello, I need a wheelchair for my elderly mother",
                "What wheelchairs do you have under 200 KWD?",
                "Can you tell me about the features of the Al Essa Light Wheelchair?"
            ]
        },
        {
            "title": "🏠 Home Appliance Shopper",
            "queries": [
                "I'm looking for a new refrigerator for my family",
                "What's the difference between Hitachi and AUX refrigerators?",
                "Do you have any special offers on air conditioners?"
            ]
        },
        {
            "title": "💰 Budget-Conscious Customer",
            "queries": [
                "I need home appliances but have a limited budget of 300 KWD",
                "What's the best value air conditioner you have?",
                "Can you help me compare prices?"
            ]
        },
        {
            "title": "🚀 Urgent Purchase",
            "queries": [
                "I need a washing machine urgently, can you help?",
                "What's available for immediate delivery?",
                "I need this installed today if possible"
            ]
        }
    ]
    
    for scenario in scenarios:
        print(f"\n\n{scenario['title']}")
        print("=" * 60)
        
        # Create new session for each scenario
        client.session_id = f"demo_{scenario['title'].replace(' ', '_').lower()}_{int(time.time())}"
        
        for query in scenario['queries']:
            response = client.chat(query)
            print_response(response, query)
            time.sleep(1)  # Brief pause between queries
    
    print(f"\n\n🎉 Demo completed!")
    print("=" * 60)
    print("The Al Essa Kuwait Sales Agent demonstrated:")
    print("• Product search and recommendations")
    print("• Price comparison and budget handling")
    print("• Customer qualification and needs assessment")
    print("• Urgency handling and solution presentation")
    print("• Professional sales conversation flow")

def interactive_mode():
    """Interactive mode for testing the sales agent"""
    client = AlEssaSalesClient()
    
    print("🏪 Al Essa Kuwait Sales Agent - Interactive Mode")
    print("=" * 60)
    print("Type your questions or 'quit' to exit")
    print("Examples:")
    print("• 'I need a wheelchair'")
    print("• 'Show me air conditioners under 300 KWD'")
    print("• 'Compare Hitachi vs AUX products'")
    print("=" * 60)
    
    while True:
        try:
            query = input("\n💬 You: ").strip()
            
            if query.lower() in ['quit', 'exit', 'bye']:
                print("👋 Thank you for using Al Essa Kuwait Sales Agent!")
                break
            
            if not query:
                continue
            
            print("🤖 Sales Agent is thinking...")
            response = client.chat(query)
            print_response(response, query)
            
        except KeyboardInterrupt:
            print("\n\n👋 Thank you for using Al Essa Kuwait Sales Agent!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        demo_scenarios()