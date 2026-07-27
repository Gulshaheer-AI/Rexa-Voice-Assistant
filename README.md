# 🎙️ Rexa - Custom AI Voice Assistant

Rexa is an advanced, Python-based personal voice assistant designed with a hybrid local/cloud architecture. It features constant background wake-word detection, voice-biometric identity verification, and a modular "Skill" system for executing specific local tasks before falling back on an LLM for conversational intelligence.

## 🚀 Key Features

* **Offline Wake Word Detection:** Utilizes Picovoice Porcupine to run a continuous, low-latency background listener for the custom wake word "Rexa" without using internet bandwidth.
* **Identity Verification:** Implements a security gate that requires a specific voice password upon initial activation before processing subsequent commands.
* **Modular Skill Architecture:** Built with an interceptor pattern. Spoken commands are first routed through localized skill modules (Weather, System, Apps, News, etc.). If no local skill matches, the prompt is routed to the AI brain.
* **Contextual AI Brain:** Integrated with Google's Gemini Flash model, maintaining chat session history for natural, multi-turn conversations.
* **Hybrid Text-to-Speech (TTS):** * *Primary (Offline):* Uses the high-fidelity Kokoro ONNX model for fast, local voice generation.
    * *Fallback (Online):* Automatically routes to Microsoft Edge-TTS if the local model fails or is missing.

## 🛠️ Technology Stack

| Component | Technology / Library |
| :--- | :--- |
| **Language** | Python 3.x |
| **Wake Word Engine** | Picovoice Porcupine (`pvporcupine`) |
| **Speech-to-Text (STT)** | Google Speech Recognition (`speech_recognition`) |
| **Text-to-Speech (TTS)** | Kokoro ONNX, Edge-TTS |
| **LLM Engine** | Google Generative AI (Gemini Flash Lite) |
| **Audio Processing** | PyAudio, Pygame, SoundFile |

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Gulshaheer-AI/Rexa-Voice-Assistant.git
cd Rexa-Voice-Assistant
```

### 2. Set Up the Virtual Environment
```bash
python -m venv j.env
.\j.env\Scripts\activate
pip install -r requirements.txt
```

### 3. Add Required Local Files
Create your `.env` file and add your Kokoro ONNX models to the root folder as described above.

### 4. Run the Assistant
```bash
python main.py
```
