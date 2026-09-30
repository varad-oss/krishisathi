'use client';

import { useState } from 'react';
import { MapPin, Pencil } from 'lucide-react';
import FarmProfileForm, { useLocationLabel } from '@/components/FarmProfileForm';
import { FarmHistoryCard } from '@/components/farm/History';
import { RiskRadar } from '@/components/farm/Intelligence';
import { TodayCard, WeatherCard } from '@/components/farm/TodayAlertsWeather';
import { CropOptionsCard } from '@/components/farm/Regenerative';
import { CropHealthCard, KvkCard, SoilRegenCard } from '@/components/farm/SoilCropKvk';
import { buttonClass, Card, LoadingBlock } from '@/components/ui';
import { getCropHealth, getFarmConditions, getFarmHistory, getFarmIntelligence, getFarmTwinIntelligence, getCropOptions, getNearestKvk, getRegenerative } from '@/lib/api';
import type { FarmTwinIntelligence } from '@/lib/types';
import { useFarmProfile } from '@/lib/farm-profile';
import { useI18n } from '@/lib/i18n';
import { useResource } from '@/lib/use-resource';
import type { MessageKey } from '@/locales/en';
import { cn } from '@/lib/utils';

const SECTIONS: { id: string; label: MessageKey }[] = [
  { id: 'today', label: 'farm.section.today' },
  { id: 'risks', label: 'farm.section.risks' },
  { id: 'weather', label: 'farm.section.weather' },
  { id: 'crop', label: 'farm.section.cropHealth' },
  { id: 'soil', label: 'farm.section.soil' },
  { id: 'options', label: 'farm.section.options' },
  { id: 'history', label: 'farm.section.history' },
];

export default function FarmPage() {
  const { t } = useI18n();
  const { profile, ready, twin, twinRevision, forgetTwin } = useFarmProfile();
  const [editing, setEditing] = useState(false);
  const locationLabel = useLocationLabel();
  const loc = profile.location;
  const crop = profile.crop;
  const sowing = profile.sowingDate;
  const key = [loc?.lat, loc?.lng, crop];

  // Each panel loads independently so one failing source never blanks the page.
  const conditions = useResource(loc ? (s) => getFarmConditions(loc.lat, loc.lng, s) : null, key);
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
    [...key, sowing, twin?.farmId, twinRevision],
  );
  const history = useResource(twin ? (s) => getFarmHistory(twin, s) : null, [twin?.farmId, twinRevision, intel.updatedAt]);
  const regen = useResource(loc ? (s) => getRegenerative(loc.lat, loc.lng, crop, sowing, s) : null, [...key, sowing]);
  const options = useResource(loc ? (s) => getCropOptions(loc.lat, loc.lng, crop, s) : null, key);
  const health = useResource(loc ? (s) => getCropHealth(loc.lat, loc.lng, s) : null, key);
  const kvk = useResource(loc ? (s) => getNearestKvk(loc.lat, loc.lng, s) : null, key);
  const cropLabel = crop ? t(`crop.${crop}` as MessageKey) : null;

  if (!ready) {
    return (
      <div className="mx-auto w-full max-w-6xl px-4 py-10 sm:px-6">
        <LoadingBlock lines={4} />
      </div>
    );
  }

  if (!loc || editing) {
    return (
      <div className="mx-auto w-full max-w-xl px-4 py-10 sm:px-6">
        <Card aria-labelledby="profile-title">
          <h1 id="profile-title" className="font-display text-[1.9rem] font-medium leading-tight">
            {t('profile.title')}
          </h1>
          <p className="mb-6 mt-2 text-ink-soft">{t('profile.body')}</p>
          <FarmProfileForm onDone={() => setEditing(false)} onCancel={loc ? () => setEditing(false) : undefined} />
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-6xl px-4 pb-12 pt-6 sm:px-6 sm:pt-10">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <h1 className="font-display text-[2rem] font-medium leading-tight sm:text-[2.5rem]">{t('farm.title')}</h1>
        <button type="button" onClick={() => setEditing(true)} className={cn(buttonClass.secondary, 'min-h-10 px-3.5')}>
          <MapPin className="h-4 w-4 text-leaf-600" aria-hidden />
          <span className="max-w-[14rem] truncate">{locationLabel(loc)}</span>
          <Pencil className="h-3.5 w-3.5 text-ink-faint" aria-hidden />
          <span className="sr-only">{t('action.change')}</span>
        </button>
      </div>

      <nav aria-label={t('farm.sections')} className="sticky top-16 z-30 -mx-4 mb-6 border-b border-line bg-paper/90 px-4 backdrop-blur-md sm:-mx-6 sm:px-6">
        <ul className="flex gap-1 overflow-x-auto">
          {SECTIONS.map((s) => (
            <li key={s.id}>
              <a href={`#${s.id}`} className="inline-flex min-h-11 items-center whitespace-nowrap border-b-2 border-transparent px-3 text-sm font-medium text-ink-soft transition-colors hover:border-leaf-500 hover:text-ink">
                {t(s.label)}
              </a>
            </li>
          ))}
        </ul>
      </nav>

      <div className="space-y-6">
        <TodayCard conditions={conditions} health={health} intel={intel} twin={twin} locationLabel={locationLabel(loc)} cropLabel={cropLabel} />
        <div className="grid items-start gap-6 lg:grid-cols-[1.6fr_1fr] [&>*]:min-w-0">
          <RiskRadar intel={intel} cropLabel={cropLabel} />
          <div className="space-y-6">
            <CropHealthCard health={health} location={loc} />
            <KvkCard kvk={kvk} />
          </div>
        </div>
        <WeatherCard conditions={conditions} />
        <SoilRegenCard regen={regen} twin={twin} onSaved={history.reload} />
        <CropOptionsCard options={options} />
        <FarmHistoryCard history={history} twin={twin} />
      </div>
    </div>
  );
}
