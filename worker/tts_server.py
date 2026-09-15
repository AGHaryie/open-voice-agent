import io
import soundfile as sf
from fastapi import FastAPI
from fastapi.responses import Response
from kokoro import KPipeline
from pydantic import BaseModel

app = FastAPI(title="Local Kokoro TTS")
pipeline = KPipeline(lang_code="a")

class TTSRequest(BaseModel):
    input: str
    voice: str = "af_heart"
    model: str = "tts-1"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/v1/audio/speech")
def generate_speech(req: TTSRequest):
    generator = pipeline(req.input, voice=req.voice, speed=1.0)
    for _, _, audio in generator:
        out = io.BytesIO()
        sf.write(out, audio, 24000, format="WAV")
        return Response(content=out.getvalue(), media_type="audio/wav")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8880)
