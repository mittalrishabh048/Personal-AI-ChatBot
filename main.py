import logging
import chatengine

# Configure logging to track application lifecycle and exceptions
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    logging.info("Chatbot application lifecycle started.")
    
    # Initialize engine storage systems before receiving user interactions
    chatengine.load_system_data()
    
    user_name = input("What's your name: ").strip()
    if not user_name:
        user_name = "User"
        
    greeting = chatengine.get_time_greeting(user_name)
    print(greeting)
    
    # Retrieve configuration dynamically rather than using hardcoded values
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
                
            if "bye" in user_input.lower():
                logging.info("User initiated shutdown sequence.")
                print("Bot response: Goodbye!")
                break
                
            reply = chatengine.get_response(user_input)
            print(f"Bot response: {reply}")
            
        except KeyboardInterrupt:
            logging.warning("Execution interrupted by user (Ctrl+C). Exiting.")
            break
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            print("Bot response: Encountered an internal error processing that request.")

    logging.info("Chatbot application lifecycle terminated safely.")

if __name__ == "__main__":
    main()