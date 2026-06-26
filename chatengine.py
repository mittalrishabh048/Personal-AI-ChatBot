import datetime
import json
import os
import logging
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Third-party Machine Learning utilities
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESPONSES_PATH = os.path.join(BASE_DIR, "config", "responses.json")
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.json")

# Global Application States
responses = {}
bot_config = {}
stemmer = PorterStemmer()

# ML Component Placeholders
vectorizer = None
knowledge_matrix = None
response_mapping = []  # Index-aligned list matching rows in the matrix to answers
CONFIDENCE_THRESHOLD = 0.35  # Strictness boundary for mathematical matching

def download_nlp_dependencies():
    """Ensures necessary NLTK data bundles are downloaded on the host device."""
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        logging.info("Downloading missing NLTK tokenizer models...")
        nltk.download('punkt', quiet=True)
        nltk.download('punkt_tab', quiet=True)

    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        logging.info("Downloading missing NLTK stopword corpora...")
        nltk.download('stopwords', quiet=True)

def preprocess_tokenizer(text: str) -> list:
    """Custom tokenizer mapping used internally by the TfidfVectorizer."""
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    
    cleaned_stems = [
        stemmer.stem(token) 
        for token in tokens 
        if token.isalnum() and token not in stop_words
    ]
    return cleaned_stems

def load_system_data():
    """Reads configuration data and fits the TF-IDF Vector Space Matrix."""
    global responses, bot_config, vectorizer, knowledge_matrix, response_mapping
    try:
        with open(RESPONSES_PATH, "r", encoding="utf-8") as f:
            responses = json.load(f)
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            bot_config = json.load(f)
            
        # Extract raw keys (intents) and values (answers) from knowledge base
        intent_keys = list(responses.keys())
        response_mapping = list(responses.values())
        
        if not intent_keys:
            raise ValueError("Knowledge base responses.json cannot be empty.")

        # Initialize the vectorizer with our custom cleaning pipeline
        vectorizer = TfidfVectorizer(tokenizer=preprocess_tokenizer, token_pattern=None)
        
        # Fit the vectorizer and transform keys into numerical coordinate vectors
        knowledge_matrix = vectorizer.fit_transform(intent_keys)
        
        logging.info(f"Vector space initialized. Vector vocabulary size: {len(vectorizer.vocabulary_)}")
    except Exception as e:
        logging.error(f"Failed to compile the vector environment: {e}")
        raise

def get_config_item(key: str) -> str:
    return bot_config.get(key, "")

def get_time_greeting(name: str, is_returning: bool = False) -> str:
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
    """Calculates Cosine Similarity between user text vector and knowledge base."""
    global vectorizer, knowledge_matrix, response_mapping
    
    # Handle direct edge case where vectorizer failed or input is blank
    if vectorizer is None or not user_query.strip():
        return bot_config.get("fallback_message", "I cannot process that message.")

    # Convert the user's incoming query into the exact same vector space
    user_vector = vectorizer.transform([user_query])
    
    # Calculate similarity score against every row in our database matrix
    # returns an array of scores (e.g., [[0.12, 0.85, 0.0, 0.23]])
    similarity_scores = cosine_similarity(user_vector, knowledge_matrix)[0]
    
    # Identify the index of the highest score
    best_match_idx = similarity_scores.argmax()
    highest_score = similarity_scores[best_match_idx]
    
    # Architectural Logging for debugging vector distances
    logging.info(f"Query: '{user_query}' -> Top Match Score: {highest_score:.4f} at index {best_match_idx}")
    
    # Algorithmic Thresholding
    if highest_score >= CONFIDENCE_THRESHOLD:
        return response_mapping[best_match_idx]
        
    return bot_config.get("fallback_message", "I cannot process that message.")