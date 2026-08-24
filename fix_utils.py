with open("frontend/src/lib/utils.ts", "r") as f:
    text = f.read()

text = text.replace(
"""export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat('en-US', {""",
"""export function formatDate(date: string | Date, lang: string = 'en'): string {
  return new Intl.DateTimeFormat(`${lang}-IN`, {""")

text = text.replace(
"""export function formatNumber(num: number): string {
  return new Intl.NumberFormat('en-IN', {""",
"""export function formatNumber(num: number, lang: string = 'en'): string {
  return new Intl.NumberFormat(`${lang}-IN`, {""")

with open("frontend/src/lib/utils.ts", "w") as f:
    f.write(text)
