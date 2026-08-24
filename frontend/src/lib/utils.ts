import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date, lang: string = 'en'): string {
  const nu = getNumberingSystem(lang);
  return new Intl.DateTimeFormat(`${lang}-IN-u-nu-${nu}`, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date(date));
}

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
    maximumFractionDigits: 1,
  }).format(num);
}

export function getSeverityColor(severity: string): string {
  switch ((severity || '').toLowerCase()) {
    case 'low':
      return 'text-green-600 bg-green-50 border-green-200';
    case 'moderate':
      return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    case 'severe':
    case 'high':
      return 'text-orange-600 bg-orange-50 border-orange-200';
    case 'critical':
      return 'text-red-600 bg-red-50 border-red-200';
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200';
  }
}

export function getConfidenceLabel(confidence: number): string {
  if (confidence >= 90) return 'Very High';
  if (confidence >= 75) return 'High';
  if (confidence >= 50) return 'Moderate';
  return 'Low';
}
