from pydantic import BaseModel
from typing import Optional
from enum import Enum

class Role(str, Enum):
    user = "user"
    system = "system"

class ChatMessage(BaseModel):
    role: Role
    content: str

class LLMResult(BaseModel):
    response: str
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    processing_time: float

class TranscriptionResult(BaseModel):
    text: str
    confidence: Optional[float] = None
    processing_time: float

class TTSResult(BaseModel):
    audio: bytes
    voice_id: str
    processing_time: float