'use client';
import React from 'react';
import { HealthScore } from '@/types';
import { Activity, Droplet, Sprout, Mountain, CheckCircle2 } from 'lucide-react';

interface IndicatorsPanelProps {
  healthScore?: HealthScore;
}

export const IndicatorsPanel: React.FC<IndicatorsPanelProps> = ({ healthScore }) => {
  if (!healthScore) {
    return <div className="p-4 text-xs text-slate-400">Loading indicators...</div>;
  }

  const getIcon = (category: string) => {
    switch (category) {
      case 'VEGETATION':
        return <Sprout className="h-4 w-4 text-emerald-600" />;
      case 'HYDROLOGICAL':
        return <Droplet className="h-4 w-4 text-blue-600" />;
      case 'LAND_CONDITION':
        return <Mountain className="h-4 w-4 text-amber-600" />;
      default:
        return <Activity className="h-4 w-4 text-purple-600" />;
    }
  };

  return (
    <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-4">
      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
        <div className="flex items-center space-x-2">
          <Activity className="h-4 w-4 text-blue-600" />
          <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wide">
            Biophysical & Hydro-Ecological Indicators
          </h3>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full border bg-blue-50 text-blue-700 border-blue-200">
            DEMO BASELINE
          </span>
          <span className="text-xs text-slate-400 hidden sm:inline">Calibrated Earth Observation Indices</span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {healthScore.components.map((comp, idx) => (
          <div
            key={idx}
            className="p-3 bg-slate-50/70 rounded-lg border border-slate-200 flex flex-col justify-between"
          >
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center space-x-2">
                {getIcon(comp.category)}
                <span className="text-xs font-bold text-slate-800">{comp.name}</span>
              </div>
              <span
                className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                  comp.status === 'OPTIMAL'
                    ? 'bg-emerald-100 text-emerald-800'
                    : 'bg-amber-100 text-amber-800'
                }`}
              >
                {comp.status}
              </span>
            </div>

            <p className="text-[11px] text-slate-600 line-clamp-2 mb-2 leading-relaxed">
              {comp.description}
            </p>

            <div className="flex items-center justify-between pt-2 border-t border-slate-200/60 text-xs">
              <span className="text-slate-500 font-medium">Calibrated Rating:</span>
              <span className="font-extrabold text-blue-700">{comp.score} / 100</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
