// Read-aloud state machine. Pure and dependency-injected so it can be tested without a browser;
// lib/speech.ts wires it to fetch, <audio> and speechSynthesis.
//
// Guarantees: one playback session at a time; every async callback checks the session token, so a
// stopped or superseded session can never change state; stop() takes effect immediately.

import type { LanguageCode } from './types';

export type SpeechStatus = 'idle' | 'loading' | 'playing' | 'paused' | 'error';
/** service: the server voice failed and the device has no native voice for the language. blocked: browser autoplay policy. */
export type SpeechErrorCode = 'service' | 'blocked';
export type SpeechEngine = 'server' | 'device';

export interface SpeechState {
  status: SpeechStatus;
  ownerId: string | null;
  engine: SpeechEngine | null;
  error: SpeechErrorCode | null;
}

export const BCP47: Record<LanguageCode, string> = {
  en: 'en-IN', hi: 'hi-IN', mr: 'mr-IN', ta: 'ta-IN', te: 'te-IN', bn: 'bn-IN', kn: 'kn-IN', gu: 'gu-IN', pa: 'pa-IN', ml: 'ml-IN',
};

/** Minimal voice shape (SpeechSynthesisVoice satisfies it). */
export interface VoiceLike {
  name: string;
  lang: string;
  localService: boolean;
}

const normLang = (tag: string) => tag.replace(/_/g, '-').toLowerCase();

/**
 * Best on-device voice for the language, or null. Only voices whose primary language subtag matches are
 * considered, so Hindi text is never given to an English voice. Prefers the Indian region, then voices
 * that are usually natural-sounding (network/"Natural"/"Neural"), and avoids known robotic engines.
 */
export function pickVoice<V extends VoiceLike>(voices: readonly V[], lang: LanguageCode): V | null {
  let best: V | null = null;
  let bestScore = -Infinity;
  for (const v of voices) {
    const tag = normLang(v.lang);
    if (tag.split('-')[0] !== lang) continue;
    let score = 0;
    if (tag === normLang(BCP47[lang])) score += 4;
    if (/natural|neural|online|enhanced|premium|google/i.test(v.name)) score += 2;
    if (!v.localService) score += 1;
    if (/espeak|eloquence|compact|novelty/i.test(v.name)) score -= 3;
    if (score > bestScore) {
      best = v;
      bestScore = score;
    }
  }
  return best;
}

/** True when a device voice is good enough to prefer over the server's plain (gTTS) voice. */
export function isHighQualityVoice(v: VoiceLike, lang: LanguageCode): boolean {
  return normLang(v.lang) === normLang(BCP47[lang]) && /natural|neural|online|enhanced|premium|google/i.test(v.name);
}

