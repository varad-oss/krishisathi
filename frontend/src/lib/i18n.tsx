'use client';

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import en, { type MessageKey, type Messages } from '@/locales/en';
import type { LanguageCode } from './types';
import { SUPPORTED_LANGUAGES } from './languages';

// English ships in the main bundle; other locales are fetched only when selected.
const loaders: Record<Exclude<LanguageCode, 'en'>, () => Promise<{ default: Messages }>> = {
  hi: () => import('@/locales/hi'),
  mr: () => import('@/locales/mr'),
  ta: () => import('@/locales/ta'),
  te: () => import('@/locales/te'),
  bn: () => import('@/locales/bn'),
  kn: () => import('@/locales/kn'),
  gu: () => import('@/locales/gu'),
  pa: () => import('@/locales/pa'),
  ml: () => import('@/locales/ml'),
};

const cache: Partial<Record<LanguageCode, Messages>> = { en };
const STORAGE_KEY = 'krishi_language';

const NUMBERING: Partial<Record<LanguageCode, string>> = {
  hi: 'deva', mr: 'deva', ta: 'tamldec', te: 'telu', bn: 'beng', kn: 'knda', gu: 'gujr', pa: 'guru', ml: 'mlym',
};

export type Params = Record<string, string | number>;

export function interpolate(template: string, params?: Params): string {
  if (!params) return template;
  return template.replace(/\{(\w+)\}/g, (m, name) => (name in params ? String(params[name]) : m));
}

export function localeTag(lang: LanguageCode): string {
  const nu = NUMBERING[lang];
  return nu ? `${lang}-IN-u-nu-${nu}` : `${lang}-IN`;
}

export async function loadMessages(lang: LanguageCode): Promise<Messages> {
  if (cache[lang]) return cache[lang]!;
  const mod = await loaders[lang as Exclude<LanguageCode, 'en'>]();
  cache[lang] = mod.default;
  return mod.default;
}

function isLanguage(v: string | null): v is LanguageCode {
  return !!v && SUPPORTED_LANGUAGES.some((l) => l.code === v);
}

export function makeFormatters(lang: LanguageCode) {
  const tag = localeTag(lang);
  const numberFormats = new Map<string, Intl.NumberFormat>();
  const num = (value: number | null | undefined, maxFractionDigits = 1): string => {
    if (value === null || value === undefined || Number.isNaN(value)) return '—';
    const key = String(maxFractionDigits);
    if (!numberFormats.has(key)) numberFormats.set(key, new Intl.NumberFormat(tag, { maximumFractionDigits: maxFractionDigits }));
    return numberFormats.get(key)!.format(value);
  };
  const date = (value: string | Date, opts: Intl.DateTimeFormatOptions = { day: 'numeric', month: 'short' }) => {
    const d = typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value) ? new Date(`${value}T00:00:00`) : new Date(value);
    return Number.isNaN(d.getTime()) ? '—' : new Intl.DateTimeFormat(tag, opts).format(d);
  };
  const weekday = (value: string) => date(value, { weekday: 'short' });
  const dateTime = (value: string | Date) => date(value, { day: 'numeric', month: 'short', hour: 'numeric', minute: '2-digit' });
  const relative = (value: string | Date | number) => {
    const ms = new Date(value).getTime() - Date.now();
    const rtf = new Intl.RelativeTimeFormat(tag, { numeric: 'auto' });
    const abs = Math.abs(ms);
    if (abs < 60_000) return rtf.format(0, 'minute');
    if (abs < 3_600_000) return rtf.format(Math.round(ms / 60_000), 'minute');
    if (abs < 86_400_000) return rtf.format(Math.round(ms / 3_600_000), 'hour');
    return rtf.format(Math.round(ms / 86_400_000), 'day');
  };
  return { num, date, weekday, dateTime, relative };
}

interface I18nValue {
  language: LanguageCode;
  setLanguage: (lang: LanguageCode) => void;
  switching: boolean;
  t: (key: MessageKey, params?: Params) => string;
  fmt: ReturnType<typeof makeFormatters>;
}

const I18nContext = createContext<I18nValue | null>(null);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguageState] = useState<LanguageCode>('en');
  const [messages, setMessages] = useState<Messages>(en);
  const [switching, setSwitching] = useState(false);

  // Only switch after the dictionary is loaded, so the UI never flashes a mix of languages.
  const setLanguage = useCallback((lang: LanguageCode) => {
    setSwitching(true);
    loadMessages(lang)
      .then((m) => {
        setMessages(m);
        setLanguageState(lang);
        try {
          localStorage.setItem(STORAGE_KEY, lang);
        } catch {
          /* storage may be unavailable (private mode) */
        }
      })
      .catch(() => {
        /* chunk failed to load (offline): keep the current language */
      })
      .finally(() => setSwitching(false));
  }, []);

  useEffect(() => {
    let stored: string | null = null;
    try {
      stored = localStorage.getItem(STORAGE_KEY);
    } catch {
      /* ignore */
    }
    if (!isLanguage(stored) || stored === 'en') return;
    const lang = stored;
    loadMessages(lang)
      .then((m) => {
        setMessages(m);
        setLanguageState(lang);
      })
      .catch(() => {
        /* offline: stay in English until the user switches again */
      });
  }, []);

  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);

  const value = useMemo<I18nValue>(() => {
    const t = (key: MessageKey, params?: Params) => interpolate(messages[key] ?? en[key] ?? key, params);
    return { language, setLanguage, switching, t, fmt: makeFormatters(language) };
  }, [language, messages, setLanguage, switching]);

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nValue {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error('useI18n must be used inside LanguageProvider');
  return ctx;
}
