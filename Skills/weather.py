import requests
from .rules import Skill


class Weatherskill(Skill):
    def __init__(self):
        # The "Memory" (State)
        self.memory_city = "Faisalabad"  # Default city

    def matches(self, command):
        return "weather" in command.lower()
    def execute(self, command, speak):
        try:
            if " in " in command.lower():
                city = command.split(" in ")[-1].strip()
                self.memory_city = city
            else:
                city = self.memory_city    
            junk = [".", "?", "!", ",", " please", " now"]
            for mark in junk:
             city = city.replace(mark, "")
            
             city = city.strip().title() # Capitalize it (e.g., "berlin" -> "Berlin")
        # ---------------------------

             print(f"DEBUG: Searching API for: '{city}'")    
                
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
            geo_data = requests.get(geo_url).json()
                
            if "results" in geo_data:
                location = geo_data["results"][0]
                latitude = location["latitude"]
                longitude = location["longitude"]
                
                url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,weather_code"
                response = requests.get(url).json()
                
                current_weather = response['current']
                temp = current_weather['temperature_2m']
                code = current_weather['weather_code']

                condition = "clear sky"
                if code in [1, 2, 3]: condition = "cloudy"
                elif code in [51, 53, 55, 61, 63, 65]: condition = "rainy"
                elif code >= 71: condition = "snowy"

                
                speak(f"The temperature in {city} is {temp} degrees Celsius and it looks {condition}.")
            else:
                speak("I couldn't find coordinates for that city.")
        except Exception as e:
            print(f"Weather error: {e}")
            speak("I couldn't get the weather data.")