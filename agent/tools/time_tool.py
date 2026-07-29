from datetime import datetime

def get_current_time() -> str:
    """
    Returns the current local date and time formatted as a human-readable string.
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

# Definition of the tool schema used for registration
TIME_TOOL_SCHEMA = {
    "name": "get_current_time",
    "description": "Get the current date and system time. Use this whenever the user asks for current time, today's date, or temporal reference points.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    },
    "func": get_current_time
}