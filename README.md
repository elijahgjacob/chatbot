# 🏪 Al Essa Kuwait Virtual Sales Assistant

An intelligent sales agent powered by LangChain and FastAPI that helps customers find and purchase medical equipment, home appliances, and technology products from Al Essa Kuwait. The system features advanced agentic workflows with web scraping, product recommendations, price comparisons, and sales conversation management.

## 🎯 Features

### 🤖 Intelligent Sales Agent
- **LangChain-powered agentic workflows** for natural conversation flow
- **Customer qualification** and needs assessment
- **Sales stage tracking** (discovery, interest, consideration, evaluation, urgency)
- **Personalized product recommendations** based on customer needs and budget
- **Objection handling** and sales conversation management

### 🛍️ Product Search & Discovery
- **Real-time web scraping** from Al Essa Kuwait website (alessa.com.kw)
- **Advanced product filtering** by category, price, brand, and features
- **Multi-category support**: Medical equipment, home appliances, technology
- **Budget-aware recommendations** with price comparisons

### 💰 Sales Tools
- **Price comparison** across multiple products
- **Upselling and cross-selling** suggestions
- **Bundle recommendations** and value propositions
- **Customer profile tracking** for personalized service
- **Inventory availability** and delivery information

### 🌐 API & Integration
- **FastAPI REST API** with comprehensive documentation
- **Session management** for ongoing customer conversations
- **Real-time chat** with conversation history
- **Webhook-ready** for integration with CRM systems

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- OpenAI API key
- Internet connection for web scraping

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd al-essa-sales-agent
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

4. **Start the sales agent:**
   ```bash
   python3 start_sales_agent.py
   ```

The server will start on `http://localhost:8000` with interactive documentation at `/docs`.

## 📋 API Endpoints

### `/chat` (POST) - Main Sales Conversation
Engage with the Al Essa Kuwait sales agent for product discovery and purchasing assistance.

**Request:**
```json
{
  "text": "I need a wheelchair under 200 KWD for my elderly father",
  "session_id": "customer_123"
}
```

**Response:**
```json
{
  "response": "I'd be happy to help you find the perfect wheelchair for your father! Based on your 200 KWD budget, I have some excellent options...",
  "reply": "...",
  "session_id": "customer_123",
  "products": [
    {
      "name": "Al Essa Light Wheelchair",
      "price": 175.0,
      "url": "https://alessa.com.kw/products/wheelchair-light",
      "vendor": "Al Essa",
      "currency": "KWD"
    }
  ],
  "workflow_steps": [
    "Present specific product options and pricing",
    "Highlight key benefits and value proposition"
  ],
  "success": true
}
```

### `/scrape-prices` (POST) - Direct Product Search
Search for products and get pricing information directly.

**Request:**
```json
{
  "query": "Hitachi air conditioner"
}
```

### `GET /` - Health Check & API Info
Returns API status and feature information.

## 🎭 Sales Agent Personality

The Al Essa Kuwait Virtual Sales Assistant is designed to:

- **Act as a professional sales representative** with deep product knowledge
- **Build rapport** and understand customer needs through discovery questions
- **Present compelling value propositions** highlighting benefits over features
- **Create urgency** with limited-time offers and stock availability
- **Guide customers** through the complete sales process from interest to purchase
- **Provide exceptional customer service** with installation and support information

## 🛠️ Architecture

### Core Components

```
app/
├── agents/
│   ├── sales_agent.py          # Main sales agent with LangChain workflows
│   └── agent.py                # Legacy agent (for reference)
├── api/
│   └── main.py                 # FastAPI application and endpoints
├── core/
│   ├── scraping.py             # Al Essa Kuwait web scraping logic
│   ├── prompts.py              # Sales-focused system prompts
│   ├── llm.py                  # OpenAI LLM integration
│   └── config.py               # Configuration management
└── tools/
    ├── tools.py                # Basic product search tools
    └── sales_tools.py          # Specialized sales tools
```

### Sales Tools

1. **ProductSearchTool**: Search Al Essa Kuwait product catalog
2. **PriceComparisonTool**: Compare prices across multiple products
3. **ProductRecommendationTool**: Generate personalized recommendations
4. **CustomerQualificationTool**: Analyze customer buying signals
5. **UpsellingSuggestionTool**: Suggest complementary products and upgrades

## 🎯 Usage Examples

### Basic Product Search
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Show me your best air conditioners",
    "session_id": "demo_session"
  }'
```

### Budget-Conscious Shopping
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I need medical equipment under 150 KWD for home care",
    "session_id": "medical_customer"
  }'
```

### Product Comparison
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Compare Hitachi vs AUX refrigerators",
    "session_id": "comparison_shopper"
  }'
```

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `LOG_LEVEL`: Logging level (default: INFO)
- `MAX_TOKENS`: Maximum tokens for LLM responses (default: 1000)

### Customization
- **Sales prompts**: Modify `app/core/prompts.py` for different sales approaches
- **Product categories**: Update `app/tools/sales_tools.py` for new product types
- **Scraping logic**: Adapt `app/core/scraping.py` for different websites

## 🧪 Testing

Run the test suite to verify system functionality:

```bash
python3 test_sales_agent.py
```

This will test:
- Product scraper functionality
- Sales agent initialization
- API structure and routes

## 📊 Sales Analytics

The system tracks:
- **Customer profiles** with budget, preferences, and buying signals
- **Sales stages** for each conversation
- **Product interests** and recommendation effectiveness
- **Conversion metrics** and successful sales interactions

## 🔒 Security & Privacy

- **No PII storage** in logs or memory beyond session duration
- **Secure API key handling** with environment variable management
- **Rate limiting** on API endpoints (configurable)
- **Input validation** and sanitization for all user inputs

## 🚀 Deployment

### Production Setup
1. Use a production WSGI server like Gunicorn
2. Set up reverse proxy with Nginx
3. Configure SSL certificates
4. Set up monitoring and logging
5. Use a proper database for conversation history

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python3", "start_sales_agent.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For technical support or questions:
- 📧 Email: support@alessa.com.kw
- 📱 Phone: 1800080
- 🌐 Website: https://alessa.com.kw

## 🎉 Acknowledgments

- **LangChain** for the powerful agent framework
- **FastAPI** for the high-performance API framework
- **OpenAI** for the intelligent language model capabilities
- **Al Essa Kuwait** for the product data and business requirements

---

**Built with ❤️ for Al Essa Kuwait customers**
