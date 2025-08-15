import os
import io
import time
from pathlib import Path
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# -------------------- Setup & Config --------------------
load_dotenv()

from services.stt import assemblyai_transcribe
from services.llm import query_gemini_llm
from services.tts import generate_murf_audio_url

ASSEMBLYAI_KEY = os.getenv("ASSEMBLYAI_KEY")
GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY")
MURF_API_KEY    = os.getenv("MURF_API_KEY")

PROJECT_DIR   = Path(__file__).parent.resolve()
STATIC_DIR    = PROJECT_DIR / "static"
TEMPLATES_DIR = PROJECT_DIR / "templates"
GENERATED_DIR = STATIC_DIR / "generated_audio"

STATIC_DIR.mkdir(exist_ok=True)
GENERATED_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="EchoBot Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# In-memory chat history (simple demo storage)
chat_histories: Dict[str, List[Dict[str, str]]] = {}

# -------------------- Utilities --------------------
def _log(msg: str):
    print(f"[EchoBot] {msg}", flush=True)

def _require_env(var_name: str):
    if not os.getenv(var_name):
        raise HTTPException(status_code=500, detail=f"Missing env var: {var_name}")

# -------------------- STT: AssemblyAI --------------------
def assemblyai_transcribe(audio_bytes: bytes) -> str:
    _require_env("ASSEMBLYAI_KEY")
    headers = {"authorization": ASSEMBLYAI_KEY}

    # 1) Upload bytes
    up_url = "https://api.assemblyai.com/v2/upload"
    ur = requests.post(up_url, headers=headers, data=audio_bytes, timeout=60)
    if ur.status_code != 200:
        raise HTTPException(status_code=502, detail=f"AssemblyAI upload failed: {ur.status_code} {ur.text}")
    audio_url = ur.json().get("upload_url")
    if not audio_url:
        raise HTTPException(status_code=502, detail="AssemblyAI upload returned no 'upload_url'")

    # 2) Create transcript job
    tr_url = "https://api.assemblyai.com/v2/transcript"
    payload = {"audio_url": audio_url, "language_code": "en_us"}
    tr = requests.post(tr_url, headers=headers, json=payload, timeout=30)
    if tr.status_code not in (200, 201):
        raise HTTPException(status_code=502, detail=f"AssemblyAI transcript request failed: {tr.status_code} {tr.text}")
    transcript_id = tr.json().get("id")
    if not transcript_id:
        raise HTTPException(status_code=502, detail="AssemblyAI transcript request returned no id")

    # 3) Poll
    poll_url = f"{tr_url}/{transcript_id}"
    start, timeout_s = time.time(), 120
    while True:
        pr = requests.get(poll_url, headers=headers, timeout=30)
        if pr.status_code != 200:
            raise HTTPException(status_code=502, detail=f"AssemblyAI poll failed: {pr.status_code} {pr.text}")
        j = pr.json()
        status = j.get("status")
        if status == "completed":
            return j.get("text", "").strip()
        if status == "error":
            raise HTTPException(status_code=500, detail=f"AssemblyAI error: {j.get('error')}")
        if time.time() - start > timeout_s:
            raise HTTPException(status_code=504, detail="AssemblyAI transcription timed out")
        time.sleep(2)

