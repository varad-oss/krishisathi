import re

with open("frontend/src/lib/speech.ts", "r") as f:
    ts = f.read()

replacement = """
let currentAudio: HTMLAudioElement | null = null;

export function speakText(text: string, langCode: string): void {
  if (typeof window === 'undefined') return;
  
  stopSpeaking(); // Stop any ongoing speech

  // 1. Check if browser has a native voice for this language
  let hasVoice = false;
  if ('speechSynthesis' in window) {
    const voices = window.speechSynthesis.getVoices();
    const targetLang = getBCP47(langCode).toLowerCase();
    hasVoice = voices.some(v => v.lang.toLowerCase().startsWith(targetLang) || v.lang.toLowerCase().startsWith(langCode.toLowerCase()));
  }

  // 2. If native voice exists, use it
  if (hasVoice && 'speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = getBCP47(langCode);
    utterance.rate = 0.9;
    window.speechSynthesis.speak(utterance);
    return;
  }

  // 3. Fallback to Server-Side gTTS API
  // gTTS supports all our 10 languages
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const url = `${API_BASE}/api/advisory/tts?text=${encodeURIComponent(text)}&lang=${langCode}`;
  
  currentAudio = new Audio(url);
  currentAudio.play().catch(e => console.error("Audio playback failed:", e));
}

export function stopSpeaking(): void {
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
  if (currentAudio) {
    currentAudio.pause();
    currentAudio.currentTime = 0;
    currentAudio = null;
  }
}
"""

ts = re.sub(
r"""export function speakText.*?export function stopSpeaking\(\): void \{.*?\}""",
replacement.strip(), ts, flags=re.DOTALL
)

with open("frontend/src/lib/speech.ts", "w") as f:
    f.write(ts)
