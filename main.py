import os
import shutil
import logging
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

import database
from config import settings
from services.conversation_manager import ConversationManager
from services.stt_service import STTService
from services.tts_service import TTSService

# Configure logging framework
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Global Holders
conversation_manager: Optional[ConversationManager] = None
stt_service: Optional[STTService] = None
tts_service: Optional[TTSService] = None

# Ensure audio storage directory exists
os.makedirs(settings.AUDIO_DIR, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initializes database schema and core AI Agent pipeline services on startup.
    """
    global conversation_manager, stt_service, tts_service
    logging.info("Booting AI Voice Agent Services...")
    
    database.init_db()
    conversation_manager = ConversationManager()
    stt_service = STTService()
    tts_service = TTSService()
    
    logging.info("STT, TTS, and Conversation Services initialized successfully.")
    yield
    logging.info("Teardown sequence complete.")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Mount static audio route to serve generated TTS files
app.mount("/audio", StaticFiles(directory=settings.AUDIO_DIR), name="audio")

# CORS Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VoiceChatResponse(BaseModel):
    greeting: str
    bot_name: str
    reply: str
    transcription: str
    audio_url: str

def remove_file(path: str):
    """Background task worker to safely remove temporary inbound audio files."""
    try:
        if os.path.exists(path):
            os.remove(path)
            logging.info(f"[Cleanup] Removed temp file: {path}")
    except Exception as e:
        logging.error(f"[Cleanup Error] Could not delete {path}: {e}")

@app.post("/chat/voice", response_model=VoiceChatResponse)
async def handle_voice_chat(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    name: str = Form("User")
) -> VoiceChatResponse:
    """
    Handles end-to-end Voice Agent requests:
    Audio Input -> STT -> Agent Reasoner -> Tool Execution -> TTS Synthesis -> Audio Response.
    """
    if not stt_service or not conversation_manager or not tts_service:
        raise HTTPException(
            status_code=503, 
            detail="Voice services are temporarily unavailable. Please try again shortly."
        )

    # 1. Guard against empty or invalid file upload
    if not file.filename or file.size == 0:
        raise HTTPException(status_code=400, detail="Uploaded audio file is empty or missing.")

    temp_inbound_audio = f"temp_{os.urandom(4).hex()}_{file.filename}"
    file_saved_successfully = False

    try:
        # 2. Save incoming file safely
        with open(temp_inbound_audio, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_saved_successfully = True

        # 3. Handle STT Transcription
        try:
            raw_user_message = stt_service.transcribe_audio(temp_inbound_audio)
        except Exception as stt_err:
            logging.error(f"[STT Failure]: {stt_err}")
            raise HTTPException(
                status_code=502, 
                detail="Failed to transcribe audio payload. Ensure your microphone is working and try again."
            )

        # Clean up transcription output (strip whitespace and common trailing punctuation)
        user_message_clean = raw_user_message.strip().strip(".").strip(",").strip()

        # 4. Handle Silent Audio / Noise Artifacts / Empty Transcription
        if not user_message_clean:
            fallback_reply = "I couldn't hear anything in your recording. Please try speaking again."
            audio_filename = f"fallback_{os.urandom(4).hex()}.mp3"
            output_audio_path = os.path.join(settings.AUDIO_DIR, audio_filename)
            
            try:
                tts_service.generate_speech(text=fallback_reply, output_path=output_audio_path)
                audio_url = f"/audio/{audio_filename}"
            except Exception:
                audio_url = ""

            background_tasks.add_task(remove_file, temp_inbound_audio)
            
            return VoiceChatResponse(
                greeting=f"Hello, {name}!",
                bot_name="Agent",
                reply=fallback_reply,
                transcription="[No Speech Detected]",
                audio_url=audio_url
            )

        logging.info(f"[STT Output]: {raw_user_message}")

        # 5. Fetch History and Process LLM Agent Pipeline
        raw_history = database.get_recent_chat_history(limit=settings.MAX_HISTORY_LIMIT)
        formatted_history = [
            {"role": "user" if msg.get("sender") == "User" else "assistant", "content": msg.get("message_text")}
            for msg in raw_history
        ]

        database.save_or_update_user(name)
        database.log_message(sender="User", message_text=f"[Voice Input]: {raw_user_message}")

        try:
            bot_reply = conversation_manager.process_message(
                user_message=raw_user_message,
                history=formatted_history
            )
        except Exception as llm_err:
            logging.error(f"[LLM Failure]: {llm_err}")
            bot_reply = "I'm having trouble connecting to my reasoning engine right now. Please try again in a moment."

        database.log_message(sender="Bot", message_text=bot_reply)

        # 6. Handle TTS Synthesis
        audio_filename = f"response_{os.urandom(4).hex()}.mp3"
        output_audio_path = os.path.join(settings.AUDIO_DIR, audio_filename)

        try:
            tts_service.generate_speech(text=bot_reply, output_path=output_audio_path)
            audio_url = f"/audio/{audio_filename}"
        except Exception as tts_err:
            logging.error(f"[TTS Failure]: {tts_err}")
            # Fall back gracefully to returning text response if audio synthesis fails
            audio_url = ""

        # Schedule temporary inbound file deletion via background task worker
        background_tasks.add_task(remove_file, temp_inbound_audio)

        return VoiceChatResponse(
            greeting=f"Hello, {name}!",
            bot_name="Agent",
            reply=bot_reply,
            transcription=raw_user_message,
            audio_url=audio_url
        )

    except HTTPException as http_ex:
        if file_saved_successfully and os.path.exists(temp_inbound_audio):
            os.remove(temp_inbound_audio)
        raise http_ex

    except Exception as general_err:
        if file_saved_successfully and os.path.exists(temp_inbound_audio):
            os.remove(temp_inbound_audio)
        logging.error(f"[Pipeline Critical Error]: {general_err}")
        raise HTTPException(
            status_code=500, 
            detail="An unexpected internal error occurred while processing your voice request."
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)