# -------------------- LLM: Gemini --------------------
def query_gemini_llm(history: List[Dict[str, str]]) -> str:
    _require_env("GEMINI_API_KEY")

    # Convert our history to Gemini format
    contents = []
    for m in history:
        role = "user" if m["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    rr = requests.post(url, json={"contents": contents}, timeout=30)
    if rr.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Gemini API error: {rr.status_code} {rr.text}")
    j = rr.json()
    try:
        text = j["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        raise HTTPException(status_code=502, detail=f"Unexpected Gemini response: {j}")
    return text.strip()

# -------------------- TTS: Murf --------------------
def _extract_murf_url(j: dict) -> Optional[str]:
    # Handle multiple possible response shapes
    if not isinstance(j, dict):
        return None
    # common
    if j.get("audioFile") and isinstance(j["audioFile"], dict) and j["audioFile"].get("url"):
        return j["audioFile"]["url"]
    for key in ("audioFileUrl", "audio_url", "url"):
        if key in j and isinstance(j[key], str):
            return j[key]
    if "data" in j and isinstance(j["data"], dict):
        for key in ("audioFile", "audioFileUrl", "audio_url", "url"):
            val = j["data"].get(key)
            if isinstance(val, str):
                return val
            if isinstance(val, dict) and val.get("url"):
                return val["url"]
    return None

def _download_to_static(url: str) -> str:
    r = requests.get(url, stream=True, timeout=60)
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Failed to download TTS audio: {r.status_code}")
    fname = f"murf_{int(time.time()*1000)}.mp3"
    out_path = GENERATED_DIR / fname
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    # return public path
    return f"/static/generated_audio/{fname}"

def generate_murf_audio_url(text: str, voice_id: str = "en-US-natalie") -> str:
    _require_env("MURF_API_KEY")
    url = "https://api.murf.ai/v1/speech/generate"

    # Murf accepts either "api-key" header (most docs) OR Authorization Bearer in some clients.
    headers = {
        "accept": "application/json",
        "api-key": MURF_API_KEY,
        "content-type": "application/json",
    }
    payload = {
        "voiceId": voice_id,
        "text": text,
        "format": "MP3",
        # "sampleRate": "48000",  # optional
    }
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    if r.status_code not in (200, 201):
        raise HTTPException(status_code=502, detail=f"Murf TTS request failed: {r.status_code} {r.text}")

    j = r.json()
    direct_url = _extract_murf_url(j)
    job_id = j.get("jobId") or j.get("id")

    if direct_url:
        return _download_to_static(direct_url)

    # Poll job if needed
    if job_id:
        poll = f"https://api.murf.ai/v1/speech/jobs/{job_id}"
        start, timeout_s = time.time(), 90
        while True:
            rr = requests.get(poll, headers=headers, timeout=20)
            if rr.status_code != 200:
                raise HTTPException(status_code=502, detail=f"Murf job poll failed: {rr.status_code} {rr.text}")
            jj = rr.json()
            direct_url = _extract_murf_url(jj)
            if direct_url:
                return _download_to_static(direct_url)
            if time.time() - start > timeout_s:
                raise HTTPException(status_code=504, detail="Murf TTS job timed out")
            time.sleep(2)

    raise HTTPException(status_code=502, detail=f"Unexpected Murf response: {j}")

# -------------------- Routes --------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """
    Serves templates/index.html (your UI).
    """
    index_path = TEMPLATES_DIR / "index.html"
    if not index_path.exists():
        return HTMLResponse("<h1>EchoBot Backend</h1><p>Put your UI in templates/index.html</p>")
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/voices")
def voices():
    if not MURF_API_KEY:
        return {"voices": [
            {"id": "en-US-natalie", "name": "Natalie (mock)", "language": "en-US"},
            {"id": "en-US-ken", "name": "Ken (mock)", "language": "en-US"},
        ]}
    headers = {"accept": "application/json", "api-key": MURF_API_KEY}
    r = requests.get("https://api.murf.ai/v1/speech/voices", headers=headers, timeout=30)
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Murf voices error: {r.status_code} {r.text}")
    return r.json()

@app.post("/agent/chat/{session_id}")
async def chat_with_agent(session_id: str, file: UploadFile = File(...)):
    """
    Accepts an audio file from the frontend, runs STT -> LLM -> TTS,
    and returns JSON:
    {
      "transcript": "...",
      "response": "...",
      "audio_url": "/static/generated_audio/xxxx.mp3"
    }
    """
    # ---- 1) Read audio
    try:
        audio_bytes = await file.read()
        _log(f"Received audio {len(audio_bytes)} bytes for session {session_id}")
    except Exception as e:
        _log(f"Read error: {e}")
        raise HTTPException(status_code=400, detail="Could not read uploaded file")

    # ---- 2) STT
    try:
        transcript = assemblyai_transcribe(audio_bytes)
        _log(f"Transcript: {transcript}")
    except Exception as e:
        _log(f"STT error: {e}")
        transcript = "(Sorry, I couldn't understand your audio.)"

    # ---- 3) Update history
    history = chat_histories.get(session_id, [])
    history.append({"role": "user", "content": transcript})

    # ---- 4) LLM
    try:
        llm_response = query_gemini_llm(history)
        _log(f"LLM response: {llm_response}")
    except Exception as e:
        _log(f"LLM error: {e}")
        llm_response = "I'm having trouble connecting right now."
    history.append({"role": "assistant", "content": llm_response})
    chat_histories[session_id] = history

    # ---- 5) TTS
    try:
        audio_url = generate_murf_audio_url(llm_response)
        _log(f"TTS audio URL: {audio_url}")
    except Exception as e:
        _log(f"TTS error: {e}")
        # Fallback: return JSON with no audio_url (frontend will just show text)
        return JSONResponse(
            {"transcript": transcript, "response": llm_response, "audio_url": None},
            status_code=200,
        )

    return {
        "transcript": transcript,
        "response": llm_response,
        "audio_url": audio_url,
    }

@app.get("/tts")
def tts(text: str):
    """
    Simple test endpoint for audio streaming.
    Returns raw MP3 bytes for the given text (via Murf).
    Use from the browser: /tts?text=Hello%20world
    """
    if not text:
        raise HTTPException(status_code=400, detail="Query param 'text' is required")

    try:
        # Generate and download as file in /static/generated_audio
        public_url = generate_murf_audio_url(text)
        # Stream back the saved file (nice for <audio src="/tts?..."> OR fetch() -> blob)
        file_path = PROJECT_DIR / public_url.lstrip("/")
        audio_bytes = file_path.read_bytes()
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=echo.mp3"}
        )
    except HTTPException:
        raise
    except Exception as e:
        _log(f"/tts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# -------------------- Local dev --------------------
if __name__ == "__main__":
    import uvicorn
    _log("Starting server at http://127.0.0.1:8000")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


