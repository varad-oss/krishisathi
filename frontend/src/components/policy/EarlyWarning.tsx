'use client';

import { Bug, CloudSun, Satellite, Siren, TrendingDown, TrendingUp } from 'lucide-react';
import { useI18n } from '@/lib/i18n';
import type { Resource } from '@/lib/use-resource';
import type { DiseaseSignal, EarlyWarning, StateConfig, WeatherThreat } from '@/lib/types';
import type { MessageKey } from '@/locales/en';
import { cn } from '@/lib/utils';
import { insightView } from '../farm/insight-text';
import { Card, CardTitle, ErrorState, LevelBadge, LoadingBlock, Note, severityDot, UnavailableNote } from '../ui';

/**
 * What every chart and map on the policy dashboard must state: period, geography, number of observations,
 * source and limitations. `source` is optional where a ProvenanceLine already shows it.
 */
export function VizMeta({ period, geography, observations, source, limits, className }: { period: string; geography: string; observations: string; source?: string; limits: string; className?: string }) {
  const { t } = useI18n();
  const rows: [MessageKey, string | undefined][] = [
    ['viz.period', period],
    ['viz.geography', geography],
    ['viz.observations', observations],
    ['viz.source', source],
    ['viz.limits', limits],
  ];
  return (
    <dl className={cn('mt-5 grid gap-x-6 gap-y-1 border-t border-dashed border-line pt-3 text-xs sm:grid-cols-2', className)}>
      {rows.filter(([, v]) => v).map(([k, v]) => (
        <div key={k} className="flex gap-1.5">
          <dt className="shrink-0 font-semibold text-ink-soft">{t(k)}:</dt>
          <dd className="min-w-0 text-ink-faint [overflow-wrap:anywhere]">{v}</dd>
        </div>
      ))}
    </dl>
  );
}

const TREND_ICON = { new: Siren, rising: TrendingUp, falling: TrendingDown, steady: null } as const;

function DiseaseItem({ s }: { s: DiseaseSignal }) {
  const { t, fmt } = useI18n();
  const Icon = TREND_ICON[s.trend];
  return (
    <li className="space-y-1 border-t border-line pt-3 text-sm first:border-t-0 first:pt-0">
      <div className="flex flex-wrap items-center gap-2">
        <span className="font-semibold" lang="en">{s.disease}</span>
        <span className={cn('inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium', s.trend === 'falling' || s.trend === 'steady' ? 'bg-paper text-ink-soft' : 'bg-watch-50 text-watch-700')}>
          {Icon && <Icon className="h-3 w-3" aria-hidden />} {t(`policy.ew.trend.${s.trend}` as MessageKey)}
        </span>
        {s.severity && <LevelBadge level={s.severity} />}
      </div>
      <p className="text-ink-soft">{t('policy.ew.reports', { count: fmt.num(s.observations, 0), previous: fmt.num(s.observations_previous, 0) })}</p>
      <p className="text-ink-soft">{t('policy.ew.confidence', { level: t(`level.${s.confidence}` as MessageKey) })}</p>
      <p className="text-xs text-ink-faint">
        {t('policy.ew.area', { lat: fmt.num(s.geography.lat, 2), lng: fmt.num(s.geography.lng, 2) })}
        {s.crops.length > 0 && ` · ${s.crops.map((c) => t(`crop.${c}` as MessageKey)).join(', ')}`}
        {` · ${t('policy.ew.lastReport', { time: fmt.relative(s.last_report) })}`}
      </p>
    </li>
  );
}

function WeatherByState({ threats, states }: { threats: WeatherThreat[]; states: StateConfig[] }) {
  const { t, fmt } = useI18n();
  const byState = new Map<string, WeatherThreat[]>();
  for (const th of threats) byState.set(th.state, [...(byState.get(th.state) ?? []), th]);
  const name = (code: string) => (states.some((s) => s.code === code) ? t(`state.${code}` as MessageKey) : code);
  return (
    <ul className="space-y-3">
      {[...byState.entries()].map(([state, list]) => {
        const v = insightView(t, fmt, list[0]);
        return (
          <li key={state} className="flex items-start gap-2 border-t border-line pt-3 text-sm first:border-t-0 first:pt-0">
            <span aria-hidden className={cn('mt-1.5 h-2 w-2 shrink-0 rounded-full', severityDot[list[0].severity])} />
            <span className="min-w-0">
              <span className="font-semibold">{name(state)}</span>
              <span className="block text-ink-soft">
                {v.title}
                <span className="sr-only"> ({t(`severity.${list[0].severity}` as MessageKey)})</span>
                {list.length > 1 && <span className="text-ink-faint"> · {t('policy.ew.weather.more', { count: fmt.num(list.length - 1, 0) })}</span>}
              </span>
            </span>
          </li>
        );
      })}
    </ul>
  );
}

