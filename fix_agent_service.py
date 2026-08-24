import re

with open("backend/services/agent_service.py", "r") as f:
    py = f.read()

new_code = """
        try:
            logger.info("Calling Gemini Agent...")
            contents = [prompt]
            if image_base64:
                import base64
                from google.genai import types
                img_bytes = base64.b64decode(image_base64)
                img_part = types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
                contents.append(img_part)
                
            response = self.client.models.generate_content(
                model=model,
                contents=contents,
"""

py = re.sub(
    r'        try:\n            logger\.info\("Calling Gemini Agent\.\.\."\)\n            response = self\.client\.models\.generate_content\(\n                model=model,\n                contents=prompt,',
    new_code.strip(),
    py
)

with open("backend/services/agent_service.py", "w") as f:
    f.write(py)
