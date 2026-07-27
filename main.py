import speech_recognition as sr
import pyaudio
import numpy as np
from openwakeword.model import Model
import pygame
import os
import edge_tts
import asyncio
from AppOpener import open as app_open
import google.generativeai as genai
import soundfile as sf
from kokoro_onnx import Kokoro
from Skills.weather import Weatherskill  
from Skills.song import Songskill
from Skills.system import Systemskill
from Skills.news import Newsskill
from Skills.web import Webskill
from Skills.apps import Appskill
from dotenv import load_dotenv
import openwakeword
# Initialize Global Variables
recognizer = sr.Recognizer()
pygame.mixer.init()

# --- SETUP KOKORO (OFFLINE BRAIN) ---
try:
    kokoro = Kokoro("kokoro.onnx", "voices-v1.0.bin")
    print("Kokoro Offline TTS loaded successfully.")
except Exception as e:
    print(f"\n[WARNING] Could not load Kokoro TTS: {e}")
    kokoro = None

# --- GEMINI SETUP ---
load_dotenv()
key = os.getenv("Gemini_KEY")

genai.configure(api_key=key)

sys_instruction = """
You are Rexa, a witty personal assistant.
You must speak in plain text only. 
Do NOT use markdown (no asterisks, no bolding, no lists).
Keep answers short and conversational.
You can understand both English and Urdu.
"""

model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=sys_instruction)
chat_session = model.start_chat(history=[])

def ask_gemini(query):
    try:
        response = chat_session.send_message(query)
        return response.text.replace("*", "") 
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "I am unable to connect to the internet, sir."

# --- VOICE FUNCTIONS ---

async def generate_voice_online(text, output_file="voice.mp3"):
    voice = "en-US-MichelleNeural" 
    communicate = edge_tts.Communicate(text, voice, rate="+20%")
    await communicate.save(output_file)

def speak(text):
    
    if kokoro:
        try:
            samples, sample_rate = kokoro.create(
                text, voice="bf_emma", speed=1.0, lang="en-us"
            )
            output_file = "temp_voice.wav"
            sf.write(output_file, samples, sample_rate)
            
            pygame.mixer.music.load(output_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.unload()
            return
            
        except Exception as e:
            print(f"Kokoro Error: {e} | Switching to Backup...")

    try:
        output_file = "temp_voice.mp3"
        asyncio.run(generate_voice_online(text, output_file))
        
        pygame.mixer.music.load(output_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
    except Exception as e:
        print(f"Error playing audio: {e}")

def docommand(c):
    if "stop rexa" in c.lower() or "go to sleep" in c.lower():
        speak("Going to sleep, sir.")
        exit() 
    else:
        AI = ask_gemini(c)
        speak(AI)    

# --- MAIN EXECUTION START ---
if __name__ == "__main__":
    load_dotenv()
    
    # 1. Setup openWakeWord Engine
    # You can specify built-in models like "hey_jarvis", "alexa", "hey_siri", "ok_google".
    # Or pass a path to a custom ONNX file: wakeword_models=["path/to/model.onnx"]
    openwakeword.utils.download_models()
    oww_model = Model(wakeword_models=["Rexxa.onnx"], inference_framework="onnx")

    # Audio configurations required by openWakeWord
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1280  # 80ms buffer size optimal for openWakeWord processing

    # 2. Setup Audio Stream
    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=RATE,
        channels=CHANNELS,
        format=FORMAT,
        input=True,
        frames_per_buffer=CHUNK
    )

    Identity = False 
    speak("Activating Rexxa.")
    print("Rexa is online and listening (openWakeWord Mode)...")
    skills = [Weatherskill(), Songskill(), Systemskill(), Newsskill(), Webskill(), Appskill()]

    # Sensitivity threshold (0.5 is standard, lower for more sensitive, higher for stricter)
    DETECTION_THRESHOLD = 0.5

    # 3. The Infinite Loop
    try:
        while True:
            # Read raw audio buffer (ignore overflow errors when assistant is busy talking)
            data = audio_stream.read(CHUNK, exception_on_overflow=False)
            
            # Convert raw byte buffer to 16-bit integer numpy array
            pcm = np.frombuffer(data, dtype=np.int16)

            # Pass audio frame to openWakeWord
            prediction = oww_model.predict(pcm)

            # Check if any active model surpassed the detection threshold
            detected = False
            for model_name, score in prediction.items():
                if score >= DETECTION_THRESHOLD:
                    detected = True
                    oww_model.reset()  # Clear memory buffer after detection
                    break

            if detected:
                print("Wake word detected!")
                
                # --- PATH A: NOT VERIFIED YET ---
                if not Identity:
                    speak("Verification required. Confirm identity.")
                    
                    r = sr.Recognizer()
                    try:
                        with sr.Microphone() as source:
                            audio = r.listen(source, timeout=3, phrase_time_limit=3)
                        password = r.recognize_google(audio).lower()
                        
                        if "shaheer" in password:   
                            speak("Identity confirmed. Welcome back sir, How may i help you.")
                            Identity = True 
                        else:   
                            speak("Access denied.")
                            continue
                    except Exception:
                        speak("I didn't hear a password.")
                        continue

                # --- PATH B: ALREADY VERIFIED ---
                else:
                    speak("Yes sir?")

                # --- COMMON LISTENER FOR COMMANDS ---
                r = sr.Recognizer()
                try:
                    with sr.Microphone() as source:
                        print("Waiting for command...")
                        r.pause_threshold = 1 
                        audio = r.listen(source, timeout=3, phrase_time_limit=5)
                    
                    command = r.recognize_google(audio).lower()
                    print("Command received:", command)

                    skill_handled = False

                    for skill in skills:
                        if skill.matches(command):
                            skill.execute(command, speak) 
                            skill_handled = True
                            break
                    if skill_handled:
                        continue

                    docommand(command) 

                except Exception:
                    pass

    except KeyboardInterrupt:
        # Cleanup
        if audio_stream: 
            audio_stream.close()
        if pa: 
            pa.terminate()