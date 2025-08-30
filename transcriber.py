import asyncio
import assemblyai as aai
from assemblyai.streaming.v3 import (
    StreamingClient, StreamingClientOptions, StreamingEvents,
    TurnEvent, BeginEvent, TerminationEvent, StreamingError, StreamingParameters
)
import google.generativeai as genai

# ---------------- Keys ----------------
aai.settings.api_key = "AIzaSyCN4cFawJJBGn1qshGbvvsZ_ApsJONrsWQ"
genai.configure(api_key="AIzaSyCN4cFawJJBGn1qshGbvvsZ_ApsJONrsWQ")
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# ---------------- Transcriber ----------------
class Transcriber:
    def __init__(self, sample_rate=16000):
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

        self.client = StreamingClient(
            StreamingClientOptions(api_key=aai.settings.api_key)
        )
        self.callbacks = {"transcript": None, "ai_response": None}

        # Event handlers
        self.client.on(StreamingEvents.Begin, self.on_begin)
        self.client.on(StreamingEvents.Turn, self.on_turn)
        self.client.on(StreamingEvents.Termination, self.on_termination)
        self.client.on(StreamingEvents.Error, self.on_error)

        # Connect with turn formatting
        self.client.connect(StreamingParameters(sample_rate=sample_rate, format_turns=True))

    # ---------------- Event Handlers ----------------
    def on_begin(self, client, event: BeginEvent):
        print(f"🎤 Session started: {event.id}")

    def on_turn(self, client, event: TurnEvent):
        print(f"Transcript: {event.transcript} (end_of_turn={event.end_of_turn})")
        if event.end_of_turn and event.transcript.strip():
            # Send transcript to frontend
            if self.callbacks["transcript"]:
                asyncio.run_coroutine_threadsafe(
                    self.callbacks["transcript"](event.transcript), self.loop
                )
            # Start AI streaming reply
            if self.callbacks["ai_response"]:
                asyncio.run_coroutine_threadsafe(
                    self.start_ai_response(event.transcript), self.loop
                )

    async def start_ai_response(self, user_text: str):
        """Stream Gemini AI response"""
        try:
            response = gemini_model.generate_content(user_text, stream=True)
            async for chunk in response:
                if chunk.text:
                    await self.callbacks["ai_response"](chunk.text)
        except Exception as e:
            print("❌ Gemini streaming error:", e)

    def on_termination(self, client, event: TerminationEvent):
        print(f"🛑 Session terminated, audio duration: {event.audio_duration_seconds}s")

    def on_error(self, client, error: StreamingError):
        print("❌ Streaming Error:", error)

    # ---------------- Methods ----------------
    def stream_audio(self, audio_chunk: bytes):
        self.client.stream(audio_chunk)

    def disconnect(self):
        self.client.disconnect()
        print("❌ Streaming client disconnected")
