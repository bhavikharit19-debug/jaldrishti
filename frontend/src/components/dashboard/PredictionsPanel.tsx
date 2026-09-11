'use client';
import React, { useEffect, useState } from 'react';
import { PredictionResponse } from '@/types';
import { api } from '@/services/api';
import { Cpu, Info, AlertCircle, TrendingUp, Calendar, ShieldCheck } from 'lucide-react';

interface PredictionsPanelProps {
  watershedId: number;
}

/**
 * PredictionsPanel
 * 
 * Government-grade Predictive Assessment Module:
 * Displays indicator outlooks, projected metrics, 95% confidence intervals,
 * and biophysical contributing factors without marketing/AI hype.
 */
export const PredictionsPanel: React.FC<PredictionsPanelProps> = ({ watershedId }) => {
  const [data, setData] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    api.getPredictions(watershedId)
      .then((res) => {
        if (isMounted) setData(res);
      })
      .catch((err) => console.error('Failed to load predictions:', err))
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [watershedId]);

  return (
    <div className="bg-white p-4 sm:p-5 rounded border border-slate-300 shadow-xs space-y-4 select-none">
      {/* Module Title Header */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-3">
        <div className="flex items-center space-x-2">
          <Cpu className="h-4 w-4 text-blue-900" />
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
            Watershed Predictive Assessment
          </h3>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-[10px] font-mono font-bold text-blue-900 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
            PROTOTYPE HORIZON: 6 MONTHS
          </span>
        </div>
      </div>

      {loading ? (
        <div className="h-32 flex items-center justify-center text-xs text-slate-500">
          Calculating statistical projections...
        </div>
      ) : data?.predictions && data.predictions.length > 0 ? (
        <div className="space-y-4">
          {/* Institutional Data Table */}
          <div className="overflow-x-auto border border-slate-200 rounded">
            <table className="w-full text-left text-xs text-slate-800 divide-y divide-slate-200">
              <thead className="bg-slate-50 text-[10px] font-bold text-slate-600 uppercase tracking-wider">
                <tr>
                  <th className="py-2.5 px-3">Target Indicator</th>
                  <th className="py-2.5 px-3">Horizon</th>
                  <th className="py-2.5 px-3">Projected Value</th>
                  <th className="py-2.5 px-3">Risk Interpretation</th>
                  <th className="py-2.5 px-3">95% Confidence Interval</th>
                  <th className="py-2.5 px-3">Input Indicators Used</th>
                  <th className="py-2.5 px-3">Contributing Rationale</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 text-xs">
                {data.predictions.map((pred) => {
                  const riskInterpretation =
                    pred.predicted_value < 0.35 || pred.predicted_value > 75
                      ? { label: 'ELEVATED STRESS', color: 'bg-red-50 text-red-900 border-red-300' }
                      : pred.predicted_value < 0.5 || pred.predicted_value > 50
                      ? { label: 'MODERATE CONCERN', color: 'bg-amber-50 text-amber-900 border-amber-300' }
                      : { label: 'STABLE PROJECTION', color: 'bg-emerald-50 text-emerald-900 border-emerald-300' };

                  return (
                    <tr key={pred.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-2.5 px-3 font-bold text-slate-900 font-mono">
                        <div>{pred.target_metric.replace(/_/g, ' ')}</div>
                        <span className="text-[9px] text-slate-400 font-mono">
                          {pred.model_name || 'Ridge Regression v1.0'}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 whitespace-nowrap">
                        <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold bg-slate-100 text-slate-800 border border-slate-300">
                          +{pred.prediction_horizon_months} Months
                        </span>
                      </td>
                      <td className="py-2.5 px-3 font-mono font-bold text-blue-950 text-sm">
                        {pred.predicted_value}
                      </td>
                      <td className="py-2.5 px-3 whitespace-nowrap">
                        <span className={`px-1.5 py-0.5 rounded text-[10px] font-extrabold border ${riskInterpretation.color}`}>
                          {riskInterpretation.label}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 font-mono text-[11px] text-slate-700 whitespace-nowrap">
                        <div>[{pred.confidence_lower} — {pred.confidence_upper}]</div>
                        <span className="text-[10px] text-slate-400">
                          Score: {Math.round(pred.confidence_score * 100)}%
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-[11px] text-slate-700 font-mono max-w-[140px]">
                        {pred.features_used?.join(', ') || 'NDVI, SMI, Rainfall, Elevation'}
                      </td>
                      <td className="py-2.5 px-3 text-[11px] text-slate-600 leading-snug max-w-[200px]">
                        {pred.rationale}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Model Provenance & Statutory Guidance */}
          <div className="p-3 bg-slate-50 border border-slate-200 rounded text-xs text-slate-700 flex items-start space-x-2">
            <Info className="h-4 w-4 text-blue-800 mt-0.5 flex-shrink-0" />
            <div className="space-y-0.5 text-[11px]">
              <div>
                <strong className="text-slate-900">Statistical Methodology: </strong>
                <span>{data.model_architecture}</span>
              </div>
              <p className="text-slate-500">
                {data.disclaimer || 'Projections represent statistical decision-support estimations and require on-site DPR ground verification before civil works are sanctioned.'}
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div className="p-4 text-xs text-slate-500 text-center">
          No predictive assessments recorded for this catchment.
        </div>
      )}
    </div>
  );
};
