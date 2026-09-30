from .rules import Skill
from .musicLibrary import music
import webbrowser
import urllib.parse

class Songskill(Skill):

    def matches(self, command):
        return "play" in command.lower()

    def execute(self, command, speak):
        cmd = command.lower()
        for song in music:
            if song.lower() in cmd:
                speak(f"Playing {song}")
                webbrowser.open(music[song])
                return
        
        # If not in custom library, search and play on YouTube
        song_query = cmd.replace("play", "").strip()
        if song_query:
            speak(f"Playing {song_query} on YouTube")
            query = urllib.parse.quote_plus(song_query)
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        else:
            speak("What song would you like me to play?")
