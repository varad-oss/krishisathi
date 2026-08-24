import Link from 'next/link';
import { Camera, MessageSquare, ShieldAlert, BarChart3, Globe2, Sprout } from 'lucide-react';

export default function Home() {
  return (
    <div className="flex-1 bg-white">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-green-50 pt-24 pb-32">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center animate-fade-in">
          <div className="inline-flex items-center gap-2 rounded-full bg-green-100 px-4 py-2 text-sm font-medium text-green-800 mb-8">
            <span className="flex h-2 w-2 rounded-full bg-green-600"></span>
            Interoperable Digital Agriculture Network
          </div>
          
          <h1 className="mx-auto max-w-4xl text-5xl font-extrabold tracking-tight text-gray-900 sm:text-6xl lg:text-7xl">
            KrishiSathi
            <span className="block text-3xl sm:text-4xl lg:text-5xl mt-2 text-green-700">
              Climate-Resilient Farming Intelligence
            </span>
          </h1>
          
          <p className="mx-auto mt-6 max-w-3xl text-lg text-gray-600 sm:text-xl">
            A scalable digital public good enabling Indian states to share agricultural data models. 
            Delivering real-time, localized agro-advisories, regenerative crop recommendations based on satellite data, soil health, and weather forecasting.
          </p>
          
          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/chat"
              className="w-full sm:w-auto flex items-center justify-center gap-2 rounded-lg bg-green-700 px-8 py-4 text-lg font-semibold text-white shadow-lg shadow-green-700/30 transition-all hover:bg-green-800 hover:-translate-y-1"
            >
              <MessageSquare className="h-5 w-5" />
              Get Regenerative Advisory
            </Link>
            <Link
              href="/diagnose"
              className="w-full sm:w-auto flex items-center justify-center gap-2 rounded-lg bg-white border-2 border-gray-200 px-8 py-4 text-lg font-semibold text-gray-700 transition-all hover:border-green-600 hover:text-green-700 hover:-translate-y-1"
            >
              <Camera className="h-5 w-5" />
              Crop Diagnostic Tool
            </Link>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-24 bg-white">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">Comprehensive Agricultural Network</h2>
            <p className="mt-4 text-lg text-gray-600">Strengthening cooperation on sustainable food production</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            {[
              { icon: Globe2, title: "1. Data Aggregation", desc: "We ingest live satellite NDVI data, Open-Meteo weather forecasts, and regional soil health metrics." },
              { icon: Sprout, title: "2. Regenerative AI", desc: "Gemini 2.5 generates hyper-localized, regenerative crop recommendations tailored to your exact microclimate." },
              { icon: ShieldAlert, title: "3. Interoperable Sync", desc: "Data models and disease outbreak patterns are shared securely across Indian states to strengthen national resilience." }
            ].map((step, idx) => (
              <div key={idx} className="flex flex-col items-center text-center group">
                <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-green-100 text-green-700 transition-all group-hover:scale-110 group-hover:bg-green-600 group-hover:text-white mb-6">
                  <step.icon className="h-10 w-10" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">{step.title}</h3>
                <p className="text-gray-600">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Key Features Grid */}
      <section className="py-24 bg-gray-50 border-y">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">Comprehensive Platform</h2>
            <p className="mt-4 text-lg text-gray-600">Built for farmers, optimized for policymakers</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              { icon: Camera, title: "Crop Disease Diagnosis", desc: "AI-powered computer vision to instantly identify 38+ common crop diseases from photos." },
              { icon: Globe2, title: "10+ Languages", desc: "Fully accessible in Hindi, Marathi, Tamil, Telugu, Bengali, Kannada, Gujarati, Punjabi, Malayalam, and more regional dialects." },
              { icon: Globe2, title: "Satellite Monitoring", desc: "Earth Engine integration for NDVI crop health tracking across vast regions." },
              { icon: ShieldAlert, title: "Real-time Alerts", desc: "Automated early warning systems for disease outbreaks and extreme weather." },
              { icon: BarChart3, title: "Policymaker Dashboard", desc: "Aggregated, anonymized data for national-level agricultural decision making." },
              { icon: MessageSquare, title: "Cross-State Intelligence", desc: "Seamless cross-state data sharing and shared learning models between Indian states." }
            ].map((feature, idx) => (
              <div key={idx} className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100 transition-all hover:shadow-md hover:border-green-200">
                <feature.icon className="h-8 w-8 text-green-600 mb-4" />
                <h3 className="text-lg font-bold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Tech Stack Section */}
      <section className="py-24 bg-white">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl mb-12">Powered by Google AI</h2>
          <div className="flex flex-wrap justify-center gap-8 items-center">
            {["Gemini 2.5 Flash", "Vertex AI Studio", "Google Earth Engine", "Translation API", "Google Maps Platform"].map((tech, idx) => (
              <div key={idx} className="px-6 py-3 rounded-full bg-gray-50 border text-gray-700 font-medium shadow-sm">
                {tech}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer CTA */}
      <section className="py-24 bg-green-900 text-white">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-6">Ready to protect your harvest?</h2>
          <p className="text-xl text-green-100 mb-10 max-w-2xl mx-auto">
            Join millions of Indian farmers using KrishiSathi to ensure food security and improve yields.
          </p>
          <Link
            href="/diagnose"
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-white px-8 py-4 text-lg font-bold text-green-900 transition-all hover:bg-green-50 hover:scale-105"
          >
            Start Diagnosing Now
          </Link>
        </div>
      </section>
    </div>
  );
}
