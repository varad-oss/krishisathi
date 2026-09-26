'use client';

import { ApiError, transcribeAudio, ttsUrl } from './api';
import type { LanguageCode } from './types';

const BCP47: Record<LanguageCode, string> = {
  en: 'en-IN', hi: 'hi-IN', mr: 'mr-IN', ta: 'ta-IN', te: 'te-IN', bn: 'bn-IN', kn: 'kn-IN', gu: 'gu-IN', pa: 'pa-IN', ml: 'ml-IN',
};

let currentAudio: HTMLAudioElement | null = null;
let listeners: ((speaking: boolean) => void)[] = [];
const notify = (s: boolean) => listeners.forEach((l) => l(s));

export function onSpeechStateChange(listener: (speaking: boolean) => void) {
  listeners.push(listener);
  return () => {
    listeners = listeners.filter((l) => l !== listener);
  };
}

/** Uses a native voice for the language when the device has one; otherwise server-side TTS. */
export function speakText(text: string, lang: LanguageCode): void {
  if (typeof window === 'undefined' || !text.trim()) return;
  stopSpeaking();
  notify(true);
  const plain = text.replace(/[#*_`>|-]/g, ' ');

  const tag = BCP47[lang].toLowerCase();
  const voices = 'speechSynthesis' in window ? window.speechSynthesis.getVoices() : [];
  if (voices.some((v) => v.lang.toLowerCase().startsWith(tag) || v.lang.toLowerCase().startsWith(lang))) {
    const u = new SpeechSynthesisUtterance(plain);
    u.lang = BCP47[lang];
    u.rate = 0.9;
    u.onend = u.onerror = () => notify(false);
    window.speechSynthesis.speak(u);
    return;
  }

  currentAudio = new Audio(ttsUrl(plain, lang));
  currentAudio.onended = currentAudio.onerror = () => notify(false);
  currentAudio.play().catch((e) => {
    if (e?.name !== 'AbortError') notify(false);
  });
}

export function stopSpeaking(): void {
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) window.speechSynthesis.cancel();
  if (currentAudio) {
    currentAudio.pause();
    currentAudio = null;
  }
  notify(false);
}

export const recordingSupported = () =>
  typeof window !== 'undefined' && !!navigator.mediaDevices?.getUserMedia && typeof MediaRecorder !== 'undefined';

let recorder: MediaRecorder | null = null;
let audioCtx: AudioContext | null = null;
let frame: number | null = null;

function cleanup() {
  if (frame) cancelAnimationFrame(frame);
  frame = null;
  audioCtx?.close().catch(() => {});
  audioCtx = null;
}

/**
 * Records until ~2.5 s of silence (or stopRecording), then transcribes on the server.
 * Errors are passed to onError as ApiError or a DOMException (e.g. NotAllowedError).
 */
export async function startRecording(lang: LanguageCode, onResult: (text: string) => void, onError: (err: unknown) => void, onEnd: () => void) {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    recorder = new MediaRecorder(stream);
    const chunks: Blob[] = [];

    audioCtx = new AudioContext();
    const analyser = audioCtx.createAnalyser();
    analyser.minDecibels = -60;
    audioCtx.createMediaStreamSource(stream).connect(analyser);
    const data = new Uint8Array(analyser.frequencyBinCount);
    let lastSound = Date.now();
    const watch = () => {
      if (!recorder || recorder.state === 'inactive') return;
      analyser.getByteFrequencyData(data);
      if (data.some((v) => v > 10)) lastSound = Date.now();
      else if (Date.now() - lastSound > 2500) return stopRecording();
      frame = requestAnimationFrame(watch);
    };
    watch();

    recorder.ondataavailable = (e) => e.data.size > 0 && chunks.push(e.data);
    recorder.onstop = async () => {
      cleanup();
      stream.getTracks().forEach((t) => t.stop());
      try {
        const blob = new Blob(chunks, { type: recorder?.mimeType || 'audio/webm' });
        const base64 = await new Promise<string>((resolve, reject) => {
          const reader = new FileReader();
          reader.onloadend = () => resolve(String(reader.result).split(',')[1] ?? '');
          reader.onerror = () => reject(reader.error);
          reader.readAsDataURL(blob);
        });
        const { text } = await transcribeAudio(base64, lang);
        if (text) onResult(text);
        else onError(new ApiError('No speech detected', 'NO_SPEECH', 422, true));
      } catch (e) {
        onError(e);
      } finally {
        onEnd();
      }
    };
    recorder.start();
  } catch (err) {
    cleanup();
    onError(err);
    onEnd();
  }
}

export function stopRecording() {
  if (recorder && recorder.state !== 'inactive') recorder.stop();
  cleanup();
}
