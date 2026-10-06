"use client";

import React, { useState, useEffect } from "react";
import { Settings, Save, CheckCircle, ShieldCheck } from "lucide-react";
import { api } from "@/lib/api";
import { StudentProfile } from "@/lib/types";

export default function SettingsPage() {
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  // Form fields
  const [rollNumber, setRollNumber] = useState("");
  const [department, setDepartment] = useState("");
  const [semester, setSemester] = useState(6);
  const [collegeName, setCollegeName] = useState("");
  const [defaultTarget, setDefaultTarget] = useState(75.0);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const p = await api.getProfile();
      setProfile(p);
      setRollNumber(p.roll_number);
      setDepartment(p.department);
      setSemester(p.semester);
      setCollegeName(p.college_name);
      setDefaultTarget(p.default_attendance_target);
      setStartDate(p.semester_start_date);
      setEndDate(p.semester_end_date);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      setSavedSuccess(false);
      const updated = await api.updateProfile({
        roll_number: rollNumber,
        department,
        semester: Number(semester),
        college_name: collegeName,
        default_attendance_target: Number(defaultTarget),
        semester_start_date: startDate,
        semester_end_date: endDate,
      });
      setProfile(updated);
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err: any) {
      alert(err.message || "Failed to save profile settings");
    } finally {
      setSaving(false);
    }
  };

  if (loading || !profile) {
    return <div className="p-12 text-center text-slate-400 text-sm">Loading settings...</div>;
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <Settings className="w-6 h-6 text-blue-600" /> Academic Rules & Student Settings
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Configure your college attendance threshold, department rules, and semester start/end dates.
          </p>
        </div>
      </div>

      <form onSubmit={handleSave} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
        {savedSuccess && (
          <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold rounded-xl flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-emerald-600" /> Profile and institutional attendance rules updated successfully!
          </div>
        )}

        {/* Section 1: Institutional Target */}
        <div>
          <h3 className="text-sm font-bold text-slate-900 mb-1 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-blue-600" /> Institutional Minimum Target Rule
          </h3>
          <p className="text-xs text-slate-500 mb-4">
            The baseline attendance required by your university/institution. (Configurable; does not enforce hardcoded 75%).
          </p>

          <div className="max-w-xs">
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              College Attendance Target (%)
            </label>
            <div className="flex items-center gap-2">
              <input
                type="number"
                step="0.5"
                min="50"
                max="100"
                required
                value={defaultTarget}
                onChange={(e) => setDefaultTarget(Number(e.target.value))}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 font-bold focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-sm font-bold text-slate-500">%</span>
            </div>
          </div>
        </div>

        {/* Section 2: Student Academic Info */}
        <div className="pt-4 border-t border-slate-100">
          <h3 className="text-sm font-bold text-slate-900 mb-3">Student & Department Credentials</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Roll / Register Number</label>
              <input
                type="text"
                required
                value={rollNumber}
                onChange={(e) => setRollNumber(e.target.value)}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">College Name</label>
              <input
                type="text"
                required
                value={collegeName}
                onChange={(e) => setCollegeName(e.target.value)}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Department</label>
              <input
                type="text"
                required
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Semester</label>
              <input
                type="number"
                min="1"
                max="10"
                required
                value={semester}
                onChange={(e) => setSemester(Number(e.target.value))}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Section 3: Semester Calendar Horizon */}
        <div className="pt-4 border-t border-slate-100">
          <h3 className="text-sm font-bold text-slate-900 mb-1">Semester Calendar Horizon</h3>
          <p className="text-xs text-slate-500 mb-3">
            Determines the remaining days and scheduled classes between today and final examinations.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-lg">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Semester Start Date</label>
              <input
                type="date"
                required
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Semester End Date</label>
              <input
                type="date"
                required
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        <div className="pt-4 border-t border-slate-100 flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-sm transition disabled:opacity-50"
          >
            <Save className="w-4 h-4" /> {saving ? "Saving Changes..." : "Save Settings"}
          </button>
        </div>
      </form>
    </div>
  );
}
