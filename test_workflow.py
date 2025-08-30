import logging
from services import llm, tts, stt
from pathlib import Path
from playsound import playsound
import os

logging.basicConfig(level=logging.INFO)

# 1️⃣ Test LLM
print("🔹 Testing LLM...")
prompt = "Hello! Can you give me a short motivational quote?"
try:
    reply = llm.get_llm_response(prompt)
    print("✅ LLM Reply:", reply)
except Exception as e:
    print("❌ Error getting LLM response:", e)
    reply = "I'm sorry, I encountered an error."

# 2️⃣ Test TTS (streaming)
print("\n🔹 Testing TTS (streaming)...")
output_file = "full_workflow_tts.wav"
try:
    audio_bytes = tts.speak(reply, output_file=output_file)
    audio_path = Path("uploads") / output_file
    print(f"✅ TTS generated: {len(audio_bytes)} bytes, saved to {audio_path}")

    # Play the generated TTS audio
    if audio_path.exists():
        print("🔊 Playing TTS audio...")
        playsound(str(audio_path))
        print("✅ TTS playback completed.")
    else:
        print("❌ Audio file not found for playback.")

except Exception as e:
    print("❌ Error generating TTS:", e)

# 3️⃣ Fetch available voices (optional)
print("\n🔹 Fetching available voices...")
try:
    voices = tts.get_available_voices()
    print(f"✅ Number of voices fetched: {len(voices)}")
except Exception as e:
    print("❌ Error fetching voices:", e)

# 4️⃣ Test STT streaming (optional)
print("\n🔹 Testing STT (streaming)...")
try:
    transcriber = stt.AssemblyAIStreamingTranscriber(
        on_partial_callback=lambda text: print(f"Partial STT: {text}"),
        on_final_callback=lambda text: print(f"Final STT: {text}")
    )

    # Test with previously generated TTS audio
    test_audio_file = Path("uploads") / output_file
    if test_audio_file.exists():
        with open(test_audio_file, "rb") as f:
            chunk = f.read(3200)  # small chunk
            while chunk:
                transcriber.stream_audio(chunk)
                chunk = f.read(3200)
    else:
        print("❌ No audio file found for STT test.")

    transcriber.close()
    print("✅ STT test completed.")

except Exception as e:
    print("❌ STT Error:", e)
