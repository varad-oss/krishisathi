'use client';

import Link from 'next/link';
import { Camera, CheckCircle2, CloudRain, CloudSun, Droplets, MapPin, MessageCircle, Sprout, TrendingDown, TrendingUp, Wind } from 'lucide-react';
import { useI18n } from '@/lib/i18n';
import type { Resource } from '@/lib/use-resource';
import type { CropHealth, FarmConditions, FarmTwin, FarmTwinIntelligence, ForecastDay } from '@/lib/types';
import type { MessageKey } from '@/locales/en';
import { cn } from '@/lib/utils';
import { buttonClass, Card, CardTitle, ErrorState, KindTag, ProvenanceLine, severityDot, Skeleton } from '../ui';
import { insightView } from './insight-text';
import { ActionFeedback } from './History';
import { DataQualityStrip, EvidenceList, SeverityChip } from './Intelligence';
import { actionWhat, because, stageText, topActionTitle } from './intelligence-text';

const accent: Record<string, string> = { low: 'bg-leaf-500', moderate: 'bg-watch-500', high: 'bg-warn-500' };

/** Crop condition in one line: satellite NDVI trend when available, otherwise an honest "no reading". */
function CropCondition({ health, cropLabel }: { health: Resource<CropHealth>; cropLabel: string | null }) {
  const { t, fmt } = useI18n();
  const h = health.data;
  let body: React.ReactNode;
  if (!h && health.status === 'loading') body = <Skeleton className="h-5 w-40" />;
  else if (h?.status === 'available' && h.ndvi != null) {
    const falling = h.change != null && h.change < 0;
    body = (
      <span className="flex flex-wrap items-center gap-x-2">
        <span className="font-semibold tabular-nums">{t('farm.crop.ndvi')} {fmt.num(h.ndvi, 2)}</span>
        {h.change != null && (
          <span className={cn('inline-flex items-center gap-1 tabular-nums', falling ? 'text-warn-700' : 'text-leaf-700')}>
            {falling ? <TrendingDown className="h-4 w-4" aria-hidden /> : <TrendingUp className="h-4 w-4" aria-hidden />}
            {h.change > 0 ? '+' : ''}
            {fmt.num(h.change, 2)}
          </span>
        )}
      </span>
    );
  } else body = <span className="text-ink-faint">{t('farm.today.noSatellite')}</span>;
  return (
    <div className="flex items-start gap-3">
      <Sprout className="mt-0.5 h-5 w-5 shrink-0 text-leaf-600" aria-hidden />
      <div className="min-w-0 text-sm">
        <p className="text-ink-soft">{cropLabel ? t('farm.today.cropCondition', { crop: cropLabel }) : t('farm.crop.title')}</p>
        <div className="mt-0.5">{body}</div>
      </div>
    </div>
  );
}

