// Locale integrity: same keys as English, same placeholders, no untranslated English copy,
// and no ASCII digits in native-numeral languages. Run: node --test tests/
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import { ZERO } from '../scripts/localize-digits.mjs';

const parse = (lang) => {
  const src = readFileSync(new URL(`../src/locales/${lang}.ts`, import.meta.url), 'utf8');
  const entries = {};
  for (const m of src.matchAll(/^\s+'([^']+)': (?:"((?:[^"\\]|\\.)*)"|'((?:[^'\\]|\\.)*)'),$/gm)) entries[m[1]] = m[2] ?? m[3];
  return entries;
};
const en = parse('en');
const placeholders = (s) => [...s.matchAll(/\{(\w+)\}/g)].map((m) => m[1]).sort();
// Identical to English is fine only for codes, units and symbols.
const SAME_OK = /^(pH|\{lat\}, \{lng\}|NDVI|KVK)$/;

for (const lang of Object.keys(ZERO)) {
  test(`${lang}: complete and consistent with English`, () => {
    const loc = parse(lang);
    assert.deepEqual(Object.keys(loc).sort(), Object.keys(en).sort(), 'key sets differ');
    for (const [key, value] of Object.entries(en)) {
      assert.deepEqual(placeholders(loc[key]), placeholders(value), `placeholders differ for ${key}`);
      if (/[a-z]{3}/i.test(value) && !SAME_OK.test(value)) assert.notEqual(loc[key], value, `${key} is untranslated`);
      assert.doesNotMatch(loc[key].replace(/\{\w+\}/g, ''), /[0-9]/, `${key} has ASCII digits`);
    }
  });
}

test('every literal t() key used in the app exists in English', async () => {
  const { execSync } = await import('node:child_process');
  const used = execSync(`grep -rhoE "t\\\\('[a-zA-Z0-9_.]+'" src || true`, { cwd: new URL('..', import.meta.url) }).toString();
  const keys = [...used.matchAll(/t\('([^']+)'/g)].map((m) => m[1]).filter((k) => k.includes('.'));
  for (const k of keys) assert.ok(k in en, `missing English key ${k}`);
});
