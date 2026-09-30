'use client';

import { useId, useState } from 'react';
import { EarlyWarningPanel } from '@/components/policy/EarlyWarning';
import { EvaluationPanel } from '@/components/policy/Evaluation';
import { CropHealthPanel, KpiRow, LimitationsPanel, OutbreaksPanel, ReportPanel, SignalsPanel, TrendAndDistribution, WeatherRiskPanel } from '@/components/policy/Panels';
import { inputClass, PageHeader } from '@/components/ui';
import { getDashboardStats, getEarlyWarning, getEvaluation, getExchangeSignals, getOutbreaks, getStates, getWeatherRisk } from '@/lib/api';
import { useI18n } from '@/lib/i18n';
import { useResource } from '@/lib/use-resource';
import type { MessageKey } from '@/locales/en';

export default function PolicyDashboardPage() {
  const { t, fmt } = useI18n();
  const [stateFilter, setStateFilter] = useState('ALL');
  const filterId = useId();

  // Independent panels: a failure in one source degrades only that panel.
  const stats = useResource((s) => getDashboardStats(s), []);
  const ew = useResource((s) => getEarlyWarning(s), []);
  const outbreaks = useResource((s) => getOutbreaks(s), []);
  const risk = useResource((s) => getWeatherRisk(s), []);
  const signals = useResource((s) => getExchangeSignals(s), []);
  const states = useResource((s) => getStates(s), []);
  const evaluation = useResource((s) => getEvaluation(s), []);
  const stateList = states.data ?? [];

  return (
    <div className="mx-auto w-full max-w-6xl px-4 pb-12 pt-6 sm:px-6 sm:pt-10">
      <PageHeader
        eyebrow={t('policy.eyebrow')}
        title={t('policy.title')}
        subtitle={
          <>
            {t('policy.subtitle')}
            {stats.data && <span className="mt-1 block text-xs text-ink-faint">{t('policy.freshness', { time: fmt.dateTime(stats.data.generated_at) })}</span>}
          </>
        }
      >
        <div className="sm:w-60">
          <label htmlFor={filterId} className="mb-1 block text-sm font-semibold">
            {t('policy.filter.state')}
          </label>
          <select id={filterId} value={stateFilter} onChange={(e) => setStateFilter(e.target.value)} className={inputClass}>
            <option value="ALL">{t('policy.filter.all')}</option>
            {stateList.map((s) => (
              <option key={s.code} value={s.code}>
                {t(`state.${s.code}` as MessageKey)}
              </option>
            ))}
          </select>
        </div>
      </PageHeader>

      <div className="space-y-6">
        <KpiRow stats={stats} />
        <EarlyWarningPanel ew={ew} states={stateList} stateFilter={stateFilter} />
        <OutbreaksPanel outbreaks={outbreaks} />
        <TrendAndDistribution stats={stats} />
        <WeatherRiskPanel risk={risk} states={stateList} stateFilter={stateFilter} />
        <div className="grid items-start gap-6 lg:grid-cols-2 [&>*]:min-w-0">
          <ReportPanel />
          <SignalsPanel signals={signals} states={stateList} stateFilter={stateFilter} />
        </div>
        <EvaluationPanel evaluation={evaluation} />
        <div className="grid items-start gap-6 lg:grid-cols-2 [&>*]:min-w-0">
          <CropHealthPanel />
          <LimitationsPanel />
        </div>
      </div>
    </div>
  );
}
