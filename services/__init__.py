# services/__init__.py

# Import submodules
from .llm import get_llm_response
from .tts import speak, convert_text_to_speech, get_available_voices
from .stt import AssemblyAIStreamingTranscriber, transcribe_audio_file

# Optional: define __all__ for cleaner imports
__all__ = [
    "get_llm_response",
    "speak",
    "convert_text_to_speech",
    "get_available_voices",
    "AssemblyAIStreamingTranscriber",
    "transcribe_audio_file",
]
