import requests
from .rules import Skill


class Newsskill(Skill):
        def matches(self, command):
         return "news" in command.lower()
        def execute(self, command, speak):
            GNEWS_API_KEY = "cab6f417f2d8ef07413f51551e9c7a4b" 
            url = f"https://gnews.io/api/v4/top-headlines?country=us&token={GNEWS_API_KEY}" 
            try:
                response = requests.get(url).json()
                articles = response.get("articles", [])
                if articles: 
                    speak("Here are the top headlines.")
                    for article in articles[:5]:
                        speak(article.get("title"))
                else:
                    speak("Sorry, I could not fetch the news right now.")
            except Exception as e:
                speak("Error fetching news.")
