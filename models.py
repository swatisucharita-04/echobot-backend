from pydantic import BaseModel

class ChatRequest(BaseModel):
    session_id: str

class TTSRequest(BaseModel):
    text: str
    voice: str = "en-US-natalie"

class ChatResponse(BaseModel):
    transcript: str
    response: str
    audio_url: str | None = None
