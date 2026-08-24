'use client';

import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { OutbreakData } from '@/lib/types';
import L from 'leaflet';

// Fix for default marker icons in Leaflet with Next.js
const icon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

export default function MapComponent({ outbreaks }: { outbreaks: any[] }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return <div className="h-full w-full bg-blue-50/50 flex items-center justify-center">Loading map...</div>;

  return (
    <MapContainer 
      center={[20.5937, 78.9629]} 
      zoom={4} 
      className="h-full w-full z-0"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      
      {outbreaks.map((outbreak, idx) => {
        // Simple color mapping based on severity
        const color = outbreak.severity.toLowerCase() === 'critical' ? '#ef4444' : 
                      outbreak.severity.toLowerCase() === 'high' || outbreak.severity.toLowerCase() === 'severe' ? '#f97316' : 
                      outbreak.severity.toLowerCase() === 'moderate' ? '#eab308' : '#22c55e';
                      
        return (
          <Circle
            key={idx}
            center={[outbreak.lat, outbreak.lng]}
            pathOptions={{ color, fillColor: color, fillOpacity: 0.4 }}
            radius={outbreak.affected_area_km2 * 100} // rough approximation for visual scale
          >
            <Popup>
              <div className="p-1">
                <h3 className="font-bold text-gray-900">{outbreak.disease}</h3>
                <p className="text-sm text-gray-600">{outbreak.region}</p>
                <div className="mt-2 text-xs">
                  <span className="font-semibold">Severity:</span> {outbreak.severity}<br/>
                  <span className="font-semibold">Reports:</span> {outbreak.reports_count}<br/>
                  <span className="font-semibold">Affected Area:</span> {outbreak.affected_area_km2} km²
                </div>
              </div>
            </Popup>
          </Circle>
        );
      })}
    </MapContainer>
  );
}
