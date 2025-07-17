#!/usr/bin/env python3
"""
Demo script showing the evaluation system catching inappropriate responses.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demonstrate_evaluation():
    """Demonstrate the evaluation system with mock data."""
    
    try:
        from app.core.response_evaluator import response_evaluator
        
        print("🎯 LLM Response Evaluation System Demo")
        print("=" * 50)
        
        # Example 1: Good response
        print("\n📋 Example 1: GOOD Response")
        print("User Query: 'I need a wheelchair'")
        print("Bot Response: Provided 5 relevant wheelchair products")
        
        evaluation1 = response_evaluator.evaluate_response(
            user_query="I need a wheelchair",
            bot_response="Here are some excellent wheelchair options for you...",
            products=[
                {"name": "Karma Wheelchair", "price": 220.0, "currency": "KWD"},
                {"name": "Drive Wheelchair", "price": 140.0, "currency": "KWD"}
            ],
            agent_type="sales",
            workflow_steps=["intelligent_routing", "sales_analysis", "product_search"]
        )
        
        print(response_evaluator.format_evaluation_summary(evaluation1))
        
        # Example 2: Bad response (the "hi" issue)
        print("\n" + "="*50)
        print("\n📋 Example 2: PROBLEMATIC Response")
        print("User Query: 'hi'")
        print("Bot Response: Recommended wheelchairs for a simple greeting")
        
        evaluation2 = response_evaluator.evaluate_response(
            user_query="hi",
            bot_response="Here are the top wheelchair options I found for your request...",
            products=[
                {"name": "Karma Wheelchair", "price": 220.0, "currency": "KWD"},
                {"name": "Drive Wheelchair", "price": 140.0, "currency": "KWD"}
            ],
            agent_type="sales",
            workflow_steps=["intelligent_routing", "sales_analysis", "product_search"]
        )
        
        print(response_evaluator.format_evaluation_summary(evaluation2))
        
        # Example 3: Irrelevant products (breast pump for wheelchair)
        print("\n" + "="*50)
        print("\n📋 Example 3: IRRELEVANT Products Issue")
        print("User Query: 'manual wheelchair'")
        print("Bot Response: Included breast pump in wheelchair results")
        
        evaluation3 = response_evaluator.evaluate_response(
            user_query="manual wheelchair",
            bot_response="Here are manual products I found...",
            products=[
                {"name": "Manual Wheelchair", "price": 45.0, "currency": "KWD"},
                {"name": "Manual Breast Pump", "price": 4.5, "currency": "KWD"},  # WRONG!
                {"name": "Reclining Wheelchair", "price": 69.0, "currency": "KWD"}
            ],
            agent_type="sales",
            workflow_steps=["intelligent_routing", "sales_analysis", "product_search"]
        )
        
        print(response_evaluator.format_evaluation_summary(evaluation3))
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("Make sure the server is running and OpenAI API key is configured.")

def show_usage():
    """Show how to use the evaluation system."""
    print("\n🛠️ HOW TO USE THE EVALUATION SYSTEM:")
    print("=" * 50)
    
    print("\n1️⃣ CLI Usage:")
    print("   python3 chatbot_cli.py --evaluate")
    print("   → Shows evaluation after each response")
    
    print("\n2️⃣ API Usage:")
    print("   Add 'evaluate_response': true to your request:")
    print("   {")
    print('     "text": "your query",')
    print('     "session_id": "user123",')
    print('     "evaluate_response": true')
    print("   }")
    
    print("\n3️⃣ What It Catches:")
    print("   ✅ Irrelevant product recommendations")
    print("   ✅ Wrong agent routing")
    print("   ✅ Inappropriate responses to simple queries")
    print("   ✅ Missing medical disclaimers")
    print("   ✅ Poor product-query matching")
    
    print("\n4️⃣ Evaluation Metrics:")
    print("   • Overall Score (0-100%)")
    print("   • Relevance (0-100%)")
    print("   • Accuracy (0-100%)")
    print("   • Completeness (0-100%)")
    print("   • Product Relevance (0-100%)")
    print("   • Agent Routing (0-100%)")

if __name__ == "__main__":
    print("🤖 Al Essa Kuwait Chatbot - Response Evaluation Demo")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--usage":
        show_usage()
    else:
        demonstrate_evaluation()
        show_usage()