import os
from pydantic import BaseModel

class AppConfig(BaseModel):
    # App Settings
    APP_NAME: str = "Smart AI Voice Agent"
    VERSION: str = "14.0.0"
    
    # Models & API Settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    STT_MODEL: str = os.getenv("STT_MODEL", "whisper-large-v3-turbo")
    
    # Directory & Storage Settings
    AUDIO_DIR: str = os.getenv("AUDIO_DIR", "static_audio")
    MAX_HISTORY_LIMIT: int = int(os.getenv("MAX_CHAT_HISTORY", "10"))

# Singleton instance for app-wide use
settings = AppConfig()