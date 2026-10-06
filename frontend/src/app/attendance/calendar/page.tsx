"use client";

import React, { useState, useEffect } from "react";
import { CalendarDays, ChevronLeft, ChevronRight, CheckCircle, XCircle, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";

export default function CalendarPage() {
  const [currentYear, setCurrentYear] = useState(2026);
  const [currentMonth, setCurrentMonth] = useState(9); // September 2026 (matches seeded term)
  const [calendarData, setCalendarData] = useState<Record<string, any>>({});
  const [selectedDay, setSelectedDay] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchCalendarData(currentYear, currentMonth);
  }, [currentYear, currentMonth]);

  const fetchCalendarData = async (year: number, month: number) => {
    try {
      setLoading(true);
      const data = await api.getCalendar(year, month);
      const map: Record<string, any> = {};
      data.forEach((item) => {
        map[item.date] = item;
      });
      setCalendarData(map);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handlePrevMonth = () => {
    if (currentMonth === 1) {
      setCurrentMonth(12);
      setCurrentYear((y) => y - 1);
    } else {
      setCurrentMonth((m) => m - 1);
    }
  };

  const handleNextMonth = () => {
    if (currentMonth === 12) {
      setCurrentMonth(1);
      setCurrentYear((y) => y + 1);
    } else {
      setCurrentMonth((m) => m + 1);
    }
  };

  // Calendar matrix computation
  const daysInMonth = new Date(currentYear, currentMonth, 0).getDate();
  const firstDayIndex = new Date(currentYear, currentMonth - 1, 1).getDay(); // 0 is Sun, 1 is Mon...
  // Shift to start Monday as 0
  const startOffset = (firstDayIndex + 6) % 7;

  const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <CalendarDays className="w-6 h-6 text-blue-600" /> Attendance Calendar
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Visual month-by-month timeline. Click on any date to inspect individual lecture and lab sessions.
          </p>
        </div>

        {/* Month selector controls */}
        <div className="flex items-center gap-2 bg-slate-100 p-1 rounded-xl">
          <button
            onClick={handlePrevMonth}
            className="p-2 rounded-lg text-slate-600 hover:bg-white transition"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="font-bold text-slate-800 text-sm px-4 min-w-[140px] text-center">
            {monthNames[currentMonth - 1]} {currentYear}
          </span>
          <button
            onClick={handleNextMonth}
            className="p-2 rounded-lg text-slate-600 hover:bg-white transition"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calendar Grid */}
        <div className="lg:col-span-2 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          {/* Weekday headers */}
          <div className="grid grid-cols-7 gap-2 text-center text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
            <span>Mon</span>
            <span>Tue</span>
            <span>Wed</span>
            <span>Thu</span>
            <span>Fri</span>
            <span>Sat</span>
            <span>Sun</span>
          </div>

          {/* Days */}
          <div className="grid grid-cols-7 gap-2">
            {/* Empty prefix cells */}
            {Array.from({ length: startOffset }).map((_, i) => (
              <div key={`empty-${i}`} className="h-20 bg-slate-50/50 rounded-xl" />
            ))}

            {/* Days of month */}
            {Array.from({ length: daysInMonth }).map((_, i) => {
              const dayNum = i + 1;
              const dateStr = `${currentYear}-${String(currentMonth).padStart(2, "0")}-${String(dayNum).padStart(2, "0")}`;
              const dayData = calendarData[dateStr];
              const isSelected = selectedDay && selectedDay.date === dateStr;

              let statusColor = "bg-white border-slate-100 hover:border-blue-300";
              if (dayData) {
                if (dayData.absent_count > 0 && dayData.present_count === 0) {
                  statusColor = "bg-red-50/60 border-red-200 hover:border-red-400";
                } else if (dayData.absent_count > 0 && dayData.present_count > 0) {
                  statusColor = "bg-amber-50/60 border-amber-200 hover:border-amber-400";
                } else if (dayData.present_count > 0) {
                  statusColor = "bg-emerald-50/60 border-emerald-200 hover:border-emerald-400";
                }
              }

              return (
                <button
                  key={dateStr}
                  onClick={() => setSelectedDay(dayData || { date: dateStr, sessions: [] })}
                  className={`h-20 p-2 rounded-xl border text-left flex flex-col justify-between transition-all ${statusColor} ${
                    isSelected ? "ring-2 ring-blue-600 border-blue-600 shadow-sm" : ""
                  }`}
                >
                  <span className="font-bold text-xs text-slate-700">{dayNum}</span>

                  {dayData && dayData.total_periods > 0 && (
                    <div className="space-y-0.5">
                      <div className="flex items-center gap-1 text-[10px]">
                        {dayData.present_count > 0 && (
                          <span className="font-semibold text-emerald-700">
                            {dayData.present_count}P
                          </span>
                        )}
                        {dayData.absent_count > 0 && (
                          <span className="font-semibold text-red-700">
                            {dayData.absent_count}A
                          </span>
                        )}
                      </div>
                      <div className="w-full bg-slate-200 h-1 rounded-full overflow-hidden flex">
                        <div
                          className="bg-emerald-500 h-full"
                          style={{
                            width: `${(dayData.present_count / dayData.total_periods) * 100}%`,
                          }}
                        />
                        <div
                          className="bg-red-500 h-full"
                          style={{
                            width: `${(dayData.absent_count / dayData.total_periods) * 100}%`,
                          }}
                        />
                      </div>
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Selected Day Inspector */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <h3 className="font-bold text-slate-900 text-base mb-1">Session Details</h3>
          <p className="text-xs text-slate-500 mb-4">
            {selectedDay ? selectedDay.date : "Click any calendar day to inspect recorded periods"}
          </p>

          {!selectedDay || !selectedDay.sessions || selectedDay.sessions.length === 0 ? (
            <div className="text-center py-12 text-slate-400 text-xs">
              No attendance sessions recorded on this date.
            </div>
          ) : (
            <div className="space-y-3">
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 flex justify-between text-xs">
                <span>Present: <strong>{selectedDay.present_count}</strong></span>
                <span>Absent: <strong className="text-red-600">{selectedDay.absent_count}</strong></span>
                <span>Total: <strong>{selectedDay.total_periods}</strong></span>
              </div>

              {selectedDay.sessions.map((s: any, idx: number) => (
                <div
                  key={idx}
                  className="p-3 rounded-xl border border-slate-100 flex items-start justify-between gap-2"
                >
                  <div className="flex items-start gap-2.5">
                    <div
                      className="w-2.5 h-8 rounded-full shrink-0 mt-0.5"
                      style={{ backgroundColor: s.subject_color }}
                    />
                    <div>
                      <span className="font-bold text-slate-900 text-xs block">
                        {s.subject_code} - {s.subject_name}
                      </span>
                      <span className="text-[11px] text-slate-500">
                        {s.periods} period{s.periods > 1 ? "s" : ""}
                        {s.reason && s.reason !== "none" ? ` • Reason: ${s.reason}` : ""}
                      </span>
                    </div>
                  </div>
                  <div>
                    {s.status === "present" ? (
                      <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full">
                        <CheckCircle className="w-3 h-3" /> P
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-[11px] font-bold text-red-700 bg-red-50 px-2 py-0.5 rounded-full">
                        <XCircle className="w-3 h-3" /> A
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
