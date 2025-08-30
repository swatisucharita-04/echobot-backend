# app.py

import json
import re
import base64
import asyncio
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from services import stt, llm, tts, skills  # include skills

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def home(request: Request):
    """Serve main HTML page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logging.info("WebSocket client connected.")

    chat_history = []
    transcript_queue = asyncio.Queue()
    loop = asyncio.get_event_loop()

    async def process_transcripts():
        while True:
            text = await transcript_queue.get()
            if text is None:
                break

            logging.info(f"Processing transcript: {text}")
            try:
                await websocket.send_json({"type": "final", "text": text})
            except RuntimeError:
                logging.info("WebSocket closed, stopping transcript processing.")
                break

            user_lower = text.strip().lower()
            full_response = ""

            # ---------------- SKILL HANDLERS ----------------
            if "weather in " in user_lower:
                city = text.lower().split("weather in ")[-1].strip()
                full_response = skills.get_weather(city)

            elif "weather" in user_lower:
                full_response = skills.get_weather("Bengaluru")

            elif user_lower.startswith("in "):
                city = text[3:].strip()
                full_response = skills.get_weather(city)

            elif "search" in user_lower:
                query = text.replace("search", "").strip()
                full_response = skills.web_search(query)

            elif "news" in user_lower:
                topic_match = re.search(r'news about (.+)', user_lower)
                topic = topic_match.group(1) if topic_match else None
                full_response = skills.get_news(topic)

            else:
                # Fallback to LLM if no skill matched
                try:
                    full_response, updated_history = llm.get_llm_response(text, chat_history)
                    chat_history.clear()
                    chat_history.extend(updated_history)
                except Exception as e:
                    logging.error(f"Error in LLM pipeline: {e}")
                    full_response = "❌ Sorry, I had an error."

            # --- Send assistant response ---
            try:
                await websocket.send_json({"type": "assistant", "text": full_response})
            except RuntimeError:
                logging.info("WebSocket closed while sending assistant response.")
                break

            # --- Stream audio sentence by sentence ---
            sentences = re.split(r'(?<=[.?!])\s+', full_response.strip())
            for sentence in sentences:
                if sentence.strip():
                    audio_bytes = await loop.run_in_executor(None, tts.speak, sentence.strip())
                    if audio_bytes:
                        b64_audio = base64.b64encode(audio_bytes).decode("utf-8")
                        try:
                            await websocket.send_json({"type": "audio", "b64": b64_audio})
                        except RuntimeError:
                            logging.info("WebSocket closed while sending audio chunk.")
                            break

    consumer_task = asyncio.create_task(process_transcripts())

    def on_final_transcript(text: str):
        asyncio.run_coroutine_threadsafe(transcript_queue.put(text), loop)

    transcriber = stt.AssemblyAIStreamingTranscriber(on_final_callback=on_final_transcript)

    try:
        while True:
            message = await websocket.receive()

            if "bytes" in message:
                transcriber.stream_audio(message["bytes"])

            elif "text" in message:
                data = json.loads(message["text"])
                msg_type = data.get("type")

                if msg_type == "persona":
                    logging.info(f"Persona switched to: {data.get('persona')}")

                elif msg_type == "user_message":
                    user_text = data.get("text", "")
                    await transcript_queue.put(user_text)

    except WebSocketDisconnect:
        logging.info("WebSocket client disconnected.")

    finally:
        await transcript_queue.put(None)
        if not consumer_task.done():
            consumer_task.cancel()
            try:
                await consumer_task
            except asyncio.CancelledError:
                pass
        transcriber.close()
        logging.info("Transcription resources released.")


if __name__ == "__main__":
    import uvicorn
    print("Starting server at http://127.0.0.1:8000")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
