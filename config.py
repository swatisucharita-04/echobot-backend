import os
from dotenv import load_dotenv
import assemblyai as aai
import google.generativeai as genai
import logging

# Load environment variables
load_dotenv()

# API Keys
MURF_API_KEY = os.getenv("MURF_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure APIs
if ASSEMBLYAI_API_KEY:
    aai.settings.api_key = ASSEMBLYAI_API_KEY
else:
    logging.warning("⚠️ ASSEMBLYAI_API_KEY not found in environment!")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logging.warning("⚠️ GEMINI_API_KEY not found in environment!")

if not MURF_API_KEY:
    logging.warning("⚠️ MURF_API_KEY not found in environment!")

# Server settings
HOST = "127.0.0.1"
PORT = 8000
