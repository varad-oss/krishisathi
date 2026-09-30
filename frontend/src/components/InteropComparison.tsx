'use client';

import { Globe2 } from 'lucide-react';
import { getInteropComparison } from '@/lib/api';
import { useI18n } from '@/lib/i18n';
import { useResource } from '@/lib/use-resource';
import type { CountryComparison } from '@/lib/types';
import type { MessageKey } from '@/locales/en';
import { cn } from '@/lib/utils';
import { Card, CardTitle, ErrorState, LoadingBlock } from './ui';

const CATEGORIES = ['crops', 'observations', 'risk_signals', 'weather_signals', 'diseases'] as const;
const STATUS_TONE: Record<string, string> = {
  available: 'bg-leaf-50 text-leaf-700',
  partner_only: 'bg-paper text-ink-soft ring-1 ring-line',
  unsupported: 'bg-paper-deep/70 text-ink-faint',
  unavailable: 'bg-warn-50 text-warn-700',
};

function Status({ value }: { value: string }) {
  const { t } = useI18n();
  const key = `interop.status.${value}` as MessageKey;
  const text = t(key);
  return <span className={cn('rounded-full px-2 py-0.5 text-xs font-semibold', STATUS_TONE[value] ?? STATUS_TONE.unsupported)}>{text === key ? value : text}</span>;
}

function Country({ c }: { c: CountryComparison }) {
  const { t } = useI18n();
  return (
    <section aria-label={c.name} className="rounded-[var(--radius-inner)] ring-1 ring-line" data-testid={`interop-${c.country_code}`}>
      <h3 className="border-b border-line px-3 py-2 font-semibold">
        <span className="mr-2 rounded bg-paper px-1.5 py-0.5 font-mono text-xs">{c.country_code}</span>
        <span lang="en">{c.name}</span>
      </h3>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[34rem] text-left text-xs">
          <thead className="text-ink-faint">
            <tr>
              {(['category', 'status', 'type', 'geography', 'period', 'source', 'confidence'] as const).map((col) => (
                <th key={col} scope="col" className="px-3 py-1.5 font-medium">{t(`interop.col.${col}` as MessageKey)}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {CATEGORIES.map((cat) => {
              const meta = c.publishes[cat];
              const sample = c.samples[cat];
              const status = c.categories[cat] === 'available' ? sample?.status ?? 'available' : c.categories[cat] ?? 'unsupported';
              return (
                <tr key={cat}>
                  <th scope="row" className="px-3 py-1.5 font-medium">{t(`interop.category.${cat}` as MessageKey)}</th>
                  <td className="px-3 py-1.5"><Status value={status} /></td>
                  <td className="px-3 py-1.5" lang="en">{meta?.types.join(', ') ?? '—'}</td>
                  <td className="px-3 py-1.5" lang="en">{meta?.geography ?? '—'}</td>
                  <td className="px-3 py-1.5" lang="en">{meta?.period ?? '—'}</td>
                  <td className="px-3 py-1.5" lang="en">{meta?.provenance_kind ?? '—'}</td>
                  <td className="px-3 py-1.5" lang="en">{meta ? meta.confidence ?? t('interop.notAssessed') : '—'}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {c.samples.observations?.items?.[0] && (
        <details className="border-t border-line px-3 py-2 text-xs">
          <summary className="flex min-h-11 cursor-pointer items-center font-medium text-leaf-700">{t('interop.sample')}</summary>
          <pre className="mt-2 max-h-64 overflow-auto whitespace-pre-wrap break-all rounded bg-paper p-2" lang="en">{JSON.stringify(c.samples.observations.items[0], null, 2)}</pre>
        </details>
      )}
      <ul className="border-t border-line px-3 py-2 text-xs text-ink-faint" lang="en">
        {c.sources.map((s) => (
          <li key={s.id}>{s.url ? <a href={s.url} target="_blank" rel="noopener noreferrer" className="underline underline-offset-2">{s.name}</a> : s.name}</li>
        ))}
      </ul>
    </section>
  );
}

/** Developer view: different national sources, the same v1.0 interoperability contract. */
export function InteropComparison() {
  const { t } = useI18n();
  const data = useResource((s) => getInteropComparison('soybean', s), []);
  return (
    <Card aria-labelledby="interop-title">
      <CardTitle icon={Globe2} id="interop-title" description={t('interop.subtitle')}>
        {t('interop.title')}
      </CardTitle>
      {data.status === 'loading' && <LoadingBlock lines={5} />}
      {data.status === 'error' && <ErrorState error={data.error} onRetry={data.reload} title={t('interop.unavailable')} />}
      {data.data && (
        <div className="space-y-4">
          {data.data.countries.map((c) => (
            <Country key={c.country_code} c={c} />
          ))}
          <p className="text-xs text-ink-faint" lang="en">{data.data.notes}</p>
        </div>
      )}
    </Card>
  );
}
