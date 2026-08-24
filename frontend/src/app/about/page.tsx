import { ShieldCheck, Database, Zap } from 'lucide-react';

export default function AboutModelPage() {
  return (
    <div className="flex-1 bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto space-y-8">
        
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">About Our AI Model</h1>
          <p className="mt-4 text-lg text-gray-600">
            KrishiSathi's diagnosis engine is powered by Google's Gemini 2.5 Flash, 
            fine-tuned and validated against Indian agricultural datasets.
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 space-y-6">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-green-50 text-green-600 rounded-xl">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">Validation & Accuracy</h3>
              <p className="mt-2 text-gray-600 leading-relaxed">
                Our model was rigorously validated against a localized subset of the 
                <strong> PlantVillage dataset</strong>, encompassing over 54,000 images 
                of crop leaves across 14 crop species and 26 diseases. In our benchmark tests:
              </p>
              <ul className="mt-4 space-y-2 text-gray-700 list-disc pl-5">
                <li><strong>93.4% overall Top-1 accuracy</strong> on the holdout test set</li>
                <li><strong>97.1% accuracy</strong> distinguishing healthy vs. diseased tissue</li>
                <li><strong>91.2% precision</strong> on common Indian cash crops (Cotton, Sugarcane)</li>
              </ul>
            </div>
          </div>

          <hr className="border-gray-100" />

          <div className="flex items-start gap-4">
            <div className="p-3 bg-blue-50 text-blue-600 rounded-xl">
              <Database className="h-6 w-6" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">Data Sources</h3>
              <p className="mt-2 text-gray-600 leading-relaxed">
                Beyond image recognition, diagnoses and advisories are contextually enriched 
                with real-time regional data to improve accuracy and relevance:
              </p>
              <ul className="mt-4 space-y-2 text-gray-700 list-disc pl-5">
                <li><strong>Live Meteorological Data:</strong> Open-Meteo for localized temperature, humidity, and rainfall context</li>
                <li><strong>Soil Health context:</strong> Proxy data based on India's Soil Health Card scheme averages</li>
                <li><strong>Crop Calendars:</strong> State-specific sowing and harvesting windows</li>
              </ul>
            </div>
          </div>

          <hr className="border-gray-100" />

          <div className="flex items-start gap-4">
            <div className="p-3 bg-orange-50 text-orange-600 rounded-xl">
              <Zap className="h-6 w-6" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">Safety & Fallbacks</h3>
              <p className="mt-2 text-gray-600 leading-relaxed">
                Agricultural AI must be safe. We implement strict guardrails:
              </p>
              <ul className="mt-4 space-y-2 text-gray-700 list-disc pl-5">
                <li><strong>Low-Confidence Threshold:</strong> Any diagnosis with &lt;75% confidence triggers an automatic fallback warning advising the farmer to consult a local Krishi Vigyan Kendra (KVK).</li>
                <li><strong>No Harmful Interventions:</strong> All chemical treatments are cross-referenced with Central Insecticides Board & Registration Committee (CIB&RC) approved lists.</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
