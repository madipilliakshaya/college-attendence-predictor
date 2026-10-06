"use client";

import React, { useState, useEffect } from "react";
import { BookOpen, Plus, Trash2, Edit2, ShieldAlert } from "lucide-react";
import { api } from "@/lib/api";
import { SubjectItem } from "@/lib/types";

export default function SubjectsPage() {
  const [subjects, setSubjects] = useState<SubjectItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingSubject, setEditingSubject] = useState<SubjectItem | null>(null);

  // Form states
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [subjectType, setSubjectType] = useState("lecture");
  const [credits, setCredits] = useState(3);
  const [durationHours, setDurationHours] = useState(1.0);
  const [targetPercentage, setTargetPercentage] = useState(75.0);
  const [color, setColor] = useState("#3B82F6");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadSubjects();
  }, []);

  const loadSubjects = async () => {
    try {
      setLoading(true);
      const data = await api.getSubjects();
      setSubjects(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenAdd = () => {
    setEditingSubject(null);
    setCode("");
    setName("");
    setSubjectType("lecture");
    setCredits(3);
    setDurationHours(1.0);
    setTargetPercentage(75.0);
    setColor("#3B82F6");
    setShowModal(true);
  };

  const handleOpenEdit = (s: SubjectItem) => {
    setEditingSubject(s);
    setCode(s.code);
    setName(s.name);
    setSubjectType(s.subject_type);
    setCredits(s.credits);
    setDurationHours(s.duration_hours);
    setTargetPercentage(s.target_percentage);
    setColor(s.color);
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      if (editingSubject) {
        await api.updateSubject(editingSubject.id, {
          name,
          subject_type: subjectType,
          credits: Number(credits),
          duration_hours: Number(durationHours),
          target_percentage: Number(targetPercentage),
          color,
        });
      } else {
        await api.createSubject({
          code: code.toUpperCase().trim(),
          name: name.trim(),
          subject_type: subjectType,
          credits: Number(credits),
          duration_hours: Number(durationHours),
          target_percentage: Number(targetPercentage),
          color,
        });
      }
      setShowModal(false);
      await loadSubjects();
    } catch (err: any) {
      alert(err.message || "Failed to save subject.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: string, sCode: string) => {
    if (!confirm(`Are you sure you want to delete ${sCode}? All its attendance records and timetable slots will also be removed!`)) return;
    try {
      await api.deleteSubject(id);
      setSubjects((prev) => prev.filter((s) => s.id !== id));
    } catch (err: any) {
      alert(err.message || "Failed to delete subject.");
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <BookOpen className="w-6 h-6 text-blue-600" /> Subject Configuration & Targets
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Configure lecture vs laboratory weightings, credit allocations, and individual attendance targets (e.g. Labs at 80%).
          </p>
        </div>
        <button
          onClick={handleOpenAdd}
          className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-sm transition"
        >
          <Plus className="w-4 h-4" /> Add New Subject
        </button>
      </div>

      {/* Grid of Subjects */}
      {loading ? (
        <div className="p-12 text-center text-slate-400 text-sm">Loading subjects...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {subjects.map((sub) => (
            <div
              key={sub.id}
              className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow relative overflow-hidden"
            >
              <div
                className="absolute top-0 left-0 right-0 h-1.5"
                style={{ backgroundColor: sub.color }}
              />

              <div>
                <div className="flex justify-between items-start mt-1">
                  <span className="text-xs font-extrabold px-2.5 py-1 rounded-md bg-slate-100 text-slate-800 uppercase tracking-wider">
                    {sub.code}
                  </span>
                  <span className="text-xs font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-full capitalize">
                    {sub.subject_type}
                  </span>
                </div>

                <h3 className="font-bold text-slate-900 text-base mt-2.5 leading-snug">
                  {sub.name}
                </h3>

                <div className="mt-4 grid grid-cols-3 gap-2 p-3 bg-slate-50 rounded-xl text-center border border-slate-100 text-xs">
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-bold">Credits</span>
                    <span className="font-bold text-slate-800">{sub.credits}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-bold">Duration</span>
                    <span className="font-bold text-slate-800">{sub.duration_hours}h</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-bold">Target</span>
                    <span className="font-bold text-blue-600">{sub.target_percentage}%</span>
                  </div>
                </div>
              </div>

              <div className="pt-4 mt-4 border-t border-slate-100 flex justify-end gap-2">
                <button
                  onClick={() => handleOpenEdit(sub)}
                  className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition flex items-center gap-1"
                >
                  <Edit2 className="w-3 h-3" /> Edit
                </button>
                <button
                  onClick={() => handleDelete(sub.id, sub.code)}
                  className="p-1.5 text-slate-400 hover:text-red-600 transition rounded-lg"
                  title="Delete subject"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl border border-slate-100 animate-in fade-in zoom-in-95">
            <h3 className="text-lg font-bold text-slate-900 mb-4">
              {editingSubject ? `Edit Subject: ${editingSubject.code}` : "Add New Subject"}
            </h3>

            <form onSubmit={handleSubmit} className="space-y-4">
              {!editingSubject && (
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Subject Code
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. CS607"
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:ring-2 focus:ring-blue-500 uppercase"
                  />
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Subject Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Cloud Architecture & DevOps"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Type
                  </label>
                  <select
                    value={subjectType}
                    onChange={(e) => setSubjectType(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="lecture">Lecture</option>
                    <option value="lab">Laboratory</option>
                    <option value="tutorial">Tutorial</option>
                    <option value="practical">Practical</option>
                    <option value="extra">Extra Class</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Target %
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    min="50"
                    max="100"
                    required
                    value={targetPercentage}
                    onChange={(e) => setTargetPercentage(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Credits
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="6"
                    required
                    value={credits}
                    onChange={(e) => setCredits(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Session Duration (Hours)
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    min="0.5"
                    max="4.0"
                    required
                    value={durationHours}
                    onChange={(e) => setDurationHours(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Color Tag
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="color"
                    value={color}
                    onChange={(e) => setColor(e.target.value)}
                    className="w-10 h-10 rounded border border-slate-200 cursor-pointer"
                  />
                  <span className="text-xs text-slate-500 font-mono">{color}</span>
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 border border-slate-200 text-slate-600 text-xs font-semibold rounded-lg hover:bg-slate-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg transition disabled:opacity-50"
                >
                  {submitting ? "Saving..." : "Save Subject"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
