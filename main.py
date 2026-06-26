import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

import chatengine
import database

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# FIXES WARNING: This modern lifestyle function replaces the old @app.on_event system cleanly
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Executes foundational system boots before listening to web traffic."""
    logging.info("FastAPI service initialization triggered via lifespan handles.")
    chatengine.download_nlp_dependencies()
    chatengine.load_system_data()
    database.init_db()
    logging.info("All underlying engine layers loaded. Server online.")
    yield  # This separates startup actions from shutdown actions
    logging.info("Shutting down server environments cleanly.")

# Initialize FastAPI passing the new lifespan manager
app = FastAPI(
    title="Smart AI Chatbot API",
    description="Production-ready stateless endpoint for personal AI chatbot processing",
    version="3.0.0",
    lifespan=lifespan
)

class ChatRequest(BaseModel):
    name: str
    message: str

class ChatResponse(BaseModel):
    greeting: str
    bot_name: str
    reply: str

@app.post("/chat", response_model=ChatResponse)
def handle_chat_session(payload: ChatRequest):
    try:
        input_name = payload.name.strip() if payload.name.strip() else "User"
        user_message = payload.message.strip()

        if not user_message:
            raise HTTPException(status_code=400, detail="Message block cannot be empty.")

        existing_user = database.get_user_profile(input_name)
        is_returning = existing_user is not None
        
        database.save_or_update_user(input_name)
        database.log_message(sender="User", message_text=user_message)

        greeting_string = chatengine.get_time_greeting(input_name, is_returning=is_returning)
        bot_identity_name = chatengine.get_config_item("bot_name")
        bot_reply = chatengine.get_response(user_message)

        database.log_message(sender="Bot", message_text=bot_reply)

        return ChatResponse(
            greeting=greeting_string,
            bot_name=bot_identity_name,
            reply=bot_reply
        )

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        logging.error(f"Internal endpoint runtime exception encountered: {e}")
        raise HTTPException(status_code=500, detail="Internal server error processing query matrix.")

if __name__ == "__main__":
    # FIXES BREAKING ERROR: Swapped "main.py:app" to "main:app" (drop the file extension suffix)
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)