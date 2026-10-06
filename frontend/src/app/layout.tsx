import type { Metadata } from "next";
import "./globals.css";
import Navigation from "@/components/Navigation";

export const metadata: Metadata = {
  title: "College Attendance Predictor | BTech Decision Support System",
  description: "Advanced predictive student attendance management, timetable-aware forecasting, safe-bunk calculation, what-if simulations, and recovery planning.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
        <Navigation />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {children}
        </main>
        <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row justify-between items-center gap-2">
            <span>
              <strong>College Attendance Predictor</strong> • BTech Information Technology Project
            </span>
            <span className="text-slate-400">
              Deterministic Math Engine + Timetable Forecasting + ML Risk Analysis
            </span>
          </div>
        </footer>
      </body>
    </html>
  );
}
