# 🤖 Smart AI Assistant

A full-stack AI Assistant built with **Python**, **FastAPI**, **SQLite**, **Groq API**, **Whisper**, **gTTS**, and a responsive **HTML + Tailwind CSS** frontend.

The application supports both **text and voice conversations**, remembers previous interactions, greets returning users, autonomously calls backend tools when needed, converts speech to text, generates spoken AI responses, and automatically manages generated audio files through a background retention engine.

---

# 🚀 Features

- AI-powered text and voice conversations
- Groq Llama 3.3 (`llama-3.3-70b-versatile`) integration
- Autonomous LLM tool-calling
- Custom backend tools (Current Time tool)
- Speech-to-Text using Groq Whisper (`whisper-large-v3-turbo`)
- Text-to-Speech using gTTS
- End-to-end voice conversation pipeline
- FastAPI REST API backend
- SQLite database for persistent storage
- Conversation memory with contextual responses
- Returning user detection
- Time-based greetings
- Silent audio and background noise detection
- Graceful fallback responses
- Automated audio retention and cleanup
- Configurable application settings
- Responsive web interface
- Voice recording with MediaRecorder API
- Cross-browser support (Desktop + Mobile)
- Mobile testing through ngrok HTTPS
- Health check endpoint
- Modular layered architecture

---

# 🛠 Technologies Used

## Backend

- Python
- FastAPI
- Uvicorn
- SQLite
- Groq API
- Llama 3.3 (`llama-3.3-70b-versatile`)
- Groq Whisper (`whisper-large-v3-turbo`)
- gTTS
- Pydantic

## Frontend

- HTML
- Tailwind CSS
- JavaScript
- Fetch API
- MediaRecorder API
- Font Awesome

---

# 📁 Project Structure

```text
SMART-AI-ASSISTANT
│
├── agent/
│   ├── __init__.py
│   ├── tool_manager.py
│   └── tools/
│       ├── __init__.py
│       └── time_tool.py
│
├── archive/
│   ├── bot.py
│   ├── config.json
│   └── responses.json
│
├── config/
│   ├── __init__.py
│   └── config.py
│
├── data/
│   └── chatbot.db
│
├── frontend/
│   └── index.html
│
├── services/
│   ├── __init__.py
│   ├── audio_cleanup.py
│   ├── conversation_manager.py
│   ├── llm_service.py
│   ├── stt_service.py
│   └── tts_service.py
│
├── static_audio/
│
├── chatengine.py
├── database.py
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
└── __pycache__/
```

---

# 🏗️ System Architecture

The application follows a layered architecture where each component has a single responsibility. User requests flow through the backend services before interacting with the AI model, tools, database, and voice processing modules.

```text
                          User
                            │
          ┌─────────────────┴─────────────────┐
          │                                   │
     Text Message                      Voice Message
          │                                   │
          │                          Speech-to-Text Service
          │                        (Groq Whisper API)
          │                                   │
          └─────────────────┬─────────────────┘
                            │
                            ▼
                   FastAPI Backend (main.py)
                            │
                            ▼
               Conversation Manager Service
                            │
                            ▼
                     LLM Service (Groq)
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
         Tool Manager             SQLite Database
                │                       ▲
                ▼                       │
      Backend Tools (Agent)      Chat History &
         • Time Tool             User Profiles
                │
                ▼
         AI Response Generated
                │
                ▼
          Text-to-Speech Service
                │
             (gTTS)
                │
                ▼
          Generated MP3 Audio
                │
                ▼
     Static Audio (/audio/{filename})
                │
                ▼
             Frontend UI
```

### Layer Responsibilities

| Layer | Responsibility |
|--------|----------------|
| **Frontend** | Collects text and voice input, displays responses, and plays generated audio. |
| **FastAPI Backend** | Receives requests, validates input, and coordinates all backend services. |
| **Conversation Manager** | Maintains conversation history and prepares context for the LLM. |
| **LLM Service** | Sends prompts to Groq Llama 3.3 and manages AI responses. |
| **Tool Manager** | Executes backend tools requested by the AI model. |
| **Agent Tools** | Perform real-world actions such as retrieving the current date and time. |
| **SQLite Database** | Stores user profiles and conversation history. |
| **STT Service** | Converts user speech into text using Groq Whisper. |
| **TTS Service** | Converts AI responses into MP3 audio using gTTS. |
| **Audio Cleanup Service** | Automatically removes expired audio files based on the configured retention period. |

---

# ⚙️ How It Works

## 1. User Interaction

Users can interact with the assistant using either:

- Text messages
- Voice messages

```
Browser
     │
     ▼
 FastAPI Backend
```

---

## 2. Speech-to-Text Processing (Voice Only)

When a voice message is received:

- Audio is uploaded to FastAPI.
- Groq Whisper transcribes speech into text.
- Silent or noisy recordings are detected.
- Invalid audio receives a graceful fallback response.

```
Voice Recording
       │
       ▼
Groq Whisper
       │
       ▼
Transcribed Text
```

---

## 3. User Validation

The backend:

- Checks whether the user already exists.
- Updates the user's last visit.
- Stores the incoming message.

---

## 4. Conversation Memory

The Conversation Manager loads recent conversation history from SQLite.

Example:

```text
User:
Hello

Assistant:
Hi! How can I help you today?

User:
What time is it?
```

Previous messages are included in the prompt so the AI can respond with context.

---

## 5. AI Reasoning & Tool Calling

The backend sends:

- System Prompt
- Conversation History
- Current User Message
- Available Backend Tools

to Groq's Llama 3.3 model.

Whenever required, the model automatically invokes backend tools.

Example:

