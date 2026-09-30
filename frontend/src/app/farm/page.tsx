'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ArrowRight, History, MapPin, Pencil, Sprout } from 'lucide-react';
import FarmProfileForm, { useLocationLabel } from '@/components/FarmProfileForm';
import { RiskRadar } from '@/components/farm/Intelligence';
import { TodayCard, WeatherCard } from '@/components/farm/TodayAlertsWeather';
import { CropOptionsCard } from '@/components/farm/Regenerative';
import { CropHealthCard, KvkCard, SoilRegenCard } from '@/components/farm/SoilCropKvk';
import { buttonClass, LoadingBlock, Section } from '@/components/ui';
import { stageText } from '@/components/farm/intelligence-text';
import { getCropHealth, getFieldCropHealth, getPlot, getFarmConditions, getFarmIntelligence, getFarmTwinIntelligence, getCropOptions, getNearestKvk, getRegenerative } from '@/lib/api';
import type { FarmTwinIntelligence } from '@/lib/types';
import { useFarmProfile } from '@/lib/farm-profile';
import { useI18n } from '@/lib/i18n';
import { useResource } from '@/lib/use-resource';
import { cacheKey } from '@/lib/offline';
import type { MessageKey } from '@/locales/en';
import { cn } from '@/lib/utils';

const SECTIONS: { id: string; label: MessageKey; href?: string }[] = [
  { id: 'risks', label: 'farm.section.risks' },
  { id: 'crop', label: 'farm.section.cropHealth' },
  { id: 'weather', label: 'farm.section.weather' },
  { id: 'soil', label: 'farm.section.soil' },
  { id: 'options', label: 'farm.section.options' },
  { id: 'history', label: 'farm.section.history', href: '/history' },
];

