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
export function speakText(text: string, langCode: string): void {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = getBCP47(langCode);
  utterance.rate = 0.9;
  window.speechSynthesis.speak(utterance);
}

export function stopSpeaking(): void {
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    window.speechSynthesis.cancel();
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
