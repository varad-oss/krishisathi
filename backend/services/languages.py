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


# Unicode blocks of each language's script (Marathi and Hindi share Devanagari).
SCRIPT_BLOCKS = {
    "hi": (0x0900, 0x097F), "mr": (0x0900, 0x097F), "bn": (0x0980, 0x09FF), "pa": (0x0A00, 0x0A7F),
    "gu": (0x0A80, 0x0AFF), "ta": (0x0B80, 0x0BFF), "te": (0x0C00, 0x0C7F), "kn": (0x0C80, 0x0CFF),
    "ml": (0x0D00, 0x0D7F),
    "en": (0x0041, 0x024F),  # Latin letters, so a Hindi answer to an English request is detected and retried
}


def language_rule(code: str) -> str:
    """Prompt sentence pinning the reply language. "Native script" is only said for Indic languages: for English
    the model otherwise tends to read it as Devanagari and answer Indian farmers in Hindi."""
    if code not in LANGUAGES or code == "en":
        return ("Write in English only. Do not reply in Hindi or any other language, even if the farmer is in India "
                "or the question uses another language.")
    return (f"Write in {language_name(code)} only, in its native script (no romanization). Do not switch to English "
            "or any other language, even when the question is written in another language.")


def script_ratio(text: str, code: str) -> float:
    """Share of letters written in the language's script (Latin for English); 1.0 for text without letters."""
    block = SCRIPT_BLOCKS.get(code)
    # Combining vowel signs are not str.isalpha(), so count every code point in the block as a letter.
    letters = [c for c in text if c.isalpha() or (block and block[0] <= ord(c) <= block[1])]
    if not block or not letters:
        return 1.0
    return sum(block[0] <= ord(c) <= block[1] for c in letters) / len(letters)


def is_in_language(text: str, code: str, minimum: float = 0.6) -> bool:
    """True when the text is mostly in the native script. Technical terms (pH, NPK) may stay in Latin."""
    return script_ratio(text, code) >= minimum
