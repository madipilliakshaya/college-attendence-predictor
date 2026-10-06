import React from "react";
import { AlertTriangle, AlertCircle, CheckCircle } from "lucide-react";
import { RiskLevel } from "@/lib/types";

interface RiskBadgeProps {
  level: RiskLevel;
  className?: string;
  showIcon?: boolean;
}

export default function RiskBadge({ level, className = "", showIcon = true }: RiskBadgeProps) {
  if (level === "HIGH") {
    return (
      <span
        className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-red-100 text-red-800 border border-red-200 ${className}`}
      >
        {showIcon && <AlertCircle className="w-3.5 h-3.5 text-red-600" />}
        <span>HIGH RISK</span>
      </span>
    );
  }

  if (level === "MEDIUM") {
    return (
      <span
        className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-200 ${className}`}
      >
        {showIcon && <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />}
        <span>MEDIUM RISK</span>
      </span>
    );
  }

  return (
    <span
      className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-200 ${className}`}
    >
      {showIcon && <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />}
      <span>LOW RISK</span>
    </span>
  );
}
