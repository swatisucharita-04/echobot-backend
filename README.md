Absolutely! Here's a **complete, ready-to-copy `README.md`** that you can paste directly into VS Code:

```markdown
# echobot-backend
Backend for EchoBot – Conversational AI using STT, LLM, and TTS

# 🎙️ EchoBot – AI Voice Agent

**EchoBot** is a real-time AI-powered voice agent that listens to user speech, understands it using AI, and responds back using **Murf AI** voices.  
It combines **Speech-to-Text (STT)**, **AI reasoning**, and **Text-to-Speech (TTS)** to create a seamless conversation experience.

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
- HTML5, CSS3, JavaScript
- Audio recording via MediaRecorder API (STT input)
- Fetch API for server communication

### Backend
- Python 3.x
- FastAPI (for API endpoints)
- Murf AI TTS API (Text-to-Speech)
- AssemblyAI STT API (Speech-to-Text)
- Google Gemini AI API (AI conversation logic)

---

## 🌐 Live Demo
Check out the live version of EchoBot here: [https://echobot-backend-6yr8.onrender.com/]

---

## 🏗 Architecture

**Flow Diagram:**

```

\[User Voice Input] → \[Frontend Recorder] → \[Backend API]
↓                     ↓
\[AssemblyAI STT] → \[Google Gemini AI Processing] → \[Murf AI TTS]
↓                     ↓
\[Audio Response] ← \[Frontend Playback]

````

This represents the complete voice agent pipeline from capturing audio to generating responses.

---

## ▶️ How to Run Locally

### 1️⃣ Clone the repository
```bash
git clone https://github.com/your-username/echobot.git
cd echobot
````

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Set environment variables

Create a `.env` file in the project root and add:

```
ASSEMBLYAI_API_KEY=your_assemblyai_api_key
MURF_API_KEY=your_murf_api_key
GEMINI_API_KEY=your_gemini_api_key
```

### 4️⃣ Start the backend server

```bash
uvicorn app:app --reload
```

### 5️⃣ One-Command Smoke Test

You can quickly test the full voice agent flow using:

```bash
python smoke_test.py
```

**smoke\_test.py** should:

* Record a short audio sample
* Process it through STT → LLM → TTS
* Play the generated audio

---

## 🛠 Troubleshooting

* **Latency issues**: Ensure your internet is stable; close other apps using the microphone.
* **Microphone permissions**: Check OS/browser settings to allow mic access.
* **Dependencies errors**: Run `pip install -r requirements.txt` and verify `.env` keys are correct.
* **Audio not playing**: Ensure `generated_audio/` folder exists and is writable.

---

## 📂 Project Structure

```
echobot/
├── __pycache__/                 # Python bytecode cache
├── .vscode/                     # VSCode project settings
├── models/                      # AI/ML model scripts or saved models
├── node_modules/                # Node.js dependencies
├── recordings/                  # Audio recordings
├── services/                    # Modular service scripts
│   ├── __init__.py
│   ├── llm.py                   # Large Language Model related functions
│   ├── stt.py                   # Speech-to-Text services
│   └── tts.py                   # Text-to-Speech services
├── static/                      # Frontend assets
│   ├── generated_audio/         # Generated TTS audio files
│   ├── JS_audio-processor.js
│   ├── JS_audioPlayer.js
│   ├── fallback.mp3             # Fallback audio
│   ├── favicon.ico
│   ├── JS_processor.js
│   ├── JS_script.js
│   ├── JS_Server.js
│   └── style.css
├── templates/                   # HTML templates
│   └── index.html               # Main UI
├── uploads/                     # User-uploaded files
├── venv/                        # Python virtual environment
├── app.py                       # Main FastAPI app
├── chat.py                      # Chat management
├── config.py                    # App configuration
├── models.py                    # ML/AI models
├── murff_config.py              # Murf TTS API config
├── server.py                    # Backend server script
├── test_env.py                  # Environment testing
├── test.py                      # Unit tests
├── transcriber.py               # Audio transcription
├── chat_memory.json             # Conversation history
├── package.json                 # Node.js config
├── package-lock.json            # Node.js dependency lock
├── .env                         # Environment variables
├── .gitignore                   # Git ignore file
├── README.md                    # Project documentation
└── requirements.txt             # Python dependencies
```

---

## 🤝 Contribution

Contributions are welcome! Please fork the repo and submit a pull request.

---

## 📝 License

MIT License

```
