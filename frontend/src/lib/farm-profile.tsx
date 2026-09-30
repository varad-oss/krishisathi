'use client';

import { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react';
import { createFarm, updateFarm } from './api';
import { CROPS, PLACES, type Crop, type PlaceId } from './catalog';
import type { FarmTwin } from './types';

export interface FarmLocation {
  lat: number;
  lng: number;
  source: 'device' | 'place';
  placeId?: PlaceId;
}

export interface FarmProfile {
  location: FarmLocation | null;
  crop: Crop | null;
  /** ISO date (YYYY-MM-DD) the crop was sown; optional, enables crop-stage estimates. */
  sowingDate: string | null;
}

const STORAGE_KEY = 'krishi_farm_profile';
const TWIN_KEY = 'krishi_farm_twin';
const EMPTY: FarmProfile = { location: null, crop: null, sowingDate: null };

export const isIsoDate = (v: unknown): v is string => typeof v === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(v) && !Number.isNaN(Date.parse(v));

function parse(raw: string | null): FarmProfile {
  if (!raw) return EMPTY;
  try {
    const p = JSON.parse(raw);
    const loc = p?.location;
    const validLoc =
      loc && typeof loc.lat === 'number' && typeof loc.lng === 'number' && Math.abs(loc.lat) <= 90 && Math.abs(loc.lng) <= 180
        ? { lat: loc.lat, lng: loc.lng, source: loc.source === 'device' ? 'device' : 'place', placeId: PLACES.find((x) => x.id === loc.placeId)?.id }
        : null;
    return { location: validLoc as FarmLocation | null, crop: CROPS.includes(p?.crop) ? p.crop : null, sowingDate: isIsoDate(p?.sowingDate) ? p.sowingDate : null };
  } catch {
    return EMPTY;
  }
}

function parseTwin(raw: string | null): FarmTwin | null {
  try {
    const t = raw ? JSON.parse(raw) : null;
    return t && typeof t.farmId === 'string' && typeof t.token === 'string' ? { farmId: t.farmId, token: t.token } : null;
  } catch {
    return null;
  }
}

function store(key: string, value: unknown) {
  try {
    if (value === null) localStorage.removeItem(key);
    else localStorage.setItem(key, JSON.stringify(value));
  } catch {
    /* storage unavailable */
  }
}

interface FarmProfileValue {
  profile: FarmProfile;
  ready: boolean;
  setProfile: (p: FarmProfile) => void;
  /** Server-side farm record (digital twin); null until registered, or when registration failed/offline. */
  twin: FarmTwin | null;
  /** Increments after the server record has been saved, so views reload it. */
  twinRevision: number;
  forgetTwin: () => void;
}

const toInput = (p: FarmProfile) => ({ lat: p.location!.lat, lng: p.location!.lng, crop: p.crop, sowing_date: p.sowingDate });

const Ctx = createContext<FarmProfileValue | null>(null);

export function FarmProfileProvider({ children }: { children: React.ReactNode }) {
  const [profile, setState] = useState<FarmProfile>(EMPTY);
  const [twin, setTwin] = useState<FarmTwin | null>(null);
  const [twinRevision, setTwinRevision] = useState(0);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let raw: string | null = null;
    let rawTwin: string | null = null;
    try {
      raw = localStorage.getItem(STORAGE_KEY);
      rawTwin = localStorage.getItem(TWIN_KEY);
    } catch {
      /* storage unavailable */
    }
    // Hydrate from device storage after mount (server render has no access to it).
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setState(parse(raw));
    setTwin(parseTwin(rawTwin));
    setReady(true);
  }, []);

  const registering = useRef(false);
  const register = useCallback((p: FarmProfile) => {
    if (!p.location || registering.current) return;
    registering.current = true;
    createFarm(toInput(p))
      .then((r) => {
        const t = { farmId: r.farm_id, token: r.farm_token };
        setTwin(t);
        store(TWIN_KEY, t);
      })
      .catch(() => {
        /* offline or server unavailable: retried on the next visit */
      })
      .finally(() => (registering.current = false));
  }, []);

  // Profiles saved before farm records existed (or whose record was lost) are registered once per visit.
  const attempted = useRef(false);
  useEffect(() => {
    if (!ready || twin || !profile.location || attempted.current) return;
    attempted.current = true;
    register(profile);
  }, [ready, twin, profile, register]);

  const forgetTwin = useCallback(() => {
    attempted.current = false;
    setTwin(null);
    store(TWIN_KEY, null);
  }, []);

  const setProfile = useCallback(
    (p: FarmProfile) => {
      setState(p);
      store(STORAGE_KEY, p);
      if (!p.location) return;
      // The farm record is best-effort: without it the farm page still works, only history and feedback wait.
      if (!twin) return register(p);
      updateFarm(twin, toInput(p)).then(() => setTwinRevision((r) => r + 1)).catch((e) => {
        if (e?.code === 'NOT_FOUND') {
          forgetTwin();
          register(p);
        }
      });
    },
    [twin, register, forgetTwin],
  );

  return <Ctx.Provider value={{ profile, ready, setProfile, twin, twinRevision, forgetTwin }}>{children}</Ctx.Provider>;
}

export function useFarmProfile(): FarmProfileValue {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error('useFarmProfile must be used inside FarmProfileProvider');
  return ctx;
}
