"""Supported UI/response languages (allow-list). Codes match the frontend."""

LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
    "kn": "Kannada",
    "gu": "Gujarati",
    "pa": "Punjabi (Gurmukhi script)",
    "ml": "Malayalam",
}

LanguageCode = str


def normalize_language(code: str | None) -> str:
    return code if code in LANGUAGES else "en"


def language_name(code: str) -> str:
    return LANGUAGES.get(code, "English")
