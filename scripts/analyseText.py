# pip install googletrans==4.0.0-rc1
from googletrans import Translator
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Creating objects to analyse and translate
sia = SentimentIntensityAnalyzer()
translator = Translator()

# Getting input
text = str(input())

# Language detection
language = translator.detect(text).lang
if language != 'en':
    # Translating detected language to english
    translated_text = translator.translate(text, src=language, dest='en').text
else:
    translated_text = text
    
# Sentiment analysis
scores = sia.polarity_scores(translated_text)
sentiment = 'Positive' if scores['compound'] > 0 else 'Negative' if scores['compound'] < 0 else 'Neutral'

# Printing results -- only for testing
print(f"\nTranslated text: {translated_text}\nSentiment: {sentiment}, Scores: {scores}\n")