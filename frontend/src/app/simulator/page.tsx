"use client";

import React, { useState, useEffect } from "react";
import { Sliders, Calendar, AlertTriangle, CheckCircle, ArrowRight, ShieldAlert, Sparkles } from "lucide-react";
import { api } from "@/lib/api";
import { SubjectItem, WhatIfResult, AbsenceSimulationResult } from "@/lib/types";
import RiskBadge from "@/components/RiskBadge";

export default function SimulatorPage() {
  const [subjects, setSubjects] = useState<SubjectItem[]>([]);
  const [loading, setLoading] = useState(true);

  // What-If Form
  const [selectedSubjectId, setSelectedSubjectId] = useState<string>("");
  const [missCount, setMissCount] = useState<number>(2);
  const [attendCount, setAttendCount] = useState<number>(0);
  const [whatIfResult, setWhatIfResult] = useState<WhatIfResult | null>(null);
  const [simulating, setSimulating] = useState(false);

  // Planned Absence Form
  const [plannedDates, setPlannedDates] = useState<string>("");
  const [absenceReason, setAbsenceReason] = useState<string>("Family Function");
  const [absenceResult, setAbsenceResult] = useState<AbsenceSimulationResult | null>(null);
  const [evaluatingAbsence, setEvaluatingAbsence] = useState(false);

  useEffect(() => {
    loadSubjects();
  }, []);

  const loadSubjects = async () => {
    try {
      setLoading(true);
      const subs = await api.getSubjects();
      setSubjects(subs);
      // Run initial default what-if simulation for overall
      runWhatIfSimulation(null, 2, 0);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const runWhatIfSimulation = async (subjId: string | null, miss: number, attend: number) => {
    try {
      setSimulating(true);
      const res = await api.runWhatIf({
        subject_id: subjId || undefined,
        miss_classes: Number(miss),
        attend_classes: Number(attend),
      });
      setWhatIfResult(res);
    } catch (err: any) {
      alert(err.message || "Simulation failed");
    } finally {
      setSimulating(false);
    }
  };

  const handleRunAbsenceSimulation = async (e: React.FormEvent) => {
    e.preventDefault();
    const dates = plannedDates
      .split(",")
      .map((d) => d.trim())
      .filter((d) => d.length > 0);

    if (dates.length === 0) {
      alert("Please enter at least one date in YYYY-MM-DD format (comma-separated).");
      return;
    }

    try {
      setEvaluatingAbsence(true);
      const res = await api.runAbsenceSimulation({
        dates,
        reason: absenceReason,
      });
      setAbsenceResult(res);
    } catch (err: any) {
      alert(err.message || "Failed to simulate absences");
    } finally {
      setEvaluatingAbsence(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <Sliders className="w-6 h-6 text-blue-600" /> Attendance Scenario Simulator
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Simulate future attendance outcomes: calculate impact of missed classes and test planned absences against your timetable.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Module 1: Interactive What-If Simulator */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="w-5 h-5 text-blue-600" />
              <h2 className="text-base font-bold text-slate-900">What-If Class Outcome Calculator</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Scope (Subject or Overall)
                </label>
                <select
                  value={selectedSubjectId}
                  onChange={(e) => {
                    setSelectedSubjectId(e.target.value);
                    runWhatIfSimulation(e.target.value || null, missCount, attendCount);
                  }}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Overall Semester Attendance</option>
                  {subjects.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.code} - {s.name} (Target: {s.target_percentage}%)
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                  <span>If I miss future classes:</span>
                  <span className="text-red-600 font-bold">{missCount} classes</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="12"
                  value={missCount}
                  onChange={(e) => {
                    const val = Number(e.target.value);
                    setMissCount(val);
                    runWhatIfSimulation(selectedSubjectId || null, val, attendCount);
                  }}
                  className="w-full accent-red-600 cursor-pointer"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                  <span>And attend future classes:</span>
                  <span className="text-emerald-600 font-bold">{attendCount} classes</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="15"
                  value={attendCount}
                  onChange={(e) => {
                    const val = Number(e.target.value);
                    setAttendCount(val);
                    runWhatIfSimulation(selectedSubjectId || null, missCount, val);
                  }}
                  className="w-full accent-emerald-600 cursor-pointer"
                />
              </div>
            </div>

            {/* Simulation Results Card */}
            {whatIfResult && (
              <div className="mt-6 p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-3">
                <div className="flex justify-between items-center border-b border-slate-200 pb-2">
                  <span className="text-xs font-bold text-slate-800">
                    {whatIfResult.subject_name}
                  </span>
                  <RiskBadge level={whatIfResult.new_risk_level} />
                </div>

                <div className="grid grid-cols-2 gap-3 text-center">
                  <div className="p-3 bg-white rounded-lg border border-slate-100">
                    <span className="text-[10px] text-slate-400 font-bold uppercase block">Current</span>
                    <span className="text-lg font-bold text-slate-800">{whatIfResult.current_percentage}%</span>
                  </div>
                  <div className="p-3 bg-white rounded-lg border border-slate-100">
                    <span className="text-[10px] text-slate-400 font-bold uppercase block">Simulated</span>
                    <span
                      className={`text-lg font-black ${
                        whatIfResult.is_target_met ? "text-emerald-600" : "text-red-600"
                      }`}
                    >
                      {whatIfResult.simulated_percentage}%
                    </span>
                    <span className="text-[10px] text-slate-500 block">
                      ({whatIfResult.percentage_change >= 0 ? "+" : ""}{whatIfResult.percentage_change}%)
                    </span>
                  </div>
                </div>

                <div className="flex justify-between text-xs text-slate-600 pt-1">
                  <span>Safe Bunks Remaining: <strong>{whatIfResult.new_safe_bunks}</strong></span>
                  <span>Classes Needed: <strong className={whatIfResult.new_classes_needed > 0 ? "text-red-600" : ""}>{whatIfResult.new_classes_needed}</strong></span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Module 2: Multi-Day Planned Absence Simulation */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Calendar className="w-5 h-5 text-indigo-600" />
              <h2 className="text-base font-bold text-slate-900">Planned Absence / Leave Simulator</h2>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Enter upcoming dates you plan to take leave. The engine cross-references your weekly timetable to project the exact attendance drop across every scheduled subject.
            </p>

            <form onSubmit={handleRunAbsenceSimulation} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Planned Leave Dates (comma-separated YYYY-MM-DD)
                </label>
                <input
                  type="text"
                  placeholder="2026-10-12, 2026-10-13, 2026-10-14"
                  value={plannedDates}
                  onChange={(e) => setPlannedDates(e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Reason for Absence
                </label>
                <input
                  type="text"
                  placeholder="e.g. Cultural Fest, Medical Appointment"
                  value={absenceReason}
                  onChange={(e) => setAbsenceReason(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <button
                type="submit"
                disabled={evaluatingAbsence}
                className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold transition disabled:opacity-50 shadow-sm"
              >
                {evaluatingAbsence ? "Simulating Leave Impact..." : "Simulate Leave Impact"}
              </button>
            </form>

            {/* Results breakdown */}
            {absenceResult && (
              <div className="mt-5 p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-3">
                <div
                  className={`p-3 rounded-lg text-xs font-semibold ${
                    absenceResult.target_breached
                      ? "bg-red-100 text-red-800 border border-red-200"
                      : "bg-emerald-100 text-emerald-800 border border-emerald-200"
                  }`}
                >
                  {absenceResult.risk_summary}
                </div>

                <div className="text-xs text-slate-600 flex justify-between">
                  <span>Total Periods Missed: <strong>{absenceResult.total_periods_missed}</strong></span>
                  <span>
                    Projected Overall:{" "}
                    <strong className={absenceResult.target_breached ? "text-red-600" : "text-slate-800"}>
                      {absenceResult.overall_projected_percentage}%
                    </strong>
                  </span>
                </div>

                <div className="space-y-1.5 max-h-40 overflow-y-auto pt-1">
                  <span className="text-[10px] uppercase font-bold text-slate-400 block">
                    Impacted Subjects Breakdown
                  </span>
                  {absenceResult.impacted_subjects.map((item) => (
                    <div
                      key={item.subject_id}
                      className="p-2 bg-white rounded border border-slate-100 flex justify-between items-center text-xs"
                    >
                      <span>
                        <strong>{item.subject_code}</strong>: -{item.periods_missed} periods
                      </span>
                      <span className={item.target_breached ? "text-red-600 font-bold" : "text-slate-700"}>
                        {item.current_percentage}% → {item.projected_percentage}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
