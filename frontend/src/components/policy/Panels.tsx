'use client';

import dynamic from 'next/dynamic';
import { useId, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Activity, CloudSun, FileText, Globe2, Map as MapIcon, RefreshCw, Satellite, ShieldAlert, Sprout } from 'lucide-react';
import { ApiError, getDashboardReport, postExchangeSignal } from '@/lib/api';
import { useI18n } from '@/lib/i18n';
import type { Resource } from '@/lib/use-resource';
import type { DashboardReport, DashboardStats, FederationReport, Outbreak, StateConfig, WeatherRisk } from '@/lib/types';
import type { MessageKey } from '@/locales/en';
import { cn } from '@/lib/utils';
import { insightView } from '../farm/insight-text';
import { buttonClass, Card, CardTitle, ErrorState, inputClass, LevelBadge, LoadingBlock, ProvenanceLine, severityDot, Skeleton, UnavailableNote } from '../ui';

const OutbreakMap = dynamic(() => import('./OutbreakMap'), { ssr: false, loading: () => <Skeleton className="h-80 sm:h-96" /> });
const TrendChart = dynamic(() => import('./TrendChart'), { ssr: false, loading: () => <Skeleton className="h-56" /> });

function Kpi({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="p-4 sm:p-6">
      <dt className="text-sm text-ink-soft [overflow-wrap:anywhere]">{label}</dt>
      <dd className="mt-1 font-display text-[2.4rem] font-medium leading-none tabular-nums">{value}</dd>
      {sub && <dd className="mt-2 text-xs text-ink-faint">{sub}</dd>}
    </div>
  );
}

export function KpiRow({ stats }: { stats: Resource<DashboardStats> }) {
  const { t, fmt } = useI18n();
  if (!stats.data && stats.status === 'loading') return <Skeleton className="h-32 rounded-[var(--radius-card)]" />;
  if (!stats.data) return stats.status === 'error' ? <ErrorState error={stats.error} onRetry={stats.reload} title={t('policy.kpi.unavailable')} /> : null;
  const s = stats.data;
  return (
    <dl className="grid grid-cols-2 divide-line overflow-hidden rounded-[var(--radius-card)] bg-surface shadow-[var(--shadow-card)] ring-1 ring-line/80 lg:grid-cols-4 lg:divide-x [&>div:nth-child(-n+2)]:border-b [&>div:nth-child(-n+2)]:border-line lg:[&>div:nth-child(-n+2)]:border-b-0 [&>div:nth-child(odd)]:border-r [&>div:nth-child(odd)]:border-line lg:[&>div:nth-child(odd)]:border-r-0">
      <Kpi label={t('policy.kpi.diagnoses')} value={fmt.num(s.total_diagnoses, 0)} />
      <Kpi label={t('policy.kpi.last7')} value={fmt.num(s.diagnoses_last_7_days, 0)} sub={t('policy.kpi.prev7', { count: fmt.num(s.diagnoses_previous_7_days, 0) })} />
      <Kpi label={t('policy.kpi.outbreaks')} value={fmt.num(s.active_outbreaks, 0)} />
      <Kpi label={t('policy.kpi.coverage')} value={fmt.num(s.coverage.grid_cells_30d, 0)} sub={t('policy.kpi.coverageNote')} />
    </dl>
  );
}

function Bars({ entries, label }: { entries: [string, number][]; label: (k: string) => string }) {
  const { fmt } = useI18n();
  const max = Math.max(...entries.map(([, v]) => v), 1);
  return (
    <ul className="space-y-2.5">
      {entries.map(([k, v]) => (
        <li key={k} className="text-sm">
          <div className="flex justify-between gap-3">
            <span className="truncate">{label(k)}</span>
            <span className="font-semibold tabular-nums">{fmt.num(v, 0)}</span>
          </div>
          <div className="mt-1 h-1.5 rounded-full bg-paper-deep/70" aria-hidden>
            <div className="h-1.5 rounded-full bg-soil-500" style={{ width: `${(v / max) * 100}%` }} />
          </div>
        </li>
      ))}
    </ul>
  );
}

