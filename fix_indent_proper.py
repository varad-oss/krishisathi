with open("backend/services/agent_service.py", "r") as f:
    text = f.read()

text = text.replace("\ntry:\n            logger.info", "\n        try:\n            logger.info")

with open("backend/services/agent_service.py", "w") as f:
    f.write(text)