/** Early warning: disease signals, weather threats and crop-health anomalies, each with its evidence. */
export function EarlyWarningPanel({ ew, states, stateFilter }: { ew: Resource<EarlyWarning>; states: StateConfig[]; stateFilter: string }) {
  const { t, fmt } = useI18n();
  const d = ew.data;
  const threats = d?.weather.threats.filter((w) => stateFilter === 'ALL' || w.state === stateFilter) ?? [];
  const range = d ? t('viz.periodRange', { start: fmt.date(d.period.start), end: fmt.date(d.period.end) }) : '';
  const section = 'min-w-0 rounded-[var(--radius-inner)] bg-paper/60 p-4 ring-1 ring-line';
  const heading = 'mb-3 flex items-center gap-2 text-sm font-semibold';
  return (
    <Card aria-labelledby="ew-title" id="early-warning">
      <CardTitle icon={Siren} id="ew-title" description={t('policy.ew.subtitle')}>
        {t('policy.ew.title')}
      </CardTitle>
      {!d && ew.status === 'loading' ? (
        <LoadingBlock lines={5} />
      ) : !d && ew.status === 'error' ? (
        <ErrorState error={ew.error} onRetry={ew.reload} />
      ) : d ? (
        <>
          {d.coverage.insufficient_data && (
            <Note tone="watch" className="mb-4">
              {t('policy.ew.insufficient', { count: fmt.num(d.coverage.observations_14d, 0), min: fmt.num(d.coverage.min_observations, 0) })}
            </Note>
          )}
          <div className="grid gap-4 lg:grid-cols-3">
            <section aria-labelledby="ew-disease" className={section}>
              <h3 id="ew-disease" className={heading}><Bug className="h-4 w-4 text-soil-700" aria-hidden /> {t('policy.ew.disease.title')}</h3>
              {d.disease.signals.length ? (
                <ul className="space-y-3">{d.disease.signals.map((s) => <DiseaseItem key={`${s.disease}:${s.geography.lat},${s.geography.lng}`} s={s} />)}</ul>
              ) : (
                <p className="text-sm text-ink-soft">{t('policy.ew.disease.empty', { min: fmt.num(d.disease.method.min_reports, 0) })}</p>
              )}
              {d.disease.below_threshold > 0 && (
                <p className="mt-3 text-xs text-ink-faint">{t('policy.ew.disease.below', { count: fmt.num(d.disease.below_threshold, 0), min: fmt.num(d.disease.method.min_reports, 0) })}</p>
              )}
            </section>
            <section aria-labelledby="ew-weather" className={section}>
              <h3 id="ew-weather" className={heading}><CloudSun className="h-4 w-4 text-sky-700" aria-hidden /> {t('policy.ew.weather.title')}</h3>
              {threats.length ? <WeatherByState threats={threats} states={states} /> : <p className="text-sm text-ink-soft">{t('policy.ew.weather.empty')}</p>}
              {d.weather.states_unavailable.length > 0 && (
                <p className="mt-3 text-xs text-ink-faint">
                  {t('policy.ew.weather.unavailable', { states: d.weather.states_unavailable.map((c) => (states.some((s) => s.code === c) ? t(`state.${c}` as MessageKey) : c)).join(', ') })}
                </p>
              )}
            </section>
            <section aria-labelledby="ew-crop" className={section}>
              <h3 id="ew-crop" className={heading}><Satellite className="h-4 w-4 text-leaf-700" aria-hidden /> {t('policy.ew.crop.title')}</h3>
              <UnavailableNote>{t(d.crop_health.reason === 'not_configured' ? 'policy.ew.crop.notConfigured' : 'policy.health.unavailable')}</UnavailableNote>
            </section>
          </div>
          <details className="mt-4 text-sm text-ink-soft">
            <summary className="flex min-h-11 cursor-pointer items-center font-semibold">{t('policy.ew.methodTitle')}</summary>
            <p className="mt-2">{t('policy.ew.method', { min: fmt.num(d.disease.method.min_reports, 0) })}</p>
          </details>
          <VizMeta
            period={`${range} (${t('policy.ew.comparedWith', { start: fmt.date(d.period.compared_with.start), end: fmt.date(d.period.compared_with.end) })})`}
            geography={t('policy.ew.geo')}
            observations={t('policy.ew.obs', { count: fmt.num(d.coverage.observations_14d, 0), cells: fmt.num(d.coverage.grid_cells_14d, 0) })}
            source={`${t('policy.ew.source')}; ${d.weather.provenance.source}`}
            limits={t('policy.ew.limits')}
          />
        </>
      ) : null}
    </Card>
  );
}
