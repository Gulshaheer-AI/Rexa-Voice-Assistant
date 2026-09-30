from .rules import Skill
import os
import pyautogui

class Systemskill(Skill):
    def matches(self, command):
        triggers = ["shutdown", "lock", "screenshot", "restart"]
        for trigger in triggers:
            if trigger in command.lower():
                return True
        return False

    def execute(self, command, speak):
        cmd = command.lower()
        if "shutdown" in cmd:
            speak("Shutting down the system, sir.")
            os.system("shutdown /s /t 5")

        elif "restart" in cmd:
            speak("Restarting the system.")
            os.system("shutdown /r /t 5")

        elif "lock" in cmd:
            speak("Locking the workstation.")
            os.system("rundll32.exe user32.dll,LockWorkStation")

        elif "screenshot" in cmd:
            speak("Taking a screenshot.")
            pictures_path = os.path.join(os.path.expanduser("~"), "Pictures")
            os.makedirs(pictures_path, exist_ok=True)
            save_path = os.path.join(pictures_path, "rexa_screenshot.png")
            pyautogui.screenshot(save_path)
            speak("Screenshot saved to your Pictures folder.")  