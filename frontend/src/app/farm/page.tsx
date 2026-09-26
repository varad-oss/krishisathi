'use client';

import { useState } from 'react';
import { MapPin, Pencil } from 'lucide-react';
import FarmProfileForm, { useLocationLabel } from '@/components/FarmProfileForm';
import { AlertsCard, TodayCard, WeatherCard, useAlertViews } from '@/components/farm/TodayAlertsWeather';
import { CropHealthCard, KvkCard, SoilRegenCard } from '@/components/farm/SoilCropKvk';
import { buttonClass, Card, LoadingBlock } from '@/components/ui';
import { getCropHealth, getFarmConditions, getNearestKvk, getPersonalizedAlerts, getRegenerative } from '@/lib/api';
import { useFarmProfile } from '@/lib/farm-profile';
import { useI18n } from '@/lib/i18n';
import { useResource } from '@/lib/use-resource';
import type { MessageKey } from '@/locales/en';

const SECTIONS: { id: string; label: MessageKey }[] = [
  { id: 'today', label: 'farm.section.today' },
  { id: 'alerts', label: 'farm.section.alerts' },
  { id: 'weather', label: 'farm.section.weather' },
  { id: 'soil', label: 'farm.section.soil' },
  { id: 'crop', label: 'farm.section.cropHealth' },
];

export default function FarmPage() {
  const { t } = useI18n();
  const { profile, ready } = useFarmProfile();
  const [editing, setEditing] = useState(false);
  const locationLabel = useLocationLabel();
  const loc = profile.location;
  const crop = profile.crop;
  const key = [loc?.lat, loc?.lng, crop];

  // Each panel loads independently so one failing source never blanks the page.
  const conditions = useResource(loc ? (s) => getFarmConditions(loc.lat, loc.lng, s) : null, key);
  const alerts = useResource(loc ? (s) => getPersonalizedAlerts(loc.lat, loc.lng, crop, s) : null, key);
  const regen = useResource(loc ? (s) => getRegenerative(loc.lat, loc.lng, crop, s) : null, key);
  const health = useResource(loc ? (s) => getCropHealth(loc.lat, loc.lng, s) : null, key);
  const kvk = useResource(loc ? (s) => getNearestKvk(loc.lat, loc.lng, s) : null, key);
  const views = useAlertViews(conditions, alerts, crop);

  if (!ready) {
    return (
      <div className="mx-auto w-full max-w-5xl px-4 py-8 sm:px-6">
        <LoadingBlock lines={4} />
      </div>
    );
  }

  if (!loc || editing) {
    return (
      <div className="mx-auto w-full max-w-xl px-4 py-8 sm:px-6">
        <Card aria-labelledby="profile-title">
          <h1 id="profile-title" className="text-2xl font-semibold tracking-tight">
            {t('profile.title')}
          </h1>
          <p className="mb-6 mt-2 text-ink-soft">{t('profile.body')}</p>
          <FarmProfileForm onDone={() => setEditing(false)} onCancel={loc ? () => setEditing(false) : undefined} />
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-5xl px-4 pb-10 pt-6 sm:px-6">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">{t('farm.title')}</h1>
        <button type="button" onClick={() => setEditing(true)} className={buttonClass.ghost}>
          <MapPin className="h-4 w-4" aria-hidden />
          <span className="max-w-[14rem] truncate">{locationLabel(loc)}</span>
          <Pencil className="h-3.5 w-3.5" aria-hidden />
          <span className="sr-only">{t('action.change')}</span>
        </button>
      </div>

      <nav aria-label={t('farm.sections')} className="sticky top-16 z-30 -mx-4 mb-5 overflow-x-auto bg-paper/95 px-4 py-2 backdrop-blur sm:mx-0 sm:rounded-xl sm:px-2">
        <ul className="flex gap-2">
          {SECTIONS.map((s) => (
            <li key={s.id}>
              <a href={`#${s.id}`} className="inline-flex min-h-10 items-center whitespace-nowrap rounded-full border border-line bg-surface px-4 text-sm font-medium text-ink-soft hover:border-leaf-500 hover:text-leaf-700">
                {t(s.label)}
              </a>
            </li>
          ))}
        </ul>
      </nav>

      <div className="space-y-5">
        <TodayCard conditions={conditions} views={views} locationLabel={locationLabel(loc)} cropLabel={crop ? t(`crop.${crop}` as MessageKey) : null} />
        <AlertsCard views={views} conditions={conditions} alerts={alerts} />
        <WeatherCard conditions={conditions} />
        <SoilRegenCard regen={regen} />
        <div className="grid gap-5 lg:grid-cols-[2fr_1fr]">
          <CropHealthCard health={health} />
          <KvkCard kvk={kvk} />
        </div>
      </div>
    </div>
  );
}
