#!/usr/bin/env python3
"""
Al Essa Kuwait Sales Agent Startup Script
"""
import os
import sys
import uvicorn
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_environment():
    """Check if the environment is properly configured"""
    print("🔍 Checking Environment Configuration...")
    
    # Check for OpenAI API key
    if not os.environ.get('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY environment variable not set!")
        print("   Please set your OpenAI API key:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        return False
    else:
        print("✅ OpenAI API key found")
    
    # Check for required modules
    required_modules = [
        'fastapi', 'uvicorn', 'langchain', 'openai', 
        'beautifulsoup4', 'requests', 'pydantic'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} available")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ {module} not found")
    
    if missing_modules:
        print(f"\n❌ Missing modules: {', '.join(missing_modules)}")
        print("   Please install requirements:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def start_server(host="0.0.0.0", port=8000, reload=True):
    """Start the FastAPI server"""
    print("🚀 Starting Al Essa Kuwait Sales Agent...")
    print(f"🌐 Server will be available at: http://{host}:{port}")
    print("📖 API documentation: http://localhost:8000/docs")
    print("🔧 Interactive API: http://localhost:8000/redoc")
    print("\n💡 Ready to serve customers with intelligent sales assistance!")
    print("=" * 60)
    
    # Start the server
    uvicorn.run(
        "app.api.main:app",
        host=host,
        port=port,
        reload=reload,
        access_log=True
    )

if __name__ == "__main__":
    print("🏪 Al Essa Kuwait Virtual Sales Assistant")
    print("=" * 60)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        sys.exit(1)
    
    print("\n✅ Environment check passed!")
    
    # Start the server
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n\n👋 Sales Agent stopped. Thank you!")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)