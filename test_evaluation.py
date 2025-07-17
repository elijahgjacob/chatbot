#!/usr/bin/env python3
"""
Test script to demonstrate the LLM-based response evaluation system.
"""

import sys
import os
import requests
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_evaluation_system():
    """Test the evaluation system with various queries."""
    
    print("🧪 Testing Response Evaluation System")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "name": "Good Wheelchair Query",
            "query": "I want to buy a wheelchair",
            "description": "Should return relevant wheelchair products"
        },
        {
            "name": "Medical Knee Pain Query", 
            "query": "I have knee pain and need medical equipment",
            "description": "Should route to doctor agent with relevant medical products"
        },
        {
            "name": "Problematic Query (from user report)",
            "query": "manual wheelchair",
            "description": "Previously returned breast pumps - should be flagged"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"🔍 Query: '{test_case['query']}'")
        print(f"📝 Expected: {test_case['description']}")
        print("-" * 30)
        
        try:
            # Send request to chatbot API with evaluation enabled
            response = requests.post(
                "http://localhost:8000/chat",
                json={
                    "text": test_case["query"],
                    "session_id": f"test_eval_{i}",
                    "evaluate_response": True
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Display basic response info
                print(f"🤖 Agent: {result.get('agent_type', 'unknown')}")
                print(f"🛍️ Products found: {len(result.get('products', []))}")
                
                # Show first few products
                products = result.get('products', [])
                if products:
                    print("📦 Top products:")
                    for j, product in enumerate(products[:3], 1):
                        name = product.get('name', 'Unknown')
                        price = product.get('price', 'N/A')
                        print(f"   {j}. {name} - {price} KWD")
                
                # Display evaluation if available
                evaluation = result.get('evaluation')
                if evaluation:
                    if 'error' in evaluation:
                        print(f"❌ Evaluation error: {evaluation['error']}")
                    else:
                        print("\n📊 EVALUATION RESULTS:")
                        print(f"   Overall Score: {evaluation.get('overall_score', 0)}%")
                        print(f"   Relevance: {evaluation.get('relevance', 0)}%")
                        print(f"   Product Relevance: {evaluation.get('product_relevance', 0)}%")
                        
                        issues = evaluation.get('critical_issues', [])
                        if issues:
                            print(f"   ⚠️ Issues: {', '.join(issues[:2])}")
                        
                        summary = evaluation.get('summary', '')
                        if summary:
                            print(f"   💬 Summary: {summary}")
                else:
                    print("📊 No evaluation data (evaluation may be disabled)")
                    
            else:
                print(f"❌ Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Evaluation testing complete!")

def demonstrate_cli_evaluation():
    """Show how to use CLI evaluation."""
    print("\n🖥️ CLI Evaluation Usage:")
    print("To enable evaluation in CLI, run:")
    print("   python3 chatbot_cli.py --evaluate")
    print("\nThis will show detailed evaluation after each response:")
    print("• Overall quality score (0-100%)")
    print("• Relevance, accuracy, completeness scores")
    print("• Critical issues identification")
    print("• Improvement suggestions")

def demonstrate_api_evaluation():
    """Show how to use API evaluation."""
    print("\n🌐 API Evaluation Usage:")
    print("Add 'evaluate_response': true to your API request:")
    
    example = {
        "text": "I need a wheelchair",
        "session_id": "user123",
        "evaluate_response": True
    }
    
    print("📝 Example request:")
    print(json.dumps(example, indent=2))
    
    print("\n📤 Response will include 'evaluation' field with:")
    print("• Detailed quality scores")
    print("• Critical issues identification")
    print("• Strengths and improvements")
    print("• Overall assessment summary")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        # Just show usage examples
        demonstrate_cli_evaluation()
        demonstrate_api_evaluation()
    else:
        # Run actual tests
        print("🚀 Starting evaluation system tests...")
        print("⚠️  Make sure the chatbot server is running on localhost:8000")
        
        # Check if server is running
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Server is running, proceeding with tests...")
                test_evaluation_system()
            else:
                print("❌ Server not responding correctly")
        except:
            print("❌ Server not running. Please start with:")
            print("   python3 -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000")
            print("\nOr run with --demo to see usage examples:")
            print("   python3 test_evaluation.py --demo")