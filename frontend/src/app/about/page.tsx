'use client';

import { BookOpen, Camera, Database, Lock, Scale } from 'lucide-react';
import { Card, CardTitle, ErrorState, LoadingBlock } from '@/components/ui';
import { getSources } from '@/lib/api';
import { useI18n } from '@/lib/i18n';
import { useResource } from '@/lib/use-resource';
import type { MessageKey } from '@/locales/en';
import { cn } from '@/lib/utils';

export default function AboutPage() {
  const { t } = useI18n();
  const sources = useResource((s) => getSources(s), []);

  return (
    <div className="mx-auto w-full max-w-3xl space-y-5 px-4 pb-10 pt-6 sm:px-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">{t('about.title')}</h1>
        <p className="mt-1 text-ink-soft">{t('about.subtitle')}</p>
      </div>

      <Card aria-labelledby="sources-title">
        <CardTitle icon={Database} id="sources-title">
          {t('about.sources.title')}
        </CardTitle>
        {sources.status === 'loading' && <LoadingBlock lines={5} />}
        {sources.status === 'error' && <ErrorState error={sources.error} onRetry={sources.reload} title={t('about.sources.unavailable')} />}
        {sources.data && (
          <ul className="divide-y divide-line">
            {sources.data.map((s) => (
              <li key={s.id} className="flex flex-col gap-1 py-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="font-medium" lang="en">
                    {s.url ? (
                      <a href={s.url} target="_blank" rel="noopener noreferrer" className="underline decoration-line-strong underline-offset-2 hover:text-leaf-700">
                        {s.name}
                      </a>
                    ) : (
                      s.name
                    )}
                  </p>
                  <p className="text-xs text-ink-faint">{t(`kind.${s.kind}` as MessageKey)}</p>
                </div>
                <span
                  className={cn(
                    'self-start rounded-full px-2.5 py-0.5 text-xs font-semibold sm:self-center',
                    s.status === 'configured' ? 'bg-leaf-50 text-leaf-700' : 'bg-paper text-ink-faint ring-1 ring-line',
                  )}
                >
                  {t(`about.sources.status.${s.status}` as MessageKey)}
                </span>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <Card aria-labelledby="diag-title">
        <CardTitle icon={Camera} id="diag-title">
          {t('about.diagnosis.title')}
        </CardTitle>
        <div className="space-y-3 text-ink-soft">
          <p>{t('about.diagnosis.body')}</p>
          <p>{t('about.diagnosis.safety')}</p>
          <p className="font-medium text-ink">{t('about.diagnosis.accuracy')}</p>
        </div>
      </Card>

      <Card aria-labelledby="rules-title">
        <CardTitle icon={Scale} id="rules-title">
          {t('about.rules.title')}
        </CardTitle>
        <p className="text-ink-soft">{t('about.rules.body')}</p>
      </Card>

      <Card aria-labelledby="privacy-title">
        <CardTitle icon={Lock} id="privacy-title">
          {t('about.privacy.title')}
        </CardTitle>
        <p className="text-ink-soft">{t('about.privacy.body')}</p>
      </Card>

      <Card aria-labelledby="limits-title" className="bg-soil-50/60">
        <CardTitle icon={BookOpen} id="limits-title">
          {t('about.limits.title')}
        </CardTitle>
        <ul className="list-disc space-y-1.5 pl-5 text-ink-soft">
          {(['about.limits.1', 'about.limits.2', 'about.limits.3', 'about.limits.4'] as const).map((k) => (
            <li key={k}>{t(k)}</li>
          ))}
        </ul>
      </Card>
    </div>
  );
}
