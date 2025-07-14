from langchain_openai import ChatOpenAI
from app.core.config import OPENAI_API_KEY
import logging

logger = logging.getLogger(__name__)

try:
    llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")
    print(f"LLM initialized: {llm}")
except Exception as e:
    print(f"Error initializing LLM: {e}")
    llm = None

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