export default function FarmPage() {
  const { t, fmt } = useI18n();
  const { profile, ready, twin, twinRevision, forgetTwin } = useFarmProfile();
  const [editing, setEditing] = useState(false);
  // Bumped when the field outline is saved or removed, so satellite values and risks are reloaded for it.
  const [plotRevision, setPlotRevision] = useState(0);
  const locationLabel = useLocationLabel();
  const loc = profile.location;
  const crop = profile.crop;
  const sowing = profile.sowingDate;
  const key = [loc?.lat, loc?.lng, crop];
  // Last good copy of each panel is kept on the device and shown, labelled with its time, only when offline.
  const saved = (panel: string) => (loc ? cacheKey(panel, loc.lat, loc.lng, crop) : null);

  // Each panel loads independently so one failing source never blanks the page.
  const conditions = useResource(loc ? (s) => getFarmConditions(loc.lat, loc.lng, s) : null, key, saved('conditions'));
  // With a farm record the engine also uses the farm's own diagnoses and records what it advised.
  const intel = useResource<FarmTwinIntelligence>(
    loc
      ? (s) =>
          twin
            ? getFarmTwinIntelligence(twin, s).catch((e) => {
                if (e?.code === 'NOT_FOUND') forgetTwin();
                throw e;
              })
            : getFarmIntelligence(loc.lat, loc.lng, crop, sowing, s)
      : null,
    [...key, sowing, twin?.farmId, twinRevision, plotRevision],
    saved(`intelligence:${sowing ?? '-'}`),
  );
  const regen = useResource(loc ? (s) => getRegenerative(loc.lat, loc.lng, crop, sowing, s) : null, [...key, sowing], saved(`regenerative:${sowing ?? '-'}`));
  const options = useResource(loc ? (s) => getCropOptions(loc.lat, loc.lng, crop, s) : null, key, saved('crop-options'));
  const plot = useResource(twin ? (s) => getPlot(twin, s) : null, [twin?.farmId, plotRevision]);
  // With a farm record, satellite values follow the drawn field (or the farm point when there is none).
  const health = useResource(
    loc ? (s) => (twin ? getFieldCropHealth(twin, s) : getCropHealth(loc.lat, loc.lng, s)) : null,
    [...key, twin?.farmId, twinRevision, plotRevision],
    saved(`crop-health:${twin ? 'field' : 'point'}`),
  );
  const kvk = useResource(loc ? (s) => getNearestKvk(loc.lat, loc.lng, s) : null, key, saved('kvk'));
  const cropLabel = crop ? t(`crop.${crop}` as MessageKey) : null;

  if (!ready) {
    return (
      <div className="mx-auto w-full max-w-6xl px-4 py-10 sm:px-6">
        <LoadingBlock lines={4} label={t('farm.loading')} />
      </div>
    );
  }

  if (!loc || editing) {
    return (
      <div className="mx-auto w-full max-w-xl px-4 pb-12 pt-8 sm:px-6 sm:pt-12">
        <h1 id="profile-title" className="font-display text-[1.85rem] leading-tight sm:text-4xl">
          {t('profile.title')}
        </h1>
        <p className="mb-8 mt-3 text-[1.05rem] text-ink-soft">{t('profile.body')}</p>
        <FarmProfileForm onDone={() => setEditing(false)} onCancel={loc ? () => setEditing(false) : undefined} />
      </div>
    );
  }

  const stage = intel.data?.farm.crop_stage;
  const field = plot.data?.plot;
  return (
    <div className="mx-auto w-full max-w-6xl px-4 pb-8 pt-6 sm:px-6 sm:pt-10">
      {/* Today's field: which farm, which crop, where, and where it stands, before any advice. */}
      <header className="mb-8 border-b border-line pb-6">
        <div className="min-w-0 [overflow-wrap:anywhere]">
          <p className="text-sm font-medium text-ink-soft">{fmt.date(new Date(), { weekday: 'long', day: 'numeric', month: 'long' })}</p>
          <div className="mt-1 flex items-start justify-between gap-4">
            <h1 className="font-display text-[1.85rem] leading-tight sm:text-[2.5rem]">{t('farm.title')}</h1>
            <button type="button" onClick={() => setEditing(true)} className={cn(buttonClass.secondary, 'mt-0.5 min-h-11 shrink-0 px-3.5 text-sm')}>
              <Pencil className="h-4 w-4" aria-hidden /> {t('action.change')}
            </button>
          </div>
          <p className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-ink-soft">
            <span className="inline-flex items-center gap-1.5 font-medium text-ink">
              <MapPin className="h-4 w-4 text-leaf-600" aria-hidden /> {locationLabel(loc)}
            </span>
            {cropLabel && (
              <span className="inline-flex items-center gap-1.5">
                <Sprout className="h-4 w-4 text-leaf-600" aria-hidden /> {cropLabel}
              </span>
            )}
            {field && <span className="tabular-nums">{t('farm.plot.saved', { area: fmt.num(field.area_ha, field.area_ha < 1 ? 2 : 1) })}</span>}
          </p>
          {stage?.stage && (
            <p className="mt-1 text-sm text-ink-soft">
              {t('farm.stage', { stage: stageText(t, stage.stage), days: fmt.num(stage.days_since_sowing, 0) })}
              {stage.confidence && ` · ${t('risk.confidence', { level: t(`level.${stage.confidence}` as MessageKey) })}`}
            </p>
          )}
        </div>
      </header>

      <TodayCard conditions={conditions} health={health} intel={intel} twin={twin} cropLabel={cropLabel} />

      <nav aria-label={t('farm.sections')} className="sticky top-[var(--header-h)] z-30 -mx-4 border-y border-line bg-paper/95 px-4 backdrop-blur sm:-mx-6 sm:px-6">
        <ul className="-mb-px flex gap-1 overflow-x-auto [scrollbar-width:none]">
          {SECTIONS.map((s) => (
            <li key={s.id}>
              <a href={s.href ?? `#${s.id}`} className="inline-flex min-h-12 items-center whitespace-nowrap border-b-2 border-transparent px-3 text-sm font-medium text-ink-soft transition-colors hover:border-leaf-500 hover:text-ink">
                {t(s.label)}
              </a>
            </li>
          ))}
        </ul>
      </nav>

      <RiskRadar intel={intel} cropLabel={cropLabel} />
      <CropHealthCard health={health} location={loc} twin={twin} plot={plot} onPlotChanged={() => setPlotRevision((r) => r + 1)} />
      <WeatherCard conditions={conditions} />
      <SoilRegenCard regen={regen} twin={twin} />
      <CropOptionsCard options={options} />
      <KvkCard kvk={kvk} />
      <Section id="farm-history" title={t('history.title')} description={t('history.subtitle')}>
        <Link href="/history" className={buttonClass.secondary}>
          <History className="h-5 w-5" aria-hidden /> {t('history.title')} <ArrowRight className="h-4 w-4" aria-hidden />
        </Link>
      </Section>
    </div>
  );
}
