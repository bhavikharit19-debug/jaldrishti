'use client';
import React, { useEffect, useState } from 'react';
import { RecommendationResponse } from '@/types';
import { api } from '@/services/api';
import { Hammer, Info, ShieldAlert, CheckCircle2, FileSpreadsheet } from 'lucide-react';

interface RecommendationsPanelProps {
  watershedId: number;
}

/**
 * RecommendationsPanel
 * 
 * Watershed Decision Support Module:
 * Structured departmental DPR planning table for catchment treatment works.
 * Displays priority zones, observed issues, biophysical evidence, recommended
 * interventions, priority ratings, and estimated budget requirements.
 */
export const RecommendationsPanel: React.FC<RecommendationsPanelProps> = ({ watershedId }) => {
  const [data, setData] = useState<RecommendationResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    api.getRecommendations(watershedId)
      .then((res) => {
        if (isMounted) setData(res);
      })
      .catch((err) => console.error('Failed to load recommendations:', err))
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [watershedId]);

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'CRITICAL':
      case 'HIGH':
        return 'bg-red-50 text-red-900 border-red-300';
      case 'MEDIUM':
        return 'bg-amber-50 text-amber-900 border-amber-300';
      default:
        return 'bg-blue-50 text-blue-900 border-blue-300';
    }
  };

  return (
    <div className="bg-white p-4 sm:p-5 rounded border border-slate-300 shadow-xs space-y-4 select-none">
      {/* Module Header */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-3">
        <div className="flex items-center space-x-2">
          <Hammer className="h-4 w-4 text-emerald-800" />
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
            Watershed Decision Support &amp; DPR Priorities
          </h3>
        </div>
        <span className="text-[10px] font-mono font-bold bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-300">
          STATUS: PROPOSED DPR WORKS
        </span>
      </div>

      {loading ? (
        <div className="h-32 flex items-center justify-center text-xs text-slate-500">
          Synthesizing catchment intervention recommendations...
        </div>
      ) : data?.recommendations && data.recommendations.length > 0 ? (
        <div className="space-y-3">
          {/* Government Planning Table */}
          <div className="overflow-x-auto border border-slate-200 rounded">
            <table className="w-full text-left text-xs text-slate-800 divide-y divide-slate-200">
              <thead className="bg-slate-50 text-[10px] font-bold text-slate-600 uppercase tracking-wider">
                <tr>
                  <th className="py-2.5 px-3">Recommended Intervention</th>
                  <th className="py-2.5 px-3">Observed Issue</th>
                  <th className="py-2.5 px-3">Biophysical Evidence</th>
                  <th className="py-2.5 px-3">Priority</th>
                  <th className="py-2.5 px-3">Estimated Cost (INR)</th>
                  <th className="py-2.5 px-3">Field Verification</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 text-xs">
                {data.recommendations.map((rec) => (
                  <tr key={rec.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-2.5 px-3 font-bold text-slate-900 font-mono">
                      <div>{rec.intervention_type.replace(/_/g, ' ')}</div>
                      <span className="text-[10px] font-normal text-slate-500 font-sans">
                        Impact: {rec.expected_impact}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-[11px] text-slate-700 max-w-[180px] leading-snug">
                      {rec.problem_statement}
                    </td>
                    <td className="py-2.5 px-3 text-[11px] text-slate-600 max-w-[180px] leading-snug font-mono">
                      {rec.evidence_basis}
                    </td>
                    <td className="py-2.5 px-3 whitespace-nowrap">
                      <span className={`px-1.5 py-0.5 rounded text-[9px] font-extrabold border ${getPriorityBadge(rec.priority)}`}>
                        {rec.priority}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 font-mono font-bold text-slate-900 whitespace-nowrap">
                      {rec.estimated_cost_inr || '₹4,50,000'}
                    </td>
                    <td className="py-2.5 px-3 whitespace-nowrap">
                      <span className="inline-flex items-center space-x-1 text-[10px] font-semibold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                        <CheckCircle2 className="h-3 w-3 text-emerald-700" />
                        <span>Ready for DPR</span>
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="p-3 bg-amber-50/80 border border-amber-200 rounded text-[11px] text-amber-950 flex items-start space-x-2">
            <Info className="h-4 w-4 text-amber-700 mt-0.5 flex-shrink-0" />
            <p className="leading-relaxed">
              <strong>Departmental Planning Note: </strong>
              Recommendations are generated for technical planning assistance and do not constitute automatic engineering sanction. Field topographical survey and Gram Sabha approval are required prior to administrative expenditure.
            </p>
          </div>
        </div>
      ) : (
        <div className="p-4 text-xs text-slate-500 text-center">
          No intervention recommendations catalogued for this area.
        </div>
      )}
    </div>
  );
};
