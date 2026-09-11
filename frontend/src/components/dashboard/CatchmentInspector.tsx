'use client';
import React, { useState } from 'react';
import {
  WatershedDetail,
  HealthScore,
  AlertItem,
  InterventionItem,
  FieldPhoto
} from '@/types';
import {
  FileText,
  AlertTriangle,
  CheckCircle2,
  Sprout,
  Droplets,
  Mountain,
  Waves,
  ShieldAlert,
  Printer,
  Camera,
  ExternalLink,
  ChevronRight,
  X
} from 'lucide-react';
import Link from 'next/link';

interface CatchmentInspectorProps {
  watershed?: WatershedDetail;
  healthScore?: HealthScore;
  alerts?: AlertItem[];
  interventions?: InterventionItem[];
  photos?: FieldPhoto[];
  onOpenReport?: () => void;
  onOpenPhotoModal?: () => void;
  onSelectTab?: (tab: string) => void;
  onClose?: () => void;
}

/**
 * CatchmentInspector
 * 
 * Right-hand GIS inspector panel for selected catchment/micro-watershed.
 * Displays administrative profile, biophysical indicators, health score,
 * active departmental alerts, and action shortcuts.
 */
export default function CatchmentInspector({
  watershed,
  healthScore,
  alerts = [],
  interventions = [],
  photos = [],
  onOpenReport,
  onOpenPhotoModal,
  onSelectTab,
  onClose
}: CatchmentInspectorProps) {
  if (!watershed) return null;

  const scoreVal = healthScore ? Math.round(healthScore.overall_health_score) : 78;
  const healthCategory = healthScore?.category_rating || 'GOOD';

  const getCompScore = (cat: string, fallback: number) => {
    const comp = healthScore?.components?.find(
      (c) => c.category === cat || c.name.toLowerCase().includes(cat.toLowerCase())
    );
    return comp ? Math.round(comp.score) : fallback;
  };

  // Severity color mapping
  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return 'bg-red-100 text-red-900 border-red-300';
      case 'HIGH':
        return 'bg-amber-100 text-amber-900 border-amber-300';
      case 'MEDIUM':
        return 'bg-blue-100 text-blue-900 border-blue-300';
      default:
        return 'bg-slate-100 text-slate-800 border-slate-300';
    }
  };

  return (
    <aside className="w-80 bg-white border-l border-slate-300 flex flex-col h-full overflow-y-auto text-xs select-none shadow-xs">
      {/* Panel Top Header */}
      <div className="px-3 py-2.5 bg-slate-100 border-b border-slate-300 flex items-center justify-between">
        <div className="flex items-center space-x-1.5">
          <FileText className="h-4 w-4 text-blue-900" />
          <span className="font-bold uppercase tracking-wider text-slate-900 text-[11px]">
            Catchment Inspector
          </span>
        </div>
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="text-slate-400 hover:text-slate-700"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      <div className="p-3 space-y-3">
        {/* 1. Catchment Primary Identity Box */}
        <div className="p-2.5 bg-slate-50 border border-slate-200 rounded">
          <div className="flex items-start justify-between">
            <div>
              <div className="text-[10px] font-mono text-slate-500 font-semibold">
                ID: {watershed.code}
              </div>
              <h3 className="font-bold text-slate-950 text-sm leading-snug">
                {watershed.name}
              </h3>
              <p className="text-[11px] text-slate-600 mt-0.5">
                {watershed.district_name || 'District'}, {watershed.state_name || 'State'}
              </p>
            </div>
            <span className="text-[10px] font-mono bg-blue-100 text-blue-900 px-1.5 py-0.5 rounded font-bold">
              {watershed.area_hectares ? `${watershed.area_hectares.toLocaleString()} ha` : '—'}
            </span>
          </div>
        </div>

        {/* 2. Biophysical Health Score (Government Compact Box) */}
        <div className="p-2.5 bg-white border border-slate-300 rounded shadow-2xs">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[11px] font-bold text-slate-800 uppercase tracking-wide">
              Biophysical Health Score
            </span>
            <span className="text-[10px] font-extrabold uppercase px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-900 border border-emerald-300">
              {healthCategory}
            </span>
          </div>

          <div className="flex items-baseline space-x-2 my-1">
            <span className="text-2xl font-black font-mono text-blue-950">
              {scoreVal}
            </span>
            <span className="text-xs text-slate-500 font-mono">/ 100</span>
          </div>

          {/* Progress Bar with Tricolour/Navy scale */}
          <div className="w-full bg-slate-200 h-2 rounded overflow-hidden mb-2">
            <div
              className={`h-full ${
                scoreVal >= 75
                  ? 'bg-emerald-700'
                  : scoreVal >= 50
                  ? 'bg-amber-600'
                  : 'bg-red-700'
              }`}
              style={{ width: `${scoreVal}%` }}
            />
          </div>

          {/* 4 Core Indicators Grid */}
          <div className="grid grid-cols-2 gap-1.5 text-[10px] pt-1 border-t border-slate-100">
            <div className="p-1.5 bg-slate-50 rounded">
              <div className="text-slate-500 flex items-center space-x-1">
                <Sprout className="h-3 w-3 text-emerald-700" />
                <span>Vegetation</span>
              </div>
              <span className="font-bold text-slate-900 font-mono">
                {getCompScore('vegetation', 78)}/100
              </span>
            </div>
            <div className="p-1.5 bg-slate-50 rounded">
              <div className="text-slate-500 flex items-center space-x-1">
                <Droplets className="h-3 w-3 text-blue-700" />
                <span>Water Spread</span>
              </div>
              <span className="font-bold text-slate-900 font-mono">
                {getCompScore('water', 82)}/100
              </span>
            </div>
            <div className="p-1.5 bg-slate-50 rounded">
              <div className="text-slate-500 flex items-center space-x-1">
                <Waves className="h-3 w-3 text-cyan-700" />
                <span>Soil Moisture</span>
              </div>
              <span className="font-bold text-slate-900 font-mono">
                {getCompScore('soil_moisture', 74)}/100
              </span>
            </div>
            <div className="p-1.5 bg-slate-50 rounded">
              <div className="text-slate-500 flex items-center space-x-1">
                <Mountain className="h-3 w-3 text-amber-700" />
                <span>Runoff Coeff</span>
              </div>
              <span className="font-bold text-slate-900 font-mono">
                {getCompScore('runoff', 79)}/100
              </span>
            </div>
          </div>
        </div>

        {/* 3. Active Departmental Alerts */}
        <div className="p-2.5 bg-white border border-slate-300 rounded shadow-2xs">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-1 text-slate-900 font-bold text-[11px] uppercase tracking-wide">
              <ShieldAlert className="h-3.5 w-3.5 text-amber-700" />
              <span>Departmental Alerts ({alerts.length})</span>
            </div>
            {onSelectTab && (
              <button
                type="button"
                onClick={() => onSelectTab('alerts')}
                className="text-[10px] text-blue-900 font-semibold hover:underline"
              >
                View All
              </button>
            )}
          </div>

          {alerts.length === 0 ? (
            <p className="text-[11px] text-slate-500">No active hazard alerts for this catchment.</p>
          ) : (
            <div className="space-y-1.5">
              {alerts.slice(0, 3).map((al) => (
                <div
                  key={al.id}
                  className="p-1.5 bg-slate-50 rounded border border-slate-200 text-[10px] space-y-0.5"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-900 truncate max-w-[150px]">
                      {al.alert_type.replace(/_/g, ' ')}
                    </span>
                    <span className={`px-1 py-0.2 rounded font-extrabold text-[9px] border ${getSeverityBadge(al.severity)}`}>
                      {al.severity}
                    </span>
                  </div>
                  <p className="text-slate-600 line-clamp-2 leading-tight">
                    {al.trigger_reason}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 4. Monitoring Counts Register */}
        <div className="p-2.5 bg-slate-50 border border-slate-200 rounded">
          <div className="text-[10px] font-bold text-slate-600 uppercase mb-1.5">
            Field &amp; Asset Status
          </div>
          <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
            <div>
              <span className="text-slate-500 text-[10px] block font-sans">Interventions:</span>
              <strong className="text-slate-900 text-xs">{interventions.length} Sites</strong>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] block font-sans">Field Photos:</span>
              <strong className="text-slate-900 text-xs">{photos.length} Verified</strong>
            </div>
          </div>
        </div>

        {/* 5. Primary Action Shortcuts */}
        <div className="space-y-1.5 pt-1">
          <Link
            href={`/reports?id=${watershed.id}`}
            className="w-full py-2 px-3 bg-blue-900 hover:bg-blue-950 text-white rounded text-xs font-bold flex items-center justify-center space-x-1.5 transition-colors shadow-xs"
          >
            <Printer className="h-3.5 w-3.5" />
            <span>Generate Diagnostic Report</span>
          </Link>

          <button
            type="button"
            onClick={onOpenPhotoModal}
            className="w-full py-1.5 px-3 bg-slate-100 hover:bg-slate-200 text-slate-800 border border-slate-300 rounded text-xs font-semibold flex items-center justify-center space-x-1.5 transition-colors"
          >
            <Camera className="h-3.5 w-3.5 text-purple-700" />
            <span>Upload Ground Truth Photo</span>
          </button>
        </div>
      </div>
    </aside>
  );
}
