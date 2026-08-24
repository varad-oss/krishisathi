'use client';

import { useState, useRef, useEffect } from 'react';
import { Camera, Upload, MapPin, AlertTriangle, ShieldCheck, Activity, Share2, Info } from 'lucide-react';
import { cn, getSeverityColor, getConfidenceLabel } from '@/lib/utils';
import { diagnoseCrop } from '@/lib/api';
import { DiagnosisResponse } from '@/lib/types';
import { SUPPORTED_LANGUAGES } from '@/lib/languages';
import { useLanguage } from '@/lib/LanguageContext';

const CROP_TYPES = ['Wheat', 'Rice', 'Tomato', 'Potato', 'Corn', 'Soybean', 'Cotton', 'Sugarcane', 'Other'];

export default function DiagnosePage() {
  const { language, setLanguage } = useLanguage();
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [cropType, setCropType] = useState<string>('Other');
  const [location, setLocation] = useState<{lat: number, lng: number} | null>(null);
  
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<DiagnosisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setPreviewUrl(URL.createObjectURL(selectedFile));
      setResult(null); // Reset previous results
      setError(null);
    }
  };

  const getLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude
          });
        },
        (err) => {
          console.warn("Geolocation denied or failed", err);
          // Fallback to demo location (New Delhi)
          setLocation({ lat: 28.6139, lng: 77.2090 });
        }
      );
    } else {
      setLocation({ lat: 28.6139, lng: 77.2090 });
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;

    setIsAnalyzing(true);
    setError(null);

    // Get location if we don't have it yet
    if (!location) {
      getLocation();
    }

    try {
      const diagnosis = await diagnoseCrop(
        file, 
        cropType, 
        location?.lat || 28.6139, 
        location?.lng || 77.2090, 
        language
      );
      setResult(diagnosis);
    } catch (err) {
      setError("Analysis failed. Please try again or check your connection.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleShare = () => {
    if (!result) return;
    const text = `KrishiSathi Alert 🌾\nDisease: ${result.disease_name}\nSeverity: ${result.severity}\nQuick Tip: ${result.treatment_plan.immediate_actions[0]}\nMore info at: krishisathi.app`;
    window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`, '_blank');
  };

  return (
    <div className="flex-1 bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">Crop Disease Diagnosis</h1>
          <p className="mt-2 text-gray-600">Upload a photo of your crop to instantly identify diseases and get AI-powered treatment plans.</p>
        </div>

        {/* Upload & Settings Section */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-6 sm:p-8 space-y-6">
            
            {/* Image Upload Area */}
            <div 
              className={cn(
                "relative border-2 border-dashed rounded-xl flex flex-col items-center justify-center p-8 transition-colors",
                previewUrl ? "border-green-500 bg-green-50" : "border-gray-300 hover:border-green-400 bg-gray-50",
                "h-64 sm:h-80"
              )}
            >
              {previewUrl ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={previewUrl} alt="Crop preview" className="absolute inset-0 w-full h-full object-contain p-2" />
              ) : (
                <div className="text-center space-y-4">
                  <div className="mx-auto h-16 w-16 bg-white rounded-full flex items-center justify-center shadow-sm">
                    <Upload className="h-8 w-8 text-gray-400" />
                  </div>
                  <div>
                    <p className="text-lg font-semibold text-gray-700">Click to upload or drag & drop</p>
                    <p className="text-sm text-gray-500">SVG, PNG, JPG or GIF (max. 10MB)</p>
                  </div>
                </div>
              )}
              <input 
                type="file" 
                ref={fileInputRef}
                onChange={handleFileChange}
                accept="image/*"
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" 
              />
              
              {/* Mobile Camera Button overlay */}
              <button 
                onClick={() => fileInputRef.current?.click()}
                className="absolute bottom-4 right-4 sm:hidden bg-green-600 text-white p-4 rounded-full shadow-lg"
              >
                <Camera className="h-6 w-6" />
              </button>
            </div>

            {/* Controls */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Crop Type (Optional)</label>
                <select 
                  value={cropType}
                  onChange={(e) => setCropType(e.target.value)}
                  className="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
                >
                  {CROP_TYPES.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Response Language</label>
                <select 
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
                >
                  {SUPPORTED_LANGUAGES.map(l => <option key={l.code} value={l.code}>{l.nativeName} ({l.name})</option>)}
                </select>
              </div>
            </div>

            {/* Action Button */}
            <button
              onClick={handleAnalyze}
              disabled={!file || isAnalyzing}
              className={cn(
                "w-full py-4 rounded-xl font-bold text-lg flex items-center justify-center gap-2 transition-all",
                !file ? "bg-gray-200 text-gray-400 cursor-not-allowed" : 
                isAnalyzing ? "bg-green-100 text-green-700" : "bg-green-700 text-white hover:bg-green-800 shadow-lg shadow-green-700/20"
              )}
            >
              {isAnalyzing ? (
                <>
                  <div className="h-5 w-5 animate-spin rounded-full border-2 border-green-700 border-t-transparent"></div>
                  AI is analyzing your crop...
                </>
              ) : (
                <>
                  <Activity className="h-5 w-5" />
                  Analyze Photo
                </>
              )}
            </button>

            {error && (
              <div className="p-4 rounded-lg bg-red-50 text-red-700 flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 mt-0.5" />
                <p>{error}</p>
              </div>
            )}
          </div>
        </div>

        {/* Results Section */}
        {result && (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden animate-fade-in-delayed">
            {/* Result Header */}
            <div className="border-b bg-gray-50 p-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{result.disease_name}</h2>
                {result.scientific_name && (
                  <p className="text-sm italic text-gray-500">{result.scientific_name}</p>
                )}
              </div>
              <div className="flex items-center gap-3">
                <span className={cn("px-3 py-1 rounded-full text-sm font-semibold border", getSeverityColor(result.severity))}>
                  {result.severity} Severity
                </span>
                <span className={cn(
                  "px-3 py-1 rounded-full text-sm font-semibold border", 
                  result.confidence < 75 ? "bg-red-50 text-red-700 border-red-200" : "bg-blue-50 text-blue-700 border-blue-200"
                )}>
                  {getConfidenceLabel(result.confidence)} Confidence ({result.confidence.toFixed(1)}%)
                </span>
              </div>
            </div>

            {/* Low Confidence Fallback UI */}
            {result.confidence < 75 && (
              <div className="mx-6 mt-6 p-4 bg-orange-50 border border-orange-200 rounded-xl flex items-start gap-3">
                <AlertTriangle className="h-6 w-6 text-orange-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-bold text-orange-900">Low Confidence Warning</h4>
                  <p className="text-orange-800 text-sm mt-1">
                    Our AI model is not highly confident about this diagnosis. The image might be blurry, or the symptoms could match multiple diseases. 
                    <strong> Please consult a human expert before applying any chemical treatments.</strong>
                  </p>
                  <button className="mt-3 px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white text-sm font-semibold rounded-lg shadow-sm transition-colors">
                    Find Nearest Krishi Vigyan Kendra (KVK)
                  </button>
                </div>
              </div>
            )}

            {/* Treatment Plan */}
            <div className="p-6 space-y-6">
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Immediate Actions */}
                <div className="space-y-3 bg-red-50/50 p-4 rounded-xl border border-red-100">
                  <h3 className="font-bold flex items-center gap-2 text-red-900">
                    <AlertTriangle className="h-5 w-5" /> Immediate Actions
                  </h3>
                  <ul className="space-y-2 list-disc list-inside text-gray-700">
                    {result.treatment_plan.immediate_actions.map((action, i) => (
                      <li key={i}>{action}</li>
                    ))}
                  </ul>
                </div>

                {/* Organic Treatment */}
                <div className="space-y-3 bg-green-50/50 p-4 rounded-xl border border-green-100">
                  <h3 className="font-bold flex items-center gap-2 text-green-900">
                    <ShieldCheck className="h-5 w-5" /> Organic Treatment
                  </h3>
                  <ul className="space-y-2 list-disc list-inside text-gray-700">
                    {result.treatment_plan.organic_treatment.map((action, i) => (
                      <li key={i}>{action}</li>
                    ))}
                  </ul>
                </div>

                {/* Chemical Treatment */}
                <div className="space-y-3 bg-blue-50/50 p-4 rounded-xl border border-blue-100">
                  <h3 className="font-bold flex items-center gap-2 text-blue-900">
                    <Info className="h-5 w-5" /> Chemical Treatment
                  </h3>
                  <ul className="space-y-2 list-disc list-inside text-gray-700">
                    {result.treatment_plan.chemical_treatment.map((action, i) => (
                      <li key={i}>{action}</li>
                    ))}
                  </ul>
                </div>

                {/* Prevention */}
                <div className="space-y-3 bg-purple-50/50 p-4 rounded-xl border border-purple-100">
                  <h3 className="font-bold flex items-center gap-2 text-purple-900">
                    <MapPin className="h-5 w-5" /> Prevention & Spread Risk
                  </h3>
                  <p className="text-sm font-medium text-gray-900 mb-2">{result.spread_risk}</p>
                  <ul className="space-y-2 list-disc list-inside text-gray-700">
                    {result.treatment_plan.prevention.map((action, i) => (
                      <li key={i}>{action}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Actions */}
              <div className="pt-4 border-t flex justify-end gap-3">
                <button 
                  onClick={() => {
                    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
                      const text = `Diagnosis: ${result.disease_name}. Severity: ${result.severity}. Immediate actions: ${result.treatment_plan.immediate_actions.join(', ')}`;
                      const utterance = new SpeechSynthesisUtterance(text);
                      // Try to match selected language, fallback to browser default
                      utterance.lang = language === 'hi' ? 'hi-IN' : language === 'mr' ? 'mr-IN' : 'en-IN';
                      window.speechSynthesis.cancel(); // stop any ongoing speech
                      window.speechSynthesis.speak(utterance);
                    } else {
                      alert("Text-to-speech is not supported in your browser.");
                    }
                  }}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 hover:bg-blue-100 font-semibold rounded-lg transition-colors"
                >
                  <Activity className="h-4 w-4" /> {/* Reusing Activity icon for audio/speaker since Volume/Speaker isn't imported */}
                  Read Aloud
                </button>
                <button 
                  onClick={handleShare}
                  className="flex items-center gap-2 px-4 py-2 bg-green-50 text-green-700 hover:bg-green-100 font-semibold rounded-lg transition-colors"
                >
                  <Share2 className="h-4 w-4" />
                  Share via WhatsApp
                </button>
              </div>

            </div>
          </div>
        )}
      </div>
    </div>
  );
}
