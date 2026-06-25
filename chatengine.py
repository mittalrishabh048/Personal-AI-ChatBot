import datetime
import json
import os
import logging
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESPONSES_PATH = os.path.join(BASE_DIR, "config", "responses.json")
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.json")

responses = {}
bot_config = {}
stemmer = PorterStemmer()

# Cached dictionary of normalized/stemmed knowledge base keys
# Maps a stemmed string back to the original dictionary answer string
processed_knowledge_base = {}

def download_nlp_dependencies():
    """Ensures necessary NLTK data bundles are downloaded on the host device."""
    try:
        # 'punkt_tab' or 'punkt' provides the rules needed to split text into distinct word tokens
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        logging.info("Downloading missing NLTK tokenizer models...")
        nltk.download('punkt', quiet=True)
        nltk.download('punkt_tab', quiet=True)

    try:
        # 'stopwords' provides lists of meaningless filler words for multiple languages
        nltk.data.find('corpora/stopwords')
    except LookupError:
        logging.info("Downloading missing NLTK stopword corpora...")
        nltk.download('stopwords', quiet=True)

def preprocess_text(text: str) -> list:
    """Transforms a raw text string into a list of cleaned, stemmed tokens."""
    # 1. Lowercase and Tokenize
    tokens = word_tokenize(text.lower())
    
    # 2. Extract standard English stop words and punctuation strings
    stop_words = set(stopwords.words('english'))
    
    # 3. Filter filler tokens and reduce remaining vocabulary to standard word roots
    cleaned_stems = [
        stemmer.stem(token) 
        for token in tokens 
        if token.isalnum() and token not in stop_words
    ]
    
    return cleaned_stems

def load_system_data():
    """Reads and parses JSON configuration data into memory."""
    global responses, bot_config, processed_knowledge_base
    try:
        with open(RESPONSES_PATH, "r", encoding="utf-8") as f:
            responses = json.load(f)
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            bot_config = json.load(f)

        # Build the preprocessed matching cache
        processed_knowledge_base.clear()
        for key, answer in responses.items():
            # Process the trigger phrase key (e.g., "motivate me" -> ["motiv"])
            stemmed_tokens = preprocess_text(key)
            # Re-join tokens into a space-separated signature string
            signature = " ".join(stemmed_tokens)
            processed_knowledge_base[signature] = answer

        logging.info("Configuration and knowledge base successfully loaded from disk.")
    except Exception as e:
        logging.error(f"Initialization configuration loading failure: {e}")
        raise

def get_config_item(key: str) -> str:
    return bot_config.get(key, "")

def get_time_greeting(name: str, is_returning: bool = False) -> str:
    """Calculates the greeting, personalizing it if the profile already existed."""
    present_hour = datetime.datetime.now().hour
    base_greeting = "Good Night"
    if 5 <= present_hour <= 11:
        base_greeting = "Good Morning"
    elif 11 < present_hour <= 17:
        base_greeting = "Good Afternoon"
    elif 17 < present_hour <= 20:
        base_greeting = "Good Evening"

    if is_returning:
        return f"{base_greeting}, {name}! Welcome back buddy!"
    return f"{base_greeting}, {name}."

def get_response(user_query: str) -> str:
    """Evaluates text intents by processing tokens through the pipeline."""
    user_stems = preprocess_text(user_query)

    # If the user input is entirely stop words, handle it gracefully
    if not user_stems:
        return bot_config.get("fallback_message", "I cannot process that message.")
    
    # Check for direct matches based on normalized token overlap
    for signature, answer in processed_knowledge_base.items():
        # Split signature back to standalone stems
        sig_stems = signature.split()
        
        # If all core keyword stems of a response key are present inside the user's input tokens
        if sig_stems and all(stem in user_stems for stem in sig_stems):
            return answer
            
    return bot_config.get("fallback_message", "I cannot process that message.")