export function TodayCard({
  conditions,
  health,
  intel,
  twin,
  locationLabel,
  cropLabel,
}: {
  conditions: Resource<FarmConditions>;
  health: Resource<CropHealth>;
  intel: Resource<FarmTwinIntelligence>;
  twin: FarmTwin | null;
  locationLabel: string;
  cropLabel: string | null;
}) {
  const { t, fmt, language } = useI18n();
  const cur = conditions.data?.current;
  const today = conditions.data?.daily[0];
  const data = intel.data;
  const top = data?.top_action;
  const stage = data?.farm.crop_stage;
  const reason = top ? because(t, language, top.drivers) : null;

  return (
    <section id="today" aria-labelledby="today-title" className="scroll-mt-header overflow-hidden rounded-[var(--radius-card)] bg-surface shadow-[var(--shadow-raised)] ring-1 ring-line/80">
      <div className="grid lg:grid-cols-[1.55fr_1fr]">
        <div className="relative p-5 sm:p-8">
          {top?.severity && accent[top.severity] && <span aria-hidden className={cn('absolute inset-y-0 left-0 w-1', accent[top.severity])} />}
          <p className="flex flex-wrap items-center gap-x-2 gap-y-1 text-sm text-ink-soft">
            <MapPin className="h-4 w-4 text-leaf-600" aria-hidden />
            <span className="font-medium text-ink">{locationLabel}</span>
            {cropLabel && <span>· {cropLabel}</span>}
            <span>· {fmt.date(new Date(), { weekday: 'long', day: 'numeric', month: 'long' })}</span>
          </p>
          {stage?.stage && (
            <p className="mt-1 text-xs text-ink-faint">
              {t('farm.stage', { stage: stageText(t, stage.stage), days: fmt.num(stage.days_since_sowing, 0) })}
              {stage.confidence && ` · ${t('risk.confidence', { level: t(`level.${stage.confidence}` as MessageKey) })}`}
            </p>
          )}
          <h2 id="today-title" className="mt-4 text-sm font-semibold text-leaf-700">
            {t('farm.today.title')}
          </h2>

          <div className="mt-2" aria-live="polite">
            {intel.status === 'error' && !data ? (
              <ErrorState error={intel.error} onRetry={intel.reload} title={t('risk.unavailable')} />
            ) : !data ? (
              <div className="space-y-3">
                <Skeleton className="h-9 w-4/5" />
                <Skeleton className="h-5 w-3/5" />
              </div>
            ) : top && top.status !== 'routine' ? (
              <>
                <p className="font-display text-[1.75rem] font-medium leading-tight text-ink sm:text-[2.1rem]">{topActionTitle(t, top)}</p>
                {top.status === 'action' && (
                  <>
                    <div className="mt-3 flex flex-wrap items-center gap-2 text-sm">
                      {top.category && <span className="font-semibold">{t(`risk.${top.category}` as MessageKey)}</span>}
                      {top.severity && <SeverityChip severity={top.severity} />}
                      {top.confidence && <span className="text-ink-faint">{t('risk.confidence', { level: t(`level.${top.confidence}` as MessageKey) })}</span>}
                    </div>
                    {reason && <p className="mt-3 text-ink-soft">{reason}</p>}
                    {top.action && (
                      <div className="mt-4 rounded-[var(--radius-inner)] bg-leaf-50 p-4">
                        <p className="text-xs font-semibold text-leaf-700">{t('risk.whatToDo')}</p>
                        <p className="mt-1 text-[1.05rem] font-medium leading-snug text-ink">{actionWhat(t, top.action, top.drivers, cropLabel)}</p>
                      </div>
                    )}
                    {top.evidence.length > 0 && (
                      <details className="group mt-3">
                        <summary className="inline-flex min-h-10 cursor-pointer list-none items-center gap-1 text-sm font-semibold text-leaf-700 hover:underline">
                          {t('today.whyThis')}
                          <span aria-hidden className="transition-transform group-open:rotate-180">▾</span>
                        </summary>
                        <div className="mt-2 rounded-[var(--radius-inner)] bg-paper/70 p-4">
                          <EvidenceList evidence={top.evidence} />
                        </div>
                      </details>
                    )}
                  </>
                )}
                {twin && data.twin?.action && (
                  <div className="mt-4">
                    <ActionFeedback key={data.twin.action.action_id} twin={twin} action={data.twin.action} />
                  </div>
                )}
                <a href="#risks" className="mt-2 inline-flex min-h-10 items-center text-sm font-semibold text-leaf-700 hover:underline">
                  {t('today.allRisks')}
                </a>
              </>
            ) : (
              <div className="flex items-start gap-3">
                <CheckCircle2 className="mt-1.5 h-6 w-6 shrink-0 text-leaf-600" aria-hidden />
                <div>
                  <p className="font-display text-[1.6rem] font-medium leading-tight">{t('action.routine_monitoring.title')}</p>
                  <p className="mt-2 text-ink-soft">{t('action.routine_monitoring.what')}</p>
                </div>
              </div>
            )}
          </div>

          <div className="mt-6 flex flex-wrap gap-3">
            <Link href="/diagnose" className={buttonClass.primary}>
              <Camera className="h-4 w-4" aria-hidden /> {t('farm.today.diagnoseCta')}
            </Link>
            <Link href="/advisor" className={buttonClass.secondary}>
              <MessageCircle className="h-4 w-4" aria-hidden /> {t('farm.today.askCta')}
            </Link>
            <Link href="/problem" className={buttonClass.ghost}>
              {t('problem.cta')}
            </Link>
          </div>
        </div>

        <aside aria-label={t('farm.weather.now')} className="border-t border-line bg-paper/60 p-5 sm:p-8 lg:border-l lg:border-t-0">
          <div className="flex items-center justify-between gap-2">
            <p className="text-sm font-semibold text-ink-soft">{t('farm.weather.now')}</p>
            <span className="text-xs"><KindTag kind="model" /></span>
          </div>
          {conditions.status === 'loading' && !cur ? (
            <Skeleton className="mt-4 h-16 w-40" />
          ) : cur ? (
            <>
              <div className="mt-3 flex items-center gap-3">
                <CloudSun className="h-11 w-11 shrink-0 text-sky-600" aria-hidden />
                <div>
                  <p className="font-display text-[2.6rem] font-medium leading-none tabular-nums">{fmt.num(cur.temperature_c)}°</p>
                  <p className="mt-1 text-sm text-ink-soft">{t(`wx.${cur.condition}` as MessageKey)}</p>
                </div>
              </div>
              <dl className="mt-5 grid grid-cols-3 gap-2 text-sm">
                <div>
                  <dt className="flex items-center gap-1 text-xs text-ink-faint"><Droplets className="h-3.5 w-3.5" aria-hidden />{t('farm.weather.humidity')}</dt>
                  <dd className="mt-0.5 font-semibold tabular-nums">{fmt.num(cur.humidity_pct, 0)}%</dd>
                </div>
                <div>
                  <dt className="flex items-center gap-1 text-xs text-ink-faint"><Wind className="h-3.5 w-3.5" aria-hidden />{t('farm.weather.wind')}</dt>
                  <dd className="mt-0.5 font-semibold tabular-nums">{fmt.num(cur.wind_kmh, 0)} {t('unit.kmh')}</dd>
                </div>
                <div>
                  <dt className="flex items-center gap-1 text-xs text-ink-faint"><CloudRain className="h-3.5 w-3.5" aria-hidden />{t('farm.weather.rainToday')}</dt>
                  <dd className="mt-0.5 font-semibold tabular-nums">{today ? `${fmt.num(today.precipitation_mm)} ${t('unit.mm')}` : '—'}</dd>
                </div>
              </dl>
            </>
          ) : (
            <p className="mt-4 text-sm text-ink-faint">{t('state.unavailable')}</p>
          )}
          <div className="mt-6 border-t border-line pt-4">
            <CropCondition health={health} cropLabel={cropLabel} />
          </div>
        </aside>
      </div>
      {data && <DataQualityStrip items={data.data_quality} />}
    </section>
  );
}

