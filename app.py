from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import edge_tts
import io

app = FastAPI()

@app.post("/tts")
async def tts(payload: dict):
    try:
        text = payload.get("text")
        voice = payload.get("voice", "en-US-GuyNeural")
        rate = payload.get("rate", "+0%")
        pitch = payload.get("pitch", "+0%")

        if not text or not isinstance(text, str):
            raise HTTPException(status_code=400, detail="Text is required")

        # Safety: limit extremely long payloads (Edge TTS is flaky beyond this)
        if len(text) > 6000:
            raise HTTPException(status_code=400, detail="Text too long")

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

        return StreamingResponse(
            audio_stream,
            media_type="audio/mpeg"
        )

    except Exception as e:
        print("TTS ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
