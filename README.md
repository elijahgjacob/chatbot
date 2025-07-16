# Al Essa Kuwait Virtual Assistant

A sophisticated AI-powered chatbot for Al Essa Kuwait, specializing in medical equipment, home appliances, and technology products. Built with FastAPI, OpenAI LLMs, and intelligent agent routing.

## 🌟 Features

### 🤖 **Intelligent Agent System**
- **Sales Agent**: Expert product recommendations and customer service
- **Doctor Agent**: Medical advice and symptom-based product suggestions
- **Intelligent Router**: LLM-driven query routing between specialized agents
- **Conversation Memory**: Maintains context across chat sessions

### 🛍️ **Live Product Integration**
- **Real-time Scraping**: Live product data from [Al Essa Kuwait](https://www.alessaonline.com)
- **LLM-Driven Alternatives**: Intelligent product suggestions when exact matches aren't found
- **Price & Availability**: Real-time pricing in Kuwaiti Dinars (KWD)
- **Product Categories**: Medical equipment, home appliances, technology, engineering solutions

### 💬 **Advanced Conversation**
- **Context Awareness**: Remembers previous conversations and user preferences
- **Natural Language**: Human-like responses with sales expertise
- **Multi-language Support**: English and Arabic capabilities
- **Personalized Recommendations**: Tailored suggestions based on user needs

### 🏥 **Medical Knowledge**
- **Virtual Doctor**: Basic medical advice and symptom analysis
- **Product Recommendations**: Medical equipment suggestions based on symptoms
- **Safety Disclaimers**: Always recommends consulting healthcare professionals
- **Emergency Awareness**: Recognizes urgent medical situations

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- OpenAI API key

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/elijahgjacob/chatbot.git
   cd chatbot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Run the server:**
   ```bash
   uvicorn app.api.main:app --reload
   ```

The server will start on `http://localhost:8000`

## 📡 API Endpoints

### `/chat` (POST)
Main chat endpoint with intelligent agent routing:
```json
{
  "text": "I need a wheelchair for my grandmother",
  "session_id": "user_123"
}
```

Response:
```json
{
  "reply": "I'd be happy to help you find the perfect wheelchair for your grandmother! Let me search our collection...",
  "products": [
    {
      "name": "Drive Medical Lightweight Wheelchair",
      "price": 85.0,
      "url": "https://www.alessaonline.com/product-url",
      "currency": "KWD"
    }
  ],
  "workflow_steps": ["intelligent_routing", "sales_analysis", "product_search"],
  "success": true
}
```

### `/scrape-prices` (POST)
Direct product search endpoint:
```json
{
  "query": "ice pack"
}
```

### `/health` (GET)
Health check endpoint.

## 🎯 Usage Examples

### CLI Interface
```bash
python chatbot_cli.py
```

### API Usage
```bash
# Chat with the assistant
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "What medical equipment do you have for back pain?", "session_id": "user_123"}'

# Search for specific products
curl -X POST http://localhost:8000/scrape-prices \
  -H "Content-Type: application/json" \
  -d '{"query": "wheelchair"}'
```

## 🏗️ Architecture

### Agent System
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Query    │───▶│  Agent Router   │───▶│  Sales Agent    │
│                 │    │   (LLM-based)   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Doctor Agent   │
                       │                 │
                       └─────────────────┘
```

### Key Components
- **`app/agents/`**: Agent implementations and routing logic
- **`app/core/`**: Core functionality (LLM, scraping, memory)
- **`app/tools/`**: Tool implementations for product search
- **`app/api/`**: FastAPI endpoints and request handling

## 🧪 Testing

Run the comprehensive test suite:
```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/test_agents.py -v
pytest tests/test_scraping.py -v
pytest tests/test_main.py -v
```

## 🔧 Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini  # Default model
```

### Agent Configuration
- **Sales Agent**: Configured for Al Essa Kuwait product knowledge
- **Doctor Agent**: Medical advice with safety disclaimers
- **Router**: LLM-driven decision making for query routing

## 🌐 Integration with Al Essa Kuwait

This chatbot integrates with the [Al Essa Kuwait website](https://www.alessaonline.com) to provide:
- **Live Product Data**: Real-time scraping of product information
- **Accurate Pricing**: Current prices in Kuwaiti Dinars
- **Product Availability**: Up-to-date stock information
- **Direct Links**: Direct product URLs for easy access

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For support or questions about Al Essa Kuwait products, visit:
- **Website**: [https://www.alessaonline.com](https://www.alessaonline.com)
- **Email**: Contact through the Al Essa Kuwait website
- **Phone**: Available on the Al Essa Kuwait website

---

**Built with ❤️ for Al Essa Kuwait customers**
