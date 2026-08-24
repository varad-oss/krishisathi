import re

with open("backend/routers/advisory.py", "r") as f:
    py = f.read()

new_endpoint = """
from pydantic import BaseModel
class TranscribeRequest(BaseModel):
    audio_base64: str
    language: str = 'en'

@router.post("/transcribe")
async def transcribe_audio(request: TranscribeRequest):
    try:
        audio_bytes = base64.b64decode(request.audio_base64)
        mime_type = get_audio_mime_type(audio_bytes)
        
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
        
        response = client.models.generate_content(
            model='gemini-flash-lite-latest',
            contents=[
                audio_part, 
                "Transcribe the audio exactly in the original language. Return only the transcribed text, nothing else."
            ]
        )
        
        transcribed_text = response.text.strip()
        return {"text": transcribed_text}
    except Exception as e:
        logger.error(f"Error in transcribe_audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))
"""

# insert before the first @router.post
py = py.replace('@router.post("", response_model=AdvisoryResponse)', new_endpoint + '\n@router.post("", response_model=AdvisoryResponse)')

with open("backend/routers/advisory.py", "w") as f:
    f.write(py)
