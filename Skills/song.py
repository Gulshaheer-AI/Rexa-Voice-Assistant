from .rules import Skill
from musicLibrary import music
import webbrowser

class Songskill(Skill):

    def matches(self, command):
        return "play" in command.lower()
    def execute(self, command, speak):

         for song in music:
            if song in command:
                speak(f"Playing {song} ")
                webbrowser.open(music[song])
        

