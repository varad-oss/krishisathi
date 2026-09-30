'use client';

import { useState } from 'react';
import { Building2, Cloud, ExternalLink, Leaf, Minus, Radio, RefreshCw, ScanLine, TrendingDown, TrendingUp } from 'lucide-react';
import { getCropHealthHistory, getFieldCropHealthHistory } from '@/lib/api';
import { useI18n } from '@/lib/i18n';
import { useResource, type Resource } from '@/lib/use-resource';
import type { CropHealth, CropHealthHistory, FarmPlot, FarmTwin, SatelliteQuality, Kvk, RegenerativeResponse, RegenTrigger, SarSummary, SoilData, SoilReason } from '@/lib/types';
import type { MessageKey } from '@/locales/en';
import { cn } from '@/lib/utils';
import { FieldOutline } from './FieldPlot';
import { PracticePlan } from './Regenerative';
import { buttonClass, ErrorState, LevelBadge, linkClass, LoadingBlock, Note, ProvenanceLine, SavedCopyTag, Section, UnavailableNote } from '../ui';

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
      <dl className="grid grid-cols-2 gap-px overflow-hidden rounded-[var(--radius-inner)] border border-soil-100 bg-soil-100 sm:grid-cols-4">
        {items.map((i) => (
          <div key={i.label} className="bg-soil-50 p-4">
            <dt className="text-sm font-medium text-soil-700">{i.label}</dt>
            <dd className="mt-1 font-display text-2xl tabular-nums">{i.value}</dd>
            {'rating' in i && i.rating && <dd className="text-sm text-ink-soft">{i.rating}</dd>}
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
    <Section id="soil" title={t('farm.soil.title')} description={t('farm.soil.subtitle')} action={regen.cached && regen.updatedAt ? <SavedCopyTag time={regen.updatedAt} /> : undefined}>
      {!data && regen.status === 'loading' ? (
        <LoadingBlock lines={4} />
      ) : !data && regen.status === 'error' ? (
        <ErrorState error={regen.error} onRetry={regen.reload} title={t('farm.regen.unavailable')} />
      ) : data ? (
        <>
          <SoilProperties soil={data.soil} onRetry={regen.reload} />

          <h3 className="mt-12 flex items-center gap-2 font-display text-xl">
            <Leaf className="h-5 w-5 text-leaf-600" aria-hidden /> {t('farm.regen.title')}
          </h3>
          <p className="mb-5 mt-1 max-w-[62ch] text-ink-soft">{t('farm.regen.subtitle')}</p>
          <PracticePlan data={data} twin={twin} onSaved={onSaved} triggerText={(tr) => triggerText(t, fmt, tr)} />
          {regen.status === 'error' && <div className="mt-4"><ErrorState compact error={regen.error} onRetry={regen.reload} updatedAt={regen.updatedAt} /></div>}
        </>
      ) : null}
    </Section>
  );
}

// Same screening threshold as the risk engine (services/risk_engine.py NDVI_DECLINE): smaller changes are "about the same".
const NDVI_CHANGE = 0.1;

function Radar({ sar }: { sar: SarSummary }) {
  const { t, fmt } = useI18n();
  const signed = (v: number) => `${v > 0 ? '+' : ''}${fmt.num(v, 1)}`;
  return (
    <div className="border-t border-line py-4 text-sm">
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
          <p className="mt-1 text-xs text-ink-soft">{t('farm.crop.radar.note')}</p>
        </>
      ) : (
        <p className="mt-1 text-ink-faint">{t(sar.status === 'no_data' ? 'farm.crop.radar.noData' : sar.status === 'insufficient_data' ? 'farm.crop.fieldTooSmall' : 'farm.crop.radar.unavailable')}</p>
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

function SatelliteHistory({ lat, lng, twin }: { lat: number; lng: number; twin: FarmTwin | null }) {
  const { t, fmt } = useI18n();
  const [open, setOpen] = useState(false);
  // With a farm record the series follows the drawn field (or the point, when there is none).
  const history = useResource(
    open ? (s) => (twin ? getFieldCropHealthHistory(twin, s) : getCropHealthHistory(lat, lng, s)) : null,
    [open, lat, lng, twin?.farmId],
  );
  const d = history.data;
  return (
    <details className="group border-t border-line pt-2" onToggle={(e) => setOpen((e.target as HTMLDetailsElement).open)}>
      <summary className={cn(linkClass, 'cursor-pointer list-none')}>
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

const QUALITY_TONE: Record<SatelliteQuality['level'], string> = { good: 'text-leaf-700', limited: 'text-watch-700', insufficient: 'text-warn-700' };

/** How much the satellite value can be trusted for this field: pixels, clear share, land cover and flags. */
function QualityDetails({ h }: { h: CropHealth }) {
  const { t, fmt } = useI18n();
  const q = h.quality;
  if (!q) return null;
  const pct = (v: number | null | undefined) => fmt.num(v == null ? null : Math.round(v * 100), 0);
  const lc = q.land_cover;
  return (
    <details className="group border-t border-line py-2 text-sm" data-testid="satellite-quality">
      <summary className="inline-flex min-h-11 cursor-pointer list-none flex-wrap items-center gap-x-2 gap-y-1">
        <span className="font-semibold">{t('farm.crop.quality.title')}:</span>
        <span className={cn('font-semibold', QUALITY_TONE[q.level])}>{t(`farm.crop.quality.level.${q.level}` as MessageKey)}</span>
        <span aria-hidden className="text-ink-faint transition-transform group-open:rotate-180">▾</span>
      </summary>
      <ul className="mt-1 space-y-1 text-ink-soft">
        {h.image_count != null && <li>{t('farm.crop.quality.scenes', { count: fmt.num(h.image_count, 0) })}</li>}
        <li>{t('farm.crop.quality.pixels', { clear: fmt.num(q.clear_pixel_count, 0), total: fmt.num(q.pixel_count, 0), pct: pct(q.clear_pixel_fraction) })}</li>
        {lc.status === 'available' && <li>{t('farm.crop.quality.cropland', { pct: pct(lc.cropland_fraction) })}</li>}
        {q.flags.map((f) => (
          <li key={f} className="text-watch-700">{t(`farm.crop.quality.flag.${f}` as MessageKey)}</li>
        ))}
      </ul>
      <p className="mt-2 text-xs text-ink-soft" lang="en">{q.method}; {q.resolution_m} m. {lc.status === 'available' ? lc.provenance.source : null}</p>
    </details>
  );
}

function Scope({ h }: { h: CropHealth }) {
  const { t, fmt } = useI18n();
  const roi = h.roi;
  if (!roi) return null;
  return (
    <p className="mb-4 inline-flex items-start gap-2 rounded-[var(--radius-tag)] bg-paper-deep/60 px-2.5 py-1.5 text-sm text-ink" data-testid="satellite-scope">
      <ScanLine className="mt-0.5 h-4 w-4 shrink-0 text-ink-soft" aria-hidden />
      <span>
        {roi.mode === 'polygon'
          ? t('farm.crop.scope.field', { area: fmt.num(roi.area_ha, roi.area_ha < 1 ? 2 : 1) })
          : t('farm.crop.scope.point')}
      </span>
    </p>
  );
}

export function CropHealthCard({
  health,
  location,
  twin,
  plot,
  onPlotChanged,
}: {
  health: Resource<CropHealth>;
  location: { lat: number; lng: number };
  twin: FarmTwin | null;
  plot: Resource<{ plot: FarmPlot | null }>;
  onPlotChanged: () => void;
}) {
  const { t, fmt } = useI18n();
  const h = health.data;
  const b = h?.baseline;
  const trend = h?.change == null ? null : h.change <= -NDVI_CHANGE ? 'decline' : h.change >= NDVI_CHANGE ? 'increase' : 'stable';
  const TrendIcon = trend === 'decline' ? TrendingDown : trend === 'increase' ? TrendingUp : Minus;
  const unavailableText = (x: CropHealth) =>
    x.reason === 'not_configured'
      ? t('farm.crop.notConfigured')
      : x.status === 'insufficient_data'
        ? t(x.reason === 'field_too_small' ? 'farm.crop.fieldTooSmall' : 'farm.crop.tooFewClearPixels')
        : x.status === 'no_data'
          ? t('farm.crop.noImagery')
          : t('farm.crop.unavailable');
  return (
    <Section
      id="crop"
      eyebrow={t('farm.crop.signalTitle')}
      title={t('farm.crop.fromAbove')}
      action={health.cached && health.updatedAt ? <SavedCopyTag time={health.updatedAt} /> : undefined}
    >
      <FieldOutline twin={twin} center={location} plot={plot} onChanged={onPlotChanged} />
      <div className="mt-6">
        {!h && health.status === 'loading' ? (
          <LoadingBlock lines={2} />
        ) : !h && health.status === 'error' ? (
          <ErrorState error={health.error} onRetry={health.reload} title={t('farm.crop.unavailable')} />
        ) : h ? (
          <>
            <Scope h={h} />
            {h.status === 'available' && h.ndvi != null ? (
              <>
                {/* The observation in words first; the index behind it underneath. */}
                <div className="flex flex-wrap items-end gap-x-10 gap-y-4">
                  {h.change != null && trend && (
                    <div>
                      <p className="text-sm text-ink-soft">{t('farm.crop.change')}</p>
                      <p className={cn('mt-0.5 flex items-center gap-2 font-display text-2xl', trend === 'decline' ? 'text-warn-700' : trend === 'increase' ? 'text-leaf-700' : 'text-ink')}>
                        <TrendIcon className="h-6 w-6" aria-hidden />
                        {t(`farm.crop.trend.${trend}` as MessageKey)}
                      </p>
                    </div>
                  )}
                  <div>
                    <p className="text-sm text-ink-soft">{t('farm.crop.ndvi')}</p>
                    <p className="mt-0.5 flex items-baseline gap-2">
                      <span className="font-display text-2xl tabular-nums" data-testid="ndvi-value">{fmt.num(h.ndvi, 2)}</span>
                      {h.change != null && <span className="text-sm tabular-nums text-ink-soft">({h.change > 0 ? '+' : ''}{fmt.num(h.change, 2)})</span>}
                    </p>
                  </div>
                </div>
                {b && (
                  <p className="mt-4 max-w-[62ch]">
                    {b.status === 'available' && b.position && b.min != null && b.max != null
                      ? t(`farm.crop.baseline.${b.position === 'below_range' ? 'below' : b.position === 'above_range' ? 'above' : 'within'}` as MessageKey, {
                          min: fmt.num(b.min, 2),
                          max: fmt.num(b.max, 2),
                        })
                      : <span className="text-ink-soft">{t('farm.crop.baseline.insufficient')}</span>}
                  </p>
                )}
                {h.latest_image_date && h.clear_pixel_fraction != null && (
                  <p className="mt-1.5 flex items-start gap-2 text-sm text-ink-soft">
                    <Cloud className="mt-0.5 h-4 w-4 shrink-0" aria-hidden />
                    {t('farm.crop.quality', { date: fmt.date(h.latest_image_date), pct: fmt.num(Math.round(h.clear_pixel_fraction * 100), 0) })}
                  </p>
                )}
                <Note tone="info" className="my-4">{t('farm.crop.indicatorNote')}</Note>
              </>
            ) : (
              <UnavailableNote className="mb-4">
                <span data-testid="satellite-unavailable">{unavailableText(h)}</span>
                <span className="mt-1 block text-xs text-ink-soft">{t('farm.crop.explain')}</span>
              </UnavailableNote>
            )}
            <QualityDetails h={h} />
            {h.sar && <Radar sar={h.sar} />}
            {h.status !== 'unavailable' && <SatelliteHistory lat={location.lat} lng={location.lng} twin={twin} />}
            {h.status !== 'unavailable' && (
              <ProvenanceLine
                source={h.sar ? 'Sentinel-1 + Sentinel-2 (Copernicus) via Google Earth Engine' : h.provenance.source}
                url={h.provenance.source_url}
                kind="satellite_observation"
                note={<>{t('farm.crop.explain')} <span lang="en">{h.provenance.resolution}</span></>}
              />
            )}
          </>
        ) : null}
      </div>
    </Section>
  );
}

export function KvkCard({ kvk }: { kvk: Resource<Kvk> }) {
  const { t, fmt } = useI18n();
  const portal = (
    <a href="https://kvk.icar.gov.in/" target="_blank" rel="noopener noreferrer" className={linkClass}>
      {t('farm.kvk.portal')} <ExternalLink className="h-3.5 w-3.5" aria-hidden />
    </a>
  );
  const k = kvk.data;
  return (
    <Section id="kvk" title={t('farm.kvk.title')}>
      {kvk.status === 'loading' && !k ? (
        <LoadingBlock lines={2} />
      ) : kvk.status === 'error' && kvk.error.code === 'NOT_FOUND' ? (
        <UnavailableNote action={portal}>{t('farm.kvk.notFound')}</UnavailableNote>
      ) : kvk.status === 'error' && !k ? (
        <ErrorState error={kvk.error} onRetry={kvk.reload} title={t('farm.kvk.unavailable')} />
      ) : k ? (
        <div className="flex items-start gap-3">
          <Building2 className="mt-1 h-5 w-5 shrink-0 text-soil-500" aria-hidden />
          <div className="min-w-0 flex-1">
            <p className="font-display text-xl" lang="en">{k.name}</p>
            <p className="mt-0.5 text-ink-soft">
              {k.match === 'site' && k.distance_km != null
                ? t('farm.kvk.distance', { distance: fmt.num(k.distance_km, k.distance_km < 10 ? 1 : 0) })
                : t('farm.kvk.district', { district: k.district })}
            </p>
            {k.match === 'district' && <p className="mt-2 text-sm text-ink-soft">{t('farm.kvk.districtNote')}</p>}
            <div className="mt-1">{portal}</div>
            <ProvenanceLine source={k.provenance.source} kind="static_reference" className="mt-3" note={t('farm.kvk.verify')} />
          </div>
        </div>
      ) : null}
    </Section>
  );
}
