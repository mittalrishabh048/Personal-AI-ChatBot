# 🤖 Personal AI Chatbot

A full-stack AI chatbot built with **Python**, **FastAPI**, **SQLite**, **Groq API**, and a simple **HTML + Tailwind CSS** frontend.

The chatbot can remember previous conversations, greet returning users, store chat history, and generate intelligent responses using the Groq LLM API.

---

# 📸 Project Preview

(Add screenshots here)

---

# 🚀 Features

- AI-powered conversations using Groq LLM
- FastAPI REST API backend
- SQLite database for persistent storage
- Conversation history (context window)
- Returning user detection
- Time-based greetings
- Fallback offline responses
- Simple responsive web interface
- Health check endpoint
- Modular project structure

---

# 🛠 Technologies Used

### Backend

- Python
- FastAPI
- Uvicorn
- SQLite
- Groq API
- Pydantic

### Frontend

- HTML
- Tailwind CSS
- JavaScript (Fetch API)

---

# 📁 Project Structure

```
PERSONAL-AI-CHATBOT
│
├── config/
│   └── config.json
│
├── data/
│   └── chatbot.db
│
├── frontend/
│   └── index.html
│
├── archive/
│
├── chatengine.py
├── database.py
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

# ⚙️ How It Works

## 1. User sends a message

The frontend sends a POST request to the FastAPI backend.

```
Frontend
      │
      ▼
FastAPI (/chat)
```

---

## 2. User Validation

The backend

- checks whether the user already exists
- updates the user's last visit
- saves the incoming message

---

## 3. Conversation Memory

The application loads the latest conversation history from SQLite.

Example:

```
User:
Hello

Bot:
Hi!

User:
Tell me about Python
```

These previous messages are sent to the AI model so it can answer with context.

---

## 4. AI Response

The backend sends:

- System Prompt
- Previous chat history
- Current user message

to the Groq API.

The AI generates a response.

---

## 5. Database Update

Both

- User message
- Bot response

are stored in SQLite.

---

## 6. Response Returned

FastAPI sends the chatbot reply back to the frontend.

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

Checks whether

- Database is working
- Groq client is initialized

Example response

```json
{
    "status":"healthy",
    "database_connectivity":"connected",
    "external_llm_client":"online"
}
```

---

## POST /chat

Request

```json
{
    "name":"Rishabh",
    "message":"Hello"
}
```

Response

```json
{
    "greeting":"Good Evening, Rishabh!",
    "bot_name":"Smart AI Chatbot",
    "reply":"Hello! How can I help you today?"
}
```

---

# ▶️ Installation

## Clone repository

```bash
git clone https://github.com/yourusername/personal-ai-chatbot.git
```

---

## Move into project

```bash
cd personal-ai-chatbot
```

---

## Install dependencies

```bash
pip install -r requirements.txt
```

---

## Set Groq API Key

Windows (PowerShell)

```powershell
$env:GROQ_API_KEY="YOUR_API_KEY"
```

Windows (CMD)

```cmd
set GROQ_API_KEY=YOUR_API_KEY
```

Linux / macOS

```bash
export GROQ_API_KEY=YOUR_API_KEY
```

---

## Run backend

```bash
python main.py
```

---

## Open frontend

Open

```
frontend/index.html
```

in your browser.

---

# 📦 Dependencies

```
fastapi
uvicorn
groq
pydantic
```

---

# 💡 What I Learned

Through this project, I learned:

- FastAPI basics
- REST APIs
- SQLite database operations
- Modular Python project structure
- API integration
- Environment variables
- JSON configuration files
- Frontend-backend communication
- Conversation memory handling
- Basic software architecture

---

# 🤖 About AI Assistance

This project was built with the assistance of AI tools.

I used AI to help generate code, explain concepts, and solve implementation problems during development.

Whenever I encountered code or concepts that I did not fully understand, I went back and studied them separately to understand how they work rather than simply copying the code.

The goal of using AI in this project was to accelerate learning while ensuring I understood the underlying concepts.

---

## Skills Demonstrated

- Python
- FastAPI
- REST API Development
- SQLite
- Database Design
- API Integration
- JSON Handling
- Error Handling
- Logging
- Environment Variables
- Project Structuring
- Frontend–Backend Communication

---

# 🔮 Future Improvements

- User authentication
- Multiple chat sessions
- Streaming responses
- Better UI
- Docker support
- Deployment on Render/Railway
- Voice input
- Voice output
- Image understanding
- File upload support
- Conversation search
- Export chat history
- Dark/Light theme switch

---

# 📜 License

This project is created for learning and educational purposes.

---

# 👨‍💻 Author

**Rishabh Mittal**

Computer Science Student

Learning Python, AI, Backend Development, and Full Stack Development by building real-world projects.
