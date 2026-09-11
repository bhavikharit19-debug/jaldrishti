'use client';
import React, { useState } from 'react';
import { HealthScore } from '@/types';
import { ShieldCheck, Info, ChevronDown, ChevronUp, CheckCircle, AlertTriangle } from 'lucide-react';

interface HealthScoreCardProps {
  healthScore?: HealthScore;
  riskLevel?: string;
  areaHectares?: number;
}

export const HealthScoreCard: React.FC<HealthScoreCardProps> = ({
  healthScore,
  riskLevel = 'LOW',
  areaHectares
}) => {
  const [showBreakdown, setShowBreakdown] = useState(false);

  if (!healthScore) {
    return (
      <div className="bg-white p-4 rounded-xl border border-slate-200 animate-pulse h-28 flex items-center justify-center text-xs text-slate-400">
        Loading Watershed Metrics...
      </div>
    );
  }

  const score = healthScore.overall_health_score;
  const getBadgeColor = (rating: string) => {
    switch (rating) {
      case 'EXCELLENT':
        return 'bg-emerald-100 text-emerald-800 border-emerald-300';
      case 'GOOD':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'VULNERABLE':
        return 'bg-amber-100 text-amber-800 border-amber-300';
      default:
        return 'bg-rose-100 text-rose-800 border-rose-300';
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'LOW':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'MEDIUM':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      default:
        return 'bg-rose-50 text-rose-700 border-rose-200';
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      {/* Top Banner KPI row */}
      <div className="p-4 sm:p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Left: Overall Score Dial */}
        <div className="flex items-center space-x-4">
          <div className="relative flex items-center justify-center">
            <svg className="w-20 h-20 transform -rotate-90">
              <circle
                cx="40"
                cy="40"
                r="32"
                stroke="#e2e8f0"
                strokeWidth="7"
                fill="transparent"
              />
              <circle
                cx="40"
                cy="40"
                r="32"
                stroke={score >= 75 ? '#10b981' : score >= 60 ? '#2563eb' : score >= 45 ? '#f59e0b' : '#ef4444'}
                strokeWidth="7"
                fill="transparent"
                strokeDasharray="201.06"
                strokeDashoffset={201.06 - (201.06 * score) / 100}
                strokeLinecap="round"
                className="transition-all duration-1000 ease-out"
              />
            </svg>
            <div className="absolute flex flex-col items-center">
              <span className="text-xl font-extrabold text-slate-800 tracking-tight leading-none">
                {score}
              </span>
              <span className="text-[10px] text-slate-400 font-bold uppercase">/ 100</span>
            </div>
          </div>

          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-base font-bold text-slate-900">Watershed Health Score</h3>
              <span
                className={`text-[11px] font-bold px-2 py-0.5 rounded-full border ${getBadgeColor(
                  healthScore.category_rating
                )}`}
              >
                {healthScore.category_rating}
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5 max-w-sm">
              Composite index synthesized from vegetation vigor, surface moisture, and structure density.
            </p>
          </div>
        </div>

        {/* Center / Right KPIs */}
        <div className="flex items-center space-x-3 sm:space-x-6">
          <div className="bg-slate-50 px-3.5 py-2 rounded-lg border border-slate-200 text-center min-w-[90px]">
            <span className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider">
              Treated Area
            </span>
            <span className="text-sm font-extrabold text-slate-800">
              {areaHectares ? `${areaHectares.toLocaleString()} ha` : '—'}
            </span>
          </div>

          <div className="bg-slate-50 px-3.5 py-2 rounded-lg border border-slate-200 text-center min-w-[90px]">
            <span className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider">
              Vulnerability
            </span>
            <span
              className={`inline-block text-xs font-bold px-2 py-0.5 rounded border mt-0.5 ${getRiskColor(
                riskLevel
              )}`}
            >
              {riskLevel} RISK
            </span>
          </div>

          <button
            onClick={() => setShowBreakdown(!showBreakdown)}
            className="flex items-center space-x-1.5 px-3 py-2 text-xs font-semibold text-blue-700 bg-blue-50 hover:bg-blue-100 rounded-lg border border-blue-200 transition-colors"
          >
            <span>{showBreakdown ? 'Hide Formula' : 'Formula Breakdown'}</span>
            {showBreakdown ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </button>
        </div>
      </div>

      {/* Expandable Mathematical Breakdown */}
      {showBreakdown && (
        <div className="bg-slate-50/80 p-4 border-t border-slate-200 text-xs">
          <div className="flex items-center justify-between mb-2">
            <span className="font-bold text-slate-700 uppercase tracking-wider">
              Transparent Multi-Criteria Weight Formula
            </span>
            <span className="text-slate-500 italic">Analytical Evaluation Methodology</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2.5">
            {healthScore.components.map((comp, idx) => (
              <div
                key={idx}
                className="bg-white p-2.5 rounded-lg border border-slate-200 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-800 text-[11px]">{comp.name}</span>
                    <span className="font-extrabold text-blue-600 text-xs">{comp.score} / 100</span>
                  </div>
                  <p className="text-[11px] text-slate-500 mt-1 leading-snug">{comp.description}</p>
                </div>
                <div className="flex items-center justify-between mt-2 pt-1 border-t border-slate-100 text-[10px] text-slate-400 font-medium">
                  <span>Weight: {(comp.weight * 100).toFixed(0)}%</span>
                  <span>Contribution: +{comp.weighted_contribution.toFixed(1)} pts</span>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-3 flex items-center space-x-2 text-[11px] text-slate-500 bg-blue-50/60 p-2 rounded border border-blue-100">
            <Info className="h-3.5 w-3.5 text-blue-600 shrink-0" />
            <span>{healthScore.data_source_disclaimer}</span>
          </div>
        </div>
      )}
    </div>
  );
};
