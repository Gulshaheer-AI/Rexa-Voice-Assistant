from .rules import Skill
from AppOpener import open as app_open

class Appskill(Skill):

    def matches(self, command):
        return "open" in command.lower()
    def execute(self, command, speak):
          if "open" in command.lower():
            app_name = command.replace("open", "").strip()
            speak(f"Opening {app_name}")
            app_open(app_name, match_closest=True)
