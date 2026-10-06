"use client";

import React, { useState, useEffect } from "react";
import { Sparkles, Brain, ShieldAlert, CheckCircle, BarChart3, HelpCircle, ArrowRight } from "lucide-react";
import { api } from "@/lib/api";
import RiskBadge from "@/components/RiskBadge";

export default function PredictPage() {
  const [forecastData, setForecastData] = useState<any | null>(null);
  const [metricsData, setMetricsData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [fData, mData] = await Promise.all([
        api.getForecast(),
        api.getMLMetrics(),
      ]);
      setForecastData(fData);
      setMetricsData(mData);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-12 text-center text-slate-400 text-sm">Evaluating predictive models...</div>;
  }

  const overall = forecastData?.overall;
  const subjects = forecastData?.subjects || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-blue-600" /> Attendance Predictor & ML Forecasting
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Combines timetable-aware schedule counts, rolling behavioral attendance momentum, and trained ML models to forecast final semester-end percentages with uncertainty bounds.
          </p>
        </div>
      </div>

      {/* Aggregate Semester Forecast Hero Card */}
      {overall && (
        <div className="bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 text-white p-6 rounded-3xl shadow-xl relative overflow-hidden">
          <div className="absolute right-0 top-0 bottom-0 w-1/3 bg-blue-500/10 blur-3xl pointer-events-none" />

          <div className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30">
                  Semester-End Projection
                </span>
                <RiskBadge level={overall.risk_level} />
              </div>
              <h2 className="text-3xl sm:text-4xl font-black tracking-tight">
                {overall.predicted_percentage}%{" "}
                <span className="text-sm font-normal text-slate-400">predicted final</span>
              </h2>
              <p className="text-xs text-slate-300 mt-1">
                Expected Range: <strong className="text-white">{overall.confidence_interval_low}% – {overall.confidence_interval_high}%</strong> (Confidence: {overall.confidence_score}%)
              </p>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 bg-white/5 p-4 rounded-2xl border border-white/10 text-xs">
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Current %</span>
                <span className="text-base font-bold text-white">{overall.current_percentage}%</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Remaining Classes</span>
                <span className="text-base font-bold text-blue-300">{overall.total_remaining}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Max Possible</span>
                <span className="text-base font-bold text-emerald-400">{overall.max_possible_percentage}%</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Subject Forecast Grid */}
      <div>
        <h2 className="text-lg font-bold text-slate-900 mb-3">Subject-Level Forecasts</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {subjects.map((sub: any) => (
            <div
              key={sub.subject_id}
              className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between"
            >
              <div>
                <div className="flex justify-between items-start">
                  <div>
                    <span className="font-extrabold text-sm text-slate-900 block">
                      {sub.subject_code}
                    </span>
                    <span className="text-xs text-slate-500 block truncate max-w-[200px]">
                      {sub.subject_name}
                    </span>
                  </div>
                  <RiskBadge level={sub.risk_level} />
                </div>

                <div className="mt-4 p-3.5 bg-slate-50 rounded-xl border border-slate-100 space-y-2">
                  <div className="flex justify-between items-baseline text-xs">
                    <span className="text-slate-500">Current Attendance:</span>
                    <span className="font-bold text-slate-800">{sub.current_percentage}%</span>
                  </div>
                  <div className="flex justify-between items-baseline text-xs">
                    <span className="text-slate-500">Predicted Final %:</span>
                    <span className="font-black text-blue-600 text-sm">{sub.predicted_percentage}%</span>
                  </div>
                  <div className="flex justify-between items-baseline text-xs">
                    <span className="text-slate-500">Target %:</span>
                    <span className="font-semibold text-slate-700">{sub.target_percentage}%</span>
                  </div>
                  <div className="flex justify-between items-baseline text-xs">
                    <span className="text-slate-500">Confidence Range:</span>
                    <span className="font-mono text-[11px] text-slate-600">
                      {sub.confidence_interval_low}% - {sub.confidence_interval_high}%
                    </span>
                  </div>
                </div>

                {sub.projected_shortage_date && (
                  <div className="mt-3 p-2.5 rounded-lg bg-red-50 border border-red-200 text-xs text-red-800">
                    <strong>Projected Shortage:</strong> Expected to breach target around{" "}
                    <strong>{sub.projected_shortage_date}</strong>.
                  </div>
                )}

                {/* Factors */}
                <div className="mt-3 space-y-1">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                    Forecasting Factors
                  </span>
                  {sub.contributing_factors.slice(0, 2).map((fac: string, idx: number) => (
                    <p key={idx} className="text-[11px] text-slate-600 leading-tight">
                      • {fac}
                    </p>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Model Evaluation & Validation Panel */}
      {metricsData && metricsData.regression_model_comparison && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center gap-2">
            <Brain className="w-5 h-5 text-indigo-600" />
            <h2 className="text-lg font-bold text-slate-900">
              Machine Learning Model Validation & Benchmark
            </h2>
          </div>
          <p className="text-xs text-slate-500 leading-relaxed">
            In compliance with academic integrity guidelines, predictions are validated against candidate regression models trained on realistic student trajectories ({metricsData.dataset_info?.total_samples} samples across a 15-week college semester).
          </p>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider border-b border-slate-200">
                <tr>
                  <th className="py-2.5 px-3">Candidate Model</th>
                  <th className="py-2.5 px-3">Mean Absolute Error (MAE)</th>
                  <th className="py-2.5 px-3">Root Mean Squared Error (RMSE)</th>
                  <th className="py-2.5 px-3">R² Score</th>
                  <th className="py-2.5 px-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {Object.entries(metricsData.regression_model_comparison).map(([mName, vals]: [string, any]) => (
                  <tr key={mName} className="hover:bg-slate-50">
                    <td className="py-2.5 px-3 font-semibold text-slate-800">
                      {mName.replace(/_/g, " ")}
                    </td>
                    <td className="py-2.5 px-3 font-mono text-slate-700">{vals.MAE}%</td>
                    <td className="py-2.5 px-3 font-mono text-slate-700">{vals.RMSE}%</td>
                    <td className="py-2.5 px-3 font-mono text-slate-700">{vals.R2}</td>
                    <td className="py-2.5 px-3">
                      {mName === metricsData.best_regression_model ? (
                        <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full">
                          Selected (Best Fit)
                        </span>
                      ) : (
                        <span className="text-[10px] text-slate-400">Benchmark</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 border-t border-slate-100 text-center">
            <div className="p-3 bg-slate-50 rounded-xl">
              <span className="text-slate-400 text-[10px] font-bold uppercase block">Risk Accuracy</span>
              <span className="text-sm font-bold text-slate-800">
                {(metricsData.risk_classification_metrics?.Accuracy * 100).toFixed(1)}%
              </span>
            </div>
            <div className="p-3 bg-slate-50 rounded-xl">
              <span className="text-slate-400 text-[10px] font-bold uppercase block">Precision</span>
              <span className="text-sm font-bold text-slate-800">
                {(metricsData.risk_classification_metrics?.Precision * 100).toFixed(1)}%
              </span>
            </div>
            <div className="p-3 bg-slate-50 rounded-xl">
              <span className="text-slate-400 text-[10px] font-bold uppercase block">Recall</span>
              <span className="text-sm font-bold text-slate-800">
                {(metricsData.risk_classification_metrics?.Recall * 100).toFixed(1)}%
              </span>
            </div>
            <div className="p-3 bg-slate-50 rounded-xl">
              <span className="text-slate-400 text-[10px] font-bold uppercase block">F1-Score</span>
              <span className="text-sm font-bold text-slate-800">
                {(metricsData.risk_classification_metrics?.F1_Score * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
