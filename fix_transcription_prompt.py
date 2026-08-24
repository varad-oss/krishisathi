import re

with open("backend/routers/advisory.py", "r") as f:
    py = f.read()

old_prompt = '"Transcribe the audio exactly in the original language. Return only the transcribed text, nothing else."'
new_prompt = 'f"Transcribe the audio exactly. You MUST output the text in the native script of the language code \'{request.language}\' (e.g. use Devanagari for hi/mr, Gujarati script for gu, Tamil script for ta, etc). Do NOT romanize or use English letters unless the user actually spoke English. Return only the transcribed text, nothing else."'

py = py.replace(old_prompt, new_prompt)

with open("backend/routers/advisory.py", "w") as f:
    f.write(py)
