from .rules import Skill
from musicLibrary import music
import webbrowser

class Webskill(Skill):

    def matches(self, command):
       triggers = ["google", "youtube", "facebook","chatgpt","gemini","whatsapp"]

       for trigger in triggers:
           if trigger in command.lower():
               return True
       return False   


    
    def execute(self, command, speak):
        if "open google" in command.lower():
         webbrowser.open("https://google.com")
        elif "open chatgpt" in command.lower() or "open chat gpt" in command.lower():
            webbrowser.open("https://chatgpt.com")
        elif "open whatsapp" in command.lower():
            webbrowser.open("https://web.whatsapp.com")
        elif "open youtube" in command.lower():
            webbrowser.open("https://youtube.com")
        elif "open facebook" in command.lower():
            webbrowser.open("https://facebook.com")
        elif "open gemini" in command.lower():
            speak("Opening Gemini")
            webbrowser.open("https://gemini.google.com/app")


    
