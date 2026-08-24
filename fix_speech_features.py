import re

with open("frontend/src/lib/speech.ts", "r") as f:
    ts = f.read()

# 1. Add state tracking for speech playback
speech_state_code = """
let currentAudio: HTMLAudioElement | null = null;
let stateListeners: ((isSpeaking: boolean) => void)[] = [];

export function onSpeechStateChange(listener: (isSpeaking: boolean) => void) {
  stateListeners.push(listener);
  // Return current state immediately
  listener(isSpeaking());
  return () => { stateListeners = stateListeners.filter(l => l !== listener); };
}

function notifyStateChange(state: boolean) {
  stateListeners.forEach(l => l(state));
}

export function isSpeaking(): boolean {
  if (typeof window !== 'undefined' && 'speechSynthesis' in window && window.speechSynthesis.speaking) return true;
  if (currentAudio && !currentAudio.paused) return true;
  return false;
}
"""
ts = re.sub(r'let currentAudio: HTMLAudioElement \| null = null;', speech_state_code.strip(), ts, count=1)

# 2. Update speakText to fire events
new_speakText = """
export function speakText(text: string, langCode: string): void {
  if (typeof window === 'undefined') return;
  
  stopSpeaking(); // Stop any ongoing speech
  notifyStateChange(true);

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
    utterance.onend = () => notifyStateChange(false);
    utterance.onerror = () => notifyStateChange(false);
    window.speechSynthesis.speak(utterance);
    return;
  }

  // 3. Fallback to Server-Side gTTS API
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const url = `${API_BASE}/api/advisory/tts?text=${encodeURIComponent(text)}&lang=${langCode}`;
  
  currentAudio = new Audio(url);
  currentAudio.onended = () => notifyStateChange(false);
  currentAudio.onerror = () => notifyStateChange(false);
  currentAudio.play().catch(e => {
    console.error("Audio playback failed:", e);
    notifyStateChange(false);
  });
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
  notifyStateChange(false);
}
"""
ts = re.sub(r'export function speakText.*?export function stopSpeaking\(\): void \{.*?\}', new_speakText.strip(), ts, flags=re.DOTALL)


# 3. Update startRecording to add silence detection
new_recording = """
let mediaRecorder: MediaRecorder | null = null;
let audioChunks: Blob[] = [];
let audioContext: AudioContext | null = null;
let silenceTimer: any = null;

export async function startRecording(langCode: string, onResult: (text: string) => void, onError: (err: any) => void, onEnd: () => void) {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    // Setup silence detection
    const AudioContext = window.AudioContext || (window as any).webkitAudioContext;
    audioContext = new AudioContext();
    const source = audioContext.createMediaStreamSource(stream);
    const analyser = audioContext.createAnalyser();
    analyser.minDecibels = -60; // Silence threshold
    source.connect(analyser);
    
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    let silenceStart = Date.now();
    
    const checkSilence = () => {
      if (!mediaRecorder || mediaRecorder.state === 'inactive') return;
      analyser.getByteFrequencyData(dataArray);
      const isSpeaking = dataArray.some(val => val > 10);
      
      if (isSpeaking) {
        silenceStart = Date.now();
      } else {
        // If silent for 2.5 seconds, auto stop
        if (Date.now() - silenceStart > 2500) {
          stopRecording();
          return;
        }
      }
      silenceTimer = requestAnimationFrame(checkSilence);
    };
    checkSilence();

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data);
      }
    };

    mediaRecorder.onstop = async () => {
      if (silenceTimer) cancelAnimationFrame(silenceTimer);
      if (audioContext) {
        audioContext.close();
        audioContext = null;
      }
      
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
  if (silenceTimer) {
    cancelAnimationFrame(silenceTimer);
    silenceTimer = null;
  }
  if (audioContext) {
    audioContext.close().catch(() => {});
    audioContext = null;
  }
}
"""

ts = re.sub(r'let mediaRecorder: MediaRecorder \| null = null;.*?export function stopRecording\(\) \{.*?\}', new_recording.strip(), ts, flags=re.DOTALL)

with open("frontend/src/lib/speech.ts", "w") as f:
    f.write(ts)
