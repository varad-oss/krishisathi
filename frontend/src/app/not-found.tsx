'use client';

import Link from 'next/link';
import { buttonClass } from '@/components/ui';
import { useI18n } from '@/lib/i18n';

export default function NotFound() {
  const { t } = useI18n();
  return (
    <div className="mx-auto flex max-w-md flex-1 flex-col items-center justify-center px-4 py-20 text-center">
      <h1 className="text-2xl font-semibold">{t('notFound.title')}</h1>
      <p className="mt-2 text-ink-soft">{t('notFound.body')}</p>
      <Link href="/" className={`${buttonClass.primary} mt-6`}>
        {t('notFound.home')}
      </Link>
    </div>
  );
}
