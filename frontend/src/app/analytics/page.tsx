"use client";

import React, { useState, useEffect } from "react";
import { TrendingUp, BarChart2, PieChart, ShieldAlert, Award } from "lucide-react";
import { api } from "@/lib/api";
import { DashboardData } from "@/lib/types";
import RiskBadge from "@/components/RiskBadge";

export default function AnalyticsPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [reasons, setReasons] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [dData, rData] = await Promise.all([
        api.getDashboard(),
        api.getAbsenceReasons(),
      ]);
      setData(dData);
      setReasons(rData);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !data) {
    return <div className="p-12 text-center text-slate-400 text-sm">Loading analytics insights...</div>;
  }

  const { overall, subjects, trend_data } = data;
  const sortedByAttendance = [...subjects].sort((a, b) => b.current_percentage - a.current_percentage);
  const totalAbsencePeriods = Object.values(reasons).reduce((a, b) => a + b, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-blue-600" /> Attendance Analytics & Behavior
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Subject standings, absence distributions by documented category, and weighted unit comparisons.
          </p>
        </div>
      </div>

      {/* Overview Metric Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">
            Unweighted Attendance
          </span>
          <span className="text-3xl font-black text-slate-900 mt-2 block">
            {overall.current_percentage}%
          </span>
          <span className="text-xs text-slate-400">Pure session count ratio (A / C)</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">
            Weighted Attendance
          </span>
          <span className="text-3xl font-black text-blue-600 mt-2 block">
            {overall.weighted_percentage}%
          </span>
          <span className="text-xs text-slate-400">Factoring credits & 2-hour lab duration</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">
            Documented Absences
          </span>
          <span className="text-3xl font-black text-slate-900 mt-2 block">
            {overall.total_absent}
          </span>
          <span className="text-xs text-slate-400">Total missed periods recorded</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Subject Leaderboard */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <Award className="w-5 h-5 text-amber-500" />
            <h3 className="font-bold text-slate-900 text-base">Subject Performance Ranking</h3>
          </div>

          <div className="space-y-3">
            {sortedByAttendance.map((s, idx) => (
              <div
                key={s.subject_id}
                className="p-3.5 bg-slate-50 rounded-xl border border-slate-100 flex items-center justify-between"
              >
                <div className="flex items-center gap-3">
                  <span className="w-6 h-6 rounded-full bg-slate-200 text-slate-700 font-bold text-xs flex items-center justify-center">
                    {idx + 1}
                  </span>
                  <div>
                    <span className="font-bold text-xs text-slate-900 block">
                      {s.subject_code} - {s.subject_name}
                    </span>
                    <span className="text-[11px] text-slate-500">
                      {s.classes_attended} / {s.classes_conducted} attended
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <RiskBadge level={s.risk_level} showIcon={false} />
                  <span
                    className={`font-black text-sm ${
                      s.is_shortage ? "text-red-600" : "text-slate-900"
                    }`}
                  >
                    {s.current_percentage}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Absence Reasons Distribution */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <PieChart className="w-5 h-5 text-blue-600" />
              <h3 className="font-bold text-slate-900 text-base">Absence Reason Categorization</h3>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Documenting absence categories is essential for verifying medical certificates and condonation requirements.
            </p>

            <div className="space-y-3">
              {Object.entries(reasons).map(([reason, count]) => {
                const pct = totalAbsencePeriods > 0 ? (count / totalAbsencePeriods) * 100 : 0;
                return (
                  <div key={reason} className="space-y-1">
                    <div className="flex justify-between text-xs font-semibold text-slate-700">
                      <span className="capitalize">{reason.replace("_", " ")}</span>
                      <span>
                        {count} period{count !== 1 ? "s" : ""} ({pct.toFixed(0)}%)
                      </span>
                    </div>
                    <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                      <div
                        className="bg-blue-600 h-full rounded-full"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-100 text-xs text-slate-500">
            Approved leaves (OD) and medical reasons are stored separately to support institutional condonation rules.
          </div>
        </div>
      </div>
    </div>
  );
}
