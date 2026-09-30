'use client';

import { ChevronDown, Languages } from 'lucide-react';
import { useI18n } from '@/lib/i18n';
import { SUPPORTED_LANGUAGES } from '@/lib/languages';
import type { LanguageCode } from '@/lib/types';
import { cn } from '@/lib/utils';

export default function LanguageSelect({ className, large }: { className?: string; large?: boolean }) {
  const { language, setLanguage, switching, t } = useI18n();
  return (
    <label className={cn('relative flex shrink-0 items-center', className)}>
      <span className="sr-only">{t('nav.language')}</span>
      <Languages className="pointer-events-none absolute left-3 h-4 w-4 text-ink-soft" aria-hidden />
      <select
        value={language}
        onChange={(e) => setLanguage(e.target.value as LanguageCode)}
        aria-busy={switching}
        className={cn(
          'w-full appearance-none rounded-[var(--radius-inner)] border border-line-strong bg-surface pl-9 pr-8 font-medium text-ink focus:outline-none focus-visible:ring-2 focus-visible:ring-leaf-200',
          large ? 'min-h-12 text-base' : 'min-h-11 max-w-[9.5rem] py-1.5 text-sm',
        )}
      >
        {SUPPORTED_LANGUAGES.map((l) => (
          <option key={l.code} value={l.code} lang={l.code}>
            {l.nativeName}
          </option>
        ))}
      </select>
      <ChevronDown className="pointer-events-none absolute right-2.5 h-4 w-4 text-ink-soft" aria-hidden />
    </label>
  );
}
