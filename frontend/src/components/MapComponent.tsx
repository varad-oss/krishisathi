"use client";

import { useEffect, useState } from 'react';
import { APIProvider, Map, Marker, InfoWindow } from '@vis.gl/react-google-maps';
import { getOutbreaks } from '@/lib/api';
import { OutbreakData } from '@/lib/types';
import { getSeverityColor, cn } from '@/lib/utils';
import { AlertTriangle } from 'lucide-react';

export default function MapComponent() {
  const [outbreaks, setOutbreaks] = useState<OutbreakData[]>([]);
  const [selectedOutbreak, setSelectedOutbreak] = useState<OutbreakData | null>(null);

  useEffect(() => {
    getOutbreaks().then(setOutbreaks);
  }, []);

  return (
    <div className="w-full h-full min-h-[500px] rounded-2xl overflow-hidden shadow-inner border border-gray-200">
      <APIProvider apiKey={process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || "DEMO_KEY"}>
        <Map
          defaultCenter={{ lat: 22.0, lng: 78.0 }} // Center of India
          defaultZoom={5}
          disableDefaultUI={false}
          gestureHandling={'greedy'}
        >
          {outbreaks.filter(o => o.lat != null && o.lng != null).map((outbreak) => (
            <Marker
              key={outbreak.id}
              position={{ lat: outbreak.lat!, lng: outbreak.lng! }}
              onClick={() => setSelectedOutbreak(outbreak)}
            />
          ))}

          {selectedOutbreak && selectedOutbreak.lat != null && selectedOutbreak.lng != null && (
            <InfoWindow
              position={{ lat: selectedOutbreak.lat, lng: selectedOutbreak.lng }}
              onCloseClick={() => setSelectedOutbreak(null)}
            >
              <div className="p-1 max-w-[200px]">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="h-4 w-4 text-red-500" />
                  <h3 className="font-bold text-gray-900 text-sm">{selectedOutbreak.disease}</h3>
                </div>
                <div className="space-y-1 text-xs">
                  <p className="text-gray-600 font-medium">{selectedOutbreak.region}</p>
                  <div className="flex justify-between items-center pt-1 border-t border-gray-100">
                    <span className="text-gray-500">Severity:</span>
                    <span className={cn("px-1.5 py-0.5 rounded font-bold", getSeverityColor(selectedOutbreak.severity))}>
                      {selectedOutbreak.severity}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-500">Reports:</span>
                    <span className="font-medium">{selectedOutbreak.reports_count}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-500">Area (km²):</span>
                    <span className="font-medium">{selectedOutbreak.affected_area_km2 || 'Unknown'}</span>
                  </div>
                </div>
              </div>
            </InfoWindow>
          )}
        </Map>
      </APIProvider>
    </div>
  );
}
