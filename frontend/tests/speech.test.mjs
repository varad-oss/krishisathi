// Read-aloud state machine, voice selection and text chunking (runs the real TS module via type stripping).
import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
  BCP47,
  BlockedError,
  cleanForSpeech,
  createSpeechController,
  isHighQualityVoice,
  pickVoice,
  splitForSpeech,
} from '../src/lib/speech-core.ts';

const tick = () => new Promise((r) => setTimeout(r, 0));
function deferred() {
  let resolve, reject;
  const promise = new Promise((res, rej) => ((resolve = res), (reject = rej)));
  promise.catch(() => {});
  return { promise, resolve, reject };
}

/** Controllable fakes: every fetch and every playback is a deferred the test settles explicitly. */
function harness({ server = 'gemini', device = null } = {}) {
  const fetches = [];
  const plays = [];
  const log = { stops: 0, devicePlays: [] };
  const audio = {
    playBlob(blob, onStart) {
      const d = deferred();
      plays.push({ blob, onStart, ...d });
      return d.promise;
    },
    play: () => Promise.reject(new Error('unused')),
    stop() {
      log.stops += 1;
      plays.forEach((p) => p.resolve());
    },
    pause() {},
    resume() {},
  };
  const devicePlayer = {
    play(chunk, onStart) {
      log.devicePlays.push(chunk);
      onStart();
      return Promise.resolve();
    },
    stop() {},
  };
  const speech = createSpeechController({
    fetchAudio(text, lang, signal) {
      const d = deferred();
      fetches.push({ text, lang, signal, ...d });
      return d.promise;
    },
    audioPlayer: () => audio,
    serverVoice: async () => server,
    deviceVoice: async () => (device ? { player: devicePlayer, highQuality: device === 'hq' } : null),
  });
  return { speech, fetches, plays, log };
}

test('starts idle', () => {
  const { speech } = harness();
  assert.deepEqual(speech.getState(), { status: 'idle', ownerId: null, engine: null, error: null });
});

test('play: loading -> playing -> idle after the last chunk', async () => {
  const { speech, fetches, plays } = harness();
  const done = speech.play('a', 'Water the field tomorrow morning.', 'en');
  assert.equal(speech.getState().status, 'loading');
  assert.equal(speech.getState().ownerId, 'a');
  await tick();
  assert.equal(fetches.length, 1);
  assert.equal(fetches[0].lang, 'en');
  fetches[0].resolve('blob-1');
  await tick();
  plays[0].onStart();
  assert.equal(speech.getState().status, 'playing');
  assert.equal(speech.getState().engine, 'server');
  plays[0].resolve();
  await done;
  assert.equal(speech.getState().status, 'idle');
  assert.equal(speech.getState().ownerId, null);
});

test('stop while loading aborts the request and ignores its late result', async () => {
  const { speech, fetches, plays } = harness();
  speech.play('a', 'Some advice.', 'hi');
  await tick();
  speech.stop();
  assert.equal(fetches[0].signal.aborted, true);
  assert.equal(speech.getState().status, 'idle');
  fetches[0].resolve('late');
  await tick();
  assert.equal(plays.length, 0, 'a stopped session must never start playing');
  assert.equal(speech.getState().status, 'idle');
});

test('stop while playing stops audio immediately and stays idle', async () => {
  const { speech, fetches, plays, log } = harness();
  speech.play('a', 'Some advice.', 'hi');
  await tick();
  fetches[0].resolve('b');
  await tick();
  plays[0].onStart();
  speech.stop();
  assert.equal(log.stops, 1);
  assert.equal(speech.getState().status, 'idle');
  plays[0].onStart(); // a stale callback from the stopped session
  await tick();
  assert.equal(speech.getState().status, 'idle');
});

test('replay after stop starts a fresh session', async () => {
  const { speech, fetches } = harness();
  speech.play('a', 'One.', 'mr');
  await tick();
  speech.stop();
  speech.play('a', 'One.', 'mr');
  await tick();
  assert.equal(fetches.length, 2);
  assert.equal(fetches[1].signal.aborted, false);
  assert.equal(speech.getState().status, 'loading');
});

test('playing another message stops the previous one (one session at a time)', async () => {
  const { speech, fetches, plays } = harness();
  speech.play('first', 'First answer.', 'ta');
  await tick();
  fetches[0].resolve('b1');
  await tick();
  plays[0].onStart();
  speech.play('second', 'Second answer.', 'ta');
  assert.equal(fetches[0].signal.aborted, true);
  assert.deepEqual([speech.getState().ownerId, speech.getState().status], ['second', 'loading']);
  plays[0].resolve(); // the first message's audio "ending" must not reset the second
  await tick();
  assert.deepEqual([speech.getState().ownerId, speech.getState().status], ['second', 'loading']);
});

test('release on unmount stops only the owner that is playing', async () => {
  const { speech } = harness();
  speech.play('a', 'Text.', 'en');
  speech.release('b');
  assert.equal(speech.getState().ownerId, 'a');
  speech.release('a');
  assert.equal(speech.getState().status, 'idle');
});

test('server failure without a native device voice is an error, not a wrong-language voice', async () => {
  const { speech, fetches, log } = harness({ device: null });
  const done = speech.play('a', 'पानी दें।', 'hi');
  await tick();
  fetches[0].reject(new Error('503'));
  await done;
  assert.deepEqual([speech.getState().status, speech.getState().error], ['error', 'service']);
  assert.equal(log.devicePlays.length, 0);
});

