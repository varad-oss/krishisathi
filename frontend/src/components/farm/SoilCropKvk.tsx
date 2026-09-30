'use client';

import { useState } from 'react';
import { Building2, ExternalLink, Layers, Leaf, Minus, Radio, RefreshCw, Satellite, TrendingDown, TrendingUp } from 'lucide-react';
import { getCropHealthHistory } from '@/lib/api';
import { useI18n } from '@/lib/i18n';
import { useResource, type Resource } from '@/lib/use-resource';
import type { CropHealth, CropHealthHistory, FarmTwin, Kvk, RegenerativeResponse, RegenTrigger, SarSummary, SoilData, SoilReason } from '@/lib/types';
import type { MessageKey } from '@/locales/en';
import { cn } from '@/lib/utils';
import { PracticePlan } from './Regenerative';
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

export function SoilRegenCard({ regen, twin, onSaved }: { regen: Resource<RegenerativeResponse>; twin: FarmTwin | null; onSaved?: () => void }) {
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
          <PracticePlan data={data} twin={twin} onSaved={onSaved} triggerText={(tr) => triggerText(t, fmt, tr)} />
          {regen.status === 'error' && <ErrorState compact error={regen.error} onRetry={regen.reload} updatedAt={regen.updatedAt} />}
        </>
      ) : null}
    </Card>
  );
}

// Same screening threshold as the risk engine (services/risk_engine.py NDVI_DECLINE): smaller changes are "about the same".
const NDVI_CHANGE = 0.1;

function Radar({ sar }: { sar: SarSummary }) {
  const { t, fmt } = useI18n();
  const signed = (v: number) => `${v > 0 ? '+' : ''}${fmt.num(v, 1)}`;
  return (
    <div className="mt-4 rounded-[var(--radius-inner)] bg-paper/70 p-3 text-sm">
      <p className="flex items-center gap-1.5 font-semibold">
        <Radio className="h-4 w-4 text-sky-700" aria-hidden /> {t('farm.crop.radar.title')}
      </p>
      {sar.status === 'available' && sar.vh_db != null ? (
        <>
          <p className="mt-1 tabular-nums text-ink-soft">
            {sar.vh_change_db != null
              ? t('farm.crop.radar.values', { vh: fmt.num(sar.vh_db, 1), change: signed(sar.vh_change_db) })
              : t('farm.crop.radar.valuesNoChange', { vh: fmt.num(sar.vh_db, 1) })}
            {sar.latest_image_date && ` · ${fmt.date(sar.latest_image_date)}`}
          </p>
          {sar.water_signal && <Note tone="watch" className="mt-2">{t('farm.crop.radar.water')}</Note>}
          <p className="mt-1 text-xs text-ink-faint">{t('farm.crop.radar.note')}</p>
        </>
      ) : (
        <p className="mt-1 text-ink-faint">{t(sar.status === 'no_data' ? 'farm.crop.radar.noData' : 'farm.crop.radar.unavailable')}</p>
      )}
    </div>
  );
}

function Sparkline({ series }: { series: NonNullable<CropHealthHistory['series']> }) {
  const w = 300;
  const h = 80;
  const x = (i: number) => 12 + (i * (w - 24)) / Math.max(1, series.length - 1);
  const y = (v: number) => h - 8 - Math.max(0, Math.min(1, v)) * (h - 16);
  // Lines join only neighbouring windows that both have a reading: a gap stays a gap.
  const segments = series.slice(1).map((p, i) => (p.ndvi != null && series[i].ndvi != null ? `M${x(i)},${y(series[i].ndvi!)} L${x(i + 1)},${y(p.ndvi)}` : ''));
  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="h-20 w-full" aria-hidden>
      <line x1="0" x2={w} y1={y(0)} y2={y(0)} className="stroke-line" />
      <path d={segments.join(' ')} className="fill-none stroke-leaf-600" strokeWidth="2" />
      {series.map((p, i) =>
        p.ndvi != null ? <circle key={p.end} cx={x(i)} cy={y(p.ndvi)} r="3.5" className="fill-leaf-600" /> : <circle key={p.end} cx={x(i)} cy={y(0)} r="3" className="fill-none stroke-line-strong" />,
      )}
    </svg>
  );
}

