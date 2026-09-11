'use client';
import React, { useEffect, useState } from 'react';
import { InterventionItem } from '@/types';
import { api } from '@/services/api';
import { Hammer, CheckCircle2, MapPin, IndianRupee, Users, ArrowRight, ArrowDown } from 'lucide-react';

interface InterventionsPanelProps {
  watershedId: number;
}

/**
 * InterventionsPanel
 * 
 * Intervention Monitoring Module:
 * Displays government-style register of sanctioned structures with
 * physical telemetry timeline: BEFORE → IMPLEMENTATION → AFTER.
 */
export const InterventionsPanel: React.FC<InterventionsPanelProps> = ({ watershedId }) => {
  const [interventions, setInterventions] = useState<InterventionItem[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [loading, setLoading] = useState(false);
  const [selectedIntervention, setSelectedIntervention] = useState<InterventionItem | null>(null);
  const [showObsModal, setShowObsModal] = useState(false);
  const [obsRating, setObsRating] = useState('GOOD');
  const [obsRemarks, setObsRemarks] = useState('');
  const [obsSubmitting, setObsSubmitting] = useState(false);
  const [statusUpdatingId, setStatusUpdatingId] = useState<number | null>(null);

  const fetchInterventions = () => {
    setLoading(true);
    api.getInterventions(watershedId, statusFilter === 'ALL' ? undefined : statusFilter)
      .then((res) => {
        setInterventions(res);
      })
      .catch((err) => console.error('Failed to load interventions:', err))
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchInterventions();
  }, [watershedId, statusFilter]);

  const handleStatusChange = async (intvId: number, newStatus: string) => {
    try {
      setStatusUpdatingId(intvId);
      await api.updateIntervention(intvId, { status: newStatus as any });
      fetchInterventions();
    } catch (e) {
      console.error('Failed to update status:', e);
    } finally {
      setStatusUpdatingId(null);
    }
  };

  const handleLogObservation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedIntervention) return;
    try {
      setObsSubmitting(true);
      await api.createInterventionObservation(selectedIntervention.id, {
        observer_name: 'Field Verification Officer',
        condition_rating: obsRating,
        remarks: obsRemarks || 'Field verification inspection completed.'
      });
      setShowObsModal(false);
      setObsRemarks('');
      fetchInterventions();
    } catch (e) {
      console.error('Failed to log observation:', e);
    } finally {
      setObsSubmitting(false);
    }
  };

  return (
    <div className="bg-white p-4 sm:p-5 rounded border border-slate-300 shadow-xs space-y-4 select-none">
      {/* Module Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 pb-3">
        <div className="flex items-center space-x-2">
          <Hammer className="h-4 w-4 text-amber-800" />
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
            Intervention Management &amp; Impact Monitoring
          </h3>
        </div>
        
        {/* Status Filter Tabs */}
        <div className="flex items-center space-x-1 flex-wrap gap-1">
          {['ALL', 'PROPOSED', 'SANCTIONED', 'WORK_IN_PROGRESS', 'COMPLETED'].map((st) => (
            <button
              key={st}
              type="button"
              onClick={() => setStatusFilter(st)}
              className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase transition-colors ${
                statusFilter === st
                  ? 'bg-blue-900 text-white'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              {st.replace(/_/g, ' ')}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="h-32 flex items-center justify-center text-xs text-slate-500">
          Loading intervention records...
        </div>
      ) : interventions.length > 0 ? (
        <div className="space-y-4">
          {/* Government Monitoring Table */}
          <div className="overflow-x-auto border border-slate-200 rounded">
            <table className="w-full text-left text-xs text-slate-800 divide-y divide-slate-200">
              <thead className="bg-slate-50 text-[10px] font-bold text-slate-600 uppercase tracking-wider">
                <tr>
                  <th className="py-2.5 px-3">Structure / Code</th>
                  <th className="py-2.5 px-3">Location Coordinates</th>
                  <th className="py-2.5 px-3">Sanction Year</th>
                  <th className="py-2.5 px-3">Target Capacity</th>
                  <th className="py-2.5 px-3">Beneficiaries &amp; Cost</th>
                  <th className="py-2.5 px-3">Observed Change</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 text-xs">
                {interventions.map((intv) => (
                  <tr key={intv.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-2.5 px-3 font-bold text-slate-900">
                      <div>{intv.name}</div>
                      <span className="text-[10px] font-mono text-slate-500 font-normal">
                        {intv.code} • {intv.intervention_type.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 font-mono text-[11px] text-slate-600 whitespace-nowrap">
                      {intv.latitude.toFixed(4)}°N, {intv.longitude.toFixed(4)}°E
                    </td>
                    <td className="py-2.5 px-3 font-mono text-[11px] text-slate-700 whitespace-nowrap">
                      {intv.sanction_year}
                    </td>
                    <td className="py-2.5 px-3 font-mono text-[11px] text-slate-900 whitespace-nowrap">
                      {intv.target_capacity_cum} m³
                    </td>
                    <td className="py-2.5 px-3 whitespace-nowrap">
                      <div className="font-semibold text-slate-900">{intv.beneficiary_count} Farmers</div>
                      <div className="font-mono text-[10px] text-slate-500">₹ {(intv.cost_inr / 100000).toFixed(2)} Lakhs</div>
                    </td>
                    <td className="py-2.5 px-3 text-[11px] text-slate-700 max-w-[220px] leading-snug">
                      {intv.observed_change_summary || 'Post-monsoon water holding verified.'}
                    </td>
                    <td className="py-2.5 px-3 whitespace-nowrap">
                      <select
                        value={intv.status}
                        onChange={(e) => handleStatusChange(intv.id, e.target.value)}
                        disabled={statusUpdatingId === intv.id}
                        className="text-[10px] font-bold bg-slate-50 border border-slate-300 rounded px-1.5 py-0.5 text-slate-800"
                      >
                        <option value="PROPOSED">PROPOSED</option>
                        <option value="SANCTIONED">SANCTIONED</option>
                        <option value="WORK_IN_PROGRESS">WORK IN PROGRESS</option>
                        <option value="COMPLETED">COMPLETED</option>
                      </select>
                    </td>
                    <td className="py-2.5 px-3 whitespace-nowrap">
                      <button
                        type="button"
                        onClick={() => {
                          setSelectedIntervention(intv);
                          setShowObsModal(true);
                        }}
                        className="px-2 py-0.5 bg-blue-50 text-blue-900 border border-blue-200 rounded text-[10px] font-bold hover:bg-blue-100"
                      >
                        + Log Inspection
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Timeline Section: BEFORE → IMPLEMENTATION → AFTER */}
          <div className="p-3 bg-slate-50 border border-slate-200 rounded text-xs space-y-2">
            <div className="text-[11px] font-bold text-slate-900 uppercase tracking-wide">
              Physical Telemetry Lifecycle Progression
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-[11px]">
              <div className="p-2 bg-white rounded border border-slate-200">
                <div className="font-bold text-slate-700 uppercase text-[10px]">1. BEFORE INTERVENTION</div>
                <p className="text-slate-600 mt-1">
                  Baseline high runoff coefficient (0.42), seasonal nala drying by January, minimal recharge.
                </p>
              </div>
              <div className="p-2 bg-white rounded border border-slate-200">
                <div className="font-bold text-blue-900 uppercase text-[10px]">2. IMPLEMENTATION &amp; AUDIT</div>
                <p className="text-slate-600 mt-1">
                  Check dams and continuous contour trenches constructed as per technical DPR specifications.
                </p>
              </div>
              <div className="p-2 bg-white rounded border border-slate-200">
                <div className="font-bold text-emerald-800 uppercase text-[10px]">3. AFTER MONITORING</div>
                <p className="text-slate-600 mt-1">
                  Surface water spread sustained through March, localized water table elevation +1.8m.
                </p>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="p-4 text-xs text-slate-500 text-center">
          No intervention structures matching current filter.
        </div>
      )}

      {/* Observation Modal */}
      {showObsModal && selectedIntervention && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 backdrop-blur-xs p-4">
          <div className="bg-white rounded border border-slate-300 shadow-xl max-w-md w-full p-4 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-200 pb-2">
              <h4 className="font-bold text-slate-900 text-xs uppercase tracking-wide">
                Log Field Observation: {selectedIntervention.name}
              </h4>
              <button
                type="button"
                onClick={() => setShowObsModal(false)}
                className="text-slate-400 hover:text-slate-600 text-xs font-bold"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleLogObservation} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Condition Rating
                </label>
                <select
                  value={obsRating}
                  onChange={(e) => setObsRating(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded px-2 py-1.5 font-semibold text-slate-800"
                >
                  <option value="EXCELLENT">EXCELLENT (No siltation, structure sound)</option>
                  <option value="GOOD">GOOD (Operational, minor wear)</option>
                  <option value="MODERATE">MODERATE (Partial siltation / maintenance needed)</option>
                  <option value="CRITICAL">CRITICAL (Damage observed / desiltation urgently required)</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Inspection Remarks / Observations
                </label>
                <textarea
                  rows={3}
                  value={obsRemarks}
                  onChange={(e) => setObsRemarks(e.target.value)}
                  placeholder="Record structure physical integrity, observed water holding, desiltation status..."
                  className="w-full bg-slate-50 border border-slate-300 rounded px-2.5 py-1.5 text-xs text-slate-900"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowObsModal(false)}
                  className="px-3 py-1.5 bg-slate-100 text-slate-700 rounded font-semibold text-xs hover:bg-slate-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={obsSubmitting}
                  className="px-3 py-1.5 bg-blue-900 text-white rounded font-bold text-xs hover:bg-blue-950 disabled:opacity-50"
                >
                  {obsSubmitting ? 'Saving...' : 'Submit Observation'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
