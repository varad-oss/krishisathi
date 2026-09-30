'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useI18n } from '@/lib/i18n';
import { cn } from '@/lib/utils';
import LanguageSelect from './LanguageSelect';
import Logo from './Logo';
import { NAV_ITEMS, isActive } from './nav';

export default function Header() {
  const pathname = usePathname();
  const { t } = useI18n();

  return (
    <header className="sticky top-0 z-40 border-b border-line bg-paper/95 backdrop-blur supports-[backdrop-filter]:bg-paper/85">
      <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-2 focus:z-50 focus:rounded-lg focus:bg-surface focus:px-3 focus:py-2 focus:text-ink">
        {t('nav.skip')}
      </a>
      <div className="mx-auto flex h-[var(--header-h)] max-w-6xl items-center justify-between gap-4 px-4 sm:px-6">
        {/* min-w-0 + truncate: long native-script names must never push the language menu off small screens. */}
        <Link href="/" className="flex min-h-11 min-w-0 items-center gap-2.5 rounded-lg" aria-label={t('app.name')}>
          <Logo className="h-7 w-7 shrink-0" />
          <span className="truncate text-lg font-semibold tracking-tight text-ink">{t('app.name')}</span>
        </Link>

        <nav aria-label={t('nav.menu')} className="hidden h-full md:block">
          <ul className="flex h-full items-stretch gap-1">
            {NAV_ITEMS.map((item) => {
              const active = isActive(pathname, item);
              return (
                <li key={item.href} className="flex">
                  <Link
                    href={item.href}
                    aria-current={active ? 'page' : undefined}
                    className={cn(
                      'relative flex items-center gap-2 whitespace-nowrap px-3 text-[0.95rem] transition-colors lg:px-3.5',
                      active
                        ? 'font-semibold text-ink after:absolute after:inset-x-2 after:bottom-0 after:h-[3px] after:rounded-t after:bg-leaf-600'
                        : 'font-medium text-ink-soft hover:text-ink',
                    )}
                  >
                    <item.icon className={cn('hidden h-4 w-4 lg:block', active ? 'text-leaf-600' : 'text-ink-faint')} aria-hidden />
                    {t(item.label)}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        <LanguageSelect />
      </div>
    </header>
  );
}
