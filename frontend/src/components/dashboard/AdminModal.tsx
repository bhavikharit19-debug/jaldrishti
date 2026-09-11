'use client';
import React, { useState, useEffect } from 'react';
import { api } from '@/services/api';
import { UserProfile, AccessRequest, AuditLogEntry } from '@/types';
import {
  Users,
  UserCheck,
  UserX,
  FileCheck,
  ShieldCheck,
  History,
  CheckCircle,
  XCircle,
  X,
  RefreshCw,
  Search,
  Filter
} from 'lucide-react';

interface AdminModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AdminModal: React.FC<AdminModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<'users' | 'requests' | 'audit'>('users');
  const [users, setUsers] = useState<UserProfile[]>([]);
  const [requests, setRequests] = useState<AccessRequest[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // Rejection modal
  const [rejectReqId, setRejectReqId] = useState<number | null>(null);
  const [rejectReason, setRejectReason] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [u, r, a] = await Promise.all([
        api.listUsers().catch(() => []),
        api.listAccessRequests().catch(() => []),
        api.listAuditLogs().catch(() => [])
      ]);
      setUsers(u);
      setRequests(r);
      setAuditLogs(a);
    } catch {
      // Error handling
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadData();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleApprove = async (reqId: number) => {
    try {
      await api.approveAccessRequest(reqId, 'JalDrishti@2026');
      setFeedback({ type: 'success', message: `Request #${reqId} approved. Officer account provisioned.` });
      loadData();
    } catch (err: any) {
      setFeedback({ type: 'error', message: err?.message || 'Failed to approve request' });
    }
  };

  const handleReject = async () => {
    if (!rejectReqId) return;
    try {
      await api.rejectAccessRequest(rejectReqId, rejectReason || 'Administrative criteria not met');
      setFeedback({ type: 'success', message: `Request #${rejectReqId} rejected.` });
      setRejectReqId(null);
      setRejectReason('');
      loadData();
    } catch (err: any) {
      setFeedback({ type: 'error', message: err?.message || 'Failed to reject request' });
    }
  };

  const handleToggleUserActive = async (user: UserProfile) => {
    try {
      await api.updateUser(user.id, { is_active: !user.is_active });
      setFeedback({
        type: 'success',
        message: `User ${user.name} is now ${!user.is_active ? 'ACTIVE' : 'DEACTIVATED'}.`
      });
      loadData();
    } catch (err: any) {
      setFeedback({ type: 'error', message: err?.message || 'Failed to update user' });
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4">
      <div className="bg-white border border-slate-300 rounded-lg shadow-2xl w-full max-w-5xl max-h-[90vh] flex flex-col text-slate-800">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50 rounded-t-lg">
          <div className="flex items-center space-x-2.5">
            <div className="h-9 w-9 rounded bg-blue-800 flex items-center justify-center text-white">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-base font-bold text-slate-900">National Administration & Access Control</h2>
                <span className="text-[10px] font-extrabold uppercase px-1.5 py-0.5 bg-red-100 text-red-800 rounded">
                  Admin Restricted
                </span>
              </div>
              <p className="text-xs text-slate-500">
                Manage officer accounts, review access requests, and inspect statutory compliance audit logs.
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={loadData}
              disabled={loading}
              className="p-1.5 text-slate-500 hover:text-slate-700 hover:bg-slate-200 rounded transition-colors"
              title="Refresh Data"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-200 rounded transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Feedback Alert */}
        {feedback && (
          <div
            className={`px-6 py-2 text-xs flex items-center justify-between ${
              feedback.type === 'success' ? 'bg-emerald-50 text-emerald-800' : 'bg-red-50 text-red-800'
            }`}
          >
            <span>{feedback.message}</span>
            <button onClick={() => setFeedback(null)} className="text-slate-400 hover:text-slate-600">
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        )}

        {/* Tabs Bar */}
        <div className="flex border-b border-slate-200 px-6 bg-white">
          <button
            onClick={() => setActiveTab('users')}
            className={`py-3 px-4 text-xs font-bold border-b-2 transition-colors flex items-center space-x-2 ${
              activeTab === 'users'
                ? 'border-blue-600 text-blue-700'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            <Users className="h-4 w-4" />
            <span>Registered Officers ({users.length})</span>
          </button>
          <button
            onClick={() => setActiveTab('requests')}
            className={`py-3 px-4 text-xs font-bold border-b-2 transition-colors flex items-center space-x-2 ${
              activeTab === 'requests'
                ? 'border-blue-600 text-blue-700'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            <FileCheck className="h-4 w-4" />
            <span>
              Access Requests (
              {requests.filter((r) => r.status === 'PENDING').length} Pending / {requests.length} Total)
            </span>
          </button>
          <button
            onClick={() => setActiveTab('audit')}
            className={`py-3 px-4 text-xs font-bold border-b-2 transition-colors flex items-center space-x-2 ${
              activeTab === 'audit'
                ? 'border-blue-600 text-blue-700'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            <History className="h-4 w-4" />
            <span>Statutory Audit Trail ({auditLogs.length})</span>
          </button>
        </div>

        {/* Body Content */}
        <div className="flex-1 overflow-y-auto p-6 bg-slate-50">
          {/* TAB 1: USERS LIST */}
          {activeTab === 'users' && (
            <div className="space-y-4">
              <div className="overflow-x-auto bg-white border border-slate-200 rounded-lg">
                <table className="min-w-full divide-y divide-slate-200 text-left text-xs">
                  <thead className="bg-slate-50 text-slate-600 font-semibold">
                    <tr>
                      <th className="px-4 py-2.5">Officer Name</th>
                      <th className="px-4 py-2.5">Official Email</th>
                      <th className="px-4 py-2.5">Assigned Role</th>
                      <th className="px-4 py-2.5">Jurisdiction Scope</th>
                      <th className="px-4 py-2.5">Organization</th>
                      <th className="px-4 py-2.5">Status</th>
                      <th className="px-4 py-2.5 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {users.map((u) => (
                      <tr key={u.id} className="hover:bg-slate-50/80">
                        <td className="px-4 py-2.5 font-semibold text-slate-900">{u.name}</td>
                        <td className="px-4 py-2.5 font-mono text-[11px] text-slate-600">{u.email}</td>
                        <td className="px-4 py-2.5">
                          <span
                            className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                              u.role === 'ADMIN'
                                ? 'bg-purple-100 text-purple-800'
                                : u.role === 'STATE_OFFICER'
                                ? 'bg-blue-100 text-blue-800'
                                : u.role === 'DISTRICT_OFFICER'
                                ? 'bg-teal-100 text-teal-800'
                                : u.role === 'FIELD_OFFICER'
                                ? 'bg-emerald-100 text-emerald-800'
                                : 'bg-slate-100 text-slate-800'
                            }`}
                          >
                            {u.role}
                          </span>
                        </td>
                        <td className="px-4 py-2.5 text-slate-600">
                          {u.watershed_id
                            ? `Watershed ID: ${u.watershed_id}`
                            : u.district_id
                            ? `District ID: ${u.district_id}`
                            : u.state_id
                            ? `State ID: ${u.state_id}`
                            : 'National'}
                        </td>
                        <td className="px-4 py-2.5 text-slate-500 truncate max-w-[160px]">{u.organization || '—'}</td>
                        <td className="px-4 py-2.5">
                          <span
                            className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                              u.is_active ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
                            }`}
                          >
                            {u.is_active ? 'ACTIVE' : 'DEACTIVATED'}
                          </span>
                        </td>
                        <td className="px-4 py-2.5 text-right">
                          <button
                            type="button"
                            onClick={() => handleToggleUserActive(u)}
                            className={`text-[11px] font-semibold underline ${
                              u.is_active ? 'text-red-600 hover:text-red-800' : 'text-emerald-600 hover:text-emerald-800'
                            }`}
                          >
                            {u.is_active ? 'Deactivate' : 'Activate'}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 2: ACCESS REQUESTS */}
          {activeTab === 'requests' && (
            <div className="space-y-4">
              {requests.length === 0 ? (
                <div className="text-center py-12 text-slate-400 text-xs">No access requests submitted yet.</div>
              ) : (
                <div className="space-y-3">
                  {requests.map((r) => (
                    <div
                      key={r.id}
                      className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-4"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center space-x-2">
                          <span className="text-xs font-bold text-slate-900">{r.name}</span>
                          <span className="text-[11px] font-mono text-slate-500">({r.email})</span>
                          <span
                            className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                              r.status === 'PENDING'
                                ? 'bg-amber-100 text-amber-800'
                                : r.status === 'APPROVED'
                                ? 'bg-emerald-100 text-emerald-800'
                                : 'bg-red-100 text-red-800'
                            }`}
                          >
                            {r.status}
                          </span>
                        </div>
                        <div className="text-xs text-slate-600">
                          Requested Role: <strong className="text-blue-700">{r.requested_role}</strong> | Agency:{' '}
                          {r.organization} {r.designation ? `(${r.designation})` : ''}
                        </div>
                        <div className="text-xs text-slate-500 bg-slate-50 p-2 rounded border border-slate-100 italic">
                          "{r.reason}"
                        </div>
                      </div>

                      {r.status === 'PENDING' && (
                        <div className="flex items-center space-x-2 flex-shrink-0">
                          <button
                            type="button"
                            onClick={() => handleApprove(r.id)}
                            className="inline-flex items-center space-x-1 px-3 py-1.5 bg-emerald-700 hover:bg-emerald-800 text-white rounded text-xs font-semibold shadow-sm transition-colors"
                          >
                            <CheckCircle className="h-3.5 w-3.5" />
                            <span>Approve & Provision</span>
                          </button>
                          <button
                            type="button"
                            onClick={() => setRejectReqId(r.id)}
                            className="inline-flex items-center space-x-1 px-3 py-1.5 bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 rounded text-xs font-semibold transition-colors"
                          >
                            <XCircle className="h-3.5 w-3.5" />
                            <span>Reject</span>
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB 3: STATUTORY AUDIT TRAIL */}
          {activeTab === 'audit' && (
            <div className="space-y-4">
              <div className="overflow-x-auto bg-white border border-slate-200 rounded-lg">
                <table className="min-w-full divide-y divide-slate-200 text-left text-xs">
                  <thead className="bg-slate-50 text-slate-600 font-semibold">
                    <tr>
                      <th className="px-4 py-2.5">Timestamp (UTC)</th>
                      <th className="px-4 py-2.5">Officer ID</th>
                      <th className="px-4 py-2.5">Action Executed</th>
                      <th className="px-4 py-2.5">Resource Domain</th>
                      <th className="px-4 py-2.5">Audit Payload & Details</th>
                      <th className="px-4 py-2.5">Client IP</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 font-mono text-[11px]">
                    {auditLogs.map((log) => (
                      <tr key={log.id} className="hover:bg-slate-50/80">
                        <td className="px-4 py-2 text-slate-500">
                          {new Date(log.timestamp).toISOString().replace('T', ' ').slice(0, 19)}
                        </td>
                        <td className="px-4 py-2 text-slate-800 font-semibold">{log.user_id}</td>
                        <td className="px-4 py-2">
                          <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-blue-50 text-blue-800">
                            {log.action}
                          </span>
                        </td>
                        <td className="px-4 py-2 text-slate-600">{log.resource_type}</td>
                        <td className="px-4 py-2 text-slate-500 font-sans truncate max-w-[280px]">
                          {JSON.stringify(log.details)}
                        </td>
                        <td className="px-4 py-2 text-slate-400">{log.ip_address || '127.0.0.1'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        {/* Reject Modal Dialog */}
        {rejectReqId && (
          <div className="fixed inset-0 z-60 flex items-center justify-center bg-slate-900/60 p-4">
            <div className="bg-white border border-slate-300 rounded-lg shadow-xl max-w-md w-full p-6 text-slate-800">
              <h3 className="text-sm font-bold text-slate-900 mb-2">Reject Access Request #{rejectReqId}</h3>
              <p className="text-xs text-slate-500 mb-3">
                Provide official administrative rationale for rejection (will be recorded in statutory audit trail):
              </p>
              <textarea
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                placeholder="e.g. Applicant credentials cannot be verified against state nodal records..."
                className="w-full text-xs p-2 border border-slate-300 rounded mb-4"
                rows={3}
              />
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setRejectReqId(null)}
                  className="px-3 py-1.5 text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 rounded"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleReject}
                  className="px-3 py-1.5 text-xs font-semibold bg-red-600 hover:bg-red-700 text-white rounded shadow-sm"
                >
                  Confirm Rejection
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-200 bg-white flex items-center justify-between text-xs text-slate-500 rounded-b-lg">
          <div>SIH 26015 Institutional Compliance: Immutable Audit Trail Enforced</div>
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-800 rounded font-semibold text-xs transition-colors"
          >
            Close Panel
          </button>
        </div>
      </div>
    </div>
  );
};
