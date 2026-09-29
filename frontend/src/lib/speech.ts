'use client';

import { useCallback, useEffect, useId, useSyncExternalStore } from 'react';
import { ApiError, getSpeechVoices, synthesizeSpeech, transcribeAudio } from './api';
import { BlockedError, createSpeechController, isHighQualityVoice, pickVoice, type Player, type SpeechState } from './speech-core';
import type { LanguageCode } from './types';

const IDLE: SpeechState = { status: 'idle', ownerId: null, engine: null, error: null };

let voicePlan: Promise<Partial<Record<LanguageCode, 'gemini' | 'gtts'>>> | null = null;

function serverVoice(lang: LanguageCode) {
  voicePlan ??= getSpeechVoices()
    .then((r) => r.languages)
    .catch((e) => {
      voicePlan = null; // retry on the next play
      throw e;
    });
  return voicePlan.then((plan) => plan[lang] ?? null);
}

function loadVoices(): Promise<SpeechSynthesisVoice[]> {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) return Promise.resolve([]);
  const now = window.speechSynthesis.getVoices();
  if (now.length) return Promise.resolve(now);
  // Chrome loads voices asynchronously; the first getVoices() call is often empty.
  return new Promise((resolve) => {
    const done = () => resolve(window.speechSynthesis.getVoices());
    window.speechSynthesis.addEventListener('voiceschanged', done, { once: true });
    setTimeout(done, 1500);
  });
}

function devicePlayer(voice: SpeechSynthesisVoice): Player {
  let settle: (() => void) | null = null;
  return {
    play: (chunk, onStart) =>
      new Promise<void>((resolve, reject) => {
        const u = new SpeechSynthesisUtterance(chunk);
        u.voice = voice;
        u.lang = voice.lang;
        u.rate = 0.95;
        u.onstart = onStart;
        u.onend = () => resolve();
        u.onerror = (e) => {
          if (e.error === 'interrupted' || e.error === 'canceled') resolve();
          else reject(e.error === 'not-allowed' ? new BlockedError() : new Error(e.error));
        };
        settle = resolve;
        window.speechSynthesis.speak(u);
      }),
    stop: () => {
      window.speechSynthesis.cancel();
      settle?.();
      settle = null;
    },
    pause: () => window.speechSynthesis.pause(),
    resume: () => window.speechSynthesis.resume(),
  };
}

function audioPlayer() {
  const audio = new Audio();
  let url: string | null = null;
  let settle: (() => void) | null = null;
  const release = () => {
    if (url) URL.revokeObjectURL(url);
    url = null;
  };
  return {
    play: () => Promise.reject(new Error('use playBlob')),
    playBlob: (blob: Blob, onStart: () => void) =>
      new Promise<void>((resolve, reject) => {
        release();
        url = URL.createObjectURL(blob);
        settle = resolve;
        audio.onended = () => resolve();
        audio.onerror = () => reject(new Error('audio playback failed'));
        audio.src = url;
        audio.play().then(onStart, (e: DOMException) => {
          if (e?.name === 'NotAllowedError') reject(new BlockedError());
          else if (e?.name === 'AbortError') resolve();
          else reject(e);
        });
      }),
    stop: () => {
      audio.pause();
      audio.removeAttribute('src');
      release();
      settle?.();
      settle = null;
    },
    pause: () => audio.pause(),
    resume: () => void audio.play().catch(() => {}),
  };
}

/** The single read-aloud session for the whole app. */
export const speech = createSpeechController({
  fetchAudio: (text, lang, signal) => synthesizeSpeech(text, lang, signal).then((r) => r.audio),
  audioPlayer,
  serverVoice,
  deviceVoice: async (lang) => {
    const voice = pickVoice(await loadVoices(), lang);
    return voice ? { player: devicePlayer(voice), highQuality: isHighQualityVoice(voice, lang) } : null;
  },
});

/**
 * Read-aloud controls for one piece of content. Status is "idle" unless this owner holds the session,
 * and the session is released when the owner unmounts.
 */
export function useSpeech() {
  const ownerId = useId();
  const state = useSyncExternalStore(speech.subscribe, speech.getState, () => IDLE);
  useEffect(() => () => speech.release(ownerId), [ownerId]);
  const mine = state.ownerId === ownerId;
  return {
    status: mine ? state.status : ('idle' as const),
    error: mine ? state.error : null,
    engine: mine ? state.engine : null,
    play: useCallback((text: string, lang: LanguageCode) => speech.play(ownerId, text, lang), [ownerId]),
    stop: speech.stop,
    pause: speech.pause,
    resume: speech.resume,
  };
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
