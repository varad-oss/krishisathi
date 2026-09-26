'use client';

import 'leaflet/dist/leaflet.css';
import { Circle, CircleMarker, MapContainer, TileLayer, Tooltip } from 'react-leaflet';
import type { Outbreak } from '@/lib/types';

const COLORS: Record<string, string> = { high: '#a3261b', moderate: '#8a5a0c', low: '#2f6b3f' };

/** Approximate cluster centres (rounded to ~11 km) with the clustering radius. Loaded only on the client. */
export default function OutbreakMap({ outbreaks, label }: { outbreaks: Outbreak[]; label: string }) {
  return (
    <div role="img" aria-label={label} className="h-80 overflow-hidden rounded-xl ring-1 ring-line sm:h-96">
      <MapContainer center={[22.5, 79]} zoom={4} scrollWheelZoom={false} style={{ height: '100%', width: '100%' }}>
        <TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {outbreaks.map((o) => (
          <Circle key={`r-${o.id}`} center={[o.lat, o.lng]} radius={o.radius_km * 1000} pathOptions={{ color: COLORS[o.severity], weight: 1, fillOpacity: 0.08 }} />
        ))}
        {outbreaks.map((o) => (
          <CircleMarker key={o.id} center={[o.lat, o.lng]} radius={7} pathOptions={{ color: '#fff', weight: 2, fillColor: COLORS[o.severity], fillOpacity: 1 }}>
            <Tooltip>
              {o.disease} · {o.report_count}
            </Tooltip>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
}
