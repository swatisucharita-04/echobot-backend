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
[User Voice Input] → [Frontend Recorder] → [Backend API]
↓ ↓
[AssemblyAI STT] → [Gemini AI Processing] → [Murf AI TTS]
↓ ↓
[Audio Response] ← [Frontend Playback] ← [Backend API]


---

## ▶️ How to Run Locally

### 1️⃣ Clone the repository
```bash
git clone https://github.com/your-username/echobot.git
cd echobot

2️⃣ Install dependencies
pip install -r requirements.txt

3️⃣ Set environment variables

Create a .env file in the project root and add:

ASSEMBLYAI_API_KEY=your_assemblyai_api_key
MURF_API_KEY=your_murf_api_key
GEMINI_API_KEY=your_gemini_api_key

4️⃣ Start the backend server
uvicorn main:app --reload

📂 Project Structure
echobot/
30 DAYS OF VOICE AI/
│
├── __pycache__/                  # Auto-generated Python bytecode cache
├── .vscode/                      # VS Code workspace settings
│
├── generated_audio/              # Possibly stores generated audio files (MP3/WAV)
│
├── static/                       # Static files for Flask (CSS, JS, images, etc.)
│   ├── generated/                # Likely generated images/audio for serving
│   ├── generated_audio/           # Another location for generated audio files
│   ├── fallback.mp3               # A default audio file used if generation fails
│   ├── script.js                  # Frontend JavaScript logic
│   └── style.css                  # Frontend CSS styling
│
├── templates/                    # HTML templates for Flask
│   └── index.html                 # Main webpage template
│
├── uploads/                      # Folder for storing uploaded files (voice/text)
│
├── venv/                         # Python virtual environment
│
├── .env                          # Environment variables (API keys, config)
├── app.py                        # Main Flask application entry point
├── chat_memory.json              # Stores chat history or conversation memory
├── murf_config.py                 # Murf API configuration and helper functions
├── README.md                     # Project description/documentation
├── requirements.txt               # Python dependencies list
├── tempCodeRunnerFile.py          # Temporary file created by VS Code when running code
└── test_env.py                    # Script to test environment variables/config


###How it works (based on structure):

Frontend:
HTML in templates/index.html
JavaScript in static/script.js (handles voice recording, sending data to backend, playing generated audio)
CSS in static/style.css

Backend:
app.py runs Flask to serve frontend and handle API requests.
Uses murf_config.py to connect with the Murf Text-to-Speech API.
Data Storage:
uploads/ → Stores user-uploaded audio files.
generated_audio/ and static/generated_audio/ → Stores generated voice output.
chat_memory.json → Keeps chat or conversation state.
Config:
.env → Stores sensitive keys like Murf API key.
requirements.txt → List of libraries needed to install.
