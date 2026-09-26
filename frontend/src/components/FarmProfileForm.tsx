'use client';

import { useId, useState } from 'react';
import { Crosshair, MapPin, Sprout } from 'lucide-react';
import { CROPS, PLACES, type Crop, type PlaceId } from '@/lib/catalog';
import { useFarmProfile, type FarmLocation } from '@/lib/farm-profile';
import { useI18n } from '@/lib/i18n';
import type { MessageKey } from '@/locales/en';
import { cn } from '@/lib/utils';
import { buttonClass, inputClass, Note } from './ui';

export function useLocationLabel() {
  const { t, fmt } = useI18n();
  return (loc: FarmLocation | null) => {
    if (!loc) return '';
    if (loc.source === 'place' && loc.placeId) return t(`place.${loc.placeId}` as MessageKey);
    return `${t('profile.deviceLocation')} (${t('profile.coordinates', { lat: fmt.num(loc.lat, 2), lng: fmt.num(loc.lng, 2) })})`;
  };
}

export default function FarmProfileForm({ onDone, onCancel }: { onDone?: () => void; onCancel?: () => void }) {
  const { t } = useI18n();
  const { profile, setProfile } = useFarmProfile();
  const locationLabel = useLocationLabel();
  const [location, setLocation] = useState<FarmLocation | null>(profile.location);
  const [crop, setCrop] = useState<Crop | null>(profile.crop);
  const [geoState, setGeoState] = useState<'idle' | 'locating' | 'denied' | 'failed'>('idle');
  const placeId = useId();
  const cropId = useId();

  const useDevice = () => {
    if (!('geolocation' in navigator)) {
      setGeoState('failed');
      return;
    }
    setGeoState('locating');
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLocation({ lat: +pos.coords.latitude.toFixed(4), lng: +pos.coords.longitude.toFixed(4), source: 'device' });
        setGeoState('idle');
      },
      // Never substitute a default location: the farmer chooses a district instead.
      (err) => setGeoState(err.code === err.PERMISSION_DENIED ? 'denied' : 'failed'),
      { enableHighAccuracy: false, timeout: 15_000, maximumAge: 600_000 },
    );
  };

  const choosePlace = (id: string) => {
    const place = PLACES.find((p) => p.id === id);
    setLocation(place ? { lat: place.lat, lng: place.lng, source: 'place', placeId: place.id as PlaceId } : null);
  };

  return (
    <form
      className="space-y-5"
      onSubmit={(e) => {
        e.preventDefault();
        if (!location) return;
        setProfile({ location, crop });
        onDone?.();
      }}
    >
      <fieldset className="space-y-3">
        <legend className="flex items-center gap-2 text-sm font-semibold text-ink">
          <MapPin className="h-4 w-4 text-leaf-600" aria-hidden /> {t('profile.location')}
        </legend>
        <button type="button" onClick={useDevice} disabled={geoState === 'locating'} className={cn(buttonClass.secondary, 'w-full sm:w-auto')}>
          <Crosshair className={cn('h-4 w-4', geoState === 'locating' && 'animate-spin')} aria-hidden />
          {geoState === 'locating' ? t('profile.locating') : t('action.useMyLocation')}
        </button>
        {(geoState === 'denied' || geoState === 'failed') && (
          <Note tone="watch">{t(geoState === 'denied' ? 'profile.locationDenied' : 'profile.locationFailed')}</Note>
        )}
        <div>
          <label htmlFor={placeId} className="mb-1 block text-sm text-ink-soft">
            {t('profile.choosePlace')}
          </label>
          <select id={placeId} className={inputClass} value={location?.source === 'place' ? location.placeId : ''} onChange={(e) => choosePlace(e.target.value)}>
            <option value="">—</option>
            {PLACES.map((p) => (
              <option key={p.id} value={p.id}>
                {t(`place.${p.id}` as MessageKey)}
              </option>
            ))}
          </select>
        </div>
        {location && (
          <p className="rounded-lg bg-leaf-50 px-3 py-2 text-sm font-medium text-leaf-700" aria-live="polite">
            {locationLabel(location)}
          </p>
        )}
        <p className="text-xs text-ink-faint">{t('profile.privacy')}</p>
      </fieldset>

      <div>
        <label htmlFor={cropId} className="mb-1 flex items-center gap-2 text-sm font-semibold text-ink">
          <Sprout className="h-4 w-4 text-leaf-600" aria-hidden /> {t('profile.crop')}
        </label>
        <select id={cropId} className={inputClass} value={crop ?? ''} onChange={(e) => setCrop((e.target.value || null) as Crop | null)}>
          <option value="">{t('profile.cropNone')}</option>
          {CROPS.map((c) => (
            <option key={c} value={c}>
              {t(`crop.${c}` as MessageKey)}
            </option>
          ))}
        </select>
      </div>

      <div className="flex flex-wrap gap-3">
        <button type="submit" disabled={!location} className={buttonClass.primary}>
          {t('action.save')}
        </button>
        {onCancel && (
          <button type="button" onClick={onCancel} className={buttonClass.secondary}>
            {t('action.cancel')}
          </button>
        )}
      </div>
    </form>
  );
}
