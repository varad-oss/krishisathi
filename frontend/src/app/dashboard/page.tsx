'use client';

import { useId, useState } from 'react';
import { CropHealthPanel, KpiRow, LimitationsPanel, OutbreaksPanel, ReportPanel, SignalsPanel, TrendAndDistribution, WeatherRiskPanel } from '@/components/policy/Panels';
import { inputClass } from '@/components/ui';
import { getDashboardStats, getExchangeSignals, getOutbreaks, getStates, getWeatherRisk } from '@/lib/api';
import { useI18n } from '@/lib/i18n';
import { useResource } from '@/lib/use-resource';
import type { MessageKey } from '@/locales/en';

export default function PolicyDashboardPage() {
  const { t, fmt } = useI18n();
  const [stateFilter, setStateFilter] = useState('ALL');
  const filterId = useId();

  // Independent panels: a failure in one source degrades only that panel.
  const stats = useResource((s) => getDashboardStats(s), []);
  const outbreaks = useResource((s) => getOutbreaks(s), []);
  const risk = useResource((s) => getWeatherRisk(s), []);
  const signals = useResource((s) => getExchangeSignals(s), []);
  const states = useResource((s) => getStates(s), []);
  const stateList = states.data ?? [];

  return (
    <div className="mx-auto w-full max-w-6xl px-4 pb-10 pt-6 sm:px-6">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">{t('policy.title')}</h1>
          <p className="mt-1 max-w-2xl text-ink-soft">{t('policy.subtitle')}</p>
          {stats.data && <p className="mt-2 text-xs text-ink-faint">{t('policy.freshness', { time: fmt.dateTime(stats.data.generated_at) })}</p>}
        </div>
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
      </div>

      <div className="space-y-5">
        <KpiRow stats={stats} />
        <TrendAndDistribution stats={stats} />
        <OutbreaksPanel outbreaks={outbreaks} />
        <div className="grid gap-5 lg:grid-cols-2">
          <WeatherRiskPanel risk={risk} states={stateList} stateFilter={stateFilter} />
          <ReportPanel />
        </div>
        <div className="grid gap-5 lg:grid-cols-2">
          <SignalsPanel signals={signals} states={stateList} stateFilter={stateFilter} />
          <div className="space-y-5">
            <CropHealthPanel />
            <LimitationsPanel />
          </div>
        </div>
      </div>
    </div>
  );
}
