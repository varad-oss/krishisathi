'use client';

import Link from 'next/link';
import { useI18n } from '@/lib/i18n';
import Logo from './Logo';

export default function Footer() {
  const { t } = useI18n();
  const link = 'inline-flex min-h-11 items-center text-ink-soft underline-offset-4 hover:text-ink hover:underline';
  return (
    <footer className="mt-8 border-t border-line">
      <div className="mx-auto grid max-w-6xl gap-6 px-4 py-8 sm:px-6 md:grid-cols-[1fr_auto] md:items-start">
        <div className="max-w-xl">
          <p className="flex items-center gap-2 font-semibold text-ink">
            <Logo className="h-5 w-5" /> {t('app.name')}
          </p>
          <p className="mt-2 text-sm text-ink-soft">{t('footer.disclaimer')}</p>
          <p className="mt-3 text-xs text-ink-faint">{t('footer.built')}</p>
        </div>
        <nav aria-label={t('nav.about')} className="flex flex-wrap gap-x-6 text-sm">
          <Link href="/about" className={link}>{t('nav.about')}</Link>
          <Link href="/dashboard" className={link}>{t('nav.policy')}</Link>
          <a href="https://github.com/varad-oss/krishisathi" target="_blank" rel="noopener noreferrer" className={link}>
            {t('footer.code')}
          </a>
        </nav>
      </div>
    </footer>
  );
}
