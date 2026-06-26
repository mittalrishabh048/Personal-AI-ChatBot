import logging
import chatengine
import database

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    logging.info("Chatbot application lifecycle started.")
    
    chatengine.download_nlp_dependencies()
    chatengine.load_system_data()
    database.init_db()
    
    input_name = input("What's your name: ").strip()
    if not input_name:
        input_name = "User"
        
    existing_user = database.get_user_profile(input_name)
    is_returning = existing_user is not None
    database.save_or_update_user(input_name)
    
    greeting = chatengine.get_time_greeting(input_name, is_returning=is_returning)
    print(greeting)
    
    bot_name = chatengine.get_config_item("bot_name")
    welcome_msg = chatengine.get_config_item("welcome_instruction")
    print(f"Hello and Welcome to {bot_name}")
    print(welcome_msg)

    while True:
        try:
            user_input = input("\nAsk Your Question: ").strip()
            
            if not user_input:
                print("Bot response: Please type something so I can help you!")
                continue
            
            database.log_message(sender="User", message_text=user_input)
                
            if "bye" in user_input.lower():
                logging.info("User initiated shutdown sequence.")
                print("Bot response: Goodbye!")
                break
                
            reply = chatengine.get_response(user_input)
            print(f"Bot response: {reply}")
            
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