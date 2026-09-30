'use client';

import Link from 'next/link';
import { Camera, CheckCircle2, ChevronDown, CloudSun, Droplets, MessageCircle, Sprout, TrendingDown, TrendingUp } from 'lucide-react';
import { useI18n } from '@/lib/i18n';
import type { Resource } from '@/lib/use-resource';
import type { CropHealth, FarmConditions, FarmTwin, FarmTwinIntelligence, ForecastDay } from '@/lib/types';
import type { MessageKey } from '@/locales/en';
import { cn } from '@/lib/utils';
import ReadAloud from '../ReadAloud';
import { ActionBlock, buttonClass, ErrorState, EvidenceRow, KindTag, linkClass, LoadingBlock, ProvenanceLine, RiskLevel, SavedCopyTag, Section, severityDot, Skeleton, SubHeading } from '../ui';
import { insightView } from './insight-text';
import { ActionFeedback } from './History';
import { ConfidenceChip, ConfidenceWhy, DataQualityStrip, EvidenceList } from './Intelligence';
import { actionWhat, because, topActionTitle } from './intelligence-text';

const RULE: Record<string, string> = { low: 'border-leaf-500', moderate: 'border-watch-500', high: 'border-warn-500' };

/** Crop condition from above in one line: satellite trend when available, otherwise an honest "no reading". */
function CropFromAbove({ health, cropLabel }: { health: Resource<CropHealth>; cropLabel: string | null }) {
  const { t, fmt } = useI18n();
  const h = health.data;
  const label = cropLabel ? t('farm.today.cropCondition', { crop: cropLabel }) : t('farm.crop.title');
  if (!h && health.status === 'loading') return <EvidenceRow icon={Sprout} tone="leaf" label={label} value={<Skeleton className="mt-1 h-5 w-40" />} />;
  if (h?.status === 'available' && h.ndvi != null) {
    const falling = h.change != null && h.change < 0;
    return (
      <EvidenceRow
        icon={Sprout}
        tone="leaf"
        label={label}
        value={
          <span className="flex flex-wrap items-center gap-x-2">
            <span className="tabular-nums">{t('farm.crop.ndvi')} {fmt.num(h.ndvi, 2)}</span>
            {h.change != null && (
              <span className={cn('inline-flex items-center gap-1 tabular-nums', falling ? 'text-warn-700' : 'text-leaf-700')}>
                {falling ? <TrendingDown className="h-4 w-4" aria-hidden /> : <TrendingUp className="h-4 w-4" aria-hidden />}
                {h.change > 0 ? '+' : ''}
                {fmt.num(h.change, 2)}
              </span>
            )}
          </span>
        }
        tag={<KindTag kind="satellite_observation" />}
      />
    );
  }
  return <EvidenceRow icon={Sprout} tone="ink" label={label} value={<span className="font-normal text-ink-soft">{t('farm.today.noSatellite')}</span>} />;
}

/**
 * The first screen of the farm: what matters today (one insight), what to do (one action), and why (the evidence),
 * in that order. The farmer never has to read raw numbers to know what to do.
 */
