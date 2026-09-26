'use client';

import { Globe } from 'lucide-react';
import { useI18n } from '@/lib/i18n';
import { SUPPORTED_LANGUAGES } from '@/lib/languages';
import type { LanguageCode } from '@/lib/types';
import { cn } from '@/lib/utils';

export default function LanguageSelect({ className, tone = 'dark' }: { className?: string; tone?: 'dark' | 'light' }) {
  const { language, setLanguage, switching, t } = useI18n();
  return (
    <label className={cn('relative flex items-center', className)}>
      <span className="sr-only">{t('nav.language')}</span>
      <Globe className={cn('pointer-events-none absolute left-3 h-4 w-4', tone === 'dark' ? 'text-leaf-100' : 'text-ink-faint')} aria-hidden />
      <select
        value={language}
        onChange={(e) => setLanguage(e.target.value as LanguageCode)}
        aria-busy={switching}
        className={cn(
          'min-h-10 appearance-none rounded-xl py-1.5 pl-9 pr-8 text-sm font-medium focus:outline-none focus-visible:ring-2',
          tone === 'dark'
            ? 'border border-leaf-500/60 bg-leaf-700 text-white focus-visible:ring-leaf-200'
            : 'border border-line-strong bg-surface text-ink focus-visible:ring-leaf-200',
        )}
      >
        {SUPPORTED_LANGUAGES.map((l) => (
          <option key={l.code} value={l.code} lang={l.code}>
            {l.nativeName}
          </option>
        ))}
      </select>
      <span aria-hidden className={cn('pointer-events-none absolute right-3 text-xs', tone === 'dark' ? 'text-leaf-100' : 'text-ink-faint')}>▾</span>
    </label>
  );
}
