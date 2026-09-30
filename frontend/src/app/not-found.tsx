'use client';

import Link from 'next/link';
import { Sprout } from 'lucide-react';
import { buttonClass } from '@/components/ui';
import { useI18n } from '@/lib/i18n';

export default function NotFound() {
  const { t } = useI18n();
  return (
    <div className="mx-auto flex w-full max-w-md flex-1 flex-col items-start justify-center px-4 py-20">
      <Sprout className="h-8 w-8 text-leaf-600" aria-hidden />
      <h1 className="mt-4 font-display text-3xl">{t('notFound.title')}</h1>
      <p className="mt-2 text-ink-soft">{t('notFound.body')}</p>
      <div className="mt-6 flex flex-wrap gap-3">
        <Link href="/farm" className={buttonClass.primary}>{t('nav.farm')}</Link>
        <Link href="/" className={buttonClass.secondary}>{t('notFound.home')}</Link>
      </div>
    </div>
  );
}
