import sys
from app.agents.agent import chatbot_agent

def main():
    print("Welcome to the Al Essa Med Chatbot CLI! Type 'exit' to quit.")
    session_id = "cli-session"
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        result = chatbot_agent.process_query(user_input, session_id=session_id)
        print(f"Bot: {result.get('response')}")
        if result.get('products'):
            print("Products:")
            for p in result['products'][:3]:
                print(f"- {p.get('name')} ({p.get('price')}): {p.get('url', p.get('link', ''))}")

if __name__ == "__main__":
    main()