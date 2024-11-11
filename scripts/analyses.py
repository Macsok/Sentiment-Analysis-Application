# pip install googletrans==4.0.0-rc1
from googletrans import Translator
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer


def analyseText(text : str = '', translate : bool = True, skip_non_eng : bool = False):
    """Analyses sentiment of a provided text. Translates every provided
    data by default, to enhance performance you may set 'translate' to False.
    Returns 1 if language not found, returns 2 if language translation failed.
    Returns 0 for every text that wasn't english and was skipped."""
    # Default return
    if text == '': return ''
    # Creating objects to analyse and translate
    sia = SentimentIntensityAnalyzer()
    translator = Translator()

    # Language detection
    try:
        language = translator.detect(text).lang
    except: return 1

    # Skip non english texts
    if skip_non_eng and language != 'en': return 0

    # Skipping this part if not translating -> better performance
    if translate:
        if language != 'en':
            # Translating detected language to english
            try:
                text = translator.translate(text, src=language, dest='en').text
            except:
                return 2
        # Scores for translated text
        scores = sia.polarity_scores(text)
        return scores['pos'], scores['neg'], scores['neu'], scores['compound'], text
        
    # Sentiment analysis
    scores = sia.polarity_scores(text)
    sentiment = 'Positive' if scores['compound'] > 0 else 'Negative' if scores['compound'] < 0 else 'Neutral'

    # Printing results -- only for testing
    # return f"\nAnalysed text: {text}\nSentiment: {sentiment}, Scores: {scores}\n"
    return scores['pos'], scores['neg'], scores['neu'], scores['compound'], text


# print(analyseText(str(input('enter text: '))))


def get_sentiment(score: float) -> str:
    """
    Returns the sentiment based on the provided score.
    Possible outputs: 'positive', 'negative', or 'neutral'.
    """
    sentiment = 'positive' if score > 0 else 'negative' if score < 0 else 'neutral'
    return sentiment


def default_analysis(text: str = ''):
    """
    Analyzes the sentiment of a provided text. Translates any non-English 
    text by default; to enhance performance, you may set 'translate' to False.
    
    Returns:
        - 1 if language detection fails.
        - 2 if language translation fails.
        - 0 for text that was not in English and was skipped.
    
    Returns sentiment scores (positive, negative, neutral, compound),
    detected language, and (if applicable) translated text.
    """
    # Default return
    if text == '': return ''
    # Creating objects to analyse and translate
    sia = SentimentIntensityAnalyzer()
    translator = Translator()

    # Language detection
    try:
        language = translator.detect(text).lang
    except: return 1

    if language != 'en':
        # Translating detected language to english
        try:
            text = translator.translate(text, src=language, dest='en').text
        except:
            return 2
    # Scores for translated text
    scores = sia.polarity_scores(text)
    return scores['pos'], scores['neg'], scores['neu'], scores['compound'], language, text