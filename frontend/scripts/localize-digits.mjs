// Converts ASCII digits inside locale string values to the language's native numerals,
// so fixed numbers in copy ("64.5 mm", "7 days") match Intl-formatted numbers in the UI.
// Placeholders like {count} are left untouched. Usage: node scripts/localize-digits.mjs [--check]
import { readFileSync, writeFileSync } from 'node:fs';

export const ZERO = { hi: 0x966, mr: 0x966, bn: 0x9e6, pa: 0xa66, gu: 0xae6, ta: 0xbe6, te: 0xc66, kn: 0xce6, ml: 0xd66 };

export function localize(value, lang) {
  const zero = ZERO[lang];
  return value.replace(/(\{\w+\})|[0-9]/g, (m, placeholder) => (placeholder ? m : String.fromCodePoint(zero + Number(m))));
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const check = process.argv.includes('--check');
  let dirty = false;
  for (const lang of Object.keys(ZERO)) {
    const path = new URL(`../src/locales/${lang}.ts`, import.meta.url);
    const src = readFileSync(path, 'utf8');
    const out = src.replace(/^(\s+'[^']+': )"(.*)",$/gm, (_, head, value) => `${head}"${localize(value, lang)}",`);
    if (out !== src) {
      dirty = true;
      if (!check) writeFileSync(path, out);
      console.log(`${check ? 'needs localizing' : 'localized'}: ${lang}`);
    }
  }
  if (check && dirty) process.exit(1);
}
