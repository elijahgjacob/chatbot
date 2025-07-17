from langchain_openai import ChatOpenAI
from app.core.config import OPENAI_API_KEY
import logging

logger = logging.getLogger(__name__)

try:
    llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-4o-mini")
    print(f"LLM initialized: {llm}")
except Exception as e:
    print(f"Error initializing LLM: {e}")

    class _DummyResponse:
        """Minimal object to mimic OpenAI response shape."""
        def __init__(self, content: str):
            self.content = content

    class DummyLLM:
        """Fallback LLM that returns deterministic responses for testing."""
        def invoke(self, _messages):
            # Basic heuristic: if prompt asks for SEARCH/CONVERSATION, default to CONVERSATION
            # if asks for SALES/DOCTOR, default to SALES.
            last_content = ""
            try:
                last_content = _messages[-1].content.lower()
            except Exception:
                pass
            if "search" in last_content and "conversation" in last_content:
                return _DummyResponse("CONVERSATION")
            elif "sales" in last_content and "doctor" in last_content:
                return _DummyResponse("SALES")
            else:
                return _DummyResponse("CONVERSATION")

    llm = DummyLLM()

def get_llm_response(query, history=None):
    logger.info("Calling OpenAI LLM...")
    # Format history as a string
    history_str = ""
    if history:
        for turn in history:
            history_str += f"User: {turn['user']}\nAssistant: {turn['bot']}\n"
    prompt = f"{history_str}User: {query}\nAssistant:"
    response = llm.invoke(prompt)
    # Only return the message content
    if isinstance(response, dict) and 'content' in response:
        reply = response['content']
    elif hasattr(response, 'content'):
        reply = response.content
    else:
        reply = str(response)
    logger.info(f"LLM response: {reply}")
    return reply 