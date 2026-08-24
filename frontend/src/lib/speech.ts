// BCP47 language map for Web Speech API
// This is the single source of truth for all speech-related language codes.
// Browser SpeechRecognition and SpeechSynthesis both use BCP47 tags.
export const LANG_TO_BCP47: Record<string, string> = {
  en: 'en-IN',
  hi: 'hi-IN',
  mr: 'mr-IN',
  ta: 'ta-IN',
  te: 'te-IN',
  bn: 'bn-IN',
  kn: 'kn-IN',
  gu: 'gu-IN',
  pa: 'pa-IN',
  ml: 'ml-IN',
};

export function getBCP47(langCode: string): string {
  return LANG_TO_BCP47[langCode] || 'en-IN';
}

/**
 * Speak text aloud using the browser's SpeechSynthesis API.
 * Uses the correct BCP47 tag for the given language code.
 */
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

/**
 * Check if SpeechRecognition is available in the current browser.
 */
export function isSpeechRecognitionSupported(): boolean {
  if (typeof window === 'undefined') return false;
  return !!((window as any).SpeechRecognition || (window as any).webkitSpeechRecognition);
}

/**
 * Create a SpeechRecognition instance configured for the given language.
 * Returns null if not supported.
 */
export function createSpeechRecognition(langCode: string): any | null {
  if (!isSpeechRecognitionSupported()) return null;
  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
  const recognition = new SpeechRecognition();
  recognition.lang = getBCP47(langCode);
  recognition.interimResults = true;
  recognition.continuous = false;
  recognition.maxAlternatives = 1;
  return recognition;
}



let mediaRecorder: MediaRecorder | null = null;
let audioChunks: Blob[] = [];

export async function startRecording(langCode: string, onResult: (text: string) => void, onError: (err: any) => void, onEnd: () => void) {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data);
      }
    };

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
      const reader = new FileReader();
      reader.readAsDataURL(audioBlob);
      reader.onloadend = async () => {
        const base64Audio = (reader.result as string).split(',')[1];
        
        try {
          const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
          const res = await fetch(`${API_BASE}/api/advisory/transcribe`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ audio_base64: base64Audio, language: langCode })
          });
          const data = await res.json();
          if (data.text) {
            onResult(data.text);
          }
        } catch (e) {
          console.error("Transcription failed", e);
          onError(e);
        } finally {
          onEnd();
        }
      };
    };

    mediaRecorder.start();
  } catch (err) {
    console.error("Microphone access denied", err);
    onError(err);
    onEnd();
  }
}

export function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
    mediaRecorder.stream.getTracks().forEach(track => track.stop());
  }
}
