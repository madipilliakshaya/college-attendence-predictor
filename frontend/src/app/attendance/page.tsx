"use client";

import React, { useState, useEffect } from "react";
import {
  CalendarCheck,
  Plus,
  Trash2,
  Filter,
  CheckCircle2,
  XCircle,
  AlertCircle,
  RefreshCw,
  Search
} from "lucide-react";
import { api } from "@/lib/api";
import { AttendanceRecordItem, SubjectItem } from "@/lib/types";

export default function AttendancePage() {
  const [records, setRecords] = useState<AttendanceRecordItem[]>([]);
  const [subjects, setSubjects] = useState<SubjectItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter state
  const [selectedSubject, setSelectedSubject] = useState<string>("");
  const [selectedStatus, setSelectedStatus] = useState<string>("");
  const [searchTerm, setSearchTerm] = useState<string>("");

  // Quick mark form state
  const [showMarkModal, setShowMarkModal] = useState(false);
  const [newSubjectId, setNewSubjectId] = useState("");
  const [newDate, setNewDate] = useState(new Date().toISOString().split("T")[0]);
  const [newStatus, setNewStatus] = useState<"present" | "absent" | "cancelled">("present");
  const [newPeriods, setNewPeriods] = useState(1);
  const [newReason, setNewReason] = useState<string>("none");
  const [newNotes, setNewNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [recs, subs] = await Promise.all([
        api.getAttendanceRecords(),
        api.getSubjects(),
      ]);
      setRecords(recs);
      setSubjects(subs);
      if (subs.length > 0 && !newSubjectId) {
        setNewSubjectId(subs[0].id);
      }
    } catch (err: any) {
      setError(err.message || "Failed to load attendance records.");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRecord = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSubjectId) return;

    try {
      setSubmitting(true);
      await api.createAttendanceRecord({
        subject_id: newSubjectId,
        date: newDate,
        status: newStatus,
        periods_count: Number(newPeriods),
        reason_category: newReason as any,
        notes: newNotes || undefined,
      });
      setShowMarkModal(false);
      setNewNotes("");
      await loadData();
    } catch (err: any) {
      alert(err.message || "Failed to save attendance record.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteRecord = async (id: string) => {
    if (!confirm("Are you sure you want to delete this attendance record?")) return;
    try {
      await api.deleteAttendanceRecord(id);
      setRecords((prev) => prev.filter((r) => r.id !== id));
    } catch (err: any) {
      alert(err.message || "Failed to delete record.");
    }
  };

  // Filtered records
  const filteredRecords = records.filter((r) => {
    if (selectedSubject && r.subject_id !== selectedSubject) return false;
    if (selectedStatus && r.status !== selectedStatus) return false;
    if (searchTerm) {
      const s = searchTerm.toLowerCase();
      const code = (r.subject_code || "").toLowerCase();
      const name = (r.subject_name || "").toLowerCase();
      const notes = (r.notes || "").toLowerCase();
      return code.includes(s) || name.includes(s) || notes.includes(s);
    }
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <CalendarCheck className="w-6 h-6 text-blue-600" /> Attendance History & Logs
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Track daily class attendances, record excused absence reasons, and manage historical sessions.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowMarkModal(true)}
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-sm transition"
          >
            <Plus className="w-4 h-4" /> Mark Attendance
          </button>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto">
          {/* Subject Filter */}
          <select
            value={selectedSubject}
            onChange={(e) => setSelectedSubject(e.target.value)}
            className="px-3 py-2 border border-slate-200 rounded-lg text-xs font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Subjects</option>
            {subjects.map((s) => (
              <option key={s.id} value={s.id}>
                {s.code} - {s.name}
              </option>
            ))}
          </select>

          {/* Status Filter */}
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-3 py-2 border border-slate-200 rounded-lg text-xs font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Statuses</option>
            <option value="present">Present</option>
            <option value="absent">Absent</option>
            <option value="cancelled">Cancelled</option>
          </select>

          {/* Search box */}
          <div className="relative flex-1 sm:w-64">
            <Search className="w-3.5 h-3.5 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              placeholder="Search code, name, notes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-3 py-2 border border-slate-200 rounded-lg text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <span className="text-xs text-slate-400 font-medium whitespace-nowrap">
          Showing {filteredRecords.length} records
        </span>
      </div>

      {/* Records Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-400 text-sm">Loading attendance logs...</div>
        ) : filteredRecords.length === 0 ? (
          <div className="p-12 text-center text-slate-400 text-sm">
            No attendance records match your filter criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-slate-500 text-xs font-semibold uppercase tracking-wider border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-4">Subject</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Periods</th>
                  <th className="py-3 px-4">Absence Reason</th>
                  <th className="py-3 px-4">Notes</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredRecords.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-4 font-medium text-slate-900 whitespace-nowrap">
                      {r.date}
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-2">
                        <div
                          className="w-2.5 h-2.5 rounded-full shrink-0"
                          style={{ backgroundColor: r.subject_color || "#3b82f6" }}
                        />
                        <span className="font-semibold text-slate-900">{r.subject_code}</span>
                        <span className="text-xs text-slate-500 truncate max-w-xs">{r.subject_name}</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      {r.status === "present" && (
                        <span className="inline-flex items-center gap-1 text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full">
                          <CheckCircle2 className="w-3.5 h-3.5" /> Present
                        </span>
                      )}
                      {r.status === "absent" && (
                        <span className="inline-flex items-center gap-1 text-xs font-bold text-red-700 bg-red-50 px-2 py-0.5 rounded-full">
                          <XCircle className="w-3.5 h-3.5" /> Absent
                        </span>
                      )}
                      {r.status === "cancelled" && (
                        <span className="inline-flex items-center gap-1 text-xs font-bold text-slate-600 bg-slate-100 px-2 py-0.5 rounded-full">
                          <AlertCircle className="w-3.5 h-3.5" /> Cancelled
                        </span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-slate-600 font-medium">
                      {r.periods_count} period{r.periods_count > 1 ? "s" : ""}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-600 capitalize">
                      {r.status === "absent" && r.reason_category !== "none" ? (
                        <span className="bg-slate-100 px-2 py-0.5 rounded text-slate-700 font-medium">
                          {r.reason_category.replace("_", " ")}
                        </span>
                      ) : (
                        <span className="text-slate-300">—</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-500 truncate max-w-xs">
                      {r.notes || <span className="text-slate-300">—</span>}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => handleDeleteRecord(r.id)}
                        className="p-1 text-slate-400 hover:text-red-600 transition"
                        title="Delete log"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Mark Attendance Modal */}
      {showMarkModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl border border-slate-100 animate-in fade-in zoom-in-95 duration-150">
            <h3 className="text-lg font-bold text-slate-900 mb-4">Mark Class Attendance</h3>
            <form onSubmit={handleCreateRecord} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Subject</label>
                <select
                  value={newSubjectId}
                  onChange={(e) => setNewSubjectId(e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:ring-2 focus:ring-blue-500"
                >
                  {subjects.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.code} - {s.name} ({s.subject_type})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Date</label>
                  <input
                    type="date"
                    value={newDate}
                    onChange={(e) => setNewDate(e.target.value)}
                    required
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Periods Count</label>
                  <input
                    type="number"
                    min={1}
                    max={4}
                    value={newPeriods}
                    onChange={(e) => setNewPeriods(Number(e.target.value))}
                    required
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Status</label>
                <div className="grid grid-cols-3 gap-2">
                  {(["present", "absent", "cancelled"] as const).map((st) => (
                    <button
                      key={st}
                      type="button"
                      onClick={() => setNewStatus(st)}
                      className={`py-2 text-xs font-bold rounded-lg border capitalize transition ${
                        newStatus === st
                          ? st === "present"
                            ? "bg-emerald-600 text-white border-emerald-600"
                            : st === "absent"
                            ? "bg-red-600 text-white border-red-600"
                            : "bg-slate-700 text-white border-slate-700"
                          : "border-slate-200 text-slate-600 hover:bg-slate-50"
                      }`}
                    >
                      {st}
                    </button>
                  ))}
                </div>
              </div>

              {newStatus === "absent" && (
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Absence Reason Category
                  </label>
                  <select
                    value={newReason}
                    onChange={(e) => setNewReason(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="none">No Specific Reason</option>
                    <option value="illness">Medical / Illness</option>
                    <option value="college_event">Official College Event / Fest</option>
                    <option value="approved_leave">Official Approved Leave (OD)</option>
                    <option value="personal">Personal / Family Reason</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Notes (Optional)
                </label>
                <input
                  type="text"
                  placeholder="e.g. Unit 3 Lab session, Guest lecture"
                  value={newNotes}
                  onChange={(e) => setNewNotes(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowMarkModal(false)}
                  className="px-4 py-2 border border-slate-200 text-slate-600 text-xs font-semibold rounded-lg hover:bg-slate-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg transition disabled:opacity-50"
                >
                  {submitting ? "Saving..." : "Save Record"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
