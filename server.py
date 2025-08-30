import asyncio
import websockets

async def send_audio():
    uri = "ws://localhost:8000"
    async with websockets.connect(uri) as ws:
        # Read a small PCM16 audio file
        with open("test_audio.raw", "rb") as f:
            chunk = f.read(3200)  # small chunks (~0.1s of audio)
            while chunk:
                await ws.send(chunk)
                chunk = f.read(3200)
        
        print("Audio sent. Waiting for transcript...")
        # Keep the connection open to receive messages
        while True:
            try:
                msg = await ws.recv()
                print("Received:", msg)
            except:
                break

asyncio.run(send_audio())
