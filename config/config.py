import os
from pydantic import BaseModel

class AppConfig(BaseModel):
    # App Settings
    APP_NAME: str = "Smart AI Voice Agent"
    VERSION: str = "15.0.0"

    # Legacy Chatbot Display Settings (Migrated from config.json)
    BOT_NAME: str = "Smart AI Chatbot"
    FALLBACK_MESSAGE: str = "Sorry, I am not able to tell you about this!"
    WELCOME_INSTRUCTION: str = "You can ask me basic questions or send a voice message."
    
    # Models & API Settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    STT_MODEL: str = os.getenv("STT_MODEL", "whisper-large-v3-turbo")
    
    # Storage & Retention Settings
    AUDIO_DIR: str = os.getenv("AUDIO_DIR", "static_audio")
    MAX_HISTORY_LIMIT: int = int(os.getenv("MAX_CHAT_HISTORY", "10"))
    
    # Single source of truth for audio retention (in seconds)
    # Default: 1800 seconds = 30 minutes
    AUDIO_RETENTION_SECONDS: int = int(os.getenv("AUDIO_RETENTION_SECONDS", "1800"))

settings = AppConfig()