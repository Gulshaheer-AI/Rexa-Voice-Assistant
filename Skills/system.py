from .rules import Skill
import os
import pyautogui
class Systemskill(Skill):
    def matches(self, command):
    # 1. Make a list of words
     triggers = ["shutdown","lock", "screenshot", "restart"]
    
        # 2. Check the list
     for trigger in triggers:
            if trigger in command.lower():
                return True
                
     return False
    def execute(self, command, speak):
       
        if "shutdown" in command.lower():
            speak("Shutting down the system, sir.")
            os.system("shutdown /s /t 5")

        elif "restart" in command.lower():
            speak("Restarting the system.")
            os.system("shutdown /r /t 5")

        elif "lock" in command.lower():
            speak("Locking the workstation.")
            os.system("rundll32.exe user32.dll,LockWorkStation")
    # CORRECT
        elif "take screenshot" in command.lower():
            speak("Taking a screenshot.")
            pictures_path = os.path.join(os.path.expanduser("~"), "Pictures")
            save_path = os.path.join(pictures_path, "jarvis_screenshot.png")
            pyautogui.screenshot(save_path)
            speak("Screenshot saved to your Pictures folder.")  