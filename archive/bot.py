# AI Buddy

import datetime
import time

name=input("What's your name:")
presenthour=datetime.datetime.now().hour
if (5<=presenthour<=11):
    print("Good Morning",name)
elif(11<=presenthour<=17):
    print("Good Afternoon",name)
elif(17<=presenthour<=20):
    print("Good Evening",name)
else:
    print("Good Night",name)


print("Hello and Welcome to your Chatbot")
print("You can ask me basic questions,Type'bye' to exit from the bot")

# Chatbot Memory Creation
responses={
    "hello":"Hi,Welcome.How can I help you?",
    "how are you":"I am fine.Thanks for asking",
    "Who are you":"I am Smart AI Chatbot.You can also make me your buddy",
    "motivate me":"Keep going.Every bug of your project makes you a better developer",
    "happy":"Greate to hear that0",
    "what are functions":"Go watch apna college's or code with harry's function video.They have created a really beginner-frienly python playlists"
}

# Method Function To Get Response Of Chatbot
def getresponse(userques):
    userques=userques.lower()
    for each in responses:
        if each in userques:
            return responses[each]
    return "Sorry,I am not able to tell you about this!"
# Take User Input
while True:
    userinput=input("Ask Your Question:")
    reply=getresponse(userinput)
    print("Bot response:",reply)

    if "bye" in userinput.lower():
        break