"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  CalendarCheck,
  CalendarDays,
  BookOpen,
  Clock,
  Sparkles,
  Sliders,
  TrendingUp,
  Settings,
  Bell,
  Menu,
  X,
  GraduationCap,
  ShieldCheck,
  Check
} from "lucide-react";
import { api } from "@/lib/api";
import { NotificationItem } from "@/lib/types";

export default function Navigation() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    loadNotifications();
  }, [pathname]);

  const loadNotifications = async () => {
    try {
      const items = await api.getNotifications();
      setNotifications(items);
      setUnreadCount(items.filter((n) => !n.is_read).length);
    } catch {
      // Ignore initial unhandled fetch error
    }
  };

  const handleMarkAsRead = async (id: string) => {
    try {
      await api.markNotificationRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      setUnreadCount((c) => Math.max(0, c - 1));
    } catch (e) {
      console.error(e);
    }
  };

  const navLinks = [
    { href: "/", label: "Dashboard", icon: LayoutDashboard },
    { href: "/attendance", label: "Attendance Logs", icon: CalendarCheck },
    { href: "/attendance/calendar", label: "Calendar View", icon: CalendarDays },
    { href: "/subjects", label: "Subjects", icon: BookOpen },
    { href: "/timetable", label: "Timetable", icon: Clock },
    { href: "/predict", label: "Predictor & ML", icon: Sparkles },
    { href: "/simulator", label: "What-If Simulator", icon: Sliders },
    { href: "/recovery", label: "Recovery Planner", icon: ShieldCheck },
    { href: "/analytics", label: "Analytics", icon: TrendingUp },
    { href: "/settings", label: "Rules & Settings", icon: Settings },
  ];

  return (
    <nav className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center space-x-3">
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
                <GraduationCap className="w-6 h-6" />
              </div>
              <div>
                <span className="font-bold text-lg text-slate-900 tracking-tight block leading-tight">
                  ATTENDANCE PREDICTOR
                </span>
                <span className="text-xs text-blue-600 font-medium tracking-wide">
                  Decision Support System
                </span>
              </div>
            </Link>
          </div>

          {/* Desktop Navigation Links */}
          <div className="hidden lg:flex items-center space-x-1">
            {navLinks.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-blue-50 text-blue-700"
                      : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? "text-blue-600" : "text-slate-400"}`} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>

          {/* Right Header Area: Notifications & User */}
          <div className="flex items-center space-x-3">
            {/* Notification Bell */}
            <div className="relative">
              <button
                onClick={() => setNotificationsOpen(!notificationsOpen)}
                className="p-2 rounded-lg text-slate-500 hover:text-slate-700 hover:bg-slate-100 relative focus:outline-none"
                aria-label="Notifications"
              >
                <Bell className="w-5 h-5" />
                {unreadCount > 0 && (
                  <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center animate-pulse">
                    {unreadCount}
                  </span>
                )}
              </button>

              {/* Notification Dropdown */}
              {notificationsOpen && (
                <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-white rounded-xl shadow-xl border border-slate-200 py-2 z-50">
                  <div className="px-4 py-2 border-b border-slate-100 flex justify-between items-center">
                    <span className="font-semibold text-slate-800 text-sm">
                      Attendance Alerts & Notifications
                    </span>
                    <span className="text-xs text-slate-400">
                      {unreadCount} unread
                    </span>
                  </div>
                  <div className="max-h-80 overflow-y-auto divide-y divide-slate-100">
                    {notifications.length === 0 ? (
                      <div className="p-4 text-center text-sm text-slate-500">
                        No active alerts.
                      </div>
                    ) : (
                      notifications.map((n) => (
                        <div
                          key={n.id}
                          className={`p-3 text-sm transition-colors ${
                            n.is_read ? "bg-white" : "bg-blue-50/50"
                          }`}
                        >
                          <div className="flex justify-between items-start gap-2">
                            <div>
                              <p className="font-medium text-slate-900 text-xs sm:text-sm">
                                {n.title}
                              </p>
                              <p className="text-xs text-slate-600 mt-0.5 leading-relaxed">
                                {n.message}
                              </p>
                            </div>
                            {!n.is_read && (
                              <button
                                onClick={() => handleMarkAsRead(n.id)}
                                title="Mark as read"
                                className="p-1 text-slate-400 hover:text-blue-600 shrink-0"
                              >
                                <Check className="w-4 h-4" />
                              </button>
                            )}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Student Profile Pill */}
            <div className="hidden sm:flex items-center space-x-2 pl-2 border-l border-slate-200">
              <div className="w-8 h-8 rounded-full bg-slate-800 text-white flex items-center justify-center text-xs font-bold">
                AS
              </div>
              <div className="text-left text-xs leading-tight">
                <span className="block font-semibold text-slate-800">Aarav Sharma</span>
                <span className="block text-slate-400">23IT4012 • Sem 6</span>
              </div>
            </div>

            {/* Mobile hamburger button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 rounded-lg text-slate-500 hover:bg-slate-100 focus:outline-none"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-t border-slate-200 bg-white px-4 pt-2 pb-4 space-y-1">
          {navLinks.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center space-x-2 px-3 py-2.5 rounded-lg text-sm font-medium ${
                  isActive
                    ? "bg-blue-50 text-blue-700 font-semibold"
                    : "text-slate-600 hover:bg-slate-50"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-blue-600" : "text-slate-400"}`} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </div>
      )}
    </nav>
  );
}
