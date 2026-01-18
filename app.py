from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import edge_tts
import io

app = FastAPI()

@app.post("/tts")
async def tts(payload: dict):
    text = payload.get("text")
    voice = payload.get("voice", "en-US-GuyNeural")
    rate = payload.get("rate", "+0%")
    pitch = payload.get("pitch", "+0%")

    if not text:
        return {"error": "Text is required"}

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        pitch=pitch
    )

    audio_stream = io.BytesIO()

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_stream.write(chunk["data"])

    audio_stream.seek(0)
    return StreamingResponse(audio_stream, media_type="audio/mpeg")
