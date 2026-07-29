import logging
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import database
from services.conversation_manager import ConversationManager

# Configure application logging framework
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Global holder for our Agent Conversation Manager
conversation_manager: Optional[ConversationManager] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and teardown events.
    Initializes database and core Agent Orchestration Services.
    """
    global conversation_manager
    logging.info("System boot sequence initiated via lifespan context handlers.")
    
    # Initialize SQLite Database
    database.init_db()
    
    # Instantiate Agent Conversation Manager
    conversation_manager = ConversationManager()
    
    logging.info("All agent modular layers successfully registered. Server online.")
    yield
    logging.info("System teardown sequence completed cleanly.")



# Initialize the main FastAPI application instance
app = FastAPI(
    title="Smart AI Agent API",
    description="Production-grade agentic API with dynamic function calling tools",
    version="11.0.0",
    lifespan=lifespan
)

# Serve static files from the frontend folder
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def read_root():
    return FileResponse("frontend/index.html")

# Attach CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Data Contract Specifications ---
class ChatRequest(BaseModel):
    name: str
    message: str

class ChatResponse(BaseModel):
    greeting: str
    bot_name: str
    reply: str

# --- Endpoints ---

@app.get("/health")
def check_system_health() -> Dict[str, Any]:
    """
    Performs system diagnostics to verify database and LLM service viability.
    """
    health_status: Dict[str, Any] = {
        "status": "healthy",
        "database_connectivity": "disconnected",
        "agent_llm_service": "offline"
    }
    
    try:
        database.get_recent_chat_history(limit=1)
        health_status["database_connectivity"] = "connected"
    except Exception as db_err:
        health_status["status"] = "unhealthy"
        health_status["database_connectivity"] = f"error: {str(db_err)}"
        
    if conversation_manager and conversation_manager.llm_service:
        health_status["agent_llm_service"] = "online"
    else:
        health_status["status"] = "unhealthy"
        
    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)
        
    return health_status


@app.post("/chat", response_model=ChatResponse)
def handle_chat_session(payload: ChatRequest) -> ChatResponse:
    """
    Processes user requests through the AI Agent execution pipeline.
    Persists user input and agent tool outputs into SQLite storage.
    """
    if not conversation_manager:
        raise HTTPException(status_code=500, detail="Conversation Manager service not initialized.")

    try:
        input_name: str = payload.name.strip() if payload.name.strip() else "User"
        user_message: str = payload.message.strip()

        if not user_message:
            raise HTTPException(status_code=400, detail="Inbound message content cannot be empty.")

        # Persist and sync user profile
        existing_user = database.get_user_profile(input_name)
        is_returning: bool = existing_user is not None
        
        database.save_or_update_user(input_name)
        database.log_message(sender="User", message_text=user_message)

        # Formulate greeting and query Agent Execution Engine
        greeting_string: str = f"Welcome back, {input_name}!" if is_returning else f"Hello, {input_name}!"
        bot_identity_name: str = "Agent"

        # Delegate execution to our Agent Pipeline
        bot_reply: str = conversation_manager.process_message(user_message=user_message)

        # Log AI Agent response
        database.log_message(sender="Bot", message_text=bot_reply)

        return ChatResponse(
            greeting=greeting_string,
            bot_name=bot_identity_name,
            reply=bot_reply
        )

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        logging.error(f"Critical exception captured inside main runtime entrypoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server agent execution error.")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)