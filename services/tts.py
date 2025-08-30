# services/tts.py
import logging
from pathlib import Path
from typing import List, Dict, Any
from config import MURF_API_KEY
from murf import Murf
import requests

# Logging setup
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Ensure uploads folder exists
UPLOADS_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

# Murf streaming TTS
def speak(text: str, voice_id: str = "en-US-natalie", output_file: str = "stream_output.wav") -> bytes:
    """
    Convert text to speech using Murf streaming API.
    Saves audio in uploads folder and returns bytes.
    """
    if not MURF_API_KEY:
        raise Exception("MURF_API_KEY not configured.")

    client = Murf(api_key=MURF_API_KEY)
    file_path = UPLOADS_DIR / output_file
    # Start with a clean file
    open(file_path, "wb").close()

    audio_bytes = b""
    try:
        res = client.text_to_speech.stream(text=text, voice_id=voice_id, style="Conversational")
        for chunk in res:
            audio_bytes += chunk
            with open(file_path, "ab") as f:
                f.write(chunk)
    except Exception as e:
        logger.error(f"Error generating TTS: {e}")
        raise e

    logger.info(f"TTS saved to {file_path}")
    return audio_bytes


# Murf synchronous TTS (returns URL)
def convert_text_to_speech(text: str, voice_id: str = "en-US-natalie") -> str:
    """
    Converts text to speech using Murf synchronous API.
    Returns URL or file reference from Murf.
    """
    if not MURF_API_KEY:
        raise Exception("MURF_API_KEY not configured.")

    headers = {"Content-Type": "application/json", "api-key": MURF_API_KEY}
    payload = {"text": text, "voiceId": voice_id, "format": "MP3", "volume": "100%"}

    try:
        response = requests.post("https://api.murf.ai/v1/speech/generate", json=payload, headers=headers)
        response.raise_for_status()
        return response.json().get("audioFile")
    except Exception as e:
        logger.error(f"Error in convert_text_to_speech: {e}")
        raise e


# Get available voices from Murf
def get_available_voices() -> List[Dict[str, Any]]:
    """
    Fetches the list of available voices from Murf AI.
    Returns a list of voice dictionaries.
    """
    if not MURF_API_KEY:
        raise Exception("MURF_API_KEY not configured.")

    headers = {"Accept": "application/json", "api-key": MURF_API_KEY}
    try:
        response = requests.get("https://api.murf.ai/v1/speech/voices", headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching voices: {e}")
        return []
