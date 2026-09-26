'use client';

import { Building2, Layers, Leaf, Satellite, TrendingDown, TrendingUp } from 'lucide-react';
import { useI18n } from '@/lib/i18n';
import type { Resource } from '@/lib/use-resource';
import type { CropHealth, Kvk, RegenerativeResponse, RegenTrigger, SoilData } from '@/lib/types';
import type { MessageKey } from '@/locales/en';
import { cn } from '@/lib/utils';
import { Card, CardTitle, ErrorState, LevelBadge, LoadingBlock, Note, ProvenanceLine, UnavailableNote } from '../ui';

function SoilProperties({ soil }: { soil: SoilData }) {
  const { t, fmt } = useI18n();
  if (soil.status === 'unavailable') return <UnavailableNote>{t('farm.soil.unavailable')}</UnavailableNote>;
  if (soil.status === 'no_data' || !soil.properties) return <UnavailableNote>{t('farm.soil.noData')}</UnavailableNote>;
  const p = soil.properties;
  const r = soil.ratings;
  const items = [
    { label: t('farm.soil.ph'), value: fmt.num(p.ph), rating: r?.ph ? t(`farm.soil.rating.${r.ph}` as MessageKey) : null },
    {
      label: t('farm.soil.organicCarbon'),
      value: p.organic_carbon_pct == null ? '—' : `${fmt.num(p.organic_carbon_pct, 2)}%`,
      level: r?.organic_carbon ?? null,
    },
    { label: t('farm.soil.clay'), value: p.clay_pct == null ? '—' : `${fmt.num(p.clay_pct, 0)}%` },
    { label: t('farm.soil.sand'), value: p.sand_pct == null ? '—' : `${fmt.num(p.sand_pct, 0)}%` },
  ];
  return (
    <>
      <dl className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {items.map((i) => (
          <div key={i.label} className="rounded-xl bg-paper p-3">
            <dt className="text-xs text-ink-soft">{i.label}</dt>
            <dd className="mt-1 text-lg font-semibold tabular-nums">{i.value}</dd>
            {'rating' in i && i.rating && <dd className="text-xs text-ink-soft">{i.rating}</dd>}
            {'level' in i && i.level && <dd className="mt-1"><LevelBadge level={i.level} /></dd>}
          </div>
        ))}
      </dl>
      <Note tone="watch" className="mt-3">{t('farm.soil.testAdvice')}</Note>
      {soil.provenance && (
        <ProvenanceLine
          source={`${soil.provenance.source} (${soil.provenance.resolution}, ${soil.provenance.depth})`}
          url={soil.provenance.source_url}
          kind="model"
          time={soil.provenance.retrieved_at}
          note={soil.ratings?.source ? <a className="underline underline-offset-2" href={soil.ratings.source.url} target="_blank" rel="noopener noreferrer">{soil.ratings.source.name}</a> : null}
        />
      )}
    </>
  );
}

function triggerText(t: (k: MessageKey, p?: Record<string, string | number>) => string, fmt: { num: (n: number | null, d?: number) => string }, tr: RegenTrigger): string | null {
  const ratingText = (r: string | null) => {
    if (!r) return '';
    const soilKey = `farm.soil.rating.${r}` as MessageKey;
    const levelKey = `level.${r}` as MessageKey;
    const soil = t(soilKey);
    if (soil !== soilKey) return soil;
    const level = t(levelKey);
    return level !== levelKey ? level : r;
  };
  switch (tr.signal) {
    case 'crop':
      return tr.value ? t('farm.regen.signal.crop', { value: t(`crop.${tr.value}` as MessageKey) }) : null;
    case 'soil_organic_carbon':
    case 'soil_ph':
    case 'soil_sand_pct':
      return t(`farm.regen.signal.${tr.signal}` as MessageKey, {
        value: typeof tr.value === 'number' ? fmt.num(tr.value, tr.signal === 'soil_ph' ? 1 : 2) : String(tr.value ?? '—'),
        rating: ratingText(tr.rating),
      });
    case 'soil_data':
    case 'forecast_dry_spell':
      return t(`farm.regen.signal.${tr.signal}` as MessageKey);
    default:
      return null;
  }
}

