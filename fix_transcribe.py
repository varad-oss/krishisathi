import re
with open("backend/routers/advisory.py", "r") as f:
    content = f.read()

content = content.replace(
    "class TranscribeRequest(BaseModel):",
    "from pydantic import Field\nclass TranscribeRequest(BaseModel):"
).replace(
    "    audio_base64: str",
    "    audio_base64: str = Field(..., max_length=10_000_000)"
)

# While here, let's enforce size inside the base64 decoding if not already done, 
# but Pydantic will catch max_length string size first, which is great.

with open("backend/routers/advisory.py", "w") as f:
    f.write(content)
