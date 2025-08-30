import os
import requests
from dotenv import load_dotenv
from io import BytesIO
import base64

load_dotenv()

MURF_API_KEY = os.getenv("MURF_API_KEY")
MURF_TTS_URL = "https://api.murf.ai/v1/speech/generate"

def generate_murf_audio(text, voice_id="en-US-natalie"):
    if not MURF_API_KEY:
        raise ValueError("❌ MURF_API_KEY not set in .env")

    headers = {
        "accept": "application/json",
        "api-key": MURF_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "voiceId": voice_id,
        "text": text,
        "format": "MP3",
        "sampleRate": "48000"
    }

    response = requests.post(MURF_TTS_URL, json=payload, headers=headers)
    response.raise_for_status()
    resp_json = response.json()

    audio_url = resp_json.get("audioFile", {}).get("url") or resp_json.get("audioFileUrl")
    if not audio_url:
        raise Exception("❌ Audio URL not found in Murf response")

    audio_resp = requests.get(audio_url)
    audio_resp.raise_for_status()
    return base64.b64encode(audio_resp.content).decode("utf-8")
