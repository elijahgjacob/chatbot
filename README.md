# FastAPI Chatbot with OpenAI & Web Scraping

This project is a chatbot backend using Python, FastAPI, OpenAI LLMs, and web scraping for product information.

## Features
- FastAPI backend with `/chat` and `/scrape-prices` endpoints
- OpenAI LLM (GPT-3.5/4) for intelligent responses
- Web scraping for real-time product and price information
- Chat history support with session management
- Comprehensive logging and error handling
- Full test suite with mocked HTTP calls

## Requirements
- Python 3.9+
- OpenAI API key

## Setup

1. **Clone the repo and install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   - Copy `.env.example` to `.env` and fill in your credentials:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ```

## Running the Server

```bash
uvicorn main:app --reload
```

The server will start on `http://localhost:8000`.

## API Endpoints

### `/chat` (POST)
Send a message to the chatbot:
```json
{
  "text": "What are your wheelchair options?",
  "session_id": "optional_session_id"
}
```

Response:
```json
{
  "reply": "AI-powered response with product information if relevant...",
  "products": [
    {
      "name": "Product Name",
      "price": "$299.99",
      "link": "https://example.com/product"
    }
  ]
}
```

### `/scrape-prices` (POST)
Directly scrape product information:
```json
{
  "query": "wheelchair"
}
```

### `/chat-history/{session_id}` (GET)
Get chat history for a session.

### `/chat-history/{session_id}` (DELETE)
Clear chat history for a session.

## Usage Examples

You can use [httpie](https://httpie.io/), [curl](https://curl.se/), or Postman:
```bash
# Chat with the bot
http POST http://localhost:8000/chat text="Tell me about crutches"

# Scrape product prices
http POST http://localhost:8000/scrape-prices query="wheelchair"
```

## Testing
Run the test suite:
```bash
pytest test_main.py -v
```

## Project Structure
```
├── main.py              # FastAPI app and endpoints
├── config.py            # Environment configuration
├── logging_config.py    # Logging setup
├── prompts.py           # System prompts
├── llm.py              # LLM integration
├── scraping.py         # Web scraping logic
├── test_main.py        # Test suite
├── requirements.txt    # Dependencies
└── .env.example       # Environment template
```

## License
MIT
