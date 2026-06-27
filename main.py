import logging
from typing import Dict, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

import chatengine
import database

# Configure application logging framework
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application startup and shutdown lifecycle events.
    Guarantees underlying dependencies are booted before processing traffic.
    """
    logging.info("System boot sequence initiated via lifespan context handlers.")
    chatengine.download_nlp_dependencies()
    chatengine.load_system_data()
    database.init_db()
    logging.info("All modular layers successfully registered. Server online.")
    yield
    logging.info("System teardown sequence completed cleanly.")

# Initialize the main FastAPI application instance
app = FastAPI(
    title="Smart AI Chatbot API",
    description="Production-grade stateful endpoint with integrated system analytics",
    version="10.0.0",
    lifespan=lifespan
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
    Performs a real-time system diagnostic check on critical infrastructure dependencies.
    Used by cloud infrastructure orchestrators to verify application viability.
    """
    health_status: Dict[str, Any] = {
        "status": "healthy",
        "database_connectivity": "disconnected",
        "external_llm_client": "offline"
    }
    
    try:
        # Check database health status
        database.get_recent_chat_history(limit=1)
        health_status["database_connectivity"] = "connected"
    except Exception as db_err:
        health_status["status"] = "unhealthy"
        health_status["database_connectivity"] = f"error: {str(db_err)}"
        
    # Check LLM client configuration state
    if chatengine.ai_client is not None:
        health_status["external_llm_client"] = "online"
    else:
        health_status["status"] = "unhealthy"
        
    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)
        
    return health_status


@app.post("/chat", response_model=ChatResponse)
def handle_chat_session(payload: ChatRequest) -> ChatResponse:
    """
    Processes stateful user conversations over a validated POST contract.
    Persists history to SQLite and aggregates contextual memory arrays for LLM inference.
    """
    try:
        input_name: str = payload.name.strip() if payload.name.strip() else "User"
        user_message: str = payload.message.strip()

        if not user_message:
            raise HTTPException(status_code=400, detail="Inbound message content cannot be empty.")

        # Evaluate existing user profile status to formulate accurate greet vectors
        existing_user = database.get_user_profile(input_name)
        is_returning: bool = existing_user is not None
        
        # Sync runtime profile data states to local database tables
        database.save_or_update_user(input_name)
        database.log_message(sender="User", message_text=user_message)

        # Compute linguistic greetings and query generative model strings
        greeting_string: str = chatengine.get_time_greeting(input_name, is_returning=is_returning)
        bot_identity_name: str = chatengine.get_config_item("bot_name")
        bot_reply: str = chatengine.get_response(user_message)

        # Persist generated response strings to history ledger rows
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
        raise HTTPException(status_code=500, detail="Internal server runtime matrix exception.")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)