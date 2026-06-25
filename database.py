import sqlite3
import os
import logging
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DB_DIR, "chatbot.db")

def init_db():
    """Ensures the data directory exists and builds the database tables."""
    # Ensure the data/ directory exists before attempting to create the db file
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        logging.info("Created missing data directory for database.")

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Table 1: User profiles to save application state
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            last_seen TEXT NOT NULL
        )
    """)

    # Table 2: Chronological chat logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            message_text TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()
    logging.info("Database structural validation complete.")

def get_user_profile(name: str):
    """Fetches a user profile row by name."""
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM user_profiles WHERE name = ?", (name,))
    user = cursor.fetchone()
    
    connection.close()
    return user

def save_or_update_user(name: str):
    """Creates a user profile or updates their last seen timestamp."""
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Insert name, or update last_seen if the name already exists
    cursor.execute("""
        INSERT INTO user_profiles (name, last_seen) 
        VALUES (?, ?)
        ON CONFLICT(name) DO UPDATE SET last_seen = excluded.last_seen
    """, (name, current_time))

    connection.commit()
    connection.close()

def log_message(sender: str, message_text: str):
    """Appends an interaction statement securely into the history logs."""
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO chat_history (sender, message_text, timestamp)
        VALUES (?, ?, ?)
    """, (sender, message_text, current_time))

    connection.commit()
    connection.close()

def get_last_interaction_context() -> str:
    """Retrieves what the bot last said to help establish context tracking later."""
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    
    # Grab the most recent entry spoken by the Bot
    cursor.execute("""
        SELECT message_text FROM chat_history 
        WHERE sender = 'Bot' 
        ORDER BY message_id DESC LIMIT 1
    """)
    result = cursor.fetchone()
    
    connection.close()
    return result[0] if result else ""