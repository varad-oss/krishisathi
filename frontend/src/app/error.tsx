'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { RefreshCw } from 'lucide-react';
import { buttonClass } from '@/components/ui';
import { useI18n } from '@/lib/i18n';

export default function ErrorPage({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  const { t } = useI18n();
  useEffect(() => {
    console.error(error);
  }, [error]);
  return (
    <div role="alert" className="mx-auto flex w-full max-w-md flex-1 flex-col items-start justify-center px-4 py-20">
      <h1 className="font-display text-3xl">{t('errorPage.title')}</h1>
      <p className="mt-2 text-ink-soft">{t('errorPage.body')}</p>
      {error.digest && <p className="mt-1 text-xs text-ink-faint">{t('error.reference', { id: error.digest })}</p>}
      <div className="mt-6 flex flex-wrap gap-3">
        <button type="button" onClick={reset} className={buttonClass.primary}>
          <RefreshCw className="h-4 w-4" aria-hidden /> {t('action.retry')}
        </button>
        <Link href="/farm" className={buttonClass.secondary}>{t('nav.farm')}</Link>
      </div>
    </div>
  );
}
