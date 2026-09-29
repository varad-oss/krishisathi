'use client';

import { Building2, ExternalLink, Layers, Leaf, RefreshCw, Satellite, TrendingDown, TrendingUp } from 'lucide-react';
import { useI18n } from '@/lib/i18n';
import type { Resource } from '@/lib/use-resource';
import type { CropHealth, Kvk, RegenerativeResponse, RegenTrigger, SoilData, SoilReason } from '@/lib/types';
import type { MessageKey } from '@/locales/en';
import { cn } from '@/lib/utils';
import { buttonClass, Card, CardTitle, ErrorState, LevelBadge, LoadingBlock, Note, ProvenanceLine, UnavailableNote } from '../ui';

const SOIL_REASON: Record<SoilReason, MessageKey> = {
  rate_limited: 'farm.soil.reason.rate_limited',
  timeout: 'farm.soil.reason.timeout',
  upstream_error: 'farm.soil.reason.provider',
  network_error: 'farm.soil.reason.provider',
  unknown_error: 'farm.soil.reason.provider',
  bad_response: 'farm.soil.reason.bad_response',
  request_rejected: 'farm.soil.reason.request_rejected',
  no_coverage: 'farm.soil.noData',
};

/** Soil values, or the specific reason SoilGrids could not provide them. Never shows placeholder values. */
function SoilProperties({ soil, onRetry }: { soil: SoilData; onRetry: () => void }) {
  const { t, fmt } = useI18n();
  if (soil.status !== 'available' || !soil.properties) {
    const key = soil.reason ? SOIL_REASON[soil.reason] ?? 'farm.soil.unavailable' : soil.status === 'no_data' ? 'farm.soil.noData' : 'farm.soil.unavailable';
    const retryable = soil.status === 'unavailable' && soil.retryable !== false;
    return (
      <UnavailableNote
        action={
          retryable ? (
            <button type="button" onClick={onRetry} className={cn(buttonClass.secondary, 'min-h-10 px-4 py-1.5')}>
              <RefreshCw className="h-4 w-4" aria-hidden /> {t('action.retry')}
            </button>
          ) : null
        }
      >
        <p className="font-semibold text-ink">{t(soil.status === 'no_data' ? 'farm.soil.noDataTitle' : 'farm.soil.unavailableTitle')}</p>
        <p className="mt-0.5">{t(key)}</p>
        <p className="mt-2 text-xs text-ink-faint">
          {t('provenance.source')}: <span lang="en">ISRIC SoilGrids 2.0</span>
        </p>
      </UnavailableNote>
    );
  }
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
      <dl className="grid grid-cols-2 overflow-hidden rounded-[var(--radius-inner)] bg-soil-50/70 ring-1 ring-soil-100 sm:grid-cols-4">
        {items.map((i, idx) => (
          <div key={i.label} className={cn('p-4', idx % 2 === 1 && 'border-l border-soil-100', idx >= 2 && 'border-t border-soil-100 sm:border-t-0', idx === 2 && 'sm:border-l')}>
            <dt className="text-xs font-medium text-soil-700">{i.label}</dt>
            <dd className="mt-1 font-display text-2xl font-medium tabular-nums">{i.value}</dd>
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
          note={
            <>
              {t('farm.soil.provenanceNote')}{' '}
              {soil.ratings?.source ? <a className="underline underline-offset-2" href={soil.ratings.source.url} target="_blank" rel="noopener noreferrer" lang="en">{soil.ratings.source.name}</a> : null}
            </>
          }
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
      <CardTitle icon={Layers} id="soil-title" description={t('farm.soil.subtitle')}>
        {t('farm.soil.title')}
      </CardTitle>
      {!data && regen.status === 'loading' ? (
        <LoadingBlock lines={4} />
      ) : !data && regen.status === 'error' ? (
        <ErrorState error={regen.error} onRetry={regen.reload} title={t('farm.regen.unavailable')} />
      ) : data ? (
        <>
          <SoilProperties soil={data.soil} onRetry={regen.reload} />

          <h3 className="mt-10 flex items-center gap-2 font-display text-xl font-medium">
            <Leaf className="h-5 w-5 text-leaf-600" aria-hidden /> {t('farm.regen.title')}
          </h3>
          <p className="mb-4 mt-1 text-sm text-ink-soft">{t('farm.regen.subtitle')}</p>
          <ol className="divide-y divide-line overflow-hidden rounded-[var(--radius-inner)] ring-1 ring-line">
            {data.recommendations.map((rec, index) => {
              const base = `regen.${rec.id}`;
              const basis = rec.triggers.map((tr) => triggerText(t, fmt, tr)).filter(Boolean) as string[];
              return (
                <li key={rec.id}>
                  <details className="group bg-surface open:bg-paper/50">
                    <summary className="flex min-h-11 cursor-pointer list-none items-center justify-between gap-3 p-4">
                      <span className="flex min-w-0 items-start gap-3">
                        <span aria-hidden className="mt-0.5 font-display text-lg leading-none text-soil-500 tabular-nums">{fmt.num(index + 1, 0)}</span>
                        <span className="min-w-0">
                          <span className="block font-semibold leading-snug">{t(`${base}.title` as MessageKey)}</span>
                          <span
                            className={cn(
                              'mt-1 inline-flex items-center gap-1.5 text-xs font-medium',
                              rec.priority === 'high' ? 'text-soil-700' : rec.priority === 'medium' ? 'text-leaf-700' : 'text-ink-faint',
                            )}
                          >
                            <span aria-hidden className={cn('h-1.5 w-1.5 rounded-full', rec.priority === 'high' ? 'bg-soil-500' : rec.priority === 'medium' ? 'bg-leaf-500' : 'bg-line-strong')} />
                            {t(`farm.regen.priority.${rec.priority}` as MessageKey)}
                          </span>
                        </span>
                      </span>
                      <span aria-hidden className="text-ink-faint transition-transform group-open:rotate-180">▾</span>
                    </summary>
                    <dl className="grid gap-3 px-4 pb-4 text-sm sm:grid-cols-2 sm:pl-11">
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
                <p className="font-display text-4xl font-medium tabular-nums">{fmt.num(h.ndvi, 2)}</p>
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
  const portal = (
    <a href="https://kvk.icar.gov.in/" target="_blank" rel="noopener noreferrer" className="inline-flex min-h-10 items-center gap-1 text-sm font-semibold text-leaf-700 underline-offset-2 hover:underline">
      {t('farm.kvk.portal')} <ExternalLink className="h-3.5 w-3.5" aria-hidden />
    </a>
  );
  const k = kvk.data;
  return (
    <Card aria-labelledby="kvk-title">
      <CardTitle icon={Building2} id="kvk-title">
        {t('farm.kvk.title')}
      </CardTitle>
      {kvk.status === 'loading' && !k ? (
        <LoadingBlock lines={2} />
      ) : kvk.status === 'error' && kvk.error.code === 'NOT_FOUND' ? (
        <UnavailableNote action={portal}>{t('farm.kvk.notFound')}</UnavailableNote>
      ) : kvk.status === 'error' && !k ? (
        <ErrorState error={kvk.error} onRetry={kvk.reload} title={t('farm.kvk.unavailable')} />
      ) : k ? (
        <>
          <p className="font-display text-xl font-medium" lang="en">{k.name}</p>
          <p className="mt-1 text-sm text-ink-soft">
            {k.match === 'site' && k.distance_km != null
              ? t('farm.kvk.distance', { distance: fmt.num(k.distance_km, k.distance_km < 10 ? 1 : 0) })
              : t('farm.kvk.district', { district: k.district })}
          </p>
          {k.match === 'district' && <p className="mt-3 text-xs text-ink-faint">{t('farm.kvk.districtNote')}</p>}
          <div className="mt-2">{portal}</div>
          <ProvenanceLine source={k.provenance.source} kind="static_reference" className="mt-4" note={t('farm.kvk.verify')} />
        </>
      ) : null}
    </Card>
  );
}
