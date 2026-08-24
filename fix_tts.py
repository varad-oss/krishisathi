with open("backend/routers/advisory.py", "r") as f:
    text = f.read()

new_tts = """@router.get("/tts")
async def text_to_speech(text: str, lang: str = "en"):
    try:
        from fastapi import Response
        safe_lang = lang if lang in ['en', 'hi', 'mr', 'ta', 'te', 'bn', 'pt', 'ru', 'zh'] else 'en'
        tts = gTTS(text=text, lang=safe_lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        audio_data = fp.getvalue()
        return Response(content=audio_data, media_type="audio/mpeg")
    except Exception as e:"""

text = text.replace("""@router.get("/tts")
async def text_to_speech(text: str, lang: str = "en"):
    try:
        safe_lang = lang if lang in ['en', 'hi', 'mr', 'ta', 'te', 'bn', 'pt', 'ru', 'zh'] else 'en'
        tts = gTTS(text=text, lang=safe_lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return StreamingResponse(fp, media_type="audio/mpeg")
    except Exception as e:""", new_tts)

with open("backend/routers/advisory.py", "w") as f:
    f.write(text)
