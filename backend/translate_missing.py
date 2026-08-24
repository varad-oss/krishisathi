import json
import asyncio
from google import genai
from google.genai import types
from config import settings

missing_strings = [
    "Wheat rust outbreak detected in Ludhiana district — recommend preventive spraying in adjacent UP wheat belt",
    "Fall Armyworm migration pattern moving south from Vidarbha",
    "INFO", "HIGH", "MODERATE", "LOW", "No active cross-state signals."
]

languages = {
    'hi': 'Hindi', 'mr': 'Marathi', 'ta': 'Tamil', 'te': 'Telugu',
    'bn': 'Bengali', 'kn': 'Kannada', 'gu': 'Gujarati', 'pa': 'Punjabi', 'ml': 'Malayalam'
}

with open("../frontend/src/lib/translations.ts", "r", encoding="utf-8") as f:
    ts_content = f.read()
    
json_start = ts_content.find("{")
json_end = ts_content.find("};\n\nexport function t")
existing_dict = json.loads(ts_content[json_start:json_end+1])

async def generate():
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
    for s in missing_strings:
        if s not in existing_dict['en']:
            existing_dict['en'][s] = s
            
    for code, lang_name in languages.items():
        missing = [s for s in missing_strings if s not in existing_dict.get(code, {})]
        if not missing:
            continue
            
        print(f"Translating {len(missing)} strings for {lang_name}...")
        prompt = f"Translate the following JSON object values to {lang_name}. Output strictly valid JSON with the exact same keys as the input.\n\nInput JSON:\n{json.dumps({s: s for s in missing}, indent=2)}"
        
        response = client.models.generate_content(
            model='gemini-flash-lite-latest',
            contents=[prompt],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        res_dict = json.loads(response.text)
        for k, v in res_dict.items():
            existing_dict[code][k] = v

    new_ts_content = f"export const UI_TRANSLATIONS: Record<string, Record<string, string>> = {json.dumps(existing_dict, indent=2, ensure_ascii=False)};\n\n"
    new_ts_content += """export function t(key: string, lang: string = 'en'): string {
  if (UI_TRANSLATIONS[lang] && UI_TRANSLATIONS[lang][key]) {
    return UI_TRANSLATIONS[lang][key];
  }
  return key; // Fallback to English
}
"""
    with open("../frontend/src/lib/translations.ts", "w", encoding="utf-8") as f:
        f.write(new_ts_content)
    print("translations.ts successfully updated with MISSING mock strings!")

asyncio.run(generate())
