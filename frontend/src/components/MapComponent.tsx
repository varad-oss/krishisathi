"use client";

"use client";

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { getOutbreaks } from '@/lib/api';
import { OutbreakData } from '@/lib/types';
import { getSeverityColor, cn } from '@/lib/utils';
import { AlertTriangle } from 'lucide-react';

// Dynamically import Leaflet components to avoid SSR window errors
const MapContainer = dynamic(() => import('react-leaflet').then(m => m.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import('react-leaflet').then(m => m.TileLayer), { ssr: false });
const Marker = dynamic(() => import('react-leaflet').then(m => m.Marker), { ssr: false });
const Popup = dynamic(() => import('react-leaflet').then(m => m.Popup), { ssr: false });

export default function MapComponent() {
  const [outbreaks, setOutbreaks] = useState<OutbreakData[]>([]);

  useEffect(() => {
    getOutbreaks().then(setOutbreaks);
    
    // Fix Leaflet default icon paths in Next.js
    import('leaflet').then(L => {
      delete (L.Icon.Default.prototype as any)._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
        iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
      });
    });
  }, []);

  // Make sure we only render the map on the client
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  if (!mounted) return <div className="w-full h-full min-h-[500px] bg-gray-100 animate-pulse rounded-2xl" />;

  return (
    <div className="w-full h-full min-h-[500px] rounded-2xl overflow-hidden shadow-inner border border-gray-200">
      <MapContainer 
        center={[22.0, 78.0]} 
        zoom={5} 
        scrollWheelZoom={true}
        style={{ height: '100%', width: '100%', minHeight: '500px' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {outbreaks.filter(o => o.lat != null && o.lng != null).map((outbreak) => (
          <Marker key={outbreak.id} position={[outbreak.lat!, outbreak.lng!]}>
            <Popup>
              <div className="p-1 max-w-[200px]">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="h-4 w-4 text-red-500" />
                  <h3 className="font-bold text-gray-900 text-sm m-0">{outbreak.disease}</h3>
                </div>
                <div className="space-y-1 text-xs">
                  <p className="text-gray-600 font-medium m-0 mb-1">{outbreak.region}</p>
                  <div className="flex justify-between items-center pt-1 border-t border-gray-100">
                    <span className="text-gray-500">Severity:</span>
                    <span className={cn("px-1.5 py-0.5 rounded font-bold", getSeverityColor(outbreak.severity))}>
                      {outbreak.severity}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-500">Reports:</span>
                    <span className="font-medium">{outbreak.reports_count}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-500">Area (km²):</span>
                    <span className="font-medium">{outbreak.affected_area_km2 || 'Unknown'}</span>
                  </div>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
