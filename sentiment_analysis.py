"""
Sentiment Analysis Script using NLTK Library
This script analyzes the sentiment of text using NLTK's VADER sentiment analyzer.
"""

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Download VADER lexicon if not already downloaded
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    print("Downloading VADER lexicon...")
    nltk.download('vader_lexicon')

def analyze_sentiment(text):
    """
    Analyze the sentiment of the given text.
    
    Args:
        text (str): The text to analyze
        
    Returns:
        dict: A dictionary containing sentiment scores
    """
    sia = SentimentIntensityAnalyzer()
    scores = sia.polarity_scores(text)
    return scores

def get_sentiment_label(scores):
    """
    Determine sentiment label based on compound score.
    
    Args:
        scores (dict): Sentiment scores from VADER
        
    Returns:
        str: Sentiment label (Positive, Negative, or Neutral)
    """
    compound = scores['compound']
    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    else:
        return "Neutral"

def main():
    """Main function to demonstrate sentiment analysis."""
    
    # Sample texts for demonstration
    sample_texts = [
        "I absolutely love this product! It's amazing and works perfectly.",
        "This is terrible. I hate it and want my money back.",
        "The weather is okay today. Nothing special.",
        "What a wonderful experience! I'm so happy and excited!",
        "I'm very disappointed with the service. It was a complete waste of time."
    ]
    
    print("=" * 60)
    print("SENTIMENT ANALYSIS RESULTS")
    print("=" * 60)
    
    for i, text in enumerate(sample_texts, 1):
        scores = analyze_sentiment(text)
        label = get_sentiment_label(scores)
        
        print(f"\nText {i}: {text}")
        print(f"  Scores: {scores}")
        print(f"  Sentiment: {label}")
    
    # Interactive mode
    print("\n" + "=" * 60)
    print("INTERACTIVE MODE - Enter text to analyze (or 'quit' to exit)")
    print("=" * 60)
    
    while True:
        user_input = input("\nEnter text: ").strip()
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        
        if not user_input:
            print("Please enter some text.")
            continue
        
        scores = analyze_sentiment(user_input)
        label = get_sentiment_label(scores)
        
        print(f"\nText: {user_input}")
        print(f"  Positive: {scores['pos']:.3f}")
        print(f"  Negative: {scores['neg']:.3f}")
        print(f"  Neutral:  {scores['neu']:.3f}")
        print(f"  Compound: {scores['compound']:.3f}")
        print(f"  Sentiment: {label}")

if __name__ == "__main__":
    main()