function RainBar({ day, className }: { day: ForecastDay; className?: string }) {
  const mm = day.precipitation_mm ?? 0;
  const width = Math.min(100, (mm / 30) * 100);
  return (
    <div className={cn('h-1.5 overflow-hidden rounded-full bg-sky-100', className)} aria-hidden>
      <div className="h-full rounded-full bg-sky-600" style={{ width: `${Math.max(mm > 0 ? 6 : 0, width)}%` }} />
    </div>
  );
}

export function WeatherCard({ conditions }: { conditions: Resource<FarmConditions> }) {
  const { t, fmt } = useI18n();
  const c = conditions.data;

  return (
    <Card id="weather" aria-labelledby="weather-title" className="scroll-mt-header">
      <CardTitle icon={CloudRain} id="weather-title" description={t('farm.weather.subtitle')}>
        {t('farm.weather.title')}
      </CardTitle>
      {!c && conditions.status === 'loading' ? (
        <div className="grid gap-2 sm:grid-cols-7">
          {Array.from({ length: 7 }, (_, i) => <Skeleton key={i} className="h-14 sm:h-36" />)}
        </div>
      ) : !c && conditions.status === 'error' ? (
        <ErrorState error={conditions.error} onRetry={conditions.reload} title={t('farm.weather.unavailable')} />
      ) : c ? (
        <>
          {conditions.status === 'error' && (
            <ErrorState compact error={conditions.error} onRetry={conditions.reload} updatedAt={conditions.updatedAt} />
          )}
          <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-ink-soft">
            {t('farm.weather.forecast')} <KindTag kind="forecast" className="text-xs font-normal" />
          </h3>
          <ol aria-label={t('farm.weather.chartLabel')} className="grid gap-1.5 sm:grid-cols-7 sm:gap-2">
            {c.daily.map((d, i) => (
              <li
                key={d.date}
                className={cn(
                  'grid grid-cols-[5.5rem_1fr_auto] items-center gap-3 rounded-[var(--radius-inner)] px-3 py-2.5 sm:flex sm:flex-col sm:items-stretch sm:gap-2 sm:px-2.5 sm:py-3 sm:text-center',
                  i === 0 ? 'bg-leaf-50 ring-1 ring-leaf-100' : 'bg-paper/70',
                )}
              >
                <p className="text-sm font-semibold leading-tight">
                  {i === 0 ? t('farm.weather.today') : fmt.weekday(d.date)}
                  <span className="block text-xs font-normal text-ink-faint">{fmt.date(d.date)}</span>
                </p>
                <div className="min-w-0 sm:order-last">
                  <RainBar day={d} />
                  <p className="mt-1 text-xs tabular-nums text-sky-700">
                    <span className="font-semibold">{fmt.num(d.precipitation_mm)}</span> {t('unit.mm')}
                    {d.precipitation_probability_pct != null && (
                      <span className="text-ink-faint"> · {fmt.num(d.precipitation_probability_pct, 0)}%<span className="sr-only"> {t('farm.weather.rainChance')}</span></span>
                    )}
                  </p>
                </div>
                <div className="text-right sm:text-center">
                  <p className="text-xs text-ink-soft">{t(`wx.${d.condition}` as MessageKey)}</p>
                  <p className="tabular-nums">
                    <span className="font-semibold">{fmt.num(d.temp_max_c, 0)}°</span>
                    <span className="text-ink-faint"> / {fmt.num(d.temp_min_c, 0)}°</span>
                  </p>
                </div>
              </li>
            ))}
          </ol>

          <div className="mt-6 grid gap-6 lg:grid-cols-[1.4fr_1fr]">
            <div>
              <h3 className="mb-2 text-sm font-semibold text-ink-soft">{t('farm.weather.meaning')}</h3>
              {c.insights.length === 0 ? <p className="text-sm text-ink-soft">{t('farm.weather.noMeaning')}</p> : <WeatherMeaning conditions={c} />}
            </div>
            <div className="rounded-[var(--radius-inner)] bg-paper/70 p-4 text-sm">
              <p className="flex items-center gap-1.5 text-ink-soft">
                <Droplets className="h-4 w-4 text-sky-600" aria-hidden /> {t('farm.weather.soilMoisture')}
              </p>
              <p className="mt-1 text-lg font-semibold tabular-nums">
                {c.current.soil_moisture_3_9cm == null ? t('state.unavailable') : `${fmt.num(c.current.soil_moisture_3_9cm, 2)} m³/m³`}
              </p>
              <p className="mt-1 text-xs text-ink-faint">{t('farm.weather.soilMoistureNote')}</p>
            </div>
          </div>
          <ProvenanceLine source={c.provenance.source} url={c.provenance.source_url} kind="model" time={c.provenance.retrieved_at} note={t('farm.weather.observedNote')} />
        </>
      ) : null}
    </Card>
  );
}

function WeatherMeaning({ conditions }: { conditions: FarmConditions }) {
  const { t, fmt } = useI18n();
  return (
    <ul className="space-y-2.5">
      {conditions.insights.map((i) => {
        const v = insightView(t, fmt, i);
        return (
          <li key={v.key} className="flex items-start gap-2.5 text-sm">
            <span aria-hidden className={cn('mt-2 h-2 w-2 shrink-0 rounded-full', severityDot[v.severity])} />
            <span>
              <span className="font-semibold">{v.title}.</span> <span className="text-ink-soft">{v.action}</span>
              <span className="sr-only"> ({t(`severity.${v.severity}` as MessageKey)})</span>
            </span>
          </li>
        );
      })}
    </ul>
  );
}
