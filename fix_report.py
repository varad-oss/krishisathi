import re

with open("backend/services/gemini_service.py", "r") as f:
    text = f.read()

text = text.replace("def generate_dashboard_report(self, data: dict) -> str:", "def generate_dashboard_report(self, data: dict, language: str = 'en') -> str:")
text = text.replace("Keep the report professional, highlighting key insights, risks, and recommendations.", "Keep the report professional, highlighting key insights, risks, and recommendations.\\n            MUST GENERATE IN LANGUAGE CODE: {language}.")

with open("backend/services/gemini_service.py", "w") as f:
    f.write(text)

with open("backend/routers/dashboard.py", "r") as f:
    text = f.read()

text = text.replace("async def get_dashboard_report():", "async def get_dashboard_report(language: str = 'en'):")
text = text.replace("report_text = gemini_service.generate_dashboard_report(report_data)", "report_text = gemini_service.generate_dashboard_report(report_data, language)")

with open("backend/routers/dashboard.py", "w") as f:
    f.write(text)
