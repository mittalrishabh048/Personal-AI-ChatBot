import datetime
import json
import os
import logging
from groq import Groq

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
        return "Engine Error: AI client is offline."
        
    try:
        bot_name = bot_config.get("bot_name", "Smart AI Chatbot")
        
        # Crafting the system instruction to give your model personality boundaries
        system_instruction = (
            f"You are a helpful, polite, and intelligent assistant named {bot_name}. "
            "Provide helpful answers to the user's input. Keep your responses concise, "
            "clear, and direct (under 3 sentences unless asked for details)."
        )
        
        # Call the Groq chat completions endpoint
        chat_completion = ai_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_instruction,
                },
                {
                    "role": "user",
                    "content": user_query,
                }
            ],
            model=MODEL_NAME,
            temperature=0.7,  # Controls creativity balance
        )
        
        logging.info("Groq API Inference executed successfully.")
        return chat_completion.choices[0].message.content.strip()
        
    except Exception as e:
        logging.error(f"Groq API communication exception: {e}")
        return "I am having trouble connecting to my external brain right now. Please try again shortly!"