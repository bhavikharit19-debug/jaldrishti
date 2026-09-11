'use client';
import React, { useEffect, useState } from 'react';
import { AlertItem } from '@/types';
import { api } from '@/services/api';
import { Bell, AlertTriangle, AlertCircle, CheckCircle, Clock } from 'lucide-react';

interface AlertsPanelProps {
  watershedId: number;
  onAlertUpdated?: () => void;
}

export const AlertsPanel: React.FC<AlertsPanelProps> = ({ watershedId, onAlertUpdated }) => {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  const fetchAlerts = () => {
    setLoading(true);
    api.getAlerts(watershedId)
      .then(setAlerts)
      .catch((err) => console.error('Failed to load alerts:', err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchAlerts();
  }, [watershedId]);

  const handleUpdateStatus = async (alertId: number, status: string) => {
    try {
      await api.updateAlertStatus(alertId, status);
      fetchAlerts();
      if (onAlertUpdated) onAlertUpdated();
    } catch (e) {
      console.error('Failed to update alert:', e);
    }
  };

  const filteredAlerts = alerts.filter((alt) => {
    if (severityFilter !== 'ALL' && alt.severity !== severityFilter) return false;
    if (statusFilter !== 'ALL' && alt.status !== statusFilter) return false;
    return true;
  });

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case 'CRITICAL':
        return 'bg-red-50 text-red-900 border-red-300';
      case 'HIGH':
        return 'bg-amber-50 text-amber-900 border-amber-300';
      case 'MEDIUM':
        return 'bg-blue-50 text-blue-900 border-blue-300';
      default:
        return 'bg-slate-50 text-slate-800 border-slate-300';
    }
  };

  const getRequiredAction = (alertType: string, severity: string) => {
    if (alertType.includes('VEGETATION') || alertType.includes('NDVI')) {
      return 'Initiate participatory ground biomass audit and deploy field officer for geocoded vegetation survey.';
    }
    if (alertType.includes('WATER') || alertType.includes('SPREAD')) {
      return 'Inspect storage perimeter, examine bund integrity, and register water level observation.';
    }
    if (alertType.includes('RISK') || severity === 'CRITICAL') {
      return 'Flag catchment for immediate District Watershed Committee technical review & DPR priority allocation.';
    }
    return 'Conduct routine field inspection and verify satellite telemetry with ground evidence.';
  };

  return (
    <div className="bg-white p-4 sm:p-5 rounded border border-slate-300 shadow-xs space-y-4 select-none">
      {/* Module Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 pb-3">
        <div className="flex items-center space-x-2">
          <Bell className="h-4 w-4 text-red-700" />
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
            Departmental Hazard &amp; Verification Alerts
          </h3>
        </div>
        <div className="flex items-center space-x-2 flex-wrap gap-2 text-xs">
          {/* Severity Filter */}
          <div className="flex items-center space-x-1">
            <span className="text-slate-500 font-semibold">Severity:</span>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="bg-slate-50 border border-slate-300 rounded px-2 py-1 text-xs text-slate-800 font-semibold"
            >
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">CRITICAL</option>
              <option value="HIGH">HIGH</option>
              <option value="MEDIUM">MEDIUM</option>
            </select>
          </div>

          {/* Status Filter */}
          <div className="flex items-center space-x-1">
            <span className="text-slate-500 font-semibold">Status:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-slate-50 border border-slate-300 rounded px-2 py-1 text-xs text-slate-800 font-semibold"
            >
              <option value="ALL">All Statuses</option>
              <option value="ACTIVE">ACTIVE</option>
              <option value="ACKNOWLEDGED">ACKNOWLEDGED</option>
              <option value="RESOLVED">RESOLVED</option>
            </select>
          </div>

          <span className="text-[10px] font-mono font-bold bg-slate-100 text-slate-700 px-2 py-1 rounded border border-slate-300">
            {alerts.filter((a) => a.status === 'ACTIVE').length} ACTIVE
          </span>
        </div>
      </div>

      {loading ? (
        <div className="h-28 flex items-center justify-center text-xs text-slate-500">
          Checking alert triggers...
        </div>
      ) : filteredAlerts.length > 0 ? (
        <div className="space-y-3">
          {filteredAlerts.map((alt) => (
            <div
              key={alt.id}
              className={`p-3.5 rounded border flex flex-col md:flex-row md:items-start justify-between gap-3 ${
                alt.status === 'ACTIVE'
                  ? 'bg-red-50/40 border-red-200'
                  : alt.status === 'ACKNOWLEDGED'
                  ? 'bg-amber-50/30 border-amber-200'
                  : 'bg-slate-50 border-slate-200 opacity-80'
              }`}
            >
              <div className="space-y-1.5 flex-1">
                <div className="flex items-center space-x-2 flex-wrap gap-1">
                  <span
                    className={`text-[10px] font-extrabold px-1.5 py-0.5 rounded border ${getSeverityBadge(
                      alt.severity
                    )}`}
                  >
                    {alt.severity}
                  </span>
                  <span className="font-bold text-slate-900 text-xs">
                    {alt.alert_type.replace(/_/g, ' ')}
                  </span>
                  <span className="text-[10px] text-slate-500 flex items-center font-mono">
                    <Clock className="h-3 w-3 mr-1 text-slate-400" />
                    Detected: {new Date(alt.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
                  </span>
                </div>

                <p className="text-xs text-slate-800 font-medium leading-snug">
                  {alt.trigger_reason}
                </p>

                {alt.supporting_indicator && (
                  <span className="text-[10px] text-slate-500 font-mono block">
                    Telemetry Trigger Source: {alt.supporting_indicator}
                  </span>
                )}

                {/* Required Action Callout */}
                <div className="p-2 bg-white/90 rounded border border-slate-200 text-[11px] text-slate-700 space-y-0.5">
                  <strong className="text-blue-950 font-bold uppercase text-[10px] block">
                    Prescribed Departmental Response:
                  </strong>
                  <p className="text-slate-600 leading-snug">
                    {getRequiredAction(alt.alert_type, alt.severity)}
                  </p>
                </div>
              </div>

              {/* Status & Officer Action Buttons */}
              <div className="shrink-0 flex items-center space-x-1.5 pt-1 md:pt-0">
                {alt.status === 'ACTIVE' && (
                  <button
                    type="button"
                    onClick={() => handleUpdateStatus(alt.id, 'ACKNOWLEDGED')}
                    className="px-2.5 py-1 bg-white hover:bg-slate-100 text-slate-700 text-xs font-semibold rounded border border-slate-300 shadow-2xs transition-colors"
                  >
                    Acknowledge
                  </button>
                )}
                {alt.status !== 'RESOLVED' && (
                  <button
                    type="button"
                    onClick={() => handleUpdateStatus(alt.id, 'RESOLVED')}
                    className="px-2.5 py-1 bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-bold rounded shadow-2xs transition-colors"
                  >
                    Resolve Alert
                  </button>
                )}
                {alt.status === 'RESOLVED' && (
                  <span className="text-xs font-bold text-emerald-800 flex items-center px-2 py-1 bg-emerald-50 rounded border border-emerald-300">
                    <CheckCircle className="h-3.5 w-3.5 mr-1 text-emerald-700" />
                    RESOLVED
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-6 text-xs text-slate-500 text-center">
          No environmental hazard alerts match the selected criteria.
        </div>
      )}
    </div>
  );
};
