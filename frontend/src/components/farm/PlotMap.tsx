'use client';

import 'leaflet/dist/leaflet.css';
import { CircleMarker, MapContainer, Polygon, Polyline, TileLayer, useMapEvents } from 'react-leaflet';
import type { Position } from '@/lib/geo';

// Aerial imagery makes field edges visible; a street map does not show them.
const IMAGERY = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';
const IMAGERY_ATTRIBUTION = 'Imagery &copy; Esri, Maxar, Earthstar Geographics, and the GIS User Community';

function Taps({ onAdd }: { onAdd: (p: Position) => void }) {
  useMapEvents({ click: (e) => onAdd([e.latlng.lng, e.latlng.lat]) });
  return null;
}

/** Tap the corners of the field. Loaded only in the browser. */
export default function PlotMap({ center, points, onAdd, label }: { center: { lat: number; lng: number }; points: Position[]; onAdd: (p: Position) => void; label: string }) {
  const latLngs = points.map(([lng, lat]) => [lat, lng] as [number, number]);
  return (
    <div role="application" aria-label={label} className="h-72 overflow-hidden rounded-[var(--radius-inner)] ring-1 ring-line sm:h-96" data-testid="plot-map">
      <MapContainer center={[center.lat, center.lng]} zoom={17} maxZoom={19} scrollWheelZoom={false} style={{ height: '100%', width: '100%', cursor: 'crosshair' }}>
        <TileLayer attribution={IMAGERY_ATTRIBUTION} url={IMAGERY} maxZoom={19} />
        <CircleMarker center={[center.lat, center.lng]} radius={5} pathOptions={{ color: '#fff', weight: 2, fillColor: '#b45309', fillOpacity: 1 }} />
        {latLngs.length >= 3 ? (
          <Polygon positions={latLngs} pathOptions={{ color: '#facc15', weight: 3, fillOpacity: 0.15 }} />
        ) : latLngs.length === 2 ? (
          <Polyline positions={latLngs} pathOptions={{ color: '#facc15', weight: 3 }} />
        ) : null}
        {latLngs.map((p, i) => (
          <CircleMarker key={`${p[0]},${p[1]},${i}`} center={p} radius={6} pathOptions={{ color: '#111', weight: 2, fillColor: '#facc15', fillOpacity: 1 }} />
        ))}
        <Taps onAdd={onAdd} />
      </MapContainer>
    </div>
  );
}
