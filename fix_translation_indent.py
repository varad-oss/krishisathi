import re

with open("backend/services/translation.py", "r") as f:
    py = f.read()

py = py.replace('def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:', '    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:')

with open("backend/services/translation.py", "w") as f:
    f.write(py)
