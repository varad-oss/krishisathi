'use client';

import Link from 'next/link';
import { Bell, Camera, CheckCircle2, CloudRain, CloudSun, Droplets, MessageCircle, Thermometer, Wind } from 'lucide-react';
import { useI18n } from '@/lib/i18n';
import type { Resource } from '@/lib/use-resource';
import type { FarmConditions, ForecastDay, PersonalizedAlerts } from '@/lib/types';
import type { MessageKey } from '@/locales/en';
import { buttonClass, Card, CardTitle, ErrorState, LoadingBlock, ProvenanceLine, SeverityBadge, Skeleton } from '../ui';
import { insightView, outbreakView, SEVERITY_RANK, type AlertView } from './insight-text';

export function useAlertViews(conditions: Resource<FarmConditions>, alerts: Resource<PersonalizedAlerts>, crop: string | null): AlertView[] {
  const { t, fmt } = useI18n();
  const weather = conditions.data?.insights.map((i) => insightView(t, fmt, i)) ?? [];
  const outbreaks = alerts.data?.alerts.map((a) => outbreakView(t, fmt, a, crop)) ?? [];
  return [...weather, ...outbreaks].sort((a, b) => SEVERITY_RANK[b.severity] - SEVERITY_RANK[a.severity]);
}

export function TodayCard({
  conditions,
  views,
  locationLabel,
  cropLabel,
}: {
  conditions: Resource<FarmConditions>;
  views: AlertView[];
  locationLabel: string;
  cropLabel: string | null;
}) {
  const { t, fmt } = useI18n();
  const top = views[0];
  const cur = conditions.data?.current;

  return (
    <Card aria-labelledby="today-title" className="scroll-mt-header border-leaf-200 bg-gradient-to-b from-leaf-50 to-surface" id="today">
      <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <p className="text-sm font-medium text-leaf-700">
            {locationLabel}
            {cropLabel && <span className="text-ink-soft"> · {cropLabel}</span>}
          </p>
          <h2 id="today-title" className="mt-1 text-2xl font-semibold tracking-tight">
            {t('farm.today.title')}
          </h2>
        </div>
        <div className="flex items-center gap-3 sm:text-right">
          {conditions.status === 'loading' && !cur ? (
            <Skeleton className="h-12 w-36" />
          ) : cur ? (
            <>
              <CloudSun className="h-10 w-10 text-sky-600" aria-hidden />
              <div>
                <p className="text-3xl font-semibold tabular-nums">{fmt.num(cur.temperature_c)}°C</p>
                <p className="text-sm text-ink-soft">{t(`wx.${cur.condition}` as MessageKey)}</p>
              </div>
            </>
          ) : null}
        </div>
      </div>

      <div className="mt-5">
        {conditions.status === 'error' && !conditions.data ? (
          <ErrorState error={conditions.error} onRetry={conditions.reload} title={t('farm.today.weatherUnavailable')} />
        ) : conditions.status === 'loading' && !conditions.data ? (
          <LoadingBlock lines={2} />
        ) : top ? (
          <div className="rounded-xl border border-line bg-surface p-4">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-semibold uppercase tracking-wide text-ink-faint">{t('farm.today.risk')}</span>
              <SeverityBadge severity={top.severity} />
            </div>
            <p className="mt-2 text-lg font-semibold">{top.title}</p>
            <p className="mt-1 text-sm text-ink-soft">
              <span className="font-semibold text-ink">{t('farm.today.topAction')}: </span>
              {top.action}
            </p>
          </div>
        ) : (
          <div className="flex items-start gap-3 rounded-xl border border-leaf-200 bg-surface p-4">
            <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-leaf-600" aria-hidden />
            <div>
              <p className="font-semibold">{t('farm.today.noRisk')}</p>
              <p className="text-sm text-ink-soft">{t('farm.today.noRiskBody')}</p>
            </div>
          </div>
        )}
      </div>

      <div className="mt-5 flex flex-wrap gap-3">
        <Link href="/diagnose" className={buttonClass.primary}>
          <Camera className="h-4 w-4" aria-hidden /> {t('farm.today.diagnoseCta')}
        </Link>
        <Link href="/advisor" className={buttonClass.secondary}>
          <MessageCircle className="h-4 w-4" aria-hidden /> {t('farm.today.askCta')}
        </Link>
      </div>
    </Card>
  );
}

