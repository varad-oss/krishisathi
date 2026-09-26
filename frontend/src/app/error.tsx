'use client';

import { useEffect } from 'react';
import { buttonClass } from '@/components/ui';
import { useI18n } from '@/lib/i18n';

export default function ErrorPage({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  const { t } = useI18n();
  useEffect(() => {
    console.error(error);
  }, [error]);
  return (
    <div role="alert" className="mx-auto flex max-w-md flex-1 flex-col items-center justify-center px-4 py-20 text-center">
      <h1 className="text-2xl font-semibold">{t('errorPage.title')}</h1>
      <p className="mt-2 text-ink-soft">{t('errorPage.body')}</p>
      {error.digest && <p className="mt-1 text-xs text-ink-faint">{t('error.reference', { id: error.digest })}</p>}
      <button type="button" onClick={reset} className={`${buttonClass.primary} mt-6`}>
        {t('action.retry')}
      </button>
    </div>
  );
}
