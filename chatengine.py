import datetime

# Chatbot Memory / Rule Base
responses = {
    "hello": "Hi, Welcome. How can I help you?",
    "how are you": "I am fine. Thanks for asking",
    "who are you": "I am Smart AI Chatbot. You can also make me your buddy",
    "motivate me": "Keep going. Every bug of your project makes you a better developer",
    "happy": "Great to hear that!",
    "what are functions": "Go watch apna college's or code with harry's function video. They have created really beginner-friendly python playlists"
}

def get_time_greeting(name: str) -> str:
    """Calculates the appropriate greeting based on the current system hour."""
    present_hour = datetime.datetime.now().hour
    if 5 <= present_hour <= 11:
        return f"Good Morning, {name}"
    elif 11 < present_hour <= 17:
        return f"Good Afternoon, {name}"
    elif 17 < present_hour <= 20:
        return f"Good Evening, {name}"
    else:
        return f"Good Night, {name}"

def get_response(user_query: str) -> str:
    """Processes input and evaluates intent matching without performing I/O."""
    normalized_query = user_query.lower()
    
    for key in responses:
        if key in normalized_query:
            return responses[key]
            
    return "Sorry, I am not able to tell you about this!"