with open("backend/services/gemini_service.py", "r") as f:
    text = f.read()

text = text.replace("\ndef generate_advisory(self,", "\n    def generate_advisory(self,")

with open("backend/services/gemini_service.py", "w") as f:
    f.write(text)
