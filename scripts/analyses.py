from googletrans import Translator
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')


def analyse_text(text: str = '', translate: bool = True, skip_non_eng: bool = False):
    """
    Analyzes the sentiment of a provided text. Translates any non-English 
    text by default.
    
    Returns:
        - 1 if language detection fails.
        - 2 if language translation fails.
        - 0 for text that was not in English and was skipped.
    
    Returns sentiment scores (positive, negative, neutral, compound),
    detected language, and (if applicable) translated text.
    """
    # Default return
    if text == '':
        return ''

    # Creating objects to analyze and translate
    sia = SentimentIntensityAnalyzer()
    translator = Translator()

    # Language detection
    try:
        language = translator.detect(text).lang
    except Exception:
        return 1

    # Skip non-English texts
    if skip_non_eng and language != 'en':
        return 0

    # Skipping this part if not translating -> better performance
    if translate:
        if language != 'en':
            # Translating detected language to English
            try:
                text = translator.translate(text, src=language, dest='en').text
            except Exception:
                return 2
        # Scores for translated text
        scores = sia.polarity_scores(text)
        return scores['pos'], scores['neg'], scores['neu'], scores['compound'], language, text

    # Sentiment analysis
    scores = sia.polarity_scores(text)
    
    # Return results
    return scores['pos'], scores['neg'], scores['neu'], scores['compound'], language, text


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
    text by default.
    
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