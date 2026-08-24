import re

with open("frontend/src/lib/speech.ts", "r") as f:
    ts = f.read()

replacement = """
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
"""

ts += "\n\n" + replacement

with open("frontend/src/lib/speech.ts", "w") as f:
    f.write(ts)