/** Removes Markdown and links so voices do not read out symbols. */
export function cleanForSpeech(text: string): string {
  return text
    .replace(/!?\[([^\]]*)\]\([^)]*\)/g, '$1') // links/images -> label
    .replace(/https?:\/\/\S+/g, '')
    .replace(/^\s{0,3}(#{1,6}|>|[-*+]|\d+[.)])\s+/gm, '') // headings, quotes, list markers
    .replace(/[*_`~|#>]+/g, ' ')
    .replace(/\s*\n+\s*/g, '. ')
    .replace(/(\.\s*){2,}/g, '. ')
    .replace(/\s{2,}/g, ' ')
    .replace(/^[.\s]+/, '')
    .trim();
}

/**
 * Splits text at sentence ends (including the Devanagari danda) into chunks. The first chunk is short so
 * audio starts quickly; later chunks are longer for natural prosody. Long sentences split at commas/spaces.
 */
export function splitForSpeech(text: string, first = 180, rest = 450): string[] {
  const sentences = text.match(/[^.!?।॥\n]+[.!?।॥]*\s*/g) ?? [];
  const chunks: string[] = [];
  let current = '';
  const limit = () => (chunks.length === 0 ? first : rest);
  const push = () => {
    // A chunk with no letters or digits (e.g. "--") has nothing to say.
    if (/[\p{L}\p{N}]/u.test(current)) chunks.push(current.trim());
    current = '';
  };
  for (const sentence of sentences) {
    if ((current + sentence).length <= limit()) {
      current += sentence;
      continue;
    }
    push();
    let s = sentence;
    while (s.length > limit()) {
      const max = limit();
      const cut = Math.max(s.lastIndexOf(',', max), s.lastIndexOf(' ', max));
      const at = cut > max / 2 ? cut + 1 : max;
      chunks.push(s.slice(0, at).trim());
      s = s.slice(at);
    }
    current = s;
  }
  push();
  return chunks;
}

/** Plays one chunk; resolves when it finishes (or is stopped), rejects on failure. */
export interface Player {
  play(chunk: string, onStart: () => void): Promise<void>;
  stop(): void;
  pause?(): void;
  resume?(): void;
}

export interface SpeechDeps {
  /** Server audio for one chunk; rejects on failure. */
  fetchAudio(text: string, lang: LanguageCode, signal: AbortSignal): Promise<Blob>;
  /** Player for server audio blobs. */
  audioPlayer(): Player & { playBlob(blob: Blob, onStart: () => void): Promise<void> };
  /** Best native device voice player, or null when the device has none for this language. */
  deviceVoice(lang: LanguageCode): Promise<{ player: Player; highQuality: boolean } | null>;
  /** Server voice kind for the language ("gemini" natural, "gtts" plain), or null if unknown. */
  serverVoice(lang: LanguageCode): Promise<'gemini' | 'gtts' | null>;
}

export class BlockedError extends Error {
  constructor() {
    super('Playback blocked');
    this.name = 'BlockedError';
  }
}

export function createSpeechController(deps: SpeechDeps) {
  let state: SpeechState = { status: 'idle', ownerId: null, engine: null, error: null };
  const listeners = new Set<() => void>();
  let session = 0;
  let abort: AbortController | null = null;
  let player: Player | null = null;

  const set = (patch: Partial<SpeechState>) => {
    state = { ...state, ...patch };
    listeners.forEach((l) => l());
  };

  function stop() {
    session += 1;
    abort?.abort();
    abort = null;
    player?.stop();
    player = null;
    if (state.status !== 'idle' || state.ownerId) set({ status: 'idle', ownerId: null, engine: null, error: null });
  }

  async function playServer(token: number, chunks: string[], lang: LanguageCode, from: { index: number }) {
    const signal = abort!.signal;
    const p = deps.audioPlayer();
    player = p;
    let next: Promise<Blob> | null = deps.fetchAudio(chunks[from.index], lang, signal);
    while (next && token === session) {
      const blob: Blob = await next;
      if (token !== session) return;
      next = from.index + 1 < chunks.length ? deps.fetchAudio(chunks[from.index + 1], lang, signal) : null;
      next?.catch(() => {}); // handled when awaited; avoids an unhandled rejection if we stop first
      await p.playBlob(blob, () => token === session && set({ status: 'playing', engine: 'server' }));
      if (token !== session) return;
      from.index += 1;
    }
  }

  async function playDevice(token: number, chunks: string[], from: { index: number }, device: Player) {
    player = device;
    while (from.index < chunks.length && token === session) {
      await device.play(chunks[from.index], () => token === session && set({ status: 'playing', engine: 'device' }));
      if (token !== session) return;
      from.index += 1;
    }
  }

  async function play(ownerId: string, text: string, lang: LanguageCode) {
    stop();
    const chunks = splitForSpeech(cleanForSpeech(text));
    if (!chunks.length) return;
    const token = ++session;
    abort = new AbortController();
    set({ status: 'loading', ownerId, engine: null, error: null });
    const from = { index: 0 };
    const finish = () => token === session && stop();
    const fail = (error: SpeechErrorCode) => {
      if (token !== session) return;
      abort?.abort();
      player?.stop();
      player = null;
      set({ status: 'error', engine: null, error });
    };

    try {
      // A natural server voice beats any device voice; a high-quality device voice beats plain gTTS.
      const [server, device] = await Promise.all([deps.serverVoice(lang).catch(() => null), deps.deviceVoice(lang).catch(() => null)]);
      if (token !== session) return;
      if (server !== 'gemini' && device?.highQuality) {
        await playDevice(token, chunks, from, device.player);
        return finish();
      }
      try {
        await playServer(token, chunks, lang, from);
        return finish();
      } catch (err) {
        if (token !== session) return;
        if (err instanceof BlockedError) return fail('blocked');
        // Server voice failed part-way: continue from the same chunk with a native device voice, if any.
        if (!device) return fail('service');
        player?.stop();
        await playDevice(token, chunks, from, device.player);
        return finish();
      }
    } catch (err) {
      fail(err instanceof BlockedError ? 'blocked' : 'service');
    }
  }

  return {
    getState: () => state,
    subscribe(listener: () => void) {
      listeners.add(listener);
      return () => void listeners.delete(listener);
    },
    play,
    stop,
    pause() {
      if (state.status !== 'playing' || !player?.pause) return;
      player.pause();
      set({ status: 'paused' });
    },
    resume() {
      if (state.status !== 'paused' || !player?.resume) return;
      player.resume();
      set({ status: 'playing' });
    },
    /** Stops only if `ownerId` owns the current session (used on unmount). */
    release(ownerId: string) {
      if (state.ownerId === ownerId) stop();
    },
  };
}

export type SpeechController = ReturnType<typeof createSpeechController>;
