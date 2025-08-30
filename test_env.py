from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env")  # Explicit path is important

print("ASSEMBLYAI_API_KEY:", os.getenv("ASSEMBLYAI_API_KEY"))
print("GEMINI_API_KEY:", os.getenv("GEMINI_API_KEY"))
print("MURF_API_KEY:", os.getenv("MURF_API_KEY"))
