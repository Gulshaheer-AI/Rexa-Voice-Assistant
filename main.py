import speech_recognition as sr
import struct
import pyaudio
import pvporcupine
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
# 1. Configure API
# (I put your key back in, but be careful sharing this online!)

load_dotenv('keys.env')
key = os.getenv("Gemini_KEY")

genai.configure(api_key=key)

# 2. Define System Instructions
sys_instruction = """
You are Rexa, a witty personal assistant.
You must speak in plain text only. 
Do NOT use markdown (no asterisks, no bolding, no lists).
Keep answers short and conversational.
You can understand both English and Urdu.
"""

# 3. Initialize Model (Global Scope)
# We use 'gemini-1.5-flash' because 2.5 is not standard yet
# --- GEMINI SETUP (UPDATED) ---
model = genai.GenerativeModel('gemini-2.5-flash-lite-preview-09-2025', system_instruction=sys_instruction)

# Start a Chat Session (This saves history)
chat_session = model.start_chat(history=[])
# 4. The Function
def ask_gemini(query):
    try:
        # We use the chat_session variable we created above
        response = chat_session.send_message(query)
        return response.text.replace("*", "") 
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "I am unable to connect to the internet, sir."

# --- VOICE FUNCTIONS ---

async def generate_voice(text, output_file="voice.mp3"):
    voice = "en-US-MichelleNeural" 
    communicate = edge_tts.Communicate(text, voice, rate="+20%")
    await communicate.save(output_file)

async def generate_voice_online(text, output_file="voice.mp3"):
    voice = "en-US-AriaNeural" 
    communicate = edge_tts.Communicate(text, voice, rate="+20%")
    await communicate.save(output_file)   

def speak(text):
# ... (The rest of your speak function stays the same) ...
    # PATH A: Try Kokoro (Offline & High Quality)
    if kokoro:
        try:
            # Generate audio data in memory
            # Voices: af_sarah, af_bella, am_adam, am_michael
            samples, sample_rate = kokoro.create(
                text, voice="bf_emma", speed=1.0, lang="en-us"
            )
            
            # Save as WAV (Kokoro uses wav)
            output_file = "temp_voice.wav"
            sf.write(output_file, samples, sample_rate)
            
            # Play it
            pygame.mixer.music.load(output_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.unload()
            return # Success! We are done.
            
        except Exception as e:
            print(f"Kokoro Error: {e} | Switching to Backup...")
    
    # PATH B: Fallback to Edge-TTS (Online)
    # This runs if Kokoro is missing OR if it crashes
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
        AI=ask_gemini(c)
        speak(AI)    

# --- MAIN EXECUTION START ---
if __name__ == "__main__":
    load_dotenv('keys.env')
    voicekey = os.getenv('Porcupine_key s')
    # 1. Setup Porcupine (The Offline Wake Word Engine)
    porcupine = pvporcupine.create(access_key=voicekey, keyword_paths=["rexa_windows.ppn"]) # This tells Python: "Hey, look inside this specific file to find the sound pattern."
    
    # 2. Setup Audio Stream (Input)
    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )
 
    Identity = False 
    speak("Activating Rexa.")
    print("Rexa is online and listening (Offline Mode)...")
    skills = [Weatherskill(),Songskill(),Systemskill(),Newsskill(),Webskill(), Appskill()]

    # 3. The Infinite Loop (No Internet Required for Waiting)
    try:
        while True:
            # Read raw audio
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            # Check for Wake Word
            keyword_index = porcupine.process(pcm)

            # If index >= 0, it heard "Rexa"
            if keyword_index >= 0:
                print("Wake word detected!")
                
                # --- PATH A: NOT VERIFIED YET ---
                if Identity == False:
                    speak("Verification required. Confirm identity.")
                    
                    # Switch to Google Recognizer for Password (needs internet)
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
                            continue # Restart loop
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
                        # Short pauses for snappy response
                        r.pause_threshold = 1 
                        audio = r.listen(source, timeout=3, phrase_time_limit=5)
                    
                    command = r.recognize_google(audio).lower()
                    print("Command received:", command)

                    skill_handled = False

                    # --- THE NEW INTERCEPTOR ---
                    for skill in skills:
                        if skill.matches(command):
                            skill.execute(command,speak) 
                            skill_handled = True
                            break
                    if skill_handled:
                            continue



                    # 👇 THIS MUST BE BACK (LEFT) AT THE SAME LEVEL AS 'if'
                    docommand(command) 

                except Exception:
                    pass

    except KeyboardInterrupt:
        # Cleanup if you press Ctrl+C
        if porcupine: porcupine.delete()
        if audio_stream: audio_stream.close()
        if pa: pa.terminate()
 
        