```text
User
"What is the current time?"

        │
        ▼

LLM decides to call

get_current_time()

        │
        ▼

Backend executes tool

        │
        ▼

Tool result returned

        │
        ▼

LLM generates final response
```

---

## 6. Text-to-Speech

After generating a response:

- gTTS converts the reply into speech.
- An MP3 file is created.
- FastAPI serves it through a static endpoint.

```text
Assistant Reply
        │
        ▼
      gTTS
        │
        ▼
 Generated MP3
        │
        ▼
 /audio/{filename}
```

---

## 7. Database Update

Both:

- User message
- Assistant response

are stored in SQLite for future conversations.

---

## 8. Automated Audio Retention Engine

A background worker continuously monitors generated MP3 files.

Old audio files are automatically deleted after the configured retention period (`AUDIO_RETENTION_SECONDS`, default: 30 minutes), preventing unnecessary storage growth.

---

## 9. Response Returned

FastAPI returns:

- Greeting
- Assistant reply
- Audio URL (if generated)

to the frontend.

---

# 🗄 Database Schema

## user_profiles

| Column | Type |
|---------|------|
| user_id | INTEGER |
| name | TEXT |
| last_seen | TEXT |

---

## chat_history

| Column | Type |
|---------|------|
| message_id | INTEGER |
| sender | TEXT |
| message_text | TEXT |
| timestamp | TEXT |

---

# 🔌 API Endpoints

## GET /health

Checks whether:

- Database is connected
- Groq client is initialized
- Voice services are available

Example response

```json
{
  "status": "healthy",
  "database_connectivity": "connected",
  "external_llm_client": "online"
}
```

---

## POST /chat

Handles text conversations.

Request

```json
{
  "name": "Rishabh",
  "message": "Hello"
}
```

Response

```json
{
  "greeting": "Good Evening, Rishabh!",
  "assistant_name": "Smart AI Assistant",
  "reply": "Hello! How can I help you today?",
  "audio_url": "/audio/reply.mp3"
}
```

---

## POST /chat/voice

Handles voice conversations.

Accepts:

- Recorded audio
- User name

Pipeline

```text
Audio
   │
   ▼
Speech-to-Text
   │
   ▼
LLM + Tool Calling
   │
   ▼
Text-to-Speech
   │
   ▼
JSON Response + Audio URL
```

---

## GET /audio/{filename}

Serves generated MP3 files for playback.

---

# ▶️ Installation

## Clone Repository

```bash
git clone https://github.com/mittalrishabh048/Smart-AI-Assistant.git
```

---

## Move into the Project

```bash
cd Smart-AI-Assistant
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Set Groq API Key

### Windows (PowerShell)

```powershell
$env:GROQ_API_KEY="YOUR_API_KEY"
```

### Windows (CMD)

```cmd
set GROQ_API_KEY=YOUR_API_KEY
```

### Linux / macOS

```bash
export GROQ_API_KEY=YOUR_API_KEY
```

---

## Run the Backend

```bash
python main.py
```

---

## Open the Frontend

Open:

```text
frontend/index.html
```

in your browser.

---

# 📱 Mobile Testing

The frontend is designed to work seamlessly on desktop and mobile devices.

Supported features include:

- Voice recording using MediaRecorder API
- Automatic MIME-type detection
- Support for:
  - `audio/webm`
  - `audio/mp4`
  - `audio/aac`
- Android Chrome compatibility
- iOS Safari compatibility
- Relative API routes (`/chat` and `/chat/voice`)
- FastAPI running on `0.0.0.0`
- HTTPS mobile testing using ngrok

---

# 📦 Dependencies

```text
fastapi
uvicorn
groq
gtts
pydantic
```

---

# 💡 What I Learned

Through this project, I learned:

- FastAPI backend development
- REST API design
- SQLite database operations
- Modular software architecture
- Layered backend architecture
- AI Agent design principles
- LLM tool calling
- Function calling workflows
- Speech-to-Text integration
- Text-to-Speech integration
- Audio processing pipelines
- Background worker implementation
- Automated file retention systems
- FastAPI static file serving
- Environment variable management
- Configuration management
- Frontend-backend communication
- Browser MediaRecorder API
- Cross-browser compatibility
- Mobile testing using ngrok
- Building production-style AI assistants

---

# 🤖 About AI Assistance

This project was built with the assistance of AI tools.

I used AI to help generate code, explain concepts, and solve implementation challenges during development.

Whenever I encountered code or concepts that I did not fully understand, I studied them separately to understand how they worked rather than simply copying the code.

The goal of using AI in this project was to accelerate learning while ensuring I understood the underlying concepts and architecture.

---

## Skills Demonstrated

- Python
- FastAPI
- REST API Development
- SQLite
- Database Design
- AI Agent Development
- LLM Tool Calling
- Groq API Integration
- Whisper Speech-to-Text
- gTTS Text-to-Speech
- Audio Processing
- Background Workers
- Static File Serving
- JSON Handling
- Error Handling
- Logging
- Environment Variables
- Configuration Management
- Project Structuring
- Frontend-Backend Communication
- Responsive Web Development

---

# 🔮 Future Improvements

- User authentication
- Multiple chat sessions
- Streaming AI responses
- Streaming audio playback
- Weather tool
- Web search tool
- Email automation
- Calendar integration
- File upload support
- Image understanding
- Multi-language support
- Voice Activity Detection (VAD)
- Conversation search
- Export chat history
- Docker support
- Deployment on Render/Railway
- Dark/Light mode

---

# 📜 License

This project is created for learning and educational purposes.

---

# 👨‍💻 Author

**Rishabh Mittal**

Computer Science Student

Passionate about Backend Development, AI Agents, Python, and Full Stack Engineering.

Currently building real-world projects to strengthen software engineering and AI development skills.