"use client";

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Cloud, Droplets, MapPin, Satellite } from 'lucide-react';
import { getAdvisory, getWeather, getCropHealth } from '@/lib/api';
import { cn } from '@/lib/utils';
import { SUPPORTED_LANGUAGES } from '@/lib/languages';
import { useLanguage } from '@/lib/LanguageContext';
import { WeatherData, CropHealthData } from '@/lib/types';

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
  
  // Default coordinates (Pune, Maharashtra)
  const defaultLat = 18.5204;
  const defaultLng = 73.8567;

  useEffect(() => {
    // Fetch real weather and satellite context on load
    getWeather(defaultLat, defaultLng).then(setWeatherData);
    getCropHealth().then(data => {
      // Find Maharashtra or use first available
      const localData = data.find(d => d.region.includes('Maharashtra')) || data[0];
      setNdviData(localData);
    });
  }, []);

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
      const response = await getAdvisory(text, defaultLat, defaultLng, language);
      
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
          <h2 className="text-lg font-bold text-gray-900 mb-1">Local Intelligence</h2>
          <p className="text-sm text-gray-500 flex items-center gap-1">
            <MapPin className="h-4 w-4" /> Selected Region: {weatherData?.location || "Pune, India"}
          </p>
        </div>
        
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2 text-blue-800">
              <Cloud className="h-5 w-5" />
              <h3 className="font-semibold">Weather Forecast</h3>
            </div>
            <p className="text-3xl font-light text-blue-900">{weatherData?.temp ? `${weatherData.temp}°C` : '...'}</p>
            <p className="text-sm text-blue-700 mt-1 capitalize">{weatherData?.description || 'Fetching local conditions...'}</p>
            {weatherData?.humidity && (
              <p className="text-xs text-blue-600 mt-1">{weatherData.humidity}% humidity • {weatherData.wind} km/h wind</p>
            )}
          </div>
          
          <div className="bg-amber-50 border border-amber-100 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2 text-amber-800">
              <Droplets className="h-5 w-5" />
              <h3 className="font-semibold">Soil Moisture</h3>
            </div>
            <div className="flex justify-between items-end">
              <div>
                <p className="text-sm text-amber-700">Recent Rainfall</p>
                <p className="text-2xl font-light text-amber-900">{weatherData?.rainfall ?? '...'} mm</p>
              </div>
              <span className="text-xs font-bold bg-amber-200 text-amber-800 px-2 py-1 rounded">
                {weatherData && weatherData.rainfall > 10 ? 'Optimal' : 'Needs Water'}
              </span>
            </div>
          </div>
          
          <div className="bg-green-50 border border-green-100 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2 text-green-800">
              <Satellite className="h-5 w-5" />
              <h3 className="font-semibold">Satellite NDVI</h3>
            </div>
            <div className="flex justify-between items-end">
              <div>
                <p className="text-sm text-green-700">Vegetation Index</p>
                <p className="text-2xl font-light text-green-900">{ndviData?.ndvi_score || '...'}</p>
              </div>
              <span className={cn(
                "text-xs font-bold px-2 py-1 rounded",
                ndviData?.health_status === 'Good' ? "bg-green-200 text-green-800" :
                ndviData?.health_status === 'Poor' ? "bg-red-200 text-red-800" :
                "bg-yellow-200 text-yellow-800"
              )}>
                {ndviData?.health_status || 'Scanning'}
              </span>
            </div>
          </div>
        </div>
        
        <div className="mt-auto pt-4 border-t">
          <p className="text-xs text-gray-500 text-center">
            AI advisories are augmented with live data from Open-Meteo and Earth Engine.
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
              <h2 className="font-bold text-gray-900">Regenerative Advisory AI</h2>
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
                <p className="text-sm md:text-base leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                <p className={cn(
                  "text-[10px] mt-2 text-right",
                  msg.role === 'user' ? "text-green-200" : "text-gray-400"
                )}>
                  {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
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
                <span className="text-sm text-gray-500">Synthesizing local data...</span>
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
                onClick={() => handleSend(action)}
                className="whitespace-nowrap text-xs font-medium bg-green-50 text-green-700 px-3 py-1.5 rounded-full border border-green-200 hover:bg-green-100 transition-colors"
              >
                {action}
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
              placeholder="Ask for a regenerative crop recommendation..."
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
