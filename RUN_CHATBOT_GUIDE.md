# 🚀 How to Run the Al Essa Kuwait Chatbot

## 📋 Prerequisites

Before running the chatbot, make sure you have:
- Python 3.9+ installed
- OpenAI API key
- Internet connection (for product scraping)

## 🛠️ Setup Steps

### 1. Install Dependencies

The chatbot requires several Python packages. Install them using:

```bash
pip3 install -r requirements.txt
```

If you get permission errors, try:
```bash
pip3 install -r requirements.txt --user
```

Or create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

The chatbot needs an OpenAI API key. Create a `.env` file in the project root:

```bash
# Create .env file
touch .env
```

Add your OpenAI API key to the `.env` file:
```
OPENAI_API_KEY=your_actual_openai_api_key_here
```

**⚠️ Important:** Replace `your_actual_openai_api_key_here` with your real OpenAI API key.

### 3. Verify Configuration

Test that the configuration is working:
```bash
python3 -c "from app.core.config import OPENAI_API_KEY; print('API Key configured:', bool(OPENAI_API_KEY))"
```

## 🚀 Running the Chatbot

### Option 1: Run the FastAPI Server (Recommended)

Start the full API server:
```bash
python3 -m uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

Or use the direct Python method:
```bash
python3 app/api/main.py
```

The server will start at: **http://localhost:8000**

### Option 2: Run the CLI Version

For a simple command-line interface:
```bash
python3 chatbot_cli.py
```

### Option 3: Run the Dashboard

To monitor system performance:
```bash
python3 dashboard.py
```

## 🌐 Using the Chatbot

### Web API Usage

Once the server is running, you can:

1. **Visit the docs:** http://localhost:8000/docs
2. **Health check:** http://localhost:8000/health
3. **Chat endpoint:** POST to http://localhost:8000/chat

Example API request:
```json
{
  "text": "I need a wheelchair for my elderly father",
  "session_id": "user_123"
}
```

### CLI Usage

If using the CLI version:
1. Type your questions when prompted
2. Use special commands:
   - `history` - View conversation history
   - `new` - Start a new session
   - `quit` or `exit` - Exit the program

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. ImportError: No module named 'langchain_openai'
```bash
pip3 install langchain-openai==0.0.2
```

#### 2. OpenAI API Key Not Found
- Check that `.env` file exists in project root
- Verify the API key is correct
- Ensure no extra spaces in the `.env` file

#### 3. Permission Denied Errors
```bash
pip3 install --user -r requirements.txt
```

#### 4. Port Already in Use
Change the port number:
```bash
python3 -m uvicorn app.api.main:app --reload --port 8001
```

#### 5. Module Not Found Errors
Ensure you're running from the project root directory:
```bash
cd /workspace
python3 app/api/main.py
```

### System Requirements Check

Verify your system meets requirements:
```bash
python3 --version  # Should be 3.9+
pip3 --version     # Should be available
```

## 📊 Testing the Setup

### 1. Quick Function Test
```bash
python3 -c "
from app.agents.doctor_agent import doctor_agent
from app.agents.sales_agent import sales_agent
print('✅ Agents imported successfully')
print('Doctor agent type:', doctor_agent.agent_type)
print('Sales agent type:', sales_agent.agent_type)
"
```

### 2. API Health Check
With the server running, test:
```bash
curl http://localhost:8000/health
```

Should return:
```json
{"status": "healthy", "timestamp": "...", "version": "1.0.0"}
```

### 3. Basic Chat Test
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello", "session_id": "test"}'
```

## 🎯 Different Usage Modes

### 1. Development Mode
```bash
python3 -m uvicorn app.api.main:app --reload --log-level debug
```

### 2. Production Mode  
```bash
python3 -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. Background Mode
```bash
nohup python3 app/api/main.py > chatbot.log 2>&1 &
```

## 📱 Access Methods

Once running, you can access the chatbot via:

1. **Web Browser:** http://localhost:8000/docs (Interactive API docs)
2. **CLI:** `python3 chatbot_cli.py`
3. **API calls:** Use curl, Postman, or any HTTP client
4. **Dashboard:** `python3 dashboard.py`

## 🔑 API Key Setup

If you don't have an OpenAI API key:
1. Go to https://platform.openai.com/api-keys
2. Sign up/login to OpenAI
3. Create a new API key
4. Add billing information if required
5. Copy the key to your `.env` file

## ⚡ Quick Start Script

Save this as `start_chatbot.sh`:
```bash
#!/bin/bash
echo "🚀 Starting Al Essa Kuwait Chatbot..."
echo "📁 Current directory: $(pwd)"
echo "🐍 Python version: $(python3 --version)"

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create one with your OpenAI API key."
    exit 1
fi

# Install dependencies if needed
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt --quiet

# Start the server
echo "🌐 Starting server on http://localhost:8000"
python3 -m uvicorn app.api.main:app --reload
```

Make it executable:
```bash
chmod +x start_chatbot.sh
./start_chatbot.sh
```

## 🎉 Success!

If everything is working, you should see:
```
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Your chatbot is now ready to help customers with medical equipment and product recommendations! 🏥🛍️