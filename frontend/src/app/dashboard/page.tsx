"use client";

import { useEffect, useState, useCallback } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import {
  getDashboardStats,
  getOutbreaks,
  getDashboardReport,
  getCropHealth,
  getExchangeSignals,
  getIndianStates,
} from "@/lib/api";
import {
  DashboardStats,
  OutbreakData,
  IndianState,
  CropHealthData,
} from "@/lib/types";
import {
  TrendingUp,
  Users,
  Globe2,
  AlertTriangle,
  FileText,
  RefreshCw,
  Activity,
} from "lucide-react";
import { formatNumber, formatDate, getSeverityColor, cn } from "@/lib/utils";
import SignalPublisher from '@/components/SignalPublisher';


import { useLanguage } from "@/lib/LanguageContext";
import { t } from "@/lib/translations";


interface CrossStateSignal {
  from_state: string;
  to_state?: string;
  severity?: string;
  message: string;
  timestamp: string;
}

export default function DashboardPage() {
  const { language } = useLanguage();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [outbreaks, setOutbreaks] = useState<OutbreakData[]>([]);
  const [states, setStates] = useState<IndianState[]>([]);
  const [healthData, setHealthData] = useState<CropHealthData[]>([]);
  const [report, setReport] = useState<string>("");
  const [loadingReport, setLoadingReport] = useState(false);
  const [selectedState, setSelectedState] = useState<string>("ALL");
  const [signals, setSignals] = useState<CrossStateSignal[]>([]);

  const [error, setError] = useState<string | null>(null);

  const loadReport = useCallback(async () => {
    try {
      setLoadingReport(true);
      const rep = await getDashboardReport(language);
      setReport(rep || "No report data available at this time.");
    } catch {
      setReport("Dashboard report is unavailable.");
    } finally {
      setLoadingReport(false);
    }
  }, [language]);

  useEffect(() => {
    async function loadData() {
      try {
        const [s, o, c, h, sig] = await Promise.all([
          getDashboardStats(),
          getOutbreaks(),
          getIndianStates(),
          getCropHealth(),
          getExchangeSignals()
        ]);
        setStats(s);
        setOutbreaks(o);
        setStates(c);
        setHealthData(h);
        setSignals((sig as { signals?: CrossStateSignal[] }).signals || []);
        loadReport();
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load dashboard data. Live dashboard data could not be loaded.");
      }
    }
    loadData();
  }, [loadReport]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (stats) loadReport();
  }, [language, stats, loadReport]);

  if (error) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-gray-50 p-6">
        <AlertTriangle className="h-12 w-12 text-red-500 mb-4" />
        <h2 className="text-xl font-bold text-gray-900 mb-2">Service Unavailable</h2>
        <p className="text-gray-600 text-center max-w-md">{error}</p>
      </div>
    );
  }

  if (!stats)
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center text-green-700">
          <Activity className="h-8 w-8 animate-spin mb-4" />
          <p className="font-semibold">Loading Dashboard Data...</p>
        </div>
      </div>
    );

  const selectedStateName = states.find(s => s.code === selectedState)?.name;

  const filteredOutbreaks = selectedState === "ALL" 
    ? outbreaks 
    : outbreaks.filter(ob => ob.region === selectedStateName);

  const filteredStates = selectedState === "ALL" 
    ? states 
    : states.filter(s => s.code === selectedState);

  const filteredSignals = selectedState === "ALL" 
    ? signals 
    : signals.filter(sig => sig.from_state === selectedState || sig.to_state === selectedState || !sig.to_state);

  const filteredHealth = selectedState === "ALL"
    ? healthData
    : healthData.filter(h => h.region === selectedStateName || h.region === selectedState);

  return (
    <div className="flex-1 bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{t('Policymaker Dashboard', language)}</h1>
            <p className="text-gray-600 mt-1">{t('Real-time agriculture intelligence across Indian states', language)}</p>
          </div>
          <div className="flex items-center gap-4">
            <select
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value)}
              className="bg-white px-4 py-2 rounded-lg border shadow-sm text-sm font-medium text-gray-700 outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value="ALL">National Overview (All States)</option>
              {states.map((s) => (
                <option key={s.code} value={s.code}>
                  {t(s.name, language)} ({s.code})
                </option>
              ))}
            </select>
            <div className="bg-white px-4 py-2 rounded-lg border shadow-sm text-sm font-medium text-gray-600 flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-green-500"></span> Live
              Data Feed
            </div>
          </div>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <div className="flex items-center gap-4 mb-4">
              <div className="p-3 bg-blue-50 text-blue-600 rounded-xl">
                <Activity className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">{t('Total Diagnoses', language)}</p>
                <h3 className="text-2xl font-bold text-gray-900">
                  {formatNumber(stats.total_diagnoses, language)}
                </h3>
              </div>
            </div>
            <div className="flex items-center gap-1 text-sm text-green-600 font-medium">
              <TrendingUp className="h-4 w-4" />
              <span>+{stats.diagnoses_trend}% this month</span>
            </div>
          </div>

          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <div className="flex items-center gap-4 mb-4">
              <div className="p-3 bg-red-50 text-red-600 rounded-xl">
                <AlertTriangle className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">{t('Active Outbreaks', language)}</p>
                <h3 className="text-2xl font-bold text-gray-900">
                  {formatNumber(stats.active_outbreaks, language)}
                </h3>
              </div>
            </div>
            <div className="text-sm text-gray-500">{t('Require immediate attention', language)}</div>
          </div>

          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <div className="flex items-center gap-4 mb-4">
              <div className="p-3 bg-green-50 text-green-600 rounded-xl">
                <Users className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">{t('Farmers Reached', language)}</p>
                <h3 className="text-2xl font-bold text-gray-900">
                  {formatNumber(stats.farmers_reached, language)}
                </h3>
              </div>
            </div>
            <div className="text-sm text-gray-500">{t(t("Across 8 states", language), language)}</div>
          </div>

          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <div className="flex items-center gap-4 mb-4">
              <div className="p-3 bg-purple-50 text-purple-600 rounded-xl">
                <Globe2 className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">{t('Languages Served', language)}</p>
                <h3 className="text-2xl font-bold text-gray-900">
                  {formatNumber(stats.languages_served, language)}
                </h3>
              </div>
            </div>
            <div className="text-sm text-gray-500">{t(t("Native language support", language), language)}</div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column: Tables & Charts */}
          <div className="lg:col-span-2 space-y-8">
            {/* Outbreaks Table */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
              <div className="p-6 border-b border-gray-100 flex justify-between items-center">
                <h3 className="text-lg font-bold text-gray-900">{t('Recent Disease Outbreaks', language)}</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="bg-gray-50 text-gray-600 font-medium border-b">
                    <tr>
                      <th className="px-6 py-3">{t(t("Disease", language), language)}</th>
                      <th className="px-6 py-3">{t(t("Region", language), language)}</th>
                      <th className="px-6 py-3">{t(t("Severity", language), language)}</th>
                      <th className="px-6 py-3">{t(t("Reports", language), language)}</th>
                      <th className="px-6 py-3">{t(t("Date", language), language)}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {filteredOutbreaks.map((ob) => (
                      <tr key={ob.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 font-medium text-gray-900">
                          {t(ob.disease, language)}
                        </td>
                        <td className="px-6 py-4 text-gray-600">{t(ob.region, language)}</td>
                        <td className="px-6 py-4">
                          <span
                            className={cn(
                              "px-2.5 py-1 rounded-full text-xs font-semibold",
                              getSeverityColor(ob.severity),
                            )}
                          >
                            {t(ob.severity, language)}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-gray-600">
                          {formatNumber(ob.reports_count, language)}
                        </td>
                        <td className="px-6 py-4 text-gray-500">{formatDate(ob.date, language)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Chart */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-6">{t('Regional Crop Health (NDVI)', language)}</h3>
              <div className="h-72 w-full">
                {filteredHealth.length === 0 ? (
                  <div className="flex items-center justify-center h-full text-gray-400">
                    <p>{t('Regional crop health data is currently unavailable.', language)}</p>
                  </div>
                ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={filteredHealth.map(h => ({...h, region: t(h.region, language)}))}
                    margin={{ top: 5, right: 5, left: -20, bottom: 5 }}
                  >
                    <CartesianGrid
                      strokeDasharray="3 3"
                      vertical={false}
                      stroke="#f0f0f0"
                    />
                    <XAxis
                      dataKey="region"
                      axisLine={false}
                      tickLine={false}
                      tick={{ fontSize: 12, fill: "#6b7280" }}
                    />
                    <YAxis
                      axisLine={false}
                      tickLine={false}
                      tick={{ fontSize: 12, fill: "#6b7280" }}
                      tickFormatter={(value) => formatNumber(value, language)}
                    />
                    <RechartsTooltip
                      cursor={{ fill: "#f9fafb" }}
                      contentStyle={{
                        borderRadius: "8px",
                        border: "none",
                        boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                      }}
                    />
                    <Bar dataKey="ndvi_score" radius={[4, 4, 0, 0]}>
                      {filteredHealth.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={
                            entry.ndvi_score > 0.6
                              ? "#22c55e"
                              : entry.ndvi_score > 0.4
                                ? "#eab308"
                                : "#ef4444"
                          }
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
                )}
              </div>
            </div>
          </div>

          {/* Right Column: AI Report & States Info */}
          <div className="space-y-8">
            {/* AI Report Card */}
            <div className="bg-gradient-to-br from-green-900 to-green-800 rounded-2xl shadow-sm text-white overflow-hidden">
              <div className="p-6 border-b border-green-700/50 flex justify-between items-center">
                <h3 className="text-lg font-bold flex items-center gap-2">
                  <FileText className="h-5 w-5 text-green-300" />{t('AI Insights Report', language)}</h3>
                <button
                  onClick={loadReport}
                  disabled={loadingReport}
                  className="p-1.5 hover:bg-green-700 rounded-md transition-colors disabled:opacity-50"
                  title="Generate New Report"
                >
                  <RefreshCw
                    className={cn("h-4 w-4", loadingReport && "animate-spin")}
                  />
                </button>
              </div>
              <div className="p-6 max-h-[400px] overflow-y-auto pr-4 custom-scrollbar">
                <div className="prose prose-invert prose-sm max-w-none">
                  {loadingReport ? (
                    <div className="flex flex-col items-center justify-center py-8 text-green-200">
                      <Activity className="h-6 w-6 animate-spin mb-2" />
                      <p>Gemini is analyzing latest data...</p>
                    </div>
                  ) : (
                    <div className="text-green-50 space-y-3 prose prose-invert max-w-none prose-p:leading-relaxed prose-li:marker:text-green-400">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {report}
                      </ReactMarkdown>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Indian States Grid */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">{t('Indian States Network', language)}</h3>
              <div className="space-y-4 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
                {filteredStates.map((s) => (
                  <div
                    key={s.code}
                    className="flex items-center justify-between p-3 rounded-xl border border-gray-100 hover:bg-gray-50 transition-colors cursor-default"
                  >
                    <div className="flex items-center gap-3">
                      <span className="flex items-center justify-center w-8 h-8 rounded-full bg-green-100 text-green-700 font-bold text-xs">
                        {s.code}
                      </span>
                      <div>
                        <p className="font-bold text-gray-900 text-sm">
                          {t(s.name, language)}
                        </p>
                        <p className="text-xs text-gray-500">
                          {t('Top:', language)} {t(s.top_crop, language)}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-gray-900">
                        {formatNumber(s.farmers_reached, language)}
                      </p>
                      <p
                        className={cn(
                          "text-xs font-medium",
                          s.active_alerts > 0
                            ? "text-orange-600"
                            : "text-green-600",
                        )}
                      >
                        {formatNumber(s.active_alerts, language)} {t('Alerts', language)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Cross-State Signals */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Globe2 className="h-5 w-5 text-blue-500" />{t('Cross-State Signals', language)}</h3>
              <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2">
                {filteredSignals.map((sig, idx) => (
                  <div key={idx} className="p-4 rounded-xl border border-blue-50 bg-blue-50/30 text-sm">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-semibold text-blue-800">
                        {sig.from_state} → {sig.to_state || 'ALL'}
                      </span>
                      <span className={cn(
                        "px-2 py-0.5 rounded text-xs font-medium",
                        getSeverityColor(sig.severity || 'info')
                      )}>
                        {t(sig.severity?.toUpperCase() || 'INFO', language)}
                      </span>
                    </div>
                    <p className="text-gray-700">{t(sig.message, language)}</p>
                    <div className="text-xs text-gray-400 mt-2 text-right">
                      {new Date(sig.timestamp).toLocaleString(`${language}-IN`)}
                    </div>
                  </div>
                ))}

                {signals.length === 0 && (
                  <p className="text-gray-500 text-sm text-center py-4">{t('No active cross-state signals.', language)}</p>
                )}
              </div>
              <SignalPublisher states={states} onPublish={async () => {
                const s = await getExchangeSignals();
                setSignals((s as { signals?: any[] }).signals || []);
              }} />
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}
