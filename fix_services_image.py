import re

with open("backend/routers/advisory.py", "r") as f:
    py = f.read()
py = py.replace('advisory_en = agent_service.process_advisory(query_en, context)', 'advisory_en = agent_service.process_advisory(query_en, context, image_base64=request.image_base64)')
py = py.replace('advisory_en = gemini_service.generate_advisory(query_en, context)', 'advisory_en = gemini_service.generate_advisory(query_en, context, image_base64=request.image_base64)')
with open("backend/routers/advisory.py", "w") as f:
    f.write(py)


with open("backend/services/agent_service.py", "r") as f:
    py = f.read()
py = py.replace('def process_advisory(self, query: str, context: dict) -> str:', 'def process_advisory(self, query: str, context: dict, image_base64: str = None) -> str:')

new_agent_call = """
        contents = [prompt]
        if image_base64:
            import base64
            from google.genai import types
            img_bytes = base64.b64decode(image_base64)
            img_part = types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
            contents.append(img_part)
            
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=contents,
"""
py = re.sub(r'try:\s*response = self\.client\.models\.generate_content\(\s*model=[\'"]gemini-2\.5-flash[\'"],\s*contents=\[prompt\],', new_agent_call.strip(), py, flags=re.DOTALL)
with open("backend/services/agent_service.py", "w") as f:
    f.write(py)


with open("backend/services/gemini_service.py", "r") as f:
    py = f.read()
py = py.replace('def generate_advisory(self, query: str, context: dict) -> str:', 'def generate_advisory(self, query: str, context: dict, image_base64: str = None) -> str:')

new_gemini_call = """
        try:
            contents = [prompt]
            if image_base64:
                import base64
                from google.genai import types
                img_bytes = base64.b64decode(image_base64)
                img_part = types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
                contents.append(img_part)
                
            response = self.client.models.generate_content(
                model='gemini-flash-lite-latest',
                contents=contents
            )
"""
py = re.sub(r'try:\s*response = self\.client\.models\.generate_content\(\s*model=[\'"]gemini-flash-lite-latest[\'"],\s*contents=\[prompt\]\s*\)', new_gemini_call.strip(), py, flags=re.DOTALL)
with open("backend/services/gemini_service.py", "w") as f:
    f.write(py)

