import datetime
import json
import os
import logging

# Define paths relative to this file's directory to ensure cross-platform safety
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESPONSES_PATH = os.path.join(BASE_DIR, "config", "responses.json")
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.json")

# Placeholders for dynamically loaded external data
responses = {}
bot_config = {}

def load_system_data():
    """Reads and parses JSON configuration data into memory."""
    global responses, bot_config
    try:
        with open(RESPONSES_PATH, "r", encoding="utf-8") as f:
            responses = json.load(f)
            
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            bot_config = json.load(f)
            
        logging.info("Configuration and knowledge base successfully loaded from disk.")
    except FileNotFoundError as e:
        logging.error(f"Critical initialization file missing: {e}")
        # Graceful basic fallbacks to keep the app functional if configurations are missing
        responses = {"hello": "System running on emergency fallback state."}
        bot_config = {
            "bot_name": "AI Bot",
            "fallback_message": "I don't know that.",
            "welcome_instruction": "System settings missing. Chatbot online."
        }
    except json.JSONDecodeError as e:
        logging.error(f"Malformed configuration file discovered: {e}")
        raise

def get_config_item(key: str) -> str:
    """Safely retrieves a configuration value by its key."""
    return bot_config.get(key, "")

def get_time_greeting(name: str) -> str:
    """Calculates the appropriate greeting based on the current system hour."""
    present_hour = datetime.datetime.now().hour
    if 5 <= present_hour <= 11:
        return f"Good Morning, {name}"
    elif 11 < present_hour <= 17:
        return f"Good Afternoon, {name}"
    elif 17 < present_hour <= 20:
        return f"Good Evening, {name}"
    else:
        return f"Good Night, {name}"

def get_response(user_query: str) -> str:
    """Processes input and evaluates intent matching using the external knowledge base."""
    normalized_query = user_query.lower()
    
    for key in responses:
        if key in normalized_query:
            return responses[key]
            
    return bot_config.get("fallback_message", "I cannot process that message.")