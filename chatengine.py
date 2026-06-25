import datetime
import json
import os
import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESPONSES_PATH = os.path.join(BASE_DIR, "config", "responses.json")
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.json")

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
    except Exception as e:
        logging.error(f"Initialization configuration loading failure: {e}")
        raise

def get_config_item(key: str) -> str:
    return bot_config.get(key, "")

def get_time_greeting(name: str, is_returning: bool = False) -> str:
    """Calculates the greeting, personalizing it if the profile already existed."""
    present_hour = datetime.datetime.now().hour
    base_greeting = ""
    
    if 5 <= present_hour <= 11:
        base_greeting = "Good Morning"
    elif 11 < present_hour <= 17:
        base_greeting = "Good Afternoon"
    elif 17 < present_hour <= 20:
        base_greeting = "Good Evening"
    else:
        base_greeting = "Good Night"

    if is_returning:
        return f"{base_greeting}, {name}! Welcome back buddy!"
    return f"{base_greeting}, {name}."

def get_response(user_query: str) -> str:
    normalized_query = user_query.lower()
    for key in responses:
        if key in normalized_query:
            return responses[key]
    return bot_config.get("fallback_message", "I cannot process that message.")