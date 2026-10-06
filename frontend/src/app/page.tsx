"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Calendar,
  Clock,
  ArrowRight,
  ShieldAlert,
  Sparkles,
  BookOpen,
  RefreshCw,
  Info
} from "lucide-react";
import { api } from "@/lib/api";
import { DashboardData } from "@/lib/types";
import RiskBadge from "@/components/RiskBadge";

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getDashboard();
      setData(res);
    } catch (err: any) {
      setError(err.message || "Failed to load dashboard data. Ensure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
        <p className="text-slate-500 font-medium text-sm">Loading attendance intelligence engine...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center max-w-xl mx-auto my-12">
        <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-3" />
        <h3 className="text-lg font-bold text-red-900 mb-1">Failed to Connect to Attendance API</h3>
        <p className="text-sm text-red-700 mb-4">{error}</p>
        <button
          onClick={fetchDashboard}
          className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white font-medium text-sm rounded-lg hover:bg-red-700 transition"
        >
          <RefreshCw className="w-4 h-4" /> Try Again
        </button>
      </div>
    );
  }

  const { overall, subjects, upcoming_classes_today, explanation_factors, student_profile, student_name } = data;

  return (
    <div className="space-y-6">
      {/* Top Welcome & Summary Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              Welcome back, {student_name || student_profile.roll_number}
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800">
              Semester {student_profile.semester}
            </span>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            {student_profile.department} • {student_profile.college_name}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchDashboard}
            className="inline-flex items-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Refresh
          </button>
          <Link
            href="/simulator"
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-sm transition"
          >
            <Sparkles className="w-3.5 h-3.5" /> What-If Simulator
          </Link>
        </div>
      </div>

      {/* Critical Shortage Warning Banner */}
      {overall.is_shortage && (
        <div className="bg-gradient-to-r from-red-500 to-rose-600 rounded-2xl p-5 text-white shadow-lg shadow-red-500/10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center shrink-0">
              <ShieldAlert className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="font-bold text-base">Attendance Shortage Detected!</h3>
              <p className="text-xs text-red-100 mt-0.5">
                Current aggregate is {overall.current_percentage}% (Target: {overall.target_percentage}%). You must attend the next <strong>{overall.classes_needed} consecutive classes</strong> to restore your eligibility.
              </p>
            </div>
          </div>
          <Link
            href="/recovery"
            className="px-4 py-2 bg-white text-red-700 font-bold text-xs rounded-xl hover:bg-red-50 shrink-0 shadow transition flex items-center gap-1.5"
          >
            Open Recovery Roadmap <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      )}

      {/* Top 4 KPI Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1: Current Attendance */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm relative overflow-hidden">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Current Attendance
            </span>
            <RiskBadge level={overall.overall_risk_level} />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-black text-slate-900">
              {overall.current_percentage}%
            </span>
            <span className="text-xs text-slate-500">
              (Target: {overall.target_percentage}%)
            </span>
          </div>
          <div className="mt-3 w-full bg-slate-100 rounded-full h-2 overflow-hidden">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${
                overall.current_percentage >= overall.target_percentage
                  ? "bg-emerald-500"
                  : "bg-red-500"
              }`}
              style={{ width: `${Math.min(100, overall.current_percentage)}%` }}
            />
          </div>
          <div className="mt-2 text-xs text-slate-500 flex justify-between">
            <span>{overall.total_attended} attended</span>
            <span>{overall.total_conducted} conducted</span>
          </div>
        </div>

        {/* Metric 2: Forecasted Final % */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Predicted Final %
            </span>
            <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-md">
              <Sparkles className="w-3 h-3" /> ML + Schedule
            </span>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-black text-blue-600">
              {overall.predicted_final_percentage}%
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Expected Range: <strong>{overall.confidence_interval_low}% – {overall.confidence_interval_high}%</strong>
          </p>
          <p className="text-[11px] text-slate-400 mt-1">
            Confidence: {overall.prediction_confidence}% • {overall.total_remaining_classes} classes remaining
          </p>
        </div>

        {/* Metric 3: Safe Bunks */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">
            Safe Bunks Available
          </span>
          <div className="mt-3 flex items-baseline gap-2">
            <span
              className={`text-3xl font-black ${
                overall.safe_bunks > 2
                  ? "text-emerald-600"
                  : overall.safe_bunks > 0
                  ? "text-amber-600"
                  : "text-red-600"
              }`}
            >
              {overall.safe_bunks}
            </span>
            <span className="text-xs text-slate-500">classes</span>
          </div>
          <p className="text-xs text-slate-600 mt-2">
            {overall.safe_bunks > 0
              ? `You can miss up to ${overall.safe_bunks} more classes while maintaining >= ${overall.target_percentage}%.`
              : "Zero buffer: any absence immediately breaches your target percentage."}
          </p>
        </div>

        {/* Metric 4: Classes Needed */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">
            Classes Needed to Recover
          </span>
          <div className="mt-3 flex items-baseline gap-2">
            <span
              className={`text-3xl font-black ${
                overall.classes_needed === 0 ? "text-slate-400" : "text-red-600"
              }`}
            >
              {overall.classes_needed}
            </span>
            <span className="text-xs text-slate-500">consecutive</span>
          </div>
          <p className="text-xs text-slate-600 mt-2">
            {overall.classes_needed === 0
              ? "On track! No recovery classes needed."
              : `Attend the next ${overall.classes_needed} classes without absence to reach ${overall.target_percentage}%.`}
          </p>
        </div>
      </div>

      {/* Subject-Wise Attendance Breakdown Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="font-bold text-slate-900 text-lg">Subject-Wise Attendance</h2>
            <p className="text-xs text-slate-500">
              Sorted by risk priority (High risk subjects appear first)
            </p>
          </div>
          <Link
            href="/subjects"
            className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1"
          >
            Manage Subjects & Targets <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-500 text-xs font-semibold uppercase tracking-wider border-b border-slate-200">
              <tr>
                <th className="py-3.5 px-4">Subject</th>
                <th className="py-3.5 px-4">Conducted</th>
                <th className="py-3.5 px-4">Attended</th>
                <th className="py-3.5 px-4">Current %</th>
                <th className="py-3.5 px-4">Predicted %</th>
                <th className="py-3.5 px-4">Safe Bunks</th>
                <th className="py-3.5 px-4">Needed</th>
                <th className="py-3.5 px-4">Risk Status</th>
                <th className="py-3.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {subjects.map((sub) => (
                <tr key={sub.subject_id} className="hover:bg-slate-50/70 transition-colors">
                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-2.5">
                      <div
                        className="w-3 h-3 rounded-full shrink-0"
                        style={{ backgroundColor: sub.color }}
                      />
                      <div>
                        <span className="font-semibold text-slate-900 block leading-tight">
                          {sub.subject_code}
                        </span>
                        <span className="text-xs text-slate-500 block truncate max-w-xs">
                          {sub.subject_name} • {sub.subject_type}
                        </span>
                      </div>
                    </div>
                  </td>
                  <td className="py-3.5 px-4 text-slate-600">{sub.classes_conducted}</td>
                  <td className="py-3.5 px-4 font-medium text-slate-900">{sub.classes_attended}</td>
                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-2">
                      <span
                        className={`font-bold ${
                          sub.is_shortage ? "text-red-600" : "text-slate-900"
                        }`}
                      >
                        {sub.current_percentage}%
                      </span>
                      <span className="text-[11px] text-slate-400">({sub.target_percentage}%)</span>
                    </div>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="font-semibold text-blue-600">
                      {sub.predicted_final_percentage}%
                    </span>
                  </td>
                  <td className="py-3.5 px-4 font-semibold">
                    <span className={sub.safe_bunks > 0 ? "text-emerald-600" : "text-slate-400"}>
                      {sub.safe_bunks}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 font-semibold">
                    <span className={sub.classes_needed > 0 ? "text-red-600 font-bold" : "text-slate-400"}>
                      {sub.classes_needed}
                    </span>
                  </td>
                  <td className="py-3.5 px-4">
                    <RiskBadge level={sub.risk_level} />
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      {sub.classes_needed > 0 ? (
                        <Link
                          href={`/recovery?subject=${sub.subject_id}`}
                          className="px-2.5 py-1 text-xs font-semibold bg-red-50 text-red-700 hover:bg-red-100 rounded-lg transition"
                        >
                          Recover
                        </Link>
                      ) : (
                        <Link
                          href={`/simulator?subject=${sub.subject_id}`}
                          className="px-2.5 py-1 text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 rounded-lg transition"
                        >
                          Simulate
                        </Link>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Two Column Grid: Today's Classes & Explainable Risk Factors */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Today's Classes from Timetable */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center mb-4">
              <div className="flex items-center gap-2">
                <Clock className="w-5 h-5 text-blue-600" />
                <h3 className="font-bold text-slate-900 text-base">Today&apos;s Scheduled Classes</h3>
              </div>
              <Link href="/timetable" className="text-xs text-blue-600 hover:underline">
                View Timetable
              </Link>
            </div>

            {upcoming_classes_today.length === 0 ? (
              <div className="text-center py-8 text-slate-400 text-sm">
                No classes scheduled for today. Enjoy your day!
              </div>
            ) : (
              <div className="space-y-3">
                {upcoming_classes_today.map((c, i) => (
                  <div
                    key={i}
                    className="p-3.5 rounded-xl border border-slate-100 bg-slate-50 flex items-center justify-between"
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className="w-2.5 h-10 rounded-full"
                        style={{ backgroundColor: c.subject_color || "#3b82f6" }}
                      />
                      <div>
                        <span className="font-bold text-slate-900 text-sm block">
                          {c.subject_code} • {c.subject_name}
                        </span>
                        <span className="text-xs text-slate-500">
                          {c.start_time} - {c.end_time} • {c.room || "LH"} ({c.periods_count} period)
                        </span>
                      </div>
                    </div>
                    <Link
                      href="/attendance"
                      className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold transition"
                    >
                      Mark
                    </Link>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="pt-4 mt-4 border-t border-slate-100 flex justify-between items-center text-xs text-slate-500">
            <span>Timetable synced with weekly schedule</span>
            <Link href="/attendance" className="font-semibold text-blue-600 hover:underline">
              Batch Mark All Attendance →
            </Link>
          </div>
        </div>

        {/* Explainable Decision-Support Factors */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <Info className="w-5 h-5 text-indigo-600" />
            <h3 className="font-bold text-slate-900 text-base">Explainable Attendance Analysis</h3>
          </div>

          <div className="space-y-2.5">
            {explanation_factors.map((factor, index) => (
              <div key={index} className="flex items-start gap-2.5 text-xs text-slate-700 leading-relaxed bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                <span className="w-5 h-5 rounded-full bg-indigo-100 text-indigo-700 font-bold flex items-center justify-center shrink-0 text-[10px]">
                  {index + 1}
                </span>
                <span>{factor}</span>
              </div>
            ))}
          </div>

          <div className="mt-5 p-3.5 rounded-xl bg-blue-50/70 border border-blue-100">
            <span className="text-xs font-bold text-blue-900 block mb-1">
              Personalized Recommendation
            </span>
            <p className="text-xs text-blue-800 leading-relaxed">
              Prioritize attendance in <strong>CS602 (DBMS)</strong> to erase your 8-class deficit before the semester midpoint. Avoid any bunks in <strong>CS604</strong> as you only have 1 safe bunk remaining.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
