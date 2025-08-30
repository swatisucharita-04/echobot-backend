# services/stt.py
import os
import logging
from dotenv import load_dotenv
import assemblyai as aai
from assemblyai.streaming.v3 import (
    StreamingClient,
    StreamingClientOptions,
    StreamingParameters,
    StreamingSessionParameters,
    StreamingEvents,
    BeginEvent,
    TurnEvent,
    TerminationEvent,
    StreamingError,
)

# Load environment variables
load_dotenv()

# Logging setup
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# AssemblyAI API key
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
if not ASSEMBLYAI_API_KEY:
    raise Exception("⚠️ ASSEMBLYAI_API_KEY not found in environment!")

aai.settings.api_key = ASSEMBLYAI_API_KEY

# ----------------- Internal Callbacks -----------------
def _on_begin(client: StreamingClient, event: BeginEvent):
    logger.info(f"🎤 AAI streaming session started: {event.id}")

def _on_termination(client: StreamingClient, event: TerminationEvent):
    logger.info(f"🛑 AAI session terminated after {event.audio_duration_seconds}s")

def _on_error(client: StreamingClient, error: StreamingError):
    logger.error(f"❌ AAI streaming error: {error}")

# ----------------- Streaming Transcriber -----------------
class AssemblyAIStreamingTranscriber:
    """
    AssemblyAI streaming wrapper.
    Callbacks:
      - on_partial_callback(text): interim transcript
      - on_final_callback(text): final transcript per turn
    """

    def __init__(self, sample_rate: int = 16000, on_partial_callback=None, on_final_callback=None):
        self.on_partial_callback = on_partial_callback or (lambda text: None)
        self.on_final_callback = on_final_callback or (lambda text: None)

        self.client = StreamingClient(
            StreamingClientOptions(api_key=ASSEMBLYAI_API_KEY, api_host="streaming.assemblyai.com")
        )

        # Register events
        self.client.on(StreamingEvents.Begin, _on_begin)
        self.client.on(StreamingEvents.Error, _on_error)
        self.client.on(StreamingEvents.Termination, _on_termination)
        self.client.on(StreamingEvents.Turn, self._on_turn)

        # Connect streaming session
        self.client.connect(StreamingParameters(sample_rate=sample_rate, format_turns=False))

    def _on_turn(self, client: StreamingClient, event: TurnEvent):
        text = (event.transcript or "").strip()
        if not text:
            return

        if event.end_of_turn:
            self.on_final_callback(text)
            if not event.turn_is_formatted:
                try:
                    client.set_params(StreamingSessionParameters(format_turns=True))
                except Exception as e:
                    logger.error(f"Failed to set turn formatting: {e}")
        else:
            self.on_partial_callback(text)

    def stream_audio(self, audio_chunk: bytes):
        """Send a chunk of audio to the streaming API"""
        try:
            self.client.stream(audio_chunk)
        except Exception as e:
            logger.error(f"Error streaming audio chunk: {e}")

    def close(self):
        """Safely disconnect streaming client"""
        try:
            self.client.disconnect(terminate=True)
        except Exception as e:
            logger.warning(f"Disconnect error (likely already closed): {e}")

# ----------------- Full-file Transcription -----------------
def transcribe_audio_file(file_path: str) -> str:
    """
    Transcribe a complete audio file using AssemblyAI API.
    Returns the final transcript text.
    """
    transcriber = aai.Transcriber()
    with open(file_path, "rb") as f:
        transcript = transcriber.transcribe(f)

    if transcript.status == aai.TranscriptStatus.error or not transcript.text:
        raise Exception(f"Transcription failed: {transcript.error or 'No speech detected'}")

    return transcript.text

# ----------------- Test Runner -----------------
if __name__ == "__main__":
    print("🔹 Testing AssemblyAI Streaming Transcriber…")
    transcriber = AssemblyAIStreamingTranscriber(
        on_partial_callback=lambda text: print(f"[Partial] {text}"),
        on_final_callback=lambda text: print(f"[Final] {text}")
    )
    print("✅ Streaming transcriber initialized successfully!")
    transcriber.close()
