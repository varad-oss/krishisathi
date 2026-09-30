import type { makeFormatters, Params } from '@/lib/i18n';
import type { Insight, InsightSeverity } from '@/lib/types';
import type { MessageKey } from '@/locales/en';

type T = (key: MessageKey, params?: Params) => string;
type Fmt = ReturnType<typeof makeFormatters>;

export interface AlertView {
  key: string;
  severity: InsightSeverity;
  category: string;
  title: string;
  why: string;
  action: string;
  impact: string;
  when: string;
  basis: string;
  basisUrl: string | null;
  kind: 'forecast' | 'current_model_estimate';
}

export function whenLabel(t: T, fmt: Fmt, date: string | null): string {
  if (!date) return t('insight.now');
  const today = new Date();
  const d = new Date(`${date}T00:00:00`);
  const diff = Math.round((d.getTime() - new Date(today.getFullYear(), today.getMonth(), today.getDate()).getTime()) / 86_400_000);
  if (diff === 0) return t('farm.weather.today');
  if (diff === 1) return t('farm.weather.tomorrow');
  return fmt.date(date, { weekday: 'long', day: 'numeric', month: 'short' });
}

export function insightView(t: T, fmt: Fmt, i: Insight): AlertView {
  const p = i.params;
  const when = whenLabel(t, fmt, i.date);
  const params: Params = {
    date: when,
    mm: fmt.num(p.precipitation_mm ?? p.precipitation_total_mm ?? null),
    prob: fmt.num(p.probability_pct ?? null, 0),
    temp: fmt.num(p.temp_max_c ?? p.temp_min_c ?? p.temp_mean_c ?? null),
    rh: fmt.num(p.humidity_mean_pct ?? null, 0),
    et0: fmt.num(p.et0_total_mm ?? null),
    days: fmt.num(p.days ?? null, 0),
    wind: fmt.num(p.wind_kmh ?? null, 0),
  };
  const whyKey: MessageKey = i.id === 'rain_expected' && p.probability_pct == null ? 'insight.rain_expected.whyNoProb' : (`insight.${i.id}.why` as MessageKey);
  const isImd = i.basis.source.name.includes('IMD');
  return {
    key: `${i.id}-${i.date ?? 'now'}`,
    severity: i.severity,
    category: i.category,
    title: t(`insight.${i.id}.title` as MessageKey, params),
    why: t(whyKey, params),
    action: t(`insight.${i.id}.action` as MessageKey),
    impact: t(`insight.${i.id}.impact` as MessageKey),
    when,
    basis: t(isImd ? 'insight.basis.imd' : 'insight.basis.guidance'),
    basisUrl: i.basis.source.url,
    kind: i.basis.kind,
  };
}
