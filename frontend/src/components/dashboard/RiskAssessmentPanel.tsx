'use client';
import React, { useEffect, useState } from 'react';
import { RiskAssessmentResponse } from '@/types';
import { api } from '@/services/api';
import { ShieldAlert, Info, AlertTriangle } from 'lucide-react';

interface RiskAssessmentPanelProps {
  watershedId: number;
}

/**
 * RiskAssessmentPanel
 * 
 * Government-grade Watershed Risk Assessment Table:
 * Structured matrix evaluating environmental vulnerabilities:
 * Water Stress, Vegetation Degradation, Land Condition, and Runoff Risks.
 */
export const RiskAssessmentPanel: React.FC<RiskAssessmentPanelProps> = ({ watershedId }) => {
  const [data, setData] = useState<RiskAssessmentResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    api.getRisks(watershedId)
      .then((res) => {
        if (isMounted) setData(res);
      })
      .catch((err) => console.error('Failed to load risks:', err))
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [watershedId]);

  const getRiskBadge = (level: string) => {
    switch (level) {
      case 'HIGH':
      case 'CRITICAL':
        return 'bg-red-50 text-red-900 border-red-300';
      case 'MEDIUM':
        return 'bg-amber-50 text-amber-900 border-amber-300';
      default:
        return 'bg-emerald-50 text-emerald-900 border-emerald-300';
    }
  };

  return (
    <div className="bg-white p-4 sm:p-5 rounded border border-slate-300 shadow-xs space-y-4 select-none">
      {/* Module Title Header */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-3">
        <div className="flex items-center space-x-2">
          <ShieldAlert className="h-4 w-4 text-amber-700" />
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
            Watershed Multi-Hazard Risk Assessment
          </h3>
        </div>
        {data && (
          <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${getRiskBadge(data.overall_risk_level)}`}>
            COMPOSITE RISK: {data.overall_risk_level}
          </span>
        )}
      </div>

      {loading ? (
        <div className="h-32 flex items-center justify-center text-xs text-slate-500">
          Synthesizing biophysical risk parameters...
        </div>
      ) : data?.risks && data.risks.length > 0 ? (
        <div className="space-y-3">
          {/* Institutional Risk Matrix Table */}
          <div className="overflow-x-auto border border-slate-200 rounded">
            <table className="w-full text-left text-xs text-slate-800 divide-y divide-slate-200">
              <thead className="bg-slate-50 text-[10px] font-bold text-slate-600 uppercase tracking-wider">
                <tr>
                  <th className="py-2.5 px-3">Risk Category</th>
                  <th className="py-2.5 px-3">Current Status</th>
                  <th className="py-2.5 px-3">Risk Level</th>
                  <th className="py-2.5 px-3">Biophysical Evidence</th>
                  <th className="py-2.5 px-3">Primary Driver</th>
                  <th className="py-2.5 px-3">Recommended Mitigation</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 text-xs">
                {data.risks.map((risk) => (
                  <tr key={risk.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-2.5 px-3 font-bold text-slate-900 font-mono">
                      {risk.risk_category.replace(/_/g, ' ')}
                    </td>
                    <td className="py-2.5 px-3 font-semibold text-slate-700">
                      {risk.risk_level === 'LOW' ? 'Normal Baseline' : risk.risk_level === 'MEDIUM' ? 'Elevated Stress' : 'Critical Hazard'}
                    </td>
                    <td className="py-2.5 px-3 whitespace-nowrap">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${getRiskBadge(risk.risk_level)}`}>
                        {risk.risk_level}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-[11px] text-slate-600 max-w-[200px] leading-snug">
                      {risk.evidence_summary}
                    </td>
                    <td className="py-2.5 px-3 text-[11px] text-slate-700 font-mono">
                      {risk.primary_driver}
                    </td>
                    <td className="py-2.5 px-3 text-[11px] text-blue-900 font-medium">
                      {risk.risk_category.includes('WATER') ? 'Percolation tanks & farm bunding' : risk.risk_category.includes('VEGETATION') ? 'Afforestation & silvipasture' : 'Contour trenches & gully plugs'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="p-2.5 bg-slate-50 border border-slate-200 rounded text-[11px] text-slate-600 flex items-center space-x-2">
            <Info className="h-4 w-4 text-slate-500 shrink-0" />
            <span>
              Risk indicators are evaluated from multi-temporal Sentinel-2 (NDVI/NDWI) and hydrological flow models. Ratings are updated during bi-weekly raster passes.
            </span>
          </div>
        </div>
      ) : (
        <div className="p-4 text-xs text-slate-500 text-center">
          No hazard risk records catalogued for this catchment.
        </div>
      )}
    </div>
  );
};
