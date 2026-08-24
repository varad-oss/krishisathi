with open("backend/services/agent_service.py", "r") as f:
    text = f.read()
text = text.replace("\\ntry:\\n            logger.info", "\\n        try:\\n            logger.info")
with open("backend/services/agent_service.py", "w") as f:
    f.write(text)

with open("backend/services/gemini_service.py", "r") as f:
    text = f.read()
text = text.replace("    def generate_advisory(self, query: str, context: dict, image_base64: str = None) -> str:", "    def generate_advisory(self, query: str, context: dict, image_base64: str = None) -> str:")
with open("backend/services/gemini_service.py", "w") as f:
    f.write(text)
