"use client";

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Cloud, Droplets, MapPin, Satellite } from 'lucide-react';
import { getAdvisory, getWeather, getCropHealth, getPersonalizedAlerts } from '@/lib/api';
import { cn } from '@/lib/utils';
import { SUPPORTED_LANGUAGES } from '@/lib/languages';
import { useLanguage } from '@/lib/LanguageContext';
import { t } from '@/lib/translations';
import { formatNumber } from '@/lib/utils';
import { WeatherData, CropHealthData } from '@/lib/types';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const QUICK_ACTIONS = [
  "Recommend drought-resistant crops",
  "How to improve soil health?",
  "Regenerative farming tips",
  "Current pest risks"
];

export default function ChatPage() {
  const { language, setLanguage } = useLanguage();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I am KrishiSathi, your AI agriculture advisor. I have analyzed your local satellite data, soil moisture, and weather forecast. What regenerative crop recommendations or farming advice do you need today?',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Data Context State
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);
  const [ndviData, setNdviData] = useState<CropHealthData | null>(null);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [mounted, setMounted] = useState(false);
  
  // Locations for demo
  const LOCATIONS = [
    { name: "Pune, MH", lat: 18.5204, lng: 73.8567, crop: "Maize" },
    { name: "Ludhiana, PB", lat: 30.9010, lng: 75.8573, crop: "Wheat" },
    { name: "Nashik, MH", lat: 20.0110, lng: 73.7909, crop: "Tomato" },
    { name: "Belgaum, KA", lat: 15.8497, lng: 74.4977, crop: "Sorghum" }
  ];
  const [activeLocation, setActiveLocation] = useState(LOCATIONS[0]);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    // Fetch real weather and satellite context on load or location change
    setWeatherData(null);
    setNdviData(null);
    setAlerts([]);
    
    getWeather(activeLocation.lat, activeLocation.lng).then(setWeatherData);
    getCropHealth().then(data => {
      // Find matching state or use first available
      const stateMatch = activeLocation.name.includes('MH') ? 'Maharashtra' : 
                         activeLocation.name.includes('PB') ? 'Punjab' : 
                         activeLocation.name.includes('KA') ? 'Karnataka' : 'Maharashtra';
      const localData = data.find(d => d.region.includes(stateMatch)) || data[0];
      setNdviData(localData);
    });
    // Fetch hyper-local pest alerts for the region and assumed crop
    getPersonalizedAlerts(activeLocation.lat, activeLocation.lng, activeLocation.crop).then(setAlerts);
  }, [activeLocation]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (text: string) => {
    if (!text.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await getAdvisory(text, activeLocation.lat, activeLocation.lng, language);
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.advisory_text || response.answer || "Here is your advisory.",
        timestamp: new Date(response.timestamp || Date.now())
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "I'm sorry, I couldn't process your request right now. Please check your connection and try again.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 bg-gray-50 flex flex-col md:flex-row h-[calc(100vh-4rem)]">
      
      {/* Contextual Data Sidebar */}
      <div className="w-full md:w-80 bg-white border-r p-6 flex flex-col gap-6 overflow-y-auto shrink-0">
        <div>
          <div className="flex justify-between items-center mb-1">
            <h2 className="text-lg font-bold text-gray-900">{t("Local Intelligence", language)}</h2>
          </div>
          <div className="flex items-center gap-1 text-sm text-gray-500">
            <MapPin className="h-4 w-4" /> 
            <select 
              className="bg-transparent border-none outline-none cursor-pointer font-medium text-green-800 hover:text-green-600 appearance-none pr-4"
              value={activeLocation.name}
              onChange={(e) => {
                const loc = LOCATIONS.find(l => l.name === e.target.value);
                if (loc) setActiveLocation(loc);
              }}
            >
              {LOCATIONS.map(loc => (
                <option key={loc.name} value={loc.name}>{t(loc.name, language)} ({t(loc.crop, language)})</option>
              ))}
            </select>
          </div>
        </div>
        
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2 text-blue-800">
              <Cloud className="h-5 w-5" />
              <h3 className="font-semibold">{t("Weather Forecast", language)}</h3>
            </div>
            <p className="text-3xl font-light text-blue-900">{weatherData?.temp ? `${formatNumber(weatherData.temp, language)}°C` : '...'}</p>
            <p className="text-sm text-blue-700 mt-1 capitalize">{t(weatherData?.description || 'Fetching local conditions...', language)}</p>
            {weatherData?.humidity && (
              <p className="text-xs text-blue-600 mt-1">{formatNumber(weatherData.humidity, language)}% {t('humidity', language)} • {formatNumber(weatherData.wind, language)} {t('km/h wind', language)}</p>
            )}
          </div>
          
          <div className="bg-amber-50 border border-amber-100 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2 text-amber-800">
              <Droplets className="h-5 w-5" />
              <h3 className="font-semibold">{t("Soil Moisture", language)}</h3>
            </div>
            <div className="flex justify-between items-end">
              <div>
                <p className="text-sm text-amber-700">{t('Volumetric Moisture', language)}</p>
                <p className="text-2xl font-light text-amber-900">
                  {weatherData?.soil_moisture !== undefined ? (weatherData.soil_moisture * 100).toFixed(1) + '%' : weatherData?.rainfall + ' mm'}
                </p>
              </div>
              <span className={cn(
                "text-xs font-bold px-2 py-1 rounded",
                (weatherData?.soil_moisture ?? 0) > 0.20 || (weatherData?.rainfall ?? 0) > 10
                  ? "bg-green-200 text-green-800"
                  : "bg-amber-200 text-amber-800"
              )}>
                {(weatherData?.soil_moisture ?? 0) > 0.20 || (weatherData?.rainfall ?? 0) > 10 ? t('Optimal', language) : t('Needs Water', language)}
              </span>
            </div>
          </div>
          
          <div className="bg-green-50 border border-green-100 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2 text-green-800">
              <Satellite className="h-5 w-5" />
              <h3 className="font-semibold">{t("Satellite NDVI", language)}</h3>
            </div>
            <div className="flex justify-between items-end">
              <div>
                <p className="text-sm text-green-700">{t("Vegetation Index", language)}</p>
                <p className="text-2xl font-light text-green-900">{ndviData ? formatNumber(ndviData.ndvi_score, language) : '...'}</p>
              </div>
              <span className={cn(
                "text-xs font-bold px-2 py-1 rounded",
                ndviData?.health_status === 'Good' ? "bg-green-200 text-green-800" :
                ndviData?.health_status === 'Poor' ? "bg-red-200 text-red-800" :
                "bg-yellow-200 text-yellow-800"
              )}>
                {t(ndviData?.health_status || 'Scanning', language)}
              </span>
            </div>
          </div>

          {alerts && alerts.length > 0 && (
            <div className="bg-red-50 border border-red-100 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3 text-red-800">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                </svg>
                <h3 className="font-semibold text-sm">{t("Hyper-Local Threats", language)}</h3>
              </div>
              <div className="space-y-3 max-h-48 overflow-y-auto custom-scrollbar pr-1">
                {alerts.map((alert, idx) => (
                  <div key={idx} className="bg-white/60 p-2 rounded-lg text-xs border border-red-100 shadow-sm">
                    <p className="font-bold text-red-900 mb-1">{t(alert.disease, language)}</p>
                    <p className="text-red-700 leading-snug">{t('High risk of', language)} {t(alert.disease, language)} {t('detected', language)} {formatNumber(alert.distance_km, language)}{t('km away in', language)} {t(alert.location, language)}.</p>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>
        
        <div className="mt-auto pt-4 border-t">
          <p className="text-xs text-gray-500 text-center">
            {t("AI advisories are augmented with live data from Open-Meteo and Earth Engine.", language)}
          </p>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 w-full mx-auto flex flex-col bg-white shadow-sm border-x">
        
        {/* Chat Header */}
        <div className="p-4 border-b bg-white flex justify-between items-center shrink-0">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 bg-green-100 rounded-full flex items-center justify-center text-green-700">
              <Bot className="h-6 w-6" />
            </div>
            <div>
              <h2 className="font-bold text-gray-900">{t("Regenerative Advisory AI", language)}</h2>
              <p className="text-xs text-green-600 font-medium flex items-center gap-1">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                </span>
                Syncing Network Data...
              </p>
            </div>
          </div>
          <select 
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm focus:border-green-500 focus:outline-none"
          >
            {SUPPORTED_LANGUAGES.map(l => <option key={l.code} value={l.code}>{l.nativeName}</option>)}
          </select>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          {messages.map((msg) => (
            <div 
              key={msg.id} 
              className={cn("flex gap-3 max-w-[85%]", msg.role === 'user' ? "ml-auto flex-row-reverse" : "")}
            >
              <div className={cn(
                "h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0 mt-1",
                msg.role === 'user' ? "bg-gray-200 text-gray-600" : "bg-green-100 text-green-700"
              )}>
                {msg.role === 'user' ? <User className="h-5 w-5" /> : <Bot className="h-5 w-5" />}
              </div>
              <div className={cn(
                "rounded-2xl px-5 py-3 shadow-sm",
                msg.role === 'user' 
                  ? "bg-green-700 text-white rounded-tr-sm" 
                  : "bg-gray-100 text-gray-800 rounded-tl-sm border border-gray-200"
              )}>
                {msg.role === 'user' ? (
                  <p className="text-sm md:text-base leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                ) : (
                  <div className="prose prose-sm md:prose-base prose-green max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {t(msg.content, language)}
                    </ReactMarkdown>
                  </div>
                )}
                <p className={cn(
                  "text-[10px] mt-2 text-right",
                  msg.role === 'user' ? "text-green-200" : "text-gray-400"
                )}>
                  {mounted ? msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                </p>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex gap-3 max-w-[80%]">
              <div className="h-8 w-8 rounded-full bg-green-100 text-green-700 flex items-center justify-center flex-shrink-0 mt-1">
                <Bot className="h-5 w-5" />
              </div>
              <div className="rounded-2xl rounded-tl-sm bg-gray-100 px-5 py-4 border border-gray-200 flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin text-green-600" />
                <span className="text-sm text-gray-500">{t("Synthesizing local data...", language)}</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-white border-t shrink-0">
          {/* Quick Actions */}
          <div className="flex overflow-x-auto pb-3 gap-2 hide-scrollbar">
            {QUICK_ACTIONS.map((action, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(t(action, language))}
                className="whitespace-nowrap text-xs font-medium bg-green-50 text-green-700 px-3 py-1.5 rounded-full border border-green-200 hover:bg-green-100 transition-colors"
              >
                {t(action, language)}
              </button>
            ))}
          </div>
          
          <form 
            onSubmit={(e) => { e.preventDefault(); handleSend(input); }}
            className="flex items-end gap-2"
          >
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={t("Ask for a regenerative crop recommendation...", language)}
              className="flex-1 max-h-32 min-h-[44px] rounded-xl border border-gray-300 bg-gray-50 px-4 py-3 text-sm focus:border-green-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-green-500 resize-none"
              rows={1}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend(input);
                }
              }}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="h-[44px] w-[44px] flex-shrink-0 flex items-center justify-center rounded-xl bg-green-700 text-white transition-colors hover:bg-green-800 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              <Send className="h-5 w-5" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
