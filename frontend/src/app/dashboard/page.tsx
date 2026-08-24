"use client";

import { useEffect, useState } from "react";
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
import { formatNumber, getSeverityColor, cn } from "@/lib/utils";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [outbreaks, setOutbreaks] = useState<OutbreakData[]>([]);
  const [states, setStates] = useState<IndianState[]>([]);
  const [healthData, setHealthData] = useState<CropHealthData[]>([]);
  const [report, setReport] = useState<string>("");
  const [loadingReport, setLoadingReport] = useState(false);
  const [signals, setSignals] = useState<any[]>([]);

  useEffect(() => {
    async function loadData() {
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
      setSignals(sig.signals || []);
      loadReport();
    }
    loadData();
  }, []);

  const loadReport = async () => {
    setLoadingReport(true);
    const rep = await getDashboardReport();
    setReport(rep);
    setLoadingReport(false);
  };

  if (!stats)
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center text-green-700">
          <Activity className="h-8 w-8 animate-spin mb-4" />
          <p className="font-semibold">Loading Dashboard Data...</p>
        </div>
      </div>
    );

  return (
    <div className="flex-1 bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Policymaker Dashboard
            </h1>
            <p className="text-gray-600 mt-1">
              Real-time agriculture intelligence across Indian states
            </p>
          </div>
          <div className="bg-white px-4 py-2 rounded-lg border shadow-sm text-sm font-medium text-gray-600 flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-green-500"></span> Live
            Data Feed
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
                <p className="text-sm font-medium text-gray-500">
                  Total Diagnoses
                </p>
                <h3 className="text-2xl font-bold text-gray-900">
                  {formatNumber(stats.total_diagnoses)}
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
                <p className="text-sm font-medium text-gray-500">
                  Active Outbreaks
                </p>
                <h3 className="text-2xl font-bold text-gray-900">
                  {stats.active_outbreaks}
                </h3>
              </div>
            </div>
            <div className="text-sm text-gray-500">
              Require immediate attention
            </div>
          </div>

          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <div className="flex items-center gap-4 mb-4">
              <div className="p-3 bg-green-50 text-green-600 rounded-xl">
                <Users className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">
                  Farmers Reached
                </p>
                <h3 className="text-2xl font-bold text-gray-900">
                  {formatNumber(stats.farmers_reached)}
                </h3>
              </div>
            </div>
            <div className="text-sm text-gray-500">Across 8 states</div>
          </div>

          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <div className="flex items-center gap-4 mb-4">
              <div className="p-3 bg-purple-50 text-purple-600 rounded-xl">
                <Globe2 className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">
                  Languages Served
                </p>
                <h3 className="text-2xl font-bold text-gray-900">
                  {stats.languages_served}
                </h3>
              </div>
            </div>
            <div className="text-sm text-gray-500">Native language support</div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column: Tables & Charts */}
          <div className="lg:col-span-2 space-y-8">
            {/* Outbreaks Table */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
              <div className="p-6 border-b border-gray-100 flex justify-between items-center">
                <h3 className="text-lg font-bold text-gray-900">
                  Recent Disease Outbreaks
                </h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="bg-gray-50 text-gray-600 font-medium border-b">
                    <tr>
                      <th className="px-6 py-3">Disease</th>
                      <th className="px-6 py-3">Region</th>
                      <th className="px-6 py-3">Severity</th>
                      <th className="px-6 py-3">Reports</th>
                      <th className="px-6 py-3">Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {outbreaks.map((ob) => (
                      <tr key={ob.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 font-medium text-gray-900">
                          {ob.disease}
                        </td>
                        <td className="px-6 py-4 text-gray-600">{ob.region}</td>
                        <td className="px-6 py-4">
                          <span
                            className={cn(
                              "px-2.5 py-1 rounded-full text-xs font-semibold",
                              getSeverityColor(ob.severity),
                            )}
                          >
                            {ob.severity}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-gray-600">
                          {formatNumber(ob.reports_count)}
                        </td>
                        <td className="px-6 py-4 text-gray-500">{ob.date}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Chart */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-6">
                Regional Crop Health (NDVI)
              </h3>
              <div className="h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={healthData}
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
                      {healthData.map((entry, index) => (
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
              </div>
            </div>
          </div>

          {/* Right Column: AI Report & States Info */}
          <div className="space-y-8">
            {/* AI Report Card */}
            <div className="bg-gradient-to-br from-green-900 to-green-800 rounded-2xl shadow-sm text-white overflow-hidden">
              <div className="p-6 border-b border-green-700/50 flex justify-between items-center">
                <h3 className="text-lg font-bold flex items-center gap-2">
                  <FileText className="h-5 w-5 text-green-300" />
                  AI Insights Report
                </h3>
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
              <div className="p-6">
                <div className="prose prose-invert prose-sm max-w-none">
                  {loadingReport ? (
                    <div className="flex flex-col items-center justify-center py-8 text-green-200">
                      <Activity className="h-6 w-6 animate-spin mb-2" />
                      <p>Gemini is analyzing latest data...</p>
                    </div>
                  ) : (
                    <div className="text-green-50 space-y-3">
                      {report.split("\n").map((line, i) => (
                        <p
                          key={i}
                          className={
                            line.startsWith("##")
                              ? "font-bold text-lg mt-4"
                              : "text-green-50"
                          }
                        >
                          {line.replace(/^#+\s*/, "")}
                        </p>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Indian States Grid */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">
                Indian States Network
              </h3>
              <div className="space-y-4">
                {states.map((s) => (
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
                          {s.name}
                        </p>
                        <p className="text-xs text-gray-500">
                          Top: {s.top_crop}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-gray-900">
                        {formatNumber(s.farmers_reached)}
                      </p>
                      <p
                        className={cn(
                          "text-xs font-medium",
                          s.active_alerts > 0
                            ? "text-orange-600"
                            : "text-green-600",
                        )}
                      >
                        {s.active_alerts} Alerts
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Cross-State Signals */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Globe2 className="h-5 w-5 text-blue-500" />
                Cross-State Signals
              </h3>
              <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2">
                {signals.map((sig, idx) => (
                  <div key={idx} className="p-4 rounded-xl border border-blue-50 bg-blue-50/30 text-sm">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-semibold text-blue-800">
                        {sig.from_state} → {sig.to_state || 'ALL'}
                      </span>
                      <span className={cn(
                        "px-2 py-0.5 rounded text-xs font-medium",
                        getSeverityColor(sig.severity || 'info')
                      )}>
                        {sig.severity?.toUpperCase() || 'INFO'}
                      </span>
                    </div>
                    <p className="text-gray-700">{sig.message}</p>
                    <div className="text-xs text-gray-400 mt-2 text-right">
                      {new Date(sig.timestamp).toLocaleString('en-IN')}
                    </div>
                  </div>
                ))}
                {signals.length === 0 && (
                  <p className="text-gray-500 text-sm text-center py-4">No active cross-state signals.</p>
                )}
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}