test('server failure falls back to a native device voice from the same chunk', async () => {
  const { speech, fetches, plays, log } = harness({ device: 'plain' });
  const text = 'पहला वाक्य। ' + 'दूसरा वाक्य बहुत लंबा है '.repeat(12) + '।';
  const chunks = splitForSpeech(cleanForSpeech(text));
  assert.ok(chunks.length >= 2);
  const done = speech.play('a', text, 'hi');
  await tick();
  fetches[0].resolve('b1');
  await tick();
  plays[0].onStart();
  fetches[1].reject(new Error('quota'));
  plays[0].resolve();
  await done;
  assert.deepEqual(log.devicePlays, chunks.slice(1));
  assert.equal(speech.getState().status, 'idle');
});

test('a high-quality device voice is preferred over the plain server voice', async () => {
  const { speech, fetches, log } = harness({ server: 'gtts', device: 'hq' });
  await speech.play('a', 'Hello farmer.', 'en');
  assert.equal(fetches.length, 0);
  assert.deepEqual(log.devicePlays, ['Hello farmer.']);
});

test('the natural server voice is preferred over any device voice', async () => {
  const { speech, fetches } = harness({ server: 'gemini', device: 'hq' });
  speech.play('a', 'Hello farmer.', 'en');
  await tick();
  assert.equal(fetches.length, 1);
});

test('autoplay block is reported as blocked', async () => {
  const { speech, fetches, plays } = harness();
  const done = speech.play('a', 'Text.', 'en');
  await tick();
  fetches[0].resolve('b');
  await tick();
  plays[0].reject(new BlockedError());
  await done;
  assert.deepEqual([speech.getState().status, speech.getState().error], ['error', 'blocked']);
});

test('empty or symbol-only text does nothing', async () => {
  const { speech, fetches } = harness();
  await speech.play('a', '** ## --', 'en');
  assert.equal(fetches.length, 0);
  assert.equal(speech.getState().status, 'idle');
});

// --- voices -------------------------------------------------------------------------

const V = (name, lang, localService = true) => ({ name, lang, localService });

test('every language maps to its Indian locale', () => {
  assert.deepEqual(BCP47, { en: 'en-IN', hi: 'hi-IN', mr: 'mr-IN', ta: 'ta-IN', te: 'te-IN', bn: 'bn-IN', kn: 'kn-IN', gu: 'gu-IN', pa: 'pa-IN', ml: 'ml-IN' });
});

test('pickVoice never gives Indic text to an English voice', () => {
  const voices = [V('Google US English', 'en-US', false), V('Microsoft Heera', 'en-IN')];
  for (const lang of ['hi', 'mr', 'ta', 'te', 'bn', 'kn', 'gu', 'pa', 'ml']) assert.equal(pickVoice(voices, lang), null);
});

test('pickVoice prefers the Indian region and natural voices, avoids robotic engines', () => {
  const voices = [V('eSpeak Hindi', 'hi'), V('Google हिन्दी', 'hi-IN', false), V('Microsoft Kalpana', 'hi-IN'), V('Google UK English', 'en-GB', false)];
  assert.equal(pickVoice(voices, 'hi').name, 'Google हिन्दी');
  assert.equal(pickVoice([V('Samantha', 'en-US'), V('Rishi', 'en-IN')], 'en').name, 'Rishi');
  assert.equal(pickVoice([V('Android Marathi', 'mr_IN')], 'mr').name, 'Android Marathi');
  assert.equal(pickVoice([V('Bengali (Bangladesh)', 'bn-BD')], 'bn').name, 'Bengali (Bangladesh)'); // same language, other region
});

test('isHighQualityVoice needs the exact Indian locale and a natural voice', () => {
  assert.equal(isHighQualityVoice(V('Google हिन्दी', 'hi-IN'), 'hi'), true);
  assert.equal(isHighQualityVoice(V('Microsoft Kalpana', 'hi-IN'), 'hi'), false);
  assert.equal(isHighQualityVoice(V('Google US English', 'en-US'), 'en'), false);
});

// --- text ---------------------------------------------------------------------------

test('cleanForSpeech removes Markdown, links and list markers', () => {
  assert.equal(
    cleanForSpeech('## What to do\n- **Irrigate** lightly\n- See [IMD](https://mausam.imd.gov.in)\n\n1. Check leaves'),
    'What to do. Irrigate lightly. See IMD. Check leaves',
  );
});

test('splitForSpeech: short first chunk, sentence (and danda) boundaries, nothing lost', () => {
  const text = 'पहला वाक्य। '.repeat(40);
  const chunks = splitForSpeech(text);
  assert.ok(chunks[0].length <= 180);
  assert.ok(chunks.slice(1).every((c) => c.length <= 450));
  assert.ok(chunks.every((c) => c.endsWith('।')));
  assert.equal(chunks.join(' ').replace(/\s+/g, ''), text.replace(/\s+/g, ''));
});

test('splitForSpeech splits an over-long sentence at spaces', () => {
  const long = 'word '.repeat(200).trim();
  const chunks = splitForSpeech(long);
  assert.ok(chunks.every((c) => c.length <= 450 && c.length > 0));
  assert.equal(chunks.join(' ').split(' ').length, 200);
});
