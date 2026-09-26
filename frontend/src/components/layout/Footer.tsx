'use client';

import Link from 'next/link';
import { useI18n } from '@/lib/i18n';
import Logo from './Logo';

export default function Footer() {
  const { t } = useI18n();
  return (
    <footer className="border-t border-line bg-surface">
      <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between">
          <div className="max-w-md">
            <p className="flex items-center gap-2 font-semibold text-ink">
              <Logo className="h-6 w-6" /> {t('app.name')}
            </p>
            <p className="mt-2 text-sm text-ink-soft">{t('footer.disclaimer')}</p>
          </div>
          <nav aria-label={t('nav.about')} className="flex flex-wrap gap-x-5 gap-y-2 text-sm">
            <Link href="/about" className="text-ink-soft hover:text-leaf-700">{t('nav.about')}</Link>
            <Link href="/dashboard" className="text-ink-soft hover:text-leaf-700">{t('nav.policy')}</Link>
            <a href="https://github.com/varad-oss/krishisathi" target="_blank" rel="noopener noreferrer" className="text-ink-soft hover:text-leaf-700">
              {t('footer.code')}
            </a>
          </nav>
        </div>
        <p className="mt-6 border-t border-line pt-4 text-xs text-ink-faint">{t('footer.built')}</p>
      </div>
    </footer>
  );
}
