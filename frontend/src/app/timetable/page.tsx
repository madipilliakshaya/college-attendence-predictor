"use client";

import React, { useState, useEffect } from "react";
import { Clock, Plus, Trash2, FileText, CheckCircle2 } from "lucide-react";
import { api } from "@/lib/api";
import { TimetableSlot, SubjectItem } from "@/lib/types";

export default function TimetablePage() {
  const [timetables, setTimetables] = useState<TimetableSlot[]>([]);
  const [subjects, setSubjects] = useState<SubjectItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Add slot modal state
  const [showAddModal, setShowAddModal] = useState(false);
  const [newSubjId, setNewSubjId] = useState("");
  const [newDay, setNewDay] = useState(0);
  const [newStartTime, setNewStartTime] = useState("09:00");
  const [newEndTime, setNewEndTime] = useState("10:00");
  const [newRoom, setNewRoom] = useState("LH-201");
  const [newPeriods, setNewPeriods] = useState(1);

  // OCR Import modal
  const [showOcrModal, setShowOcrModal] = useState(false);
  const [ocrText, setOcrText] = useState(
    "Mon 09:00-10:00 CS601 LH-201\nMon 10:00-11:00 CS602 LH-201\nTue 09:00-10:00 CS604 LH-202"
  );
  const [importing, setImporting] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [tData, sData] = await Promise.all([api.getTimetables(), api.getSubjects()]);
      setTimetables(tData);
      setSubjects(sData);
      if (sData.length > 0 && !newSubjId) setNewSubjId(sData[0].id);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSlot = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createTimetableSlot({
        subject_id: newSubjId,
        day_of_week: Number(newDay),
        start_time: newStartTime,
        end_time: newEndTime,
        room: newRoom,
        periods_count: Number(newPeriods),
      });
      setShowAddModal(false);
      await loadData();
    } catch (err: any) {
      alert(err.message || "Failed to create timetable slot");
    }
  };

  const handleDeleteSlot = async (id: string) => {
    if (!confirm("Are you sure you want to remove this timetable slot?")) return;
    try {
      await api.deleteTimetableSlot(id);
      setTimetables((prev) => prev.filter((t) => t.id !== id));
    } catch (err: any) {
      alert(err.message || "Failed to remove slot");
    }
  };

  const handleOcrImport = async () => {
    try {
      setImporting(true);
      const res = await api.importTimetableText(ocrText);
      alert(`Imported ${res.imported_entries} timetable slots successfully!`);
      setShowOcrModal(false);
      await loadData();
    } catch (err: any) {
      alert(err.message || "Failed to parse timetable text");
    } finally {
      setImporting(false);
    }
  };

  const daysOfWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <Clock className="w-6 h-6 text-blue-600" /> Weekly Class Schedule
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Weekly recurring schedule used by the prediction engine to calculate exact remaining classes in the semester.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowOcrModal(true)}
            className="inline-flex items-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition"
          >
            <FileText className="w-4 h-4" /> Quick Import / OCR
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-sm transition"
          >
            <Plus className="w-4 h-4" /> Add Class Slot
          </button>
        </div>
      </div>

      {/* Timetable Days Grid */}
      <div className="space-y-4">
        {daysOfWeek.map((dayName, dayIndex) => {
          const slotsForDay = timetables.filter((t) => t.day_of_week === dayIndex);

          return (
            <div
              key={dayIndex}
              className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm"
            >
              <div className="flex justify-between items-center mb-3 border-b border-slate-100 pb-2">
                <span className="font-bold text-slate-800 text-sm flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-blue-600" />
                  {dayName}
                </span>
                <span className="text-xs text-slate-400 font-medium">
                  {slotsForDay.length} session{slotsForDay.length !== 1 ? "s" : ""}
                </span>
              </div>

              {slotsForDay.length === 0 ? (
                <p className="text-xs text-slate-400 py-3 italic">No classes scheduled on {dayName}.</p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {slotsForDay.map((slot) => (
                    <div
                      key={slot.id}
                      className="p-3.5 rounded-xl border border-slate-100 bg-slate-50 flex items-start justify-between gap-3 relative overflow-hidden"
                    >
                      <div
                        className="absolute left-0 top-0 bottom-0 w-1"
                        style={{ backgroundColor: slot.subject_color || "#3b82f6" }}
                      />

                      <div className="pl-1">
                        <span className="font-bold text-slate-900 text-xs block">
                          {slot.subject_code} • {slot.subject_name}
                        </span>
                        <span className="text-xs text-blue-600 font-semibold mt-1 block">
                          {slot.start_time} - {slot.end_time}
                        </span>
                        <span className="text-[11px] text-slate-500 block mt-0.5">
                          Room: {slot.room || "LH"} ({slot.periods_count} period{slot.periods_count > 1 ? "s" : ""})
                        </span>
                      </div>

                      <button
                        onClick={() => handleDeleteSlot(slot.id)}
                        className="p-1 text-slate-400 hover:text-red-600 transition"
                        title="Delete slot"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Add Slot Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl border border-slate-100 animate-in fade-in zoom-in-95">
            <h3 className="text-lg font-bold text-slate-900 mb-4">Add Weekly Schedule Slot</h3>
            <form onSubmit={handleCreateSlot} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Subject</label>
                <select
                  value={newSubjId}
                  onChange={(e) => setNewSubjId(e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:ring-2 focus:ring-blue-500"
                >
                  {subjects.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.code} - {s.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Day of Week</label>
                  <select
                    value={newDay}
                    onChange={(e) => setNewDay(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:ring-2 focus:ring-blue-500"
                  >
                    {daysOfWeek.map((d, i) => (
                      <option key={i} value={i}>{d}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Room / Lab</label>
                  <input
                    type="text"
                    required
                    value={newRoom}
                    onChange={(e) => setNewRoom(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Start Time (HH:MM)</label>
                  <input
                    type="text"
                    pattern="^\d{2}:\d{2}$"
                    required
                    placeholder="09:00"
                    value={newStartTime}
                    onChange={(e) => setNewStartTime(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">End Time (HH:MM)</label>
                  <input
                    type="text"
                    pattern="^\d{2}:\d{2}$"
                    required
                    placeholder="10:00"
                    value={newEndTime}
                    onChange={(e) => setNewEndTime(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Periods Count</label>
                <input
                  type="number"
                  min={1}
                  max={4}
                  required
                  value={newPeriods}
                  onChange={(e) => setNewPeriods(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 border border-slate-200 text-slate-600 text-xs font-semibold rounded-lg hover:bg-slate-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg transition"
                >
                  Save Slot
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Quick OCR / Text Parser Modal */}
      {showOcrModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl p-6 max-w-lg w-full shadow-2xl border border-slate-100 animate-in fade-in zoom-in-95">
            <h3 className="text-lg font-bold text-slate-900 mb-2">Schedule Text & OCR Importer</h3>
            <p className="text-xs text-slate-500 mb-4">
              Paste lines formatted as: <code className="bg-slate-100 px-1 py-0.5 rounded font-mono">Day Start-End Code Room</code>
            </p>

            <textarea
              rows={6}
              value={ocrText}
              onChange={(e) => setOcrText(e.target.value)}
              className="w-full p-3 font-mono text-xs border border-slate-200 rounded-xl text-slate-800 focus:ring-2 focus:ring-blue-500"
            />

            <div className="flex justify-end gap-2 pt-3 border-t border-slate-100 mt-4">
              <button
                type="button"
                onClick={() => setShowOcrModal(false)}
                className="px-4 py-2 border border-slate-200 text-slate-600 text-xs font-semibold rounded-lg hover:bg-slate-50 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleOcrImport}
                disabled={importing}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg transition disabled:opacity-50"
              >
                {importing ? "Importing..." : "Parse & Import"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