export function TodayCard({
  conditions,
  health,
  intel,
  twin,
  cropLabel,
}: {
  conditions: Resource<FarmConditions>;
  health: Resource<CropHealth>;
  intel: Resource<FarmTwinIntelligence>;
  twin: FarmTwin | null;
  cropLabel: string | null;
}) {
  const { t, fmt, language } = useI18n();
  const cur = conditions.data?.current;
  const today = conditions.data?.daily[0];
  const data = intel.data;
  const top = data?.top_action;
  const reason = top ? because(t, language, top.drivers) : null;
  const what = top?.action ? actionWhat(t, top.action, top.drivers, cropLabel) : '';
  const acting = top && top.status === 'action';
  // What is read aloud: the insight, the action and the reason. Never the dashboard's numbers.
  const spoken = top ? [topActionTitle(t, top), acting ? what : t('action.routine_monitoring.what'), acting ? reason : null].filter(Boolean).join('. ') : '';

  return (
    <section id="today" aria-labelledby="today-title" className="scroll-mt-header grid gap-8 pb-10 lg:grid-cols-[minmax(0,1.55fr)_minmax(0,1fr)] lg:gap-12">
      <div className="min-w-0">
        <h2 id="today-title" className="text-[0.95rem] font-semibold text-leaf-700">
          {t('farm.today.title')}
        </h2>

        <div className="mt-3" aria-live="polite">
          {intel.status === 'error' && !data ? (
            <ErrorState error={intel.error} onRetry={intel.reload} title={t('risk.unavailable')} />
          ) : !data ? (
            <div className="space-y-4">
              <LoadingBlock lines={0} label={t('farm.loading')} />
              <Skeleton className="h-10 w-4/5" />
              <Skeleton className="h-20 w-full" />
            </div>
          ) : top && top.status !== 'routine' ? (
            <div className="animate-rise">
              {intel.cached && intel.updatedAt && <SavedCopyTag time={intel.updatedAt} className="mb-3" />}
              <div className={cn(acting && top.severity && RULE[top.severity] && `border-l-[3px] pl-4 sm:pl-5 ${RULE[top.severity]}`)}>
                <p className="font-display text-[1.7rem] leading-[1.15] text-ink [overflow-wrap:anywhere] sm:text-[2.35rem]">{topActionTitle(t, top)}</p>
                {acting && (
                  <div className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-2">
                    {top.category && <span className="font-semibold">{t(`risk.${top.category}` as MessageKey)}</span>}
                    {top.severity && <RiskLevel level={top.severity} />}
                    {top.confidence && <ConfidenceChip level={top.confidence} />}
                  </div>
                )}
              </div>
              {acting && (
                <>
                  {reason && <p className="mt-3 max-w-[62ch] text-[1.05rem] text-ink-soft">{reason}</p>}
                  {top.priority_reason && <p className="mt-1.5 text-sm text-ink-soft" data-testid="priority-reason">{t(`priority.${top.priority_reason}` as MessageKey)}</p>}
                  {what && <ActionBlock label={t('risk.whatToDo')} className="mt-5">{what}</ActionBlock>}
                </>
              )}
              <div className="mt-5 flex flex-wrap items-center gap-x-5 gap-y-2">
                <ReadAloud text={spoken} language={language} />
                {acting && top.evidence.length > 0 && (
                  <details className="group w-full">
                    <summary className={cn(linkClass, 'cursor-pointer list-none')}>
                      {t('today.whyThis')}
                      <ChevronDown aria-hidden className="h-4 w-4 transition-transform group-open:rotate-180" />
                    </summary>
                    <div className="mt-2 space-y-4 rounded-[var(--radius-inner)] border border-line bg-surface p-4">
                      <ConfidenceWhy basis={top.confidence_basis} />
                      <EvidenceList evidence={top.evidence} rules={top.rules} />
                    </div>
                  </details>
                )}
              </div>
              {twin && data.twin?.action && (
                <div className="mt-5">
                  <ActionFeedback key={data.twin.action.action_id} twin={twin} action={data.twin.action} />
                </div>
              )}
            </div>
          ) : (
            <div className="flex animate-rise items-start gap-3">
              <CheckCircle2 className="mt-1.5 h-7 w-7 shrink-0 text-leaf-600" aria-hidden />
              <div>
                <p className="font-display text-[1.7rem] leading-tight sm:text-[2.2rem]">{t('action.routine_monitoring.title')}</p>
                <p className="mt-2 text-[1.05rem] text-ink-soft">{t('action.routine_monitoring.what')}</p>
                <div className="mt-4"><ReadAloud text={spoken} language={language} /></div>
              </div>
            </div>
          )}
        </div>

        <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center">
          <Link href="/diagnose" className={buttonClass.primary}>
            <Camera className="h-5 w-5" aria-hidden /> {t('farm.today.diagnoseCta')}
          </Link>
          <Link href="/advisor" className={buttonClass.secondary}>
            <MessageCircle className="h-5 w-5" aria-hidden /> {t('farm.today.askCta')}
          </Link>
          <Link href="/problem" className={cn(linkClass, 'sm:ml-2')}>
            {t('problem.cta')}
          </Link>
        </div>
      </div>

      {/* Why: the conditions behind today's advice, as plain statements with their numbers underneath. */}
      <aside aria-label={t('farm.weather.now')} className="min-w-0 lg:border-l lg:border-line lg:pl-10">
        <p className="text-sm font-semibold text-ink-soft">{t('farm.weather.now')}</p>
        <ul className="divide-y divide-line">
          {conditions.status === 'loading' && !cur ? (
            <li className="py-4"><Skeleton className="h-14 w-full" /></li>
          ) : cur ? (
            <EvidenceRow
              icon={CloudSun}
              tone="sky"
              label={t(`wx.${cur.condition}` as MessageKey)}
              value={<span className="font-display text-[2rem] leading-none tabular-nums">{fmt.num(cur.temperature_c)}°</span>}
              detail={
                <span className="tabular-nums">
                  {t('farm.weather.humidity')} {fmt.num(cur.humidity_pct, 0)}% · {t('farm.weather.wind')} {fmt.num(cur.wind_kmh, 0)} {t('unit.kmh')}
                  {today && <> · {t('farm.weather.rainToday')} {fmt.num(today.precipitation_mm)} {t('unit.mm')}</>}
                </span>
              }
              tag={<KindTag kind="model" />}
            />
          ) : (
            <EvidenceRow icon={CloudSun} label={t('farm.weather.now')} value={<span className="font-normal text-ink-soft">{t('state.unavailable')}</span>} />
          )}
          <CropFromAbove health={health} cropLabel={cropLabel} />
        </ul>
        {conditions.cached && conditions.updatedAt && <SavedCopyTag time={conditions.updatedAt} className="mt-2" />}
      </aside>
      {data && <div className="min-w-0 lg:col-span-2"><DataQualityStrip items={data.data_quality} /></div>}
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
    <Section
      id="weather"
      title={t('farm.weather.title')}
      description={t('farm.weather.subtitle')}
      action={conditions.cached && conditions.updatedAt ? <SavedCopyTag time={conditions.updatedAt} /> : undefined}
    >
      {!c && conditions.status === 'loading' ? (
        <div className="grid gap-2 sm:grid-cols-7">
          {Array.from({ length: 7 }, (_, i) => <Skeleton key={i} className="h-14 sm:h-32" />)}
        </div>
      ) : !c && conditions.status === 'error' ? (
        <ErrorState error={conditions.error} onRetry={conditions.reload} title={t('farm.weather.unavailable')} />
      ) : c ? (
        <>
          {conditions.status === 'error' && <ErrorState compact error={conditions.error} onRetry={conditions.reload} updatedAt={conditions.updatedAt} />}
          {/* Meaning first, then the numbers it comes from. */}
          <SubHeading>{t('farm.weather.meaning')}</SubHeading>
          {c.insights.length === 0 ? <p className="text-ink-soft">{t('farm.weather.noMeaning')}</p> : <WeatherMeaning conditions={c} />}

          <SubHeading className="mt-8 flex items-center gap-2">
            {t('farm.weather.forecast')} <KindTag kind="forecast" className="text-xs font-normal" />
          </SubHeading>
          <ol aria-label={t('farm.weather.chartLabel')} className="divide-y divide-line border-y border-line sm:grid sm:grid-cols-7 sm:divide-x sm:divide-y-0">
            {c.daily.map((d, i) => (
              <li
                key={d.date}
                className={cn(
                  'grid grid-cols-[5.5rem_1fr_auto] items-center gap-3 px-1 py-3 sm:flex sm:flex-col sm:items-stretch sm:gap-2 sm:px-2.5 sm:py-4 sm:text-center',
                  i === 0 && 'bg-leaf-50/70',
                )}
              >
                <p className="text-sm font-semibold leading-tight">
                  {i === 0 ? t('farm.weather.today') : fmt.weekday(d.date)}
                  <span className="block text-xs font-normal text-ink-soft">{fmt.date(d.date)}</span>
                </p>
                <div className="min-w-0 sm:order-last">
                  <RainBar day={d} />
                  <p className="mt-1 text-xs tabular-nums text-sky-700">
                    <span className="font-semibold">{fmt.num(d.precipitation_mm)}</span> {t('unit.mm')}
                    {d.precipitation_probability_pct != null && (
                      <span className="text-ink-soft"> · {fmt.num(d.precipitation_probability_pct, 0)}%<span className="sr-only"> {t('farm.weather.rainChance')}</span></span>
                    )}
                  </p>
                </div>
                <div className="text-right sm:text-center">
                  <p className="text-xs text-ink-soft">{t(`wx.${d.condition}` as MessageKey)}</p>
                  <p className="tabular-nums">
                    <span className="font-semibold">{fmt.num(d.temp_max_c, 0)}°</span>
                    <span className="text-ink-soft"> / {fmt.num(d.temp_min_c, 0)}°</span>
                  </p>
                </div>
              </li>
            ))}
          </ol>

          <ul className="mt-4">
            <EvidenceRow
              icon={Droplets}
              tone="sky"
              label={t('farm.weather.soilMoisture')}
              value={<span className="tabular-nums">{c.current.soil_moisture_3_9cm == null ? t('state.unavailable') : `${fmt.num(c.current.soil_moisture_3_9cm, 2)} m³/m³`}</span>}
              detail={t('farm.weather.soilMoistureNote')}
              tag={<KindTag kind="model" />}
            />
          </ul>
          <ProvenanceLine source={c.provenance.source} url={c.provenance.source_url} kind="model" time={c.provenance.retrieved_at} note={t('farm.weather.observedNote')} />
        </>
      ) : null}
    </Section>
  );
}

function WeatherMeaning({ conditions }: { conditions: FarmConditions }) {
  const { t, fmt } = useI18n();
  return (
    <ul className="space-y-3">
      {conditions.insights.map((i) => {
        const v = insightView(t, fmt, i);
        return (
          <li key={v.key} className="flex items-start gap-3">
            <span aria-hidden className={cn('mt-2 h-2.5 w-2.5 shrink-0 rounded-full', severityDot[v.severity])} />
            <span className="min-w-0">
              <span className="block font-semibold">{v.title}</span>
              <span className="block text-ink-soft">{v.action}</span>
              <span className="sr-only"> ({t(`severity.${v.severity}` as MessageKey)})</span>
            </span>
          </li>
        );
      })}
    </ul>
  );
}

