'use client';

import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { CROPS, PLACES, type Crop, type PlaceId } from './catalog';

export interface FarmLocation {
  lat: number;
  lng: number;
  source: 'device' | 'place';
  placeId?: PlaceId;
}

export interface FarmProfile {
  location: FarmLocation | null;
  crop: Crop | null;
}

const STORAGE_KEY = 'krishi_farm_profile';
const EMPTY: FarmProfile = { location: null, crop: null };

function parse(raw: string | null): FarmProfile {
  if (!raw) return EMPTY;
  try {
    const p = JSON.parse(raw);
    const loc = p?.location;
    const validLoc =
      loc && typeof loc.lat === 'number' && typeof loc.lng === 'number' && Math.abs(loc.lat) <= 90 && Math.abs(loc.lng) <= 180
        ? { lat: loc.lat, lng: loc.lng, source: loc.source === 'device' ? 'device' : 'place', placeId: PLACES.find((x) => x.id === loc.placeId)?.id }
        : null;
    return { location: validLoc as FarmLocation | null, crop: CROPS.includes(p?.crop) ? p.crop : null };
  } catch {
    return EMPTY;
  }
}

interface FarmProfileValue {
  profile: FarmProfile;
  ready: boolean;
  setProfile: (p: FarmProfile) => void;
}

const Ctx = createContext<FarmProfileValue | null>(null);

export function FarmProfileProvider({ children }: { children: React.ReactNode }) {
  const [profile, setState] = useState<FarmProfile>(EMPTY);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let raw: string | null = null;
    try {
      raw = localStorage.getItem(STORAGE_KEY);
    } catch {
      /* storage unavailable */
    }
    // Hydrate from device storage after mount (server render has no access to it).
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setState(parse(raw));
    setReady(true);
  }, []);

  const setProfile = useCallback((p: FarmProfile) => {
    setState(p);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(p));
    } catch {
      /* ignore */
    }
  }, []);

  return <Ctx.Provider value={{ profile, ready, setProfile }}>{children}</Ctx.Provider>;
}

export function useFarmProfile(): FarmProfileValue {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error('useFarmProfile must be used inside FarmProfileProvider');
  return ctx;
}
