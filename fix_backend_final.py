import re

# 1. Fix gemini_service.py
with open("backend/services/gemini_service.py", "r") as f:
    gem = f.read()

new_generate_advisory = """    def generate_advisory(self, query: str, context: dict, image_base64: str = None) -> str:
        if not self.client:
            return "Based on mock data, ensure proper irrigation and apply balanced NPK fertilizers."
            
        try:
            prompt = f\"\"\"
            You are an expert agricultural advisor. Provide detailed, actionable advice for the following query.
            Query: {query}
            Context (Weather, soil, etc.): {context}
            
            Provide the advisory clearly and concisely.
            \"\"\"
            
            image_part = None
            if image_base64:
                import base64
                from google.genai import types
                img_bytes = base64.b64decode(image_base64)
                image_part = types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
            
            response = self._call_with_fallback(
                prompt=prompt, 
                image_part=image_part,
                use_pro=False, 
                temperature=0.5
            )
            return response.text
        except Exception as e:
            import traceback; traceback.print_exc()"""

gem = re.sub(
    r'    def generate_advisory\(self, query: str, context: dict, image_base64: str = None\) -> str:.*?import traceback; traceback.print_exc\(\)',
    new_generate_advisory.strip(),
    gem,
    flags=re.DOTALL
)

with open("backend/services/gemini_service.py", "w") as f:
    f.write(gem)


# 2. Fix agent_service.py syntax error
with open("backend/services/agent_service.py", "r") as f:
    agent = f.read()

# I will rewrite the entire block from `try:` to the end of the method
new_agent_call = """        try:
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
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    tools=[get_weather_tool, get_kvk_tool, get_state_config_tool],
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(
                        disable=False
                    )
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Agent processing failed: {e}")
            raise e"""

agent = re.sub(
    r'        try:\n            logger\.info\("Calling Gemini Agent\.\.\."\).*?            raise e',
    new_agent_call,
    agent,
    flags=re.DOTALL
)

with open("backend/services/agent_service.py", "w") as f:
    f.write(agent)

