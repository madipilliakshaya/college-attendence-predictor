"use client";

import React, { useState, useEffect, Suspense } from "react";
import { ShieldCheck, AlertTriangle, CheckCircle, ArrowRight, BookOpen, Target, ListChecks } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { SubjectItem, RecoveryPlan } from "@/lib/types";

// Inner component that uses useSearchParams — must be wrapped in <Suspense>
function RecoveryContent() {
  const searchParams = useSearchParams();
  const initialSubject = searchParams.get("subject") || "overall";

  const [subjects, setSubjects] = useState<SubjectItem[]>([]);
  const [selectedSubjectId, setSelectedSubjectId] = useState<string>(initialSubject);
  const [plan, setPlan] = useState<RecoveryPlan | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSubjects();
  }, []);

  useEffect(() => {
    if (selectedSubjectId) {
      loadRecoveryPlan(selectedSubjectId);
    }
  }, [selectedSubjectId]);

  const loadSubjects = async () => {
    try {
      const subs = await api.getSubjects();
      setSubjects(subs);
    } catch (e) {
      console.error(e);
    }
  };

  const loadRecoveryPlan = async (subjectId: string) => {
    try {
      setLoading(true);
      const res = await api.getRecoveryPlan(subjectId);
      setPlan(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <ShieldCheck className="w-6 h-6 text-blue-600" /> Attendance Recovery Planner
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Actionable, dynamic recovery milestones to lift your attendance back above college eligibility thresholds.
          </p>
        </div>

        {/* Subject switcher */}
        <div className="w-full sm:w-72">
          <select
            value={selectedSubjectId}
            onChange={(e) => setSelectedSubjectId(e.target.value)}
            className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs font-semibold text-slate-800 focus:ring-2 focus:ring-blue-500 bg-white"
          >
            <option value="overall">Overall Attendance</option>
            {subjects.map((s) => (
              <option key={s.id} value={s.id}>
                {s.code} - {s.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading || !plan ? (
        <div className="p-12 text-center text-slate-400 text-sm">Calculating recovery trajectory...</div>
      ) : (
        <div className="space-y-6">
          {/* Status Hero Card */}
          <div
            className={`p-6 rounded-3xl border shadow-sm ${
              plan.is_achievable
                ? plan.classes_needed === 0
                  ? "bg-emerald-50/70 border-emerald-200"
                  : "bg-blue-50/70 border-blue-200"
                : "bg-red-50/70 border-red-200"
            }`}
          >
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500 block mb-1">
                  {plan.subject_name}
                </span>
                <h2 className="text-2xl font-extrabold text-slate-900">
                  {plan.classes_needed === 0
                    ? "Attendance Target Satisfied!"
                    : plan.is_achievable
                    ? `Attend Next ${plan.classes_needed} Consecutive Classes`
                    : "Target Mathematically Unachievable"}
                </h2>
                <p className="text-xs text-slate-600 mt-1">
                  Current: <strong>{plan.current_percentage}%</strong> • Target Requirement: <strong>{plan.target_percentage}%</strong> • Remaining in Term: <strong>{plan.remaining_classes_in_semester} classes</strong>
                </p>
              </div>

              <div className="flex items-center gap-3">
                <div className="p-3 bg-white rounded-2xl border border-slate-200 shadow-sm text-center min-w-[120px]">
                  <span className="text-[10px] text-slate-400 font-bold uppercase block">Max Possible %</span>
                  <span className="text-lg font-black text-slate-900">{plan.max_achievable_percentage}%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Progressive Milestones */}
          {plan.steps.length > 0 && (
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
              <div className="flex items-center gap-2">
                <Target className="w-5 h-5 text-blue-600" />
                <h3 className="font-bold text-slate-900 text-base">Step-by-Step Recovery Milestones</h3>
              </div>

              <div className="space-y-3">
                {plan.steps.map((st) => (
                  <div
                    key={st.step_number}
                    className={`p-4 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
                      st.target_achieved
                        ? "bg-emerald-50/50 border-emerald-200"
                        : "bg-slate-50 border-slate-200"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs shrink-0 ${
                          st.target_achieved
                            ? "bg-emerald-600 text-white"
                            : "bg-slate-200 text-slate-700"
                        }`}
                      >
                        {st.target_achieved ? <CheckCircle className="w-4 h-4" /> : st.step_number}
                      </div>
                      <div>
                        <span className="font-bold text-slate-900 text-sm block">
                          {st.milestone_name}
                        </span>
                        <span className="text-xs text-slate-500 block">{st.notes}</span>
                      </div>
                    </div>

                    <div className="text-right">
                      <span className="text-xs text-slate-400 block text-left sm:text-right">Expected Attendance</span>
                      <span
                        className={`font-black text-base ${
                          st.target_achieved ? "text-emerald-700" : "text-slate-900"
                        }`}
                      >
                        {st.expected_attendance_percentage}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Items Guidance */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <ListChecks className="w-5 h-5 text-indigo-600" />
              <h3 className="font-bold text-slate-900 text-base">Actionable Student Directives</h3>
            </div>
            <ul className="space-y-2">
              {plan.action_items.map((act, i) => (
                <li
                  key={i}
                  className="flex items-start gap-2.5 text-xs text-slate-700 bg-slate-50 p-3 rounded-xl border border-slate-100"
                >
                  <ArrowRight className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                  <span>{act}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

// Page default export — wraps content in Suspense (required by Next.js 14 for useSearchParams)
export default function RecoveryPage() {
  return (
    <Suspense
      fallback={
        <div className="p-12 text-center text-slate-400 text-sm">
          Loading recovery planner...
        </div>
      }
    >
      <RecoveryContent />
    </Suspense>
  );
}