export function AlertsCard({ views, conditions, alerts }: { views: AlertView[]; conditions: Resource<FarmConditions>; alerts: Resource<PersonalizedAlerts> }) {
  const { t } = useI18n();
  const loading = (conditions.status === 'loading' && !conditions.data) || (alerts.status === 'loading' && !alerts.data);
  return (
    <Card id="alerts" aria-labelledby="alerts-title" className="scroll-mt-header">
      <CardTitle icon={Bell} id="alerts-title">
        {t('farm.alerts.title')}
      </CardTitle>
      {loading ? (
        <LoadingBlock />
      ) : (
        <div className="space-y-3">
          {views.length === 0 && conditions.status === 'success' && (
            <div className="rounded-xl bg-paper p-4 text-sm">
              <p className="font-semibold">{t('farm.alerts.none')}</p>
              <p className="mt-1 text-ink-soft">{t('farm.alerts.noneBody')}</p>
            </div>
          )}
          <ul className="space-y-3">
            {views.map((v) => (
              <li key={v.key}>
                <details className="group rounded-xl border border-line bg-surface open:shadow-sm">
                  <summary className="flex min-h-11 cursor-pointer list-none items-start justify-between gap-3 p-4 [&::-webkit-details-marker]:hidden">
                    <div className="min-w-0">
                      <div className="mb-1 flex flex-wrap items-center gap-2">
                        <SeverityBadge severity={v.severity} />
                        <span className="text-xs text-ink-faint">{v.when}</span>
                      </div>
                      <p className="font-semibold">{v.title}</p>
                      <p className="mt-0.5 text-sm text-ink-soft">{v.action}</p>
                    </div>
                    <span aria-hidden className="mt-1 text-ink-faint transition-transform group-open:rotate-180">▾</span>
                  </summary>
                  <dl className="grid gap-3 border-t border-line px-4 pb-4 pt-3 text-sm sm:grid-cols-2">
                    <div>
                      <dt className="font-semibold">{t('farm.alerts.why')}</dt>
                      <dd className="text-ink-soft">{v.why}</dd>
                    </div>
                    <div>
                      <dt className="font-semibold">{t('farm.alerts.impact')}</dt>
                      <dd className="text-ink-soft">{v.impact}</dd>
                    </div>
                    <div className="sm:col-span-2">
                      <dt className="font-semibold">{t('provenance.source')}</dt>
                      <dd className="text-ink-soft">
                        {v.kind === 'ai_classified_user_reports' ? t('kind.ai_classified_user_reports') : `Open-Meteo · ${t(v.kind === 'forecast' ? 'kind.forecast' : 'kind.model')}`}
                        {' · '}
                        {v.basisUrl ? (
                          <a href={v.basisUrl} target="_blank" rel="noopener noreferrer" className="underline underline-offset-2">
                            {v.basis}
                          </a>
                        ) : (
                          v.basis
                        )}
                      </dd>
                    </div>
                  </dl>
                </details>
              </li>
            ))}
          </ul>
          {conditions.status === 'error' && (
            <ErrorState compact error={conditions.error} onRetry={conditions.reload} title={t('farm.weather.unavailable')} updatedAt={conditions.updatedAt} />
          )}
          {alerts.status === 'error' && <ErrorState compact error={alerts.error} onRetry={alerts.reload} title={t('farm.alerts.outbreaksUnavailable')} />}
        </div>
      )}
    </Card>
  );
}

function RainBar({ day }: { day: ForecastDay }) {
  const mm = day.precipitation_mm ?? 0;
  const height = Math.min(100, (mm / 30) * 100);
  return (
    <div className="flex h-10 items-end justify-center" aria-hidden>
      <div className="w-2.5 rounded-t bg-sky-600/70" style={{ height: `${Math.max(mm > 0 ? 6 : 0, height)}%` }} />
    </div>
  );
}

