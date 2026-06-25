import logging
import chatengine
import database

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    logging.info("Chatbot application lifecycle started.")
    
    # 1. Initialize System Storage and Configurations
    chatengine.load_system_data()
    database.init_db()
    
    # 2. Handle User Authentication State
    input_name = input("What's your name: ").strip()
    if not input_name:
        input_name = "User"
        
    # Check if this profile has visited before
    existing_user = database.get_user_profile(input_name)
    is_returning = existing_user is not None
    
    # Update state profile tracking records
    database.save_or_update_user(input_name)
    
    # 3. Dynamic User Greeting Sequences
    greeting = chatengine.get_time_greeting(input_name, is_returning=is_returning)
    print(greeting)
    
    bot_name = chatengine.get_config_item("bot_name")
    welcome_msg = chatengine.get_config_item("welcome_instruction")
    print(f"Hello and Welcome to {bot_name}")
    print(welcome_msg)

    # 4. Interactive Core State Loop
    while True:
        try:
            user_input = input("\nAsk Your Question: ").strip()
            
            if not user_input:
                print("Bot response: Please type something so I can help you!")
                continue
            
            # Log the incoming query statement safely to the history table
            database.log_message(sender="User", message_text=user_input)
                
            if "bye" in user_input.lower():
                logging.info("User initiated shutdown sequence.")
                print("Bot response: Goodbye!")
                break
                
            reply = chatengine.get_response(user_input)
            print(f"Bot response: {reply}")
            
            # Log the bot's outgoing reaction state cleanly to the database
            database.log_message(sender="Bot", message_text=reply)
            
        except KeyboardInterrupt:
            logging.warning("Execution interrupted by user (Ctrl+C). Exiting.")
            break
        except Exception as e:
            logging.error(f"An unexpected runtime error occurred: {e}")
            print("Bot response: Encountered an internal error processing that request.")

    logging.info("Chatbot application lifecycle terminated safely.")

if __name__ == "__main__":
    main()