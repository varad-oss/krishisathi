'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { getCropHealth, getAlerts, getOutbreaks } from '@/lib/api';
import { CropHealthData, Alert, OutbreakData } from '@/lib/types';
import { MapPin, AlertTriangle, CloudRain, ThermometerSun } from 'lucide-react';
import { cn, getSeverityColor } from '@/lib/utils';

// Dynamically import the map component so it only loads on the client side
const MapComponent = dynamic(() => import('@/components/MapComponent'), { 
  ssr: false,
  loading: () => <div className="h-full w-full bg-blue-50/50 flex items-center justify-center">Loading interactive map...</div>
});

import { useLanguage } from "@/lib/LanguageContext";
import { t } from "@/lib/translations";

export default function MapPage() {
  const { language } = useLanguage();
  const [healthData, setHealthData] = useState<CropHealthData[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [outbreaks, setOutbreaks] = useState<OutbreakData[]>([]);

  useEffect(() => {
    async function loadData() {
      const [hData, aData, oData] = await Promise.all([
        getCropHealth(),
        getAlerts(),
        getOutbreaks()
      ]);
      setHealthData(hData);
      setAlerts(aData);
      setOutbreaks(oData);
    }
    loadData();
  }, []);

  return (
    <div className="flex-1 bg-gray-50 flex flex-col md:flex-row h-[calc(100vh-64px)] overflow-hidden">
      {/* Main Map Area */}
      <div className="flex-1 relative border-r z-0">
        <MapComponent />
        
        <div className="absolute top-4 left-14 z-[400] bg-white/90 backdrop-blur-sm p-4 rounded-xl shadow-md border border-gray-200 pointer-events-auto">
          <h2 className="font-bold text-gray-900 flex items-center gap-2">
            <MapPin className="h-5 w-5 text-green-600" />{t('Disease Outbreaks', language)}</h2>
          <p className="text-xs text-gray-500 mt-1">{t("Live tracking across Indian states", language)}</p>
          
          <div className="mt-4 space-y-2">
            <p className="text-xs font-semibold text-gray-700 uppercase tracking-wider">{t("Severity Legend", language)}</p>
            <div className="flex items-center gap-2 text-xs">
              <div className="h-3 w-3 rounded-full bg-red-500 opacity-60 border border-red-500"></div>{t('Critical', language)}</div>
            <div className="flex items-center gap-2 text-xs">
              <div className="h-3 w-3 rounded-full bg-orange-500 opacity-60 border border-orange-500"></div>{t('Severe / High', language)}</div>
            <div className="flex items-center gap-2 text-xs">
              <div className="h-3 w-3 rounded-full bg-yellow-500 opacity-60 border border-yellow-500"></div>{t('Moderate', language)}</div>
          </div>
        </div>
      </div>

      {/* Sidebar Data Area */}
      <div className="w-full md:w-96 bg-white overflow-y-auto h-full z-10">
        <div className="p-6 space-y-8">
          
          {/* Active Alerts */}
          <div>
            <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />{t('Active Regional Alerts', language)}</h3>
            <div className="space-y-3">
              {alerts.map(alert => (
                <div key={alert.id} className={cn("p-4 rounded-xl border", getSeverityColor(alert.severity))}>
                  <div className="flex justify-between items-start mb-1">
                    <h4 className="font-bold">{t(alert.title, language)}</h4>
                    <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-white/50">{t(alert.severity, language)}</span>
                  </div>
                  <p className="text-sm opacity-90">{t(alert.message, language)}</p>
                  <p className="text-xs mt-2 opacity-75 font-medium">{alert.date}</p>
                </div>
              ))}
              {alerts.length === 0 && (
                <p className="text-sm text-gray-500">{t('No active alerts.', language)}</p>
              )}
            </div>
          </div>

          {/* Regional Health Data */}
          <div>
            <h3 className="text-lg font-bold text-gray-900 mb-4">{t("Regional NDVI Data", language)}</h3>
            <div className="space-y-4">
              {healthData.map((data, idx) => (
                <div key={idx} className="p-4 bg-gray-50 rounded-xl border border-gray-100">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-bold text-gray-800">{data.region}</span>
                    <span className={cn(
                      "text-xs font-bold px-2 py-1 rounded-full",
                      data.health_status === 'Excellent' || data.health_status === 'Good' ? "bg-green-100 text-green-700" :
                      data.health_status === 'Fair' ? "bg-yellow-100 text-yellow-700" : "bg-red-100 text-red-700"
                    )}>
                      {data.health_status}
                    </span>
                  </div>
                  
                  {/* Progress bar for NDVI */}
                  <div className="mb-3">
                    <div className="flex justify-between text-xs text-gray-500 mb-1">
                      <span>{t('NDVI Score', language)}</span>
                      <span>{data.ndvi_score.toFixed(2)}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={cn("h-2 rounded-full", data.ndvi_score > 0.6 ? "bg-green-500" : data.ndvi_score > 0.4 ? "bg-yellow-500" : "bg-red-500")}
                        style={{ width: `${Math.min(100, Math.max(0, data.ndvi_score * 100))}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-sm mt-3 pt-3 border-t">
                    <div className="flex items-center gap-1.5 text-gray-600">
                      <CloudRain className="h-4 w-4 text-blue-500" />
                      Risk: {data.drought_risk}
                    </div>
                    <div className="flex items-center gap-1.5 text-gray-600">
                      <ThermometerSun className="h-4 w-4 text-orange-500" />
                      {data.primary_crop}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
