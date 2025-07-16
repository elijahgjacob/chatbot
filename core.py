"""
Core chatbot functionality.
"""

import re
import random
from typing import Dict, List, Optional
from .utils import preprocess_text, get_sentiment


class Chatbot:
    """Main chatbot class with conversation capabilities."""
    
    def __init__(self):
        """Initialize the chatbot with response patterns."""
        self.responses = {
            "greetings": [
                "Hello! How can I help you today?",
                "Hi there! Nice to meet you!",
                "Hey! What's on your mind?",
                "Greetings! How are you doing?"
            ],
            "farewells": [
                "Goodbye! Have a great day!",
                "See you later!",
                "Take care!",
                "Bye! Come back soon!"
            ],
            "thanks": [
                "You're welcome!",
                "No problem at all!",
                "Glad I could help!",
                "Anytime!"
            ],
            "unknown": [
                "I'm not sure I understand. Could you rephrase that?",
                "That's interesting! Tell me more.",
                "I'm still learning. Could you explain that differently?",
                "I don't have a specific response for that yet."
            ],
            "weather": [
                "I can't check the weather yet, but I'd recommend checking a weather app!",
                "Weather forecasting isn't my specialty, but I'm happy to chat about other things!",
                "I don't have access to real-time weather data, but I can help with other questions!"
            ],
            "jokes": [
                "Why don't scientists trust atoms? Because they make up everything!",
                "What do you call a fake noodle? An impasta!",
                "Why did the scarecrow win an award? He was outstanding in his field!",
                "I told my wife she was drawing her eyebrows too high. She looked surprised!"
            ]
        }
        
        # Pattern matching for different types of inputs
        self.patterns = {
            "greetings": r"\b(hi|hello|hey|greetings|good morning|good afternoon|good evening)\b",
            "farewells": r"\b(bye|goodbye|see you|farewell|take care)\b",
            "thanks": r"\b(thanks|thank you|thx|appreciate it)\b",
            "weather": r"\b(weather|temperature|forecast|rain|sunny)\b",
            "jokes": r"\b(joke|funny|humor|laugh)\b"
        }
    
    def get_response(self, user_input: str) -> str:
        """
        Generate a response based on user input.
        
        Args:
            user_input: The user's message
            
        Returns:
            A response string
        """
        # Preprocess the input
        processed_input = preprocess_text(user_input.lower())
        
        # Check for patterns and return appropriate response
        for category, pattern in self.patterns.items():
            if re.search(pattern, processed_input):
                return random.choice(self.responses[category])
        
        # If no pattern matches, return unknown response
        return random.choice(self.responses["unknown"])
    
    def get_sentiment_response(self, user_input: str) -> str:
        """
        Get a response based on the sentiment of the user input.
        
        Args:
            user_input: The user's message
            
        Returns:
            A sentiment-aware response
        """
        sentiment = get_sentiment(user_input)
        
        if sentiment == "positive":
            return "That sounds great! I'm glad to hear that!"
        elif sentiment == "negative":
            return "I'm sorry to hear that. Is there anything I can do to help?"
        else:
            return self.get_response(user_input) 