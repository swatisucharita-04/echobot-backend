# echobot-backend
Backend for EchoBot – Conversational AI using STT, LLM, and TTS

# 🎙️ EchoBot – AI Voice Agent

**EchoBot** is an AI-powered voice agent that listens to user speech, understands it, and responds back using **Murf AI** voices.  
It combines **speech-to-text**, **AI reasoning**, and **text-to-speech** to create a seamless conversation experience.

---

## ✨ Features
- 🎤 **Voice Recording** – Capture user audio directly in the browser.
- 📝 **Speech-to-Text** – Convert spoken audio into text using **AssemblyAI**.
- 🤖 **AI Understanding** – Process user queries with **Google Gemini AI**.
- 🗣 **Text-to-Speech** – Generate natural-sounding responses with **Murf AI**.
- 🌐 **Real-time Web Interface** – Interactive UI with playback support.
- 🔄 **End-to-End Flow** – Fully integrated voice conversation cycle.

---

## 🛠 Technologies Used
### Frontend
- HTML5, CSS3, JavaScript (Vanilla)
- Audio recording via MediaRecorder API
- Fetch API for server communication

### Backend
- Python 3.x
- FastAPI (for API endpoints)
- Murf AI API (Text-to-Speech)
- AssemblyAI API (Speech-to-Text)
- Google Gemini API (AI conversation logic)

---

## 🏗 Architecture

**Flow Diagram:**

[User Voice Input] → [Frontend Recorder] → [Backend API]
↓ ↓
[AssemblyAI STT] → [Gemini AI Processing] → [Murf AI TTS]
↓ ↓
[Audio Response] ← [Frontend Playback]


This represents the complete voice agent pipeline from capturing audio to generating responses.

---

## ▶️ How to Run Locally

### 1️⃣ Clone the repository
```bash
git clone https://github.com/your-username/echobot.git
cd echobot

2️⃣ Install dependencies
bash
pip install -r requirements.txt

3️⃣ Set environment variables
Create a .env file in the project root and add:
ASSEMBLYAI_API_KEY=your_assemblyai_api_key
MURF_API_KEY=your_murf_api_key
GEMINI_API_KEY=your_gemini_api_key

4️⃣ Start the backend server
bash
uvicorn app:app --reload

▶️ One-Command Smoke Test
You can quickly test the full voice agent flow using:

bash
python smoke_test.py

smoke_test.py should:
Record a short audio sample
Process it through STT → LLM → TTS
Play the generated audio

🛠 Troubleshooting
Latency issues: Ensure your internet is stable; close other apps using the microphone.
Microphone permissions: Check OS/browser settings to allow mic access.
Dependencies errors: Run pip install -r requirements.txt and verify .env keys are correct.
Audio not playing: Ensure generated_audio/ folder exists and is writable.

📂 Project Structure
echobot/
30-DAYS-OF-VOICE-AGENTS/
│
├── __pycache__/                 # Python bytecode cache
├── .vscode/                     # VSCode project settings
├── models/                      # AI/ML model scripts or saved models
│
├── node_modules/                # Node.js dependencies
│
├── recordings/                  # Audio recordings
│
├── services/                    # Modular service scripts
│   ├── __pycache__/
│   ├── __init__.py
│   ├── llm.py                   # Large Language Model related functions
│   ├── stt.py                   # Speech-to-Text services
│   └── tts.py                   # Text-to-Speech services
│
├── static/                      # Frontend assets
│   ├── generated_audio/         # Generated TTS audio files
│   ├── JS_audio-processor.js
│   ├── JS_audioPlayer.js
│   ├── fallback.mp3             # Fallback audio
│   ├── favicon.ico
│   ├── JS_processor.js          # Audio/voice processing
│   ├── JS_script.js             # Main frontend JS logic
│   ├── JS_Server.js             # WebSocket or server communication
│   └── style.css
│
├── templates/                   # HTML templates
│   └── index.html               # Main UI
│
├── uploads/                     # User-uploaded files
│
├── venv/                        # Python virtual environment
│
├── Python Scripts
│   ├── __init__.py
│   ├── app.py                   # Main Flask/FastAPI app
│   ├── chat.py                  # Chat management
│   ├── config.py                # App configuration
│   ├── models.py                # ML/AI models
│   ├── murff_config.py          # Murf TTS API config
│   ├── server.py                # Backend server script
│   ├── tempCodeRunnerFile.py    # Temporary VSCode file
│   ├── test_env.py              # Environment testing
│   ├── test.py                  # Unit tests
│   └── transcriber.py           # Audio transcription
│
├── Data / Other Files
│   ├── assembly_recorded_20250821_161627.wav  # Sample audio recording
│   ├── chat_memory.json         # Conversation history
│   ├── package.json             # Node.js project config
│   ├── package-lock.json        # Node.js dependency lock
│   ├── .env                     # Environment variables
│   ├── .gitignore               # Files/folders Git ignores
│   ├── README.md                # Project documentation
│   └── requirements.txt         # Python dependencies


How it works

Frontend:
HTML in templates/index.html
JavaScript in static/script.js (handles voice recording, sending data to backend, playing generated audio)
CSS in static/style.css

Backend:
app.py runs FastAPI to serve frontend and handle API requests
murf_config.py connects with Murf TTS API

Data Storage:
uploads/ → Stores user-uploaded audio files
generated_audio/ & static/generated_audio/ → Stores generated voice output
chat_memory.json → Keeps chat or conversation state

Config:
.env → Stores API keys
requirements.txt → Python dependencies