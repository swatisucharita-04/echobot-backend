# murfconfig.py
import os
import requests
from dotenv import load_dotenv
from io import BytesIO

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

    try:
        # Step 1: Generate the audio
        response = requests.post(MURF_TTS_URL, json=payload, headers=headers)
        response.raise_for_status()
        resp_json = response.json()

        # Step 2: Extract the audio file URL
        audio_url = None
        if "audioFile" in resp_json and "url" in resp_json["audioFile"]:
            audio_url = resp_json["audioFile"]["url"]
        elif "audioFileUrl" in resp_json:
            audio_url = resp_json["audioFileUrl"]

        if not audio_url:
            raise Exception("❌ Audio URL not found in Murf response")

        # Step 3: Download the MP3 file
        audio_resp = requests.get(audio_url)
        audio_resp.raise_for_status()

        return BytesIO(audio_resp.content)  # Return audio in memory for streaming

    except requests.RequestException as e:
        raise Exception(f"❌ Murf API request failed: {e}")
