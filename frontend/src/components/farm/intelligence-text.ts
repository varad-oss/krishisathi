import type { makeFormatters, Params } from '@/lib/i18n';
import type { Evidence, EvidenceBasis, Risk, TopAction } from '@/lib/types';
import type { MessageKey } from '@/locales/en';
import { whenLabel } from './insight-text';

type T = (key: MessageKey, params?: Params) => string;
type Fmt = ReturnType<typeof makeFormatters>;

/** What to do for each engine action. Weather actions reuse the existing, reviewed insight advice. */
const ACTION_WHAT: Record<string, MessageKey> = {
  clear_drainage: 'insight.heavy_rain.action',
  delay_irrigation: 'insight.rain_expected.action',
  irrigate_soon: 'insight.dry_spell.action',
  protect_from_heat: 'insight.heat_stress.action',
  protect_from_cold: 'insight.cold_stress.action',
  postpone_spraying: 'action.postpone_spraying.what',
  protect_harvest: 'action.protect_harvest.what',
  inspect_field: 'action.inspect_field.what',
  routine_monitoring: 'action.routine_monitoring.what',
};

const IMPACT: Partial<Record<Risk['category'], MessageKey>> = {
  waterlogging: 'insight.heavy_rain.impact',
  water_stress: 'insight.dry_spell.impact',
  heat_stress: 'insight.heat_stress.impact',
  cold_stress: 'insight.cold_stress.impact',
  disease: 'farm.alerts.outbreakImpact',
  spray_window: 'insight.spray_wind.impact',
};

/** Drivers that explain a raised risk. "no_*" drivers mean nothing crossed a rule and are not listed. */
const DRIVERS = new Set([
  'heavy_rain_forecast', 'rain_expected', 'soil_wet', 'soil_dry', 'dry_spell_forecast', 'heat_stress_forecast',
  'cold_stress_forecast', 'sensitive_stage', 'fungal_weather', 'nearby_outbreak', 'recent_farm_diagnosis', 'wind_high',
  'rain_soon', 'harvest_stage', 'ndvi_decline', 'ndvi_stable', 'not_harvest_stage', 'sar_water_signal', 'ndvi_below_baseline',
]);

const BASIS_KIND: Record<EvidenceBasis, string> = {
  observed: 'observed',
  forecast: 'forecast',
  model_estimate: 'model',
  satellite_observation: 'satellite_observation',
  rule_based: 'rule',
  ai_generated: 'ai_model',
  ai_classified_reports: 'ai_classified_user_reports',
  farmer_reported: 'farmer_reported',
  static_reference: 'static_reference',
};

export const basisKind = (b: EvidenceBasis) => BASIS_KIND[b];

export function actionTitle(t: T, action: string | null): string {
  return action ? t(`action.${action}.title` as MessageKey) : '';
}

export function actionWhat(t: T, action: string, drivers: string[], cropLabel: string | null): string {
  if (action === 'scout_for_disease') {
    return drivers.includes('nearby_outbreak') || drivers.includes('recent_farm_diagnosis')
      ? t('farm.alerts.outbreakWhat', { crop: cropLabel ?? t('farm.alerts.yourCrop') })
      : t('insight.fungal_risk.action');
  }
  return ACTION_WHAT[action] ? t(ACTION_WHAT[action]) : '';
}

export const impactText = (t: T, r: Risk) => (IMPACT[r.category] ? t(IMPACT[r.category]!) : null);

function driverTexts(t: T, drivers: string[]): string[] {
  return drivers.filter((d) => DRIVERS.has(d)).map((d) => t(`driver.${d}` as MessageKey));
}

/** "Because A, B and C." joined with the language's own list conjunction. */
export function because(t: T, lang: string, drivers: string[]): string | null {
  const parts = driverTexts(t, drivers);
  if (!parts.length) return null;
  const list = new Intl.ListFormat(lang, { style: 'long', type: 'conjunction' }).format(parts);
  return t('today.because', { reasons: list });
}

export function reasonText(t: T, reason: string | null): string {
  const key = `reason.${reason}` as MessageKey;
  const text = reason ? t(key) : key;
  return text === key ? t('reason.unavailable') : text;
}

export function stageText(t: T, stage: string | null): string {
  return stage ? t(`stage.${stage}` as MessageKey) : '';
}

export function evidenceText(t: T, fmt: Fmt, e: Evidence): string {
  const p = e.params;
  const num = (v: unknown, d = 1) => fmt.num(typeof v === 'number' ? v : null, d);
  const date = whenLabel(t, fmt, e.date && /^\d{4}-\d{2}-\d{2}$/.test(e.date) ? e.date : null);
  switch (e.id) {
    case 'rain_forecast':
      return p.probability_pct == null
        ? t('evidence.rain_forecast_noprob', { date, mm: num(e.value) })
        : t('evidence.rain_forecast', { date, mm: num(e.value), prob: num(p.probability_pct, 0) });
    case 'temp_max_forecast':
      return t('evidence.temp_max_forecast', { date, temp: num(e.value) });
    case 'temp_min_forecast':
      return t('evidence.temp_min_forecast', { date, temp: num(e.value) });
    case 'humid_forecast':
      return t('evidence.humid_forecast', { date, rh: num(e.value, 0), temp: num(p.temp_mean_c) });
    case 'dry_spell_forecast':
      return t('evidence.dry_spell_forecast', { days: num(p.days, 0), mm: num(e.value), et0: num(p.et0_total_mm) });
    case 'wind_now':
      return t('evidence.wind_now', { wind: num(e.value, 0) });
    case 'soil_moisture':
      return t('evidence.soil_moisture', { value: num(e.value, 2) });
    case 'soil_water_status':
      return t('evidence.soil_water_status', {
        status: t(`soilwater.${e.value}` as MessageKey),
        pct: num(typeof p.available_water_fraction === 'number' ? Math.round(p.available_water_fraction * 100) : null, 0),
      });
    case 'crop_stage':
      return t('evidence.crop_stage', { stage: stageText(t, String(e.value)), days: num(p.days_since_sowing, 0) });
    case 'nearby_outbreak':
      return t('farm.alerts.outbreakWhy', { count: num(p.report_count, 0), disease: String(e.value), distance: num(p.distance_km, 0) });
    case 'recent_diagnosis':
      return t('evidence.recent_diagnosis', {
        date: e.date ? fmt.date(e.date) : '—',
        disease: String(e.value ?? '—'),
        certainty: p.certainty ? t(`level.${p.certainty}` as MessageKey) : '—',
      });
    case 'ndvi_change':
      return t('evidence.ndvi_change', { ndvi: num(p.ndvi, 2), change: `${typeof e.value === 'number' && e.value > 0 ? '+' : ''}${num(e.value, 2)}` });
    case 'ndvi_baseline':
      return t('evidence.ndvi_baseline', { ndvi: num(p.ndvi, 2), years: num(p.years, 0), min: num(p.min, 2), max: num(p.max, 2) });
    case 'sar_vh_change':
      return t('evidence.sar_vh_change', { vh: num(p.vh_db, 1), change: `${typeof e.value === 'number' && e.value > 0 ? '+' : ''}${num(e.value, 1)}` });
    default:
      return String(e.value ?? '');
  }
}

export const topActionTitle = (t: T, a: TopAction) => (a.status === 'unavailable' ? t('farm.today.weatherUnavailable') : actionTitle(t, a.action));
