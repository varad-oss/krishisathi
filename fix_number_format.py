with open("frontend/src/lib/utils.ts", "r") as f:
    text = f.read()

replacement = """
export function getNumberingSystem(lang: string): string {
  const map: Record<string, string> = {
    hi: 'deva', mr: 'deva',
    ta: 'tamldec', te: 'telu',
    bn: 'beng', kn: 'knda',
    gu: 'gujr', pa: 'guru',
    ml: 'mlym'
  };
  return map[lang] || 'latn';
}

export function formatNumber(num: number, lang: string = 'en'): string {
  const nu = getNumberingSystem(lang);
  return new Intl.NumberFormat(`${lang}-IN-u-nu-${nu}`, {
    notation: 'compact',
    compactDisplay: 'short',
  }).format(num);
}
"""

import re
# Replace the existing formatNumber
text = re.sub(r"export function formatNumber\(num: number, lang: string = 'en'\): string \{\n  return new Intl.NumberFormat\(`\$\{lang\}-IN`, \{\n    notation: 'compact',\n    compactDisplay: 'short',\n  \}\)\.format\(num\);\n\}", replacement.strip(), text)

# Replace the existing formatDate
text = re.sub(r"export function formatDate\(date: string \| Date, lang: string = 'en'\): string \{\n  return new Intl.DateTimeFormat\(`\$\{lang\}-IN`, \{\n    month: 'short',\n    day: 'numeric',\n    year: 'numeric',\n  \}\)\.format\(new Date\(date\)\);\n\}", 
"""export function formatDate(date: string | Date, lang: string = 'en'): string {
  const nu = getNumberingSystem(lang);
  return new Intl.DateTimeFormat(`${lang}-IN-u-nu-${nu}`, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date(date));
}""", text)

with open("frontend/src/lib/utils.ts", "w") as f:
    f.write(text)
