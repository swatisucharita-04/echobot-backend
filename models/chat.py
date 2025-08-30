# chat.py
from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from uuid import uuid4
from pathlib import Path
from services.stt import stt_service
from services.tts import tts_service
from services.llm import llm_service

router = APIRouter()

# Local chat history dictionary
chat_histories = {}  # session_id -> list of messages

# Response model
class ChatResponse(BaseModel):
    transcript: str
    response: str
    audio_url: str = None

# Ensure audio folder exists
Path("static/generated_audio").mkdir(exist_ok=True)

@router.post("/agent/chat/{session_id}", response_model=ChatResponse)
async def chat_with_agent(session_id: str, file: UploadFile = File(...)):
    """Handle voice query → STT → LLM → TTS → return response and audio URL."""
    # -------------------
    # 1️⃣ Read and transcribe audio
    # -------------------
    try:
        audio_bytes = await file.read()
        transcript_result = await stt_service.transcribe(audio_bytes)
        transcript = transcript_result.text if transcript_result.text else "(No speech detected)"
    except Exception as e:
        transcript = "(STT failed)"
        print(f"STT Error: {e}")

    # -------------------
    # 2️⃣ Update chat history
    # -------------------
    history = chat_histories.get(session_id, [])
    history.append({"role": "user", "content": transcript})

    # -------------------
    # 3️⃣ Generate AI response
    # -------------------
    try:
        # Flatten chat history for context
        context = []
        for msg in history:
            role = msg["role"]
            content = msg["content"]
            context.append(f"{role.capitalize()}: {content}")
        context_str = "\n".join(context)

        llm_result = await llm_service.generate_response(context_str)
        ai_response = llm_result.response
    except Exception as e:
        ai_response = "(LLM failed)"
        print(f"LLM Error: {e}")

    history.append({"role": "assistant", "content": ai_response})
    chat_histories[session_id] = history

    # -------------------
    # 4️⃣ Convert AI response to TTS
    # -------------------
    try:
        tts_result = await tts_service.synthesize(ai_response)
        filename = Path("static/generated_audio") / f"{uuid4().hex}.wav"
        with open(filename, "wb") as f:
            f.write(tts_result.audio)
        audio_url = f"/static/generated_audio/{filename.name}"
    except Exception as e:
        audio_url = None
        print(f"TTS Error: {e}")

    # -------------------
    # 5️⃣ Return final response
    # -------------------
    return ChatResponse(
        transcript=transcript,
        response=ai_response,
        audio_url=audio_url
    )
