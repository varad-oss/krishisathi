import re

with open("backend/services/gemini_service.py", "r") as f:
    content = f.read()

content = content.replace(
    "def _call(self, prompt, image_part=None, model=None, response_mime_type=None, temperature=0.3, error_message=\"AI model is temporarily unavailable.\"):",
    "def _call(self, prompt, image_part=None, model=None, response_mime_type=None, temperature=0.3, error_message=\"AI model is temporarily unavailable.\", system_instruction=None):"
)

content = content.replace(
    "            temperature=temperature",
    "            temperature=temperature,\n            system_instruction=system_instruction"
)

with open("backend/services/gemini_service.py", "w") as f:
    f.write(content)