function SatelliteHistory({ lat, lng }: { lat: number; lng: number }) {
  const { t, fmt } = useI18n();
  const [open, setOpen] = useState(false);
  const history = useResource(open ? (s) => getCropHealthHistory(lat, lng, s) : null, [open, lat, lng]);
  const d = history.data;
  return (
    <details className="group mt-4" onToggle={(e) => setOpen((e.target as HTMLDetailsElement).open)}>
      <summary className="inline-flex min-h-10 cursor-pointer list-none items-center gap-1 text-sm font-semibold text-leaf-700 hover:underline">
        {t('farm.crop.history.show')} <span aria-hidden className="transition-transform group-open:rotate-180">▾</span>
      </summary>
      <div className="mt-2">
        {history.status === 'loading' ? (
          <LoadingBlock lines={2} />
        ) : history.status === 'error' ? (
          <ErrorState compact error={history.error} onRetry={history.reload} title={t('farm.crop.history.unavailable')} />
        ) : d?.status === 'unavailable' || !d?.series ? (
          d ? <UnavailableNote>{t('farm.crop.history.unavailable')}</UnavailableNote> : null
        ) : (
          <>
            <p className="text-sm font-semibold">{t('farm.crop.history.title')}</p>
            {d.status === 'insufficient_data' && <p className="text-sm text-ink-soft">{t('farm.crop.history.insufficient')}</p>}
            <Sparkline series={d.series} />
            <table className="mt-1 w-full text-xs">
              <caption className="sr-only">{t('farm.crop.history.chartLabel')}</caption>
              <tbody className="flex justify-between gap-1">
                {d.series.map((p) => (
                  <tr key={p.end} className="flex flex-col items-center">
                    <th scope="row" className="font-normal text-ink-faint">{fmt.date(p.end, { month: 'short' })}</th>
                    <td className="tabular-nums">{p.ndvi != null ? fmt.num(p.ndvi, 2) : <span className="text-ink-faint">{t('farm.crop.history.noImage')}</span>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}
      </div>
    </details>
  );
}

export function CropHealthCard({ health, location }: { health: Resource<CropHealth>; location: { lat: number; lng: number } }) {
  const { t, fmt } = useI18n();
  const h = health.data;
  const b = h?.baseline;
  const trend = h?.change == null ? null : h.change <= -NDVI_CHANGE ? 'decline' : h.change >= NDVI_CHANGE ? 'increase' : 'stable';
  const TrendIcon = trend === 'decline' ? TrendingDown : trend === 'increase' ? TrendingUp : Minus;
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
        <>
          {h.status === 'available' && h.ndvi != null ? (
            <>
              <div className="flex flex-wrap items-end gap-6">
                <div>
                  <p className="text-sm text-ink-soft">{t('farm.crop.ndvi')}</p>
                  <p className="font-display text-4xl font-medium tabular-nums">{fmt.num(h.ndvi, 2)}</p>
                </div>
                {h.change != null && trend && (
                  <div>
                    <p className="text-sm text-ink-soft">{t('farm.crop.change')}</p>
                    <p className={cn('flex items-center gap-1 text-lg font-semibold', trend === 'decline' ? 'text-warn-700' : 'text-leaf-700')}>
                      <TrendIcon className="h-5 w-5" aria-hidden />
                      {t(`farm.crop.trend.${trend}` as MessageKey)}
                      <span className="text-sm font-normal tabular-nums text-ink-soft">({h.change > 0 ? '+' : ''}{fmt.num(h.change, 2)})</span>
                    </p>
                  </div>
                )}
              </div>
              {b && (
                <p className="mt-3 text-sm">
                  {b.status === 'available' && b.position && b.min != null && b.max != null
                    ? t(`farm.crop.baseline.${b.position === 'below_range' ? 'below' : b.position === 'above_range' ? 'above' : 'within'}` as MessageKey, {
                        min: fmt.num(b.min, 2),
                        max: fmt.num(b.max, 2),
                      })
                    : <span className="text-ink-soft">{t('farm.crop.baseline.insufficient')}</span>}
                </p>
              )}
              {h.latest_image_date && h.clear_pixel_fraction != null && (
                <p className="mt-1 text-xs text-ink-faint">
                  {t('farm.crop.quality', { date: fmt.date(h.latest_image_date), pct: fmt.num(Math.round(h.clear_pixel_fraction * 100), 0) })}
                </p>
              )}
              <p className="mt-3 text-sm text-ink-soft">{t('farm.crop.explain')}</p>
            </>
          ) : (
            <UnavailableNote>
              {t(h.reason === 'not_configured' ? 'farm.crop.notConfigured' : h.status === 'no_data' ? 'farm.crop.noImagery' : 'farm.crop.unavailable')}
              <span className="mt-1 block text-xs text-ink-faint">{t('farm.crop.explain')}</span>
            </UnavailableNote>
          )}
          {h.sar && <Radar sar={h.sar} />}
          {h.status !== 'unavailable' && <SatelliteHistory lat={location.lat} lng={location.lng} />}
          {h.status !== 'unavailable' && (
            <ProvenanceLine source={h.sar ? 'Sentinel-1 + Sentinel-2 (Copernicus) via Google Earth Engine' : h.provenance.source} url={h.provenance.source_url} kind="satellite_observation" note={h.provenance.resolution} />
          )}
        </>
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
