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
  const items = [...NAV_ITEMS.map((i) => ({ href: i.href, label: i.label })), { href: '/about', label: 'nav.about' as const }];

  return (
    <header className="sticky top-0 z-40 border-b border-line bg-paper/90 backdrop-blur-md supports-[backdrop-filter]:bg-paper/80">
      <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-2 focus:z-50 focus:rounded-lg focus:bg-surface focus:px-3 focus:py-2 focus:text-ink">
        {t('nav.skip')}
      </a>
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between gap-4 px-4 sm:px-6">
        {/* min-w-0 + truncate: long native-script names must never push the language menu off small screens. */}
        <Link href="/" className="flex min-w-0 items-center gap-2.5 rounded-lg" aria-label={t('app.name')}>
          <Logo />
          <span className="truncate font-display text-xl font-medium text-ink">{t('app.name')}</span>
        </Link>

        <nav aria-label={t('nav.menu')} className="hidden h-full items-stretch gap-1 md:flex">
          {items.map((item) => {
            const active = isActive(pathname, item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={active ? 'page' : undefined}
                className={cn(
                  'relative flex items-center px-3 text-sm font-medium transition-colors',
                  active ? 'text-ink after:absolute after:inset-x-3 after:bottom-0 after:h-0.5 after:rounded-full after:bg-leaf-600' : 'text-ink-soft hover:text-ink',
                )}
              >
                {t(item.label)}
              </Link>
            );
          })}
        </nav>

        <LanguageSelect tone="light" />
      </div>
    </header>
  );
}
