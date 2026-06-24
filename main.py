import logging
import chatengine

# Configure logging to track application lifecycle and exceptions
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    logging.info("Chatbot application lifecycle started.")
    
    user_name = input("What's your name: ").strip()
    if not user_name:
        user_name = "User"
        
    greeting = chatengine.get_time_greeting(user_name)
    print(greeting)
    print("Hello and Welcome to your Chatbot")
    print("You can ask me basic questions. Type 'bye' to exit from the bot.")

    while True:
        try:
            user_input = input("\nAsk Your Question: ").strip()
            
            # Edge Case Handling: Catch empty inputs early
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