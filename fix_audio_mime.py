with open("backend/routers/advisory.py", "r") as f:
    content = f.read()

replacement = """def get_audio_mime_type(audio_bytes: bytes) -> str:
    if audio_bytes.startswith(b'RIFF'):
        return 'audio/wav'
    elif audio_bytes.startswith(b'\\x1A\\x45\\xdf\\xa3'):
        return 'audio/webm'
    elif audio_bytes.startswith(b'OggS'):
        return 'audio/ogg'
    elif audio_bytes.startswith(b'ID3') or audio_bytes.startswith(b'\\xff\\xfb') or audio_bytes.startswith(b'\\xff\\xf3') or audio_bytes.startswith(b'\\xff\\xf2'):
        return 'audio/mp3'
    else:
        raise HTTPException(status_code=415, detail='Unsupported audio format')"""

start_idx = content.find("def get_audio_mime_type")
end_idx = content.find("        return 'audio/mp3'", start_idx) + len("        return 'audio/mp3'")

new_content = content[:start_idx] + replacement + content[end_idx:]

with open("backend/routers/advisory.py", "w") as f:
    f.write(new_content)
