"""
Utility functions for the chatbot.
"""

import re
from typing import List


def preprocess_text(text: str) -> str:
    """
    Preprocess text by removing extra whitespace and normalizing.
    
    Args:
        text: Input text to preprocess
        
    Returns:
        Preprocessed text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    # Convert to lowercase
    text = text.lower()
    return text


def get_sentiment(text: str) -> str:
    """
    Simple sentiment analysis based on keyword matching.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Sentiment classification: 'positive', 'negative', or 'neutral'
    """
    positive_words = [
        'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
        'awesome', 'love', 'like', 'happy', 'joy', 'pleased', 'satisfied',
        'perfect', 'best', 'brilliant', 'outstanding', 'superb'
    ]
    
    negative_words = [
        'bad', 'terrible', 'awful', 'horrible', 'disappointing', 'sad',
        'angry', 'frustrated', 'upset', 'worried', 'scared', 'afraid',
        'hate', 'dislike', 'worst', 'terrible', 'dreadful'
    ]
    
    text_lower = text.lower()
    words = text_lower.split()
    
    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)
    
    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    else:
        return "neutral"


def extract_keywords(text: str) -> List[str]:
    """
    Extract potential keywords from text.
    
    Args:
        text: Input text
        
    Returns:
        List of keywords
    """
    # Simple keyword extraction - words longer than 3 characters
    words = re.findall(r'\b\w{4,}\b', text.lower())
    return list(set(words))  # Remove duplicates 