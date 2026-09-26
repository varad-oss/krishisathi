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
    <header className="sticky top-0 z-40 bg-leaf-900 text-white">
      <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-2 focus:z-50 focus:rounded-lg focus:bg-white focus:px-3 focus:py-2 focus:text-ink">
        {t('nav.skip')}
      </a>
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between gap-4 px-4 sm:px-6">
        <Link href="/" className="flex items-center gap-2.5 rounded-lg" aria-label={t('app.name')}>
          <Logo />
          <span className="text-lg font-semibold tracking-tight">{t('app.name')}</span>
        </Link>

        <nav aria-label={t('nav.menu')} className="hidden items-center gap-1 md:flex">
          {NAV_ITEMS.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              aria-current={isActive(pathname, item.href) ? 'page' : undefined}
              className={cn(
                'rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive(pathname, item.href) ? 'bg-leaf-700 text-white' : 'text-leaf-100 hover:bg-leaf-700/60 hover:text-white',
              )}
            >
              {t(item.label)}
            </Link>
          ))}
          <Link
            href="/about"
            aria-current={isActive(pathname, '/about') ? 'page' : undefined}
            className={cn('rounded-lg px-3 py-2 text-sm font-medium text-leaf-100 hover:bg-leaf-700/60 hover:text-white', isActive(pathname, '/about') && 'bg-leaf-700 text-white')}
          >
            {t('nav.about')}
          </Link>
        </nav>

        <LanguageSelect />
      </div>
    </header>
  );
}