export function WeatherCard({ conditions }: { conditions: Resource<FarmConditions> }) {
  const { t, fmt } = useI18n();
  const c = conditions.data;

  return (
    <Card id="weather" aria-labelledby="weather-title" className="scroll-mt-header">
      <CardTitle icon={CloudRain} id="weather-title">
        {t('farm.weather.title')}
      </CardTitle>
      {!c && conditions.status === 'loading' ? (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {Array.from({ length: 4 }, (_, i) => <Skeleton key={i} className="h-20" />)}
          </div>
          <Skeleton className="h-36" />
        </div>
      ) : !c && conditions.status === 'error' ? (
        <ErrorState error={conditions.error} onRetry={conditions.reload} title={t('farm.weather.unavailable')} />
      ) : c ? (
        <>
          {conditions.status === 'error' && (
            <ErrorState compact error={conditions.error} onRetry={conditions.reload} updatedAt={conditions.updatedAt} />
          )}
          <h3 className="mb-2 text-sm font-semibold text-ink-soft">
            {t('farm.weather.now')} <span className="font-normal text-ink-faint">· {t('kind.model')}</span>
          </h3>
          <dl className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {[
              { icon: Thermometer, label: t('farm.weather.temperature'), value: `${fmt.num(c.current.temperature_c)}°C` },
              { icon: Droplets, label: t('farm.weather.humidity'), value: `${fmt.num(c.current.humidity_pct, 0)}%` },
              { icon: Wind, label: t('farm.weather.wind'), value: `${fmt.num(c.current.wind_kmh, 0)} km/h` },
              { icon: CloudRain, label: t('farm.weather.soilMoisture'), value: c.current.soil_moisture_3_9cm == null ? t('state.unavailable') : `${fmt.num(c.current.soil_moisture_3_9cm, 2)} m³/m³` },
            ].map((m) => (
              <div key={m.label} className="rounded-xl bg-paper p-3">
                <dt className="flex items-center gap-1.5 text-xs text-ink-soft">
                  <m.icon className="h-3.5 w-3.5" aria-hidden /> {m.label}
                </dt>
                <dd className="mt-1 text-lg font-semibold tabular-nums">{m.value}</dd>
              </div>
            ))}
          </dl>
          <p className="mt-2 text-xs text-ink-faint">{t('farm.weather.soilMoistureNote')}</p>

          <h3 className="mb-2 mt-6 text-sm font-semibold text-ink-soft">
            {t('farm.weather.forecast')} <span className="font-normal text-ink-faint">· {t('kind.forecast')}</span>
          </h3>
          <div className="relative -mx-1 overflow-x-auto pb-1">
            <table className="w-full min-w-[560px] border-separate border-spacing-x-1 text-center text-sm">
              <caption className="sr-only">{t('farm.weather.chartLabel')}</caption>
              <thead>
                <tr>
                  {c.daily.map((d, i) => (
                    <th key={d.date} scope="col" className="rounded-t-lg bg-paper px-1 pt-2 text-xs font-semibold">
                      {i === 0 ? t('farm.weather.today') : fmt.weekday(d.date)}
                      <span className="block font-normal text-ink-faint">{fmt.date(d.date)}</span>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                <tr>
                  {c.daily.map((d) => (
                    <td key={d.date} className="bg-paper px-1 py-1 text-xs text-ink-soft">
                      {t(`wx.${d.condition}` as MessageKey)}
                    </td>
                  ))}
                </tr>
                <tr>
                  {c.daily.map((d) => (
                    <td key={d.date} className="bg-paper px-1 py-1 tabular-nums">
                      <span className="font-semibold">{fmt.num(d.temp_max_c, 0)}°</span>
                      <span className="text-ink-faint"> / {fmt.num(d.temp_min_c, 0)}°</span>
                    </td>
                  ))}
                </tr>
                <tr>
                  {c.daily.map((d) => (
                    <td key={d.date} className="bg-paper px-1 pt-1">
                      <RainBar day={d} />
                    </td>
                  ))}
                </tr>
                <tr>
                  {c.daily.map((d) => (
                    <td key={d.date} className="rounded-b-lg bg-paper px-1 pb-2 text-xs tabular-nums">
                      <span className="block font-semibold text-sky-700">
                        {fmt.num(d.precipitation_mm)} <span className="sr-only">mm</span>
                        <span aria-hidden>mm</span>
                      </span>
                      {d.precipitation_probability_pct != null && (
                        <span className="text-ink-faint">
                          {fmt.num(d.precipitation_probability_pct, 0)}%<span className="sr-only"> {t('farm.weather.rainChance')}</span>
                        </span>
                      )}
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>

          <h3 className="mb-2 mt-6 text-sm font-semibold text-ink-soft">{t('farm.weather.meaning')}</h3>
          {c.insights.length === 0 ? (
            <p className="text-sm text-ink-soft">{t('farm.weather.noMeaning')}</p>
          ) : (
            <WeatherMeaning conditions={c} />
          )}
          <ProvenanceLine source={c.provenance.source} url={c.provenance.source_url} kind="model" time={c.provenance.retrieved_at} note={t('farm.weather.observedNote')} />
        </>
      ) : null}
    </Card>
  );
}

function WeatherMeaning({ conditions }: { conditions: FarmConditions }) {
  const { t, fmt } = useI18n();
  return (
    <ul className="space-y-2">
      {conditions.insights.map((i) => {
        const v = insightView(t, fmt, i);
        return (
          <li key={v.key} className="flex items-start gap-2 text-sm">
            <SeverityBadge severity={v.severity} className="mt-0.5 shrink-0" />
            <span>
              <span className="font-semibold">{v.title}.</span> <span className="text-ink-soft">{v.action}</span>
            </span>
          </li>
        );
      })}
    </ul>
  );
}
