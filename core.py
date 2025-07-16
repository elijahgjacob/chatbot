"""
Core chatbot functionality with enhanced conversational capabilities.
"""

import re
import random
from typing import Dict, List, Optional
from .utils import preprocess_text, get_sentiment


class Chatbot:
    """Main chatbot class with enhanced conversation capabilities."""
    
    def __init__(self):
        """Initialize the chatbot with enriched response patterns."""
        self.responses = {
            "greetings": [
                "Hello! I'm so excited to meet you! 😊 How can I brighten your day?",
                "Hi there! Welcome! I'm thrilled you're here - what brings you my way today?",
                "Hey! What a pleasure to see you! I'm here and ready to help with whatever you need!",
                "Greetings! I hope you're having a wonderful day! How can I assist you?",
                "Hello friend! I'm so glad you stopped by! What can I help you discover today?",
                "Hi! It's great to connect with you! What's on your mind today?"
            ],
            "farewells": [
                "Goodbye! It's been absolutely wonderful chatting with you! Have an amazing day! 🌟",
                "See you later! I've really enjoyed our conversation - come back anytime!",
                "Take care! It was such a pleasure helping you today! Until next time! 😊",
                "Bye! Thanks for such a lovely chat - I'm always here when you need me!",
                "Farewell! You've made my day brighter! Hope to see you again soon!",
                "Goodbye for now! Remember, I'm always here if you need anything at all!"
            ],
            "thanks": [
                "You're so welcome! It absolutely makes my day to help! 😊",
                "It's completely my pleasure! I'm thrilled I could assist you!",
                "Aww, thank you for saying that! I love being helpful - anytime!",
                "You're very welcome! That's exactly what I'm here for!",
                "I'm so glad I could help! Your appreciation really means a lot to me!",
                "Anytime! Helping wonderful people like you is what I live for!"
            ],
            "unknown": [
                "That's really interesting! I'd love to learn more about what you're thinking. Could you tell me a bit more?",
                "Hmm, that's fascinating! I want to make sure I understand you perfectly - could you elaborate?",
                "I'm curious about that! Could you help me understand better by explaining it differently?",
                "That sounds intriguing! I'm still learning, so could you give me a bit more context?",
                "Ooh, that's a unique perspective! I'd love to dive deeper - what specifically interests you about that?",
                "I find that thought-provoking! Could you share more details so I can better assist you?"
            ],
            "weather": [
                "I wish I could check the weather for you! For the most accurate forecast, I'd recommend checking your favorite weather app. But I'm happy to chat about anything else! ☀️",
                "Weather forecasting isn't one of my superpowers yet, but I bet there's a great weather app that can help! Meanwhile, what else can I assist you with?",
                "I don't have access to real-time weather data, but I'd love to help with other questions! Is there something else I can help you explore? 🌤️",
                "While I can't predict the weather, I can definitely brighten your day in other ways! What else would you like to chat about?"
            ],
            "jokes": [
                "Here's one of my favorites: Why don't scientists trust atoms? Because they make up everything! 😄 Want to hear another?",
                "I love this one: What do you call a fake noodle? An impasta! 🍝 That always makes me smile!",
                "This one cracks me up: Why did the scarecrow win an award? He was outstanding in his field! 🌾 Pretty corny, right?",
                "Here's a fun one: I told my wife she was drawing her eyebrows too high. She looked surprised! 😮 Hope that gave you a chuckle!",
                "How about this: Why did the math book look so sad? Because it was full of problems! 📚 Want me to find more jokes for you?",
                "I've got one: What do you call a bear with no teeth? A gummy bear! 🐻 That one's pretty sweet, don't you think?"
            ],
            "compliments": [
                "Aww, thank you so much! That really brightens my day! You seem pretty amazing yourself! ✨",
                "You're so kind! I really appreciate that - it means a lot coming from someone as thoughtful as you!",
                "That's incredibly sweet of you to say! You've just made me smile so big! 😊",
                "Thank you! That's such a lovely compliment! You clearly have excellent taste! 😄"
            ],
            "emotions": {
                "sad": [
                    "I'm so sorry you're feeling down. 💙 I wish I could give you a big hug! Is there anything I can do to help brighten your day?",
                    "I hear that you're feeling sad, and I want you to know that your feelings are completely valid. I'm here to listen if you'd like to talk about it.",
                    "I'm really sorry you're going through a tough time. 🤗 Sometimes it helps to talk - I'm here if you need someone to listen."
                ],
                "happy": [
                    "That's absolutely wonderful! 🎉 I love hearing that you're feeling great! Your happiness is contagious!",
                    "I'm so thrilled to hear that! 😊 Happy people make my day so much brighter! What's making you feel so good?",
                    "That's fantastic news! 🌟 I'm practically glowing with joy hearing how happy you are!"
                ],
                "angry": [
                    "I can sense you might be feeling frustrated, and that's completely understandable. Would you like to talk about what's bothering you?",
                    "It sounds like something has really upset you. I'm here to listen without judgment if you'd like to share what's going on.",
                    "I hear your frustration, and I want to help if I can. Sometimes just talking through things can help - I'm all ears."
                ]
            }
        }
        
        # Enhanced pattern matching for different types of inputs
        self.patterns = {
            "greetings": r"\b(hi|hello|hey|greetings|good morning|good afternoon|good evening|howdy|what's up)\b",
            "farewells": r"\b(bye|goodbye|see you|farewell|take care|catch you later|talk to you later|ttyl)\b",
            "thanks": r"\b(thanks|thank you|thx|appreciate it|grateful|much appreciated)\b",
            "weather": r"\b(weather|temperature|forecast|rain|sunny|cloudy|snow|storm)\b",
            "jokes": r"\b(joke|funny|humor|laugh|make me laugh|tell me something funny)\b",
            "compliments": r"\b(you're great|you're awesome|you're amazing|you're helpful|love you|you're the best)\b",
            "questions_about_me": r"\b(who are you|what are you|tell me about yourself|your name)\b",
            "how_are_you": r"\b(how are you|how's it going|how do you feel|what's up with you)\b",
            "capabilities": r"\b(what can you do|help me|your abilities|features)\b"
        }
        
        # Emotion detection patterns
        self.emotion_patterns = {
            "sad": r"\b(sad|depressed|down|unhappy|crying|upset|hurt|disappointed)\b",
            "happy": r"\b(happy|excited|great|awesome|fantastic|wonderful|amazing|thrilled)\b",
            "angry": r"\b(angry|mad|furious|annoyed|irritated|frustrated|pissed)\b"
        }
        
        # Conversation state tracking
        self.conversation_state = {
            "user_name": None,
            "topics_discussed": [],
            "mood": "neutral",
            "interaction_count": 0
        }
    
    def get_response(self, user_input: str, user_name: str = None) -> str:
        """
        Generate an enhanced conversational response based on user input.
        
        Args:
            user_input: The user's message
            user_name: Optional user name for personalization
            
        Returns:
            A personalized, conversational response string
        """
        # Update conversation state
        self.conversation_state["interaction_count"] += 1
        if user_name:
            self.conversation_state["user_name"] = user_name
        
        # Preprocess the input
        processed_input = preprocess_text(user_input.lower())
        
        # Check for emotional content first
        emotion_response = self._check_emotions(processed_input)
        if emotion_response:
            return self._personalize_response(emotion_response, user_name)
        
        # Check for specific patterns
        for category, pattern in self.patterns.items():
            if re.search(pattern, processed_input):
                response = self._get_category_response(category, user_input)
                return self._personalize_response(response, user_name)
        
        # If no pattern matches, return engaging unknown response
        response = random.choice(self.responses["unknown"])
        return self._personalize_response(response, user_name)
    
    def _check_emotions(self, processed_input: str) -> Optional[str]:
        """Check for emotional content and respond appropriately."""
        for emotion, pattern in self.emotion_patterns.items():
            if re.search(pattern, processed_input):
                self.conversation_state["mood"] = emotion
                return random.choice(self.responses["emotions"][emotion])
        return None
    
    def _get_category_response(self, category: str, original_input: str) -> str:
        """Get a response for a specific category with context awareness."""
        base_responses = self.responses.get(category, self.responses["unknown"])
        
        # Add special handling for certain categories
        if category == "greetings" and self.conversation_state["interaction_count"] > 1:
            return "Welcome back! I'm so happy to see you again! 😊 What can I help you with this time?"
        
        elif category == "how_are_you":
            return "I'm doing wonderfully, thank you for asking! 😊 I love chatting with amazing people like you! How are YOU doing today?"
        
        elif category == "questions_about_me":
            return "I'm your friendly AI assistant! I love having conversations, helping people, and learning new things every day! I'm here to chat about whatever interests you! What would you like to know about me? 😊"
        
        elif category == "capabilities":
            return "I love to chat about all sorts of things! 🌟 I can have conversations, tell jokes, listen to how you're feeling, and help with questions. I'm always learning and growing! What would you like to explore together?"
        
        return random.choice(base_responses)
    
    def _personalize_response(self, response: str, user_name: str = None) -> str:
        """Add personalization to responses when possible."""
        if user_name and not response.startswith(user_name):
            # Add name naturally to responses
            if "!" in response and not any(word in response.lower() for word in ["hello", "hi", "hey"]):
                # Add name after first exclamation for enthusiasm
                response = response.replace("!", f", {user_name}!", 1)
            elif response.startswith(("That's", "I'm", "You're")):
                # Add name at the end for these types of responses
                response = response.rstrip('.!') + f", {user_name}!"
        
        return response
    
    def get_sentiment_response(self, user_input: str, user_name: str = None) -> str:
        """
        Get a response based on the sentiment of the user input with enhanced empathy.
        
        Args:
            user_input: The user's message
            user_name: Optional user name for personalization
            
        Returns:
            A sentiment-aware, personalized response
        """
        sentiment = get_sentiment(user_input)
        
        responses = {
            "positive": [
                "That sounds absolutely wonderful! I'm so happy to hear such positive energy from you! ✨",
                "I love your enthusiasm! It's contagious and it's making me smile too! 😊",
                "That's fantastic! Your positivity is really brightening my day!",
                "I'm thrilled to hear that! You seem like such an upbeat person!"
            ],
            "negative": [
                "I'm really sorry to hear that you're going through this. 💙 I'm here to listen if you need someone to talk to.",
                "That sounds really challenging. I wish I could help make things better for you. Would you like to talk about it?",
                "I can hear that something is bothering you, and I want you to know that your feelings are completely valid. I'm here for you.",
                "I'm so sorry you're dealing with that. Sometimes it helps just to know someone is listening - I'm here."
            ]
        }
        
        if sentiment in responses:
            response = random.choice(responses[sentiment])
        else:
            response = self.get_response(user_input, user_name)
        
        return self._personalize_response(response, user_name)
    
    def get_conversation_context(self) -> Dict:
        """Get the current conversation context."""
        return self.conversation_state.copy()
    
    def reset_conversation(self):
        """Reset the conversation state for a fresh start."""
        self.conversation_state = {
            "user_name": None,
            "topics_discussed": [],
            "mood": "neutral",
            "interaction_count": 0
        } 