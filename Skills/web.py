from .rules import Skill
import webbrowser

class Webskill(Skill):

    def matches(self, command):
        triggers = ["google", "youtube", "facebook", "chatgpt", "gemini", "whatsapp"]
        for trigger in triggers:
            if trigger in command.lower():
                return True
        return False   

    def execute(self, command, speak):
        cmd = command.lower()
        if "open google" in cmd:
            speak("Opening Google")
            webbrowser.open("https://google.com")
        elif "open chatgpt" in cmd or "open chat gpt" in cmd:
            speak("Opening ChatGPT")
            webbrowser.open("https://chatgpt.com")
        elif "open whatsapp" in cmd:
            speak("Opening WhatsApp Web")
            webbrowser.open("https://web.whatsapp.com")
        elif "open youtube" in cmd:
            speak("Opening YouTube")
            webbrowser.open("https://youtube.com")
        elif "open facebook" in cmd:
            speak("Opening Facebook")
            webbrowser.open("https://facebook.com")
        elif "open gemini" in cmd:
            speak("Opening Google Gemini")
            webbrowser.open("https://gemini.google.com/app")


    
