import datetime
import json
import os
import logging
from groq import Groq

import database

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.json")

# Global configuration states
bot_config = {}
ai_client = None
MODEL_NAME = "llama-3.3-70b-versatile"  # High-performance free-tier model

def download_nlp_dependencies():
    """Placeholder to maintain backward compatibility with main.py lifecycle."""
    pass

def load_system_data():
    """Reads system configurations and initializes the Groq Client."""
    global bot_config, ai_client
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            bot_config = json.load(f)
            
        # Fetch the API key safely from the system environment variables
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is missing! Please set it in your terminal.")
            
        # Initialize the official Groq Client
        ai_client = Groq(api_key=api_key)
        logging.info(f"Groq AI Client successfully initialized using model: {MODEL_NAME}")
        
    except Exception as e:
        logging.error(f"Failed to initialize the Groq engine layer: {e}")
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
    """Sends user text to Groq API embedded with a System Prompt context."""
    global ai_client
    
    if ai_client is None:
        return get_local_fallback_response(user_query)
        
    try:
        bot_name = bot_config.get("bot_name", "Smart AI Chatbot")
        
        # 1. Define the persistent structural persona rule
        system_instruction = (
            f"You are a helpful, polite, and intelligent assistant named {bot_name}. "
            "Provide helpful answers to the user's input. Keep your responses concise, "
            "clear, and direct (under 3 sentences unless asked for details)."
        )
        
        # 2. Extract recent conversation arrays directly from our SQLite records
        # Pulls the last 6 lines of conversation to form the context memory window
        chat_memory_window = database.get_recent_chat_history(limit=6)
        
        # 3. Construct the full sequential payload array
        # Start with the structural blueprint
        messages_payload = [
            {"role": "system", "content": system_instruction}
        ]
        
        # Extend the payload with our sequential history list from the DB
        messages_payload.extend(chat_memory_window)
        
        # Finally, append the active incoming message turn
        messages_payload.append({"role": "user", "content": user_query})

        # 4. Fire the complete stateful payload block over the network interface
        chat_completion = ai_client.chat.completions.create(
            messages=messages_payload,
            model=MODEL_NAME,
            temperature=0.7,  # Controls creativity balance
        )
        
        logging.info("Groq API Inference executed successfully.")
        return chat_completion.choices[0].message.content.strip()
        
    except Exception as e:
        logging.error(f"Groq API communication exception: {e}")
        return get_local_fallback_response(user_query)

def get_local_fallback_response(user_query: str) -> str:
    """
    A robust, local backup generator that handles communication gracefully 
    when external cloud APIs are unreachable.
    """
    bot_name = bot_config.get("bot_name", "Smart AI Chatbot")
    
    # Analyze the input locally for basic survival keywords
    query_clean = user_query.lower()
    if "help" in query_clean or "support" in query_clean:
        return f"I am {bot_name}. My cloud connection is briefly offline, but you can check documentation or try again in a moment!"
    if "hello" in query_clean or "hi" in query_clean:
        return f"Hello there! I am operating in local safe-mode right now while my external processors refresh."
        
    # Standard polite fallback message
    return f"My advanced cloud engine is currently adjusting its network circuits. I am safely online, but please ask that complex question again in a minute!"