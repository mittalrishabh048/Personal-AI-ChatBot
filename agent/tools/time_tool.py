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
    "description": "CRITICAL: You do NOT have an internal clock. You MUST invoke this function whenever the user asks for the current time, date, or temporal reference points.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    },
    "func": get_current_time
}