export function SoilRegenCard({ regen }: { regen: Resource<RegenerativeResponse> }) {
  const { t, fmt } = useI18n();
  const data = regen.data;
  return (
    <Card id="soil" aria-labelledby="soil-title" className="scroll-mt-header">
      <CardTitle icon={Layers} id="soil-title">
        {t('farm.soil.title')}
      </CardTitle>
      {!data && regen.status === 'loading' ? (
        <LoadingBlock lines={4} />
      ) : !data && regen.status === 'error' ? (
        <ErrorState error={regen.error} onRetry={regen.reload} title={t('farm.regen.unavailable')} />
      ) : data ? (
        <>
          <SoilProperties soil={data.soil} />

          <h3 className="mt-8 flex items-center gap-2 text-lg font-semibold">
            <Leaf className="h-5 w-5 text-leaf-600" aria-hidden /> {t('farm.regen.title')}
          </h3>
          <p className="mb-4 mt-1 text-sm text-ink-soft">{t('farm.regen.subtitle')}</p>
          <ol className="space-y-3">
            {data.recommendations.map((rec) => {
              const base = `regen.${rec.id}`;
              const basis = rec.triggers.map((tr) => triggerText(t, fmt, tr)).filter(Boolean) as string[];
              return (
                <li key={rec.id}>
                  <details className="group rounded-xl border border-line open:bg-paper/60">
                    <summary className="flex min-h-11 cursor-pointer list-none items-center justify-between gap-3 p-4 [&::-webkit-details-marker]:hidden">
                      <span className="min-w-0">
                        <span
                          className={cn(
                            'mb-1 inline-block rounded-full px-2 py-0.5 text-xs font-semibold',
                            rec.priority === 'high' ? 'bg-soil-100 text-soil-700' : rec.priority === 'medium' ? 'bg-leaf-50 text-leaf-700' : 'bg-paper text-ink-soft ring-1 ring-line',
                          )}
                        >
                          {t(`farm.regen.priority.${rec.priority}` as MessageKey)}
                        </span>
                        <span className="block font-semibold">{t(`${base}.title` as MessageKey)}</span>
                      </span>
                      <span aria-hidden className="text-ink-faint transition-transform group-open:rotate-180">▾</span>
                    </summary>
                    <dl className="grid gap-3 px-4 pb-4 text-sm sm:grid-cols-2">
                      {(['why', 'what', 'when', 'benefit'] as const).map((f) => (
                        <div key={f}>
                          <dt className="font-semibold">{t(`farm.regen.${f}` as MessageKey)}</dt>
                          <dd className="text-ink-soft">{t(`${base}.${f}` as MessageKey)}</dd>
                        </div>
                      ))}
                      <div className="sm:col-span-2">
                        <dt className="font-semibold">{t('farm.regen.basis')}</dt>
                        <dd className="text-ink-soft">{basis.length ? basis.join(' · ') : t('farm.regen.basisGeneral')}</dd>
                      </div>
                    </dl>
                  </details>
                </li>
              );
            })}
          </ol>
          {regen.status === 'error' && <ErrorState compact error={regen.error} onRetry={regen.reload} updatedAt={regen.updatedAt} />}
        </>
      ) : null}
    </Card>
  );
}

export function CropHealthCard({ health }: { health: Resource<CropHealth> }) {
  const { t, fmt } = useI18n();
  const h = health.data;
  return (
    <Card id="crop" aria-labelledby="crop-title" className="scroll-mt-header">
      <CardTitle icon={Satellite} id="crop-title">
        {t('farm.crop.title')}
      </CardTitle>
      {!h && health.status === 'loading' ? (
        <LoadingBlock lines={2} />
      ) : !h && health.status === 'error' ? (
        <ErrorState error={health.error} onRetry={health.reload} title={t('farm.crop.unavailable')} />
      ) : h ? (
        h.status === 'available' && h.ndvi != null ? (
          <>
            <div className="flex flex-wrap items-end gap-6">
              <div>
                <p className="text-sm text-ink-soft">{t('farm.crop.ndvi')}</p>
                <p className="text-3xl font-semibold tabular-nums">{fmt.num(h.ndvi, 2)}</p>
              </div>
              {h.change != null && (
                <div>
                  <p className="text-sm text-ink-soft">{t('farm.crop.change')}</p>
                  <p className={cn('flex items-center gap-1 text-xl font-semibold tabular-nums', h.change < 0 ? 'text-warn-700' : 'text-leaf-700')}>
                    {h.change < 0 ? <TrendingDown className="h-5 w-5" aria-hidden /> : <TrendingUp className="h-5 w-5" aria-hidden />}
                    {h.change > 0 ? '+' : ''}
                    {fmt.num(h.change, 2)}
                  </p>
                </div>
              )}
            </div>
            <p className="mt-3 text-sm text-ink-soft">{t('farm.crop.explain')}</p>
            {h.window && (
              <p className="mt-1 text-xs text-ink-faint">
                {t('farm.crop.images', { count: fmt.num(h.image_count ?? 0, 0), start: fmt.date(h.window.start), end: fmt.date(h.window.end) })}
              </p>
            )}
            <ProvenanceLine source={h.provenance.source} url={h.provenance.source_url} kind="satellite_observation" note={h.provenance.resolution} />
          </>
        ) : (
          <UnavailableNote>
            {t(h.reason === 'not_configured' ? 'farm.crop.notConfigured' : h.status === 'no_data' ? 'farm.crop.noImagery' : 'farm.crop.unavailable')}
            <span className="mt-1 block text-xs text-ink-faint">{t('farm.crop.explain')}</span>
          </UnavailableNote>
        )
      ) : null}
    </Card>
  );
}

export function KvkCard({ kvk }: { kvk: Resource<Kvk> }) {
  const { t, fmt } = useI18n();
  if (kvk.status !== 'success') return null; // optional helper: hide rather than show an error block
  const k = kvk.data;
  return (
    <Card aria-labelledby="kvk-title">
      <CardTitle icon={Building2} id="kvk-title">
        {t('farm.kvk.title')}
      </CardTitle>
      <p className="font-semibold">{k.name}</p>
      <p className="text-sm text-ink-soft">{t('farm.kvk.distance', { distance: fmt.num(k.distance_km, 0) })}</p>
      <ProvenanceLine
        source={k.provenance.source}
        kind="static_reference"
        note={
          <>
            {t('farm.kvk.verify')}{' '}
            {k.provenance.verify_url && (
              <a href={k.provenance.verify_url} target="_blank" rel="noopener noreferrer" className="underline underline-offset-2">
                kvk.icar.gov.in
              </a>
            )}
          </>
        }
      />
    </Card>
  );
}