export function TrendAndDistribution({ stats }: { stats: Resource<DashboardStats> }) {
  const { t, fmt } = useI18n();
  const s = stats.data;
  if (!s) return null;
  const diseases = Object.entries(s.disease_distribution);
  const crops = Object.entries(s.crop_distribution_30d);
  const cropLabel = (k: string) => {
    const key = `crop.${k}` as MessageKey;
    const v = t(key);
    return v === key ? k : v;
  };
  return (
    <div className="grid gap-6 lg:grid-cols-[3fr_2fr] [&>*]:min-w-0">
      <Card aria-labelledby="trend-title">
        <CardTitle icon={Activity} id="trend-title">
          {t('policy.trend.title')}
        </CardTitle>
        {s.daily_diagnoses_30d.length === 0 ? (
          <p className="text-sm text-ink-soft">{t('policy.trend.empty')}</p>
        ) : (
          <>
            <TrendChart data={s.daily_diagnoses_30d} formatDate={(d) => fmt.date(d)} formatNumber={(n) => fmt.num(n, 0)} />
            <div className="sr-only">
            <table>
              <caption>{t('policy.trend.chartLabel')}</caption>
              <tbody>
                {s.daily_diagnoses_30d.map((d) => (
                  <tr key={d.date}>
                    <th scope="row">{fmt.date(d.date)}</th>
                    <td>{fmt.num(d.count, 0)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            </div>
          </>
        )}
        <ProvenanceLine source={s.provenance.source} kind={s.provenance.kind} time={s.generated_at} note={t('policy.limits.1')} />
      </Card>
      <Card aria-labelledby="dist-title">
        <CardTitle icon={Sprout} id="dist-title">
          {t('policy.diseases.title')}
        </CardTitle>
        {diseases.length ? <Bars entries={diseases} label={(k) => k} /> : <UnavailableNote>{t('policy.diseases.empty')}</UnavailableNote>}
        {crops.length > 0 && (
          <>
            <h3 className="mb-3 mt-6 text-sm font-semibold text-ink-soft">{t('policy.crops.title')}</h3>
            <Bars entries={crops} label={cropLabel} />
          </>
        )}
      </Card>
    </div>
  );
}

export function OutbreaksPanel({ outbreaks }: { outbreaks: Resource<Outbreak[]> }) {
  const { t, fmt } = useI18n();
  const list = outbreaks.data;
  return (
    <Card aria-labelledby="clusters-title" id="map">
      <CardTitle icon={MapIcon} id="clusters-title" description={t('policy.outbreaks.subtitle')}>
        {t('policy.outbreaks.title')}
      </CardTitle>
      {!list && outbreaks.status === 'loading' ? (
        <Skeleton className="h-80" />
      ) : !list && outbreaks.status === 'error' ? (
        <ErrorState error={outbreaks.error} onRetry={outbreaks.reload} />
      ) : list && list.length === 0 ? (
        <UnavailableNote>{t('policy.outbreaks.empty')}</UnavailableNote>
      ) : list ? (
        <>
          <OutbreakMap outbreaks={list} label={t('policy.map.label')} />
          <div className="relative mt-4 overflow-x-auto">
            <table className="w-full min-w-[520px] text-left text-sm">
              <thead className="border-b border-line text-xs text-ink-faint">
                <tr>
                  <th scope="col" className="py-2 pr-3">{t('policy.outbreaks.disease')}</th>
                  <th scope="col" className="py-2 pr-3">{t('policy.outbreaks.area')}</th>
                  <th scope="col" className="py-2 pr-3">{t('policy.outbreaks.reports')}</th>
                  <th scope="col" className="py-2 pr-3">{t('policy.outbreaks.severity')}</th>
                  <th scope="col" className="py-2">{t('policy.outbreaks.last')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {list.map((o) => (
                  <tr key={o.id}>
                    <td className="py-2.5 pr-3 font-medium" lang="en">{o.disease}</td>
                    <td className="py-2.5 pr-3 tabular-nums text-ink-soft">
                      {fmt.num(o.lat, 1)}°, {fmt.num(o.lng, 1)}°
                    </td>
                    <td className="py-2.5 pr-3 tabular-nums">{fmt.num(o.report_count, 0)}</td>
                    <td className="py-2.5 pr-3"><LevelBadge level={o.severity} /></td>
                    <td className="py-2.5 text-ink-soft">{fmt.relative(o.timestamp)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      ) : null}
      <ProvenanceLine source="KrishiSathi" kind="ai_classified_user_reports" note={t('policy.limits.2')} />
    </Card>
  );
}

export function WeatherRiskPanel({ risk, states, stateFilter }: { risk: Resource<WeatherRisk>; states: StateConfig[]; stateFilter: string }) {
  const { t, fmt } = useI18n();
  const regions = risk.data?.regions.filter((r) => stateFilter === 'ALL' || r.state === stateFilter) ?? [];
  return (
    <Card aria-labelledby="wx-title">
      <CardTitle icon={CloudSun} id="wx-title" description={t('policy.weather.note')}>
        {t('policy.weather.title')}
      </CardTitle>
      {!risk.data && risk.status === 'loading' ? (
        <LoadingBlock lines={4} />
      ) : !risk.data && risk.status === 'error' ? (
        <ErrorState error={risk.error} onRetry={risk.reload} />
      ) : (
        <>
        <p className="mb-4 flex flex-wrap gap-x-4 gap-y-1 text-xs text-ink-soft" aria-hidden>
          {(['warning', 'watch', 'info'] as const).map((sev) => (
            <span key={sev} className="inline-flex items-center gap-1.5">
              <span className={cn('h-2 w-2 rounded-full', severityDot[sev])} /> {t(`severity.${sev}`)}
            </span>
          ))}
        </p>
        <ul className="grid gap-x-8 gap-y-5 sm:grid-cols-2 lg:grid-cols-4">
          {regions.map((r) => (
            <li key={r.state} className="border-t border-line pt-3">
              <p className="font-semibold">{states.some((s) => s.code === r.state) ? t(`state.${r.state}` as MessageKey) : r.state}</p>
              {r.status === 'unavailable' ? (
                <p className="mt-1 text-sm text-ink-faint">{t('policy.weather.unavailable')}</p>
              ) : r.insights.length === 0 ? (
                <p className="mt-1 text-sm text-ink-soft">{t('policy.weather.none')}</p>
              ) : (
                <ul className="mt-1.5 space-y-1.5">
                  {r.insights.map((i) => {
                    const v = insightView(t, fmt, i);
                    return (
                      <li key={v.key} className="flex items-start gap-2 text-sm leading-snug">
                        <span aria-hidden className={cn('mt-1.5 h-2 w-2 shrink-0 rounded-full', severityDot[v.severity])} />
                        <span>
                          {v.title}
                          <span className="sr-only"> ({t(`severity.${v.severity}` as MessageKey)})</span>
                        </span>
                      </li>
                    );
                  })}
                </ul>
              )}
            </li>
          ))}
        </ul>
        </>
      )}
      {risk.data && <ProvenanceLine source={risk.data.provenance.source} url={risk.data.provenance.source_url} kind="forecast" time={risk.data.provenance.retrieved_at} />}
    </Card>
  );
}

export function CropHealthPanel() {
  const { t } = useI18n();
  return (
    <Card aria-labelledby="health-title">
      <CardTitle icon={Satellite} id="health-title">
        {t('policy.health.title')}
      </CardTitle>
      <UnavailableNote>{t('policy.health.unavailable')}</UnavailableNote>
    </Card>
  );
}

export function ReportPanel() {
  const { t, language, fmt } = useI18n();
  const [state, setState] = useState<{ status: 'idle' | 'loading' | 'done' | 'error'; report?: DashboardReport; error?: ApiError }>({ status: 'idle' });
  const generate = async () => {
    setState({ status: 'loading' });
    try {
      setState({ status: 'done', report: await getDashboardReport(language) });
    } catch (e) {
      setState({ status: 'error', error: e instanceof ApiError ? e : new ApiError('error', 'INTERNAL_ERROR', null, true) });
    }
  };
  const r = state.report;
  return (
    <Card aria-labelledby="report-title">
      <CardTitle
        icon={FileText}
        id="report-title"
        action={
          state.status !== 'idle' && (
            <button type="button" onClick={generate} disabled={state.status === 'loading'} className={buttonClass.ghost} aria-label={t('policy.report.regenerate')}>
              <RefreshCw className={cn('h-4 w-4', state.status === 'loading' && 'animate-spin')} aria-hidden />
            </button>
          )
        }
      >
        {t('policy.report.title')}
      </CardTitle>
      {state.status === 'idle' && (
        <button type="button" onClick={generate} className={buttonClass.secondary}>
          {t('policy.report.generate')}
        </button>
      )}
      {state.status === 'loading' && (
        <div>
          <p className="mb-3 text-sm text-ink-soft">{t('policy.report.loading')}</p>
          <LoadingBlock lines={5} />
        </div>
      )}
      {state.status === 'error' && state.error && <ErrorState error={state.error} onRetry={generate} />}
      {state.status === 'done' && r && (
        r.status === 'insufficient_data' ? (
          <UnavailableNote>{t('policy.report.insufficient', { records: fmt.num(r.records ?? 0, 0), minimum: fmt.num(r.minimum_records ?? 0, 0) })}</UnavailableNote>
        ) : (
          <>
            <div className="prose prose-sm max-h-[28rem] max-w-none overflow-y-auto">
              <ReactMarkdown remarkPlugins={[remarkGfm]} skipHtml>
                {r.report_text ?? ''}
              </ReactMarkdown>
            </div>
            <ProvenanceLine source="Google Gemini" kind="ai_generated_summary" time={r.generated_at} note={t('policy.report.note')} />
          </>
        )
      )}
    </Card>
  );
}

export function SignalsPanel({ signals, states, stateFilter }: { signals: Resource<FederationReport>; states: StateConfig[]; stateFilter: string }) {
  const { t, fmt } = useI18n();
  const [open, setOpen] = useState(false);
  const list = (signals.data?.signals ?? []).filter((s) => stateFilter === 'ALL' || s.from_state === stateFilter || s.to_state === stateFilter || !s.to_state);
  return (
    <Card aria-labelledby="signals-title">
      <CardTitle icon={Globe2} id="signals-title">
        {t('policy.signals.title')}
      </CardTitle>
      {!signals.data && signals.status === 'loading' ? (
        <LoadingBlock />
      ) : !signals.data && signals.status === 'error' ? (
        <ErrorState error={signals.error} onRetry={signals.reload} />
      ) : list.length === 0 ? (
        <p className="text-sm text-ink-soft">{t('policy.signals.empty')}</p>
      ) : (
        <ul className="max-h-96 space-y-3 overflow-y-auto">
          {list.map((s) => (
            <li key={s.signal_id} className="rounded-[var(--radius-inner)] bg-paper/60 p-3 text-sm ring-1 ring-line">
              <div className="mb-1 flex flex-wrap items-center justify-between gap-2">
                <span className="font-semibold">
                  {t(`state.${s.from_state}` as MessageKey)} → {s.to_state ? t(`state.${s.to_state}` as MessageKey) : t('policy.signals.broadcast')}
                </span>
                <span className="text-xs text-ink-faint">{fmt.relative(s.timestamp)}</span>
              </div>
              <p className="mb-1 text-xs text-ink-soft">
                {t(`policy.signals.type.${s.signal_type}` as MessageKey)} · {t(`severity.${s.severity === 'critical' ? 'critical' : s.severity === 'high' ? 'warning' : s.severity === 'moderate' ? 'watch' : 'info'}` as MessageKey)}
              </p>
              <p lang="en">{s.message}</p>
            </li>
          ))}
        </ul>
      )}
      {signals.data && <p className="mt-3 text-xs text-ink-faint">{t('policy.signals.note')}</p>}
      <div className="mt-4 border-t border-line pt-4">
        {open ? (
          <PublishForm states={states} onDone={() => { setOpen(false); signals.reload(); }} onCancel={() => setOpen(false)} />
        ) : (
          <button type="button" onClick={() => setOpen(true)} className={buttonClass.secondary}>
            <ShieldAlert className="h-4 w-4" aria-hidden /> {t('policy.signals.publish')}
          </button>
        )}
      </div>
    </Card>
  );
}

function PublishForm({ states, onDone, onCancel }: { states: StateConfig[]; onDone: () => void; onCancel: () => void }) {
  const { t } = useI18n();
  const ids = { token: useId(), from: useId(), to: useId(), type: useId(), sev: useId(), msg: useId() };
  const [form, setForm] = useState({ token: '', from: states[0]?.code ?? 'MH', to: '', type: 'disease_alert', severity: 'moderate', message: '' });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const set = (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => setForm((f) => ({ ...f, [k]: e.target.value }));

  return (
    <form
      className="space-y-3"
      onSubmit={async (e) => {
        e.preventDefault();
        setBusy(true);
        setError(null);
        try {
          await postExchangeSignal(
            { from_state: form.from, to_state: form.to || null, signal_type: form.type, severity: form.severity as 'moderate', message: form.message },
            form.token.trim(),
          );
          onDone();
        } catch (err) {
          setError(err instanceof ApiError ? err : new ApiError('error', 'INTERNAL_ERROR', null, true));
        } finally {
          setBusy(false);
        }
      }}
    >
      <div>
        <label htmlFor={ids.token} className="mb-1 block text-sm font-semibold">{t('policy.signals.token')}</label>
        <input id={ids.token} type="password" autoComplete="off" required value={form.token} onChange={set('token')} className={inputClass} />
        <p className="mt-1 text-xs text-ink-faint">{t('policy.signals.tokenHelp')}</p>
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        <div>
          <label htmlFor={ids.from} className="mb-1 block text-sm font-semibold">{t('policy.signals.from')}</label>
          <select id={ids.from} value={form.from} onChange={set('from')} className={inputClass}>
            {states.map((s) => <option key={s.code} value={s.code}>{t(`state.${s.code}` as MessageKey)}</option>)}
          </select>
        </div>
        <div>
          <label htmlFor={ids.to} className="mb-1 block text-sm font-semibold">{t('policy.signals.to')}</label>
          <select id={ids.to} value={form.to} onChange={set('to')} className={inputClass}>
            <option value="">{t('policy.signals.broadcast')}</option>
            {states.map((s) => <option key={s.code} value={s.code}>{t(`state.${s.code}` as MessageKey)}</option>)}
          </select>
        </div>
        <div>
          <label htmlFor={ids.type} className="mb-1 block text-sm font-semibold">{t('policy.signals.type')}</label>
          <select id={ids.type} value={form.type} onChange={set('type')} className={inputClass}>
            {['disease_alert', 'pest_advisory', 'weather_advisory', 'best_practice'].map((v) => (
              <option key={v} value={v}>{t(`policy.signals.type.${v}` as MessageKey)}</option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor={ids.sev} className="mb-1 block text-sm font-semibold">{t('policy.signals.severity')}</label>
          <select id={ids.sev} value={form.severity} onChange={set('severity')} className={inputClass}>
            <option value="info">{t('severity.info')}</option>
            <option value="moderate">{t('severity.watch')}</option>
            <option value="high">{t('severity.warning')}</option>
            <option value="critical">{t('severity.critical')}</option>
          </select>
        </div>
      </div>
      <div>
        <label htmlFor={ids.msg} className="mb-1 block text-sm font-semibold">{t('policy.signals.message')}</label>
        <textarea id={ids.msg} required maxLength={1000} rows={3} value={form.message} onChange={set('message')} className={inputClass} />
      </div>
      {error && <ErrorState compact error={error} />}
      <div className="flex flex-wrap gap-3">
        <button type="submit" disabled={busy} className={buttonClass.primary}>{t('policy.signals.submit')}</button>
        <button type="button" onClick={onCancel} className={buttonClass.secondary}>{t('action.cancel')}</button>
      </div>
    </form>
  );
}

export function LimitationsPanel() {
  const { t } = useI18n();
  return (
    <Card aria-labelledby="limits-title" className="bg-soil-50/60 shadow-none">
      <h2 id="limits-title" className="mb-3 font-display text-[1.3rem] font-medium">{t('policy.limits.title')}</h2>
      <ul className="list-disc space-y-1.5 pl-5 text-sm text-ink-soft">
        {(['policy.limits.1', 'policy.limits.2', 'policy.limits.3', 'policy.limits.4'] as const).map((k) => (
          <li key={k}>{t(k)}</li>
        ))}
      </ul>
    </Card>
  );
}
