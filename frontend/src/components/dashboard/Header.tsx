'use client';
import React from 'react';
import {
  FileText,
  Bell,
  Database,
  LogOut,
  LogIn,
  Shield,
  ExternalLink,
  Printer,
  ChevronDown
} from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import JalDrishtiLogo from '@/components/common/JalDrishtiLogo';

interface HeaderProps {
  watershedName?: string;
  alertsCount?: number;
  onOpenAlerts?: () => void;
  selectedWatershedId?: number;
  onOpenDataIntegration?: () => void;
  onOpenAdminModal?: () => void;
}

/**
 * Header
 * 
 * Government-grade institutional top bar for JalDrishti:
 * - India Map Watershed Vector Logo
 * - Department & Ministry hierarchy branding
 * - "सत्यमेव जयते" & SIH 26015 Prototype demarcation
 * - Restrained Tricolour accent rule (Saffron → White → Green)
 * - Officer cadre & jurisdictional purview badge
 * - Administrative console (Admin only), Data Ingestion, Reports & Logout
 */
export const Header: React.FC<HeaderProps> = ({
  watershedName,
  alertsCount = 0,
  onOpenAlerts,
  selectedWatershedId = 1,
  onOpenDataIntegration,
  onOpenAdminModal
}) => {
  const router = useRouter();
  const { user, role, isAuthenticated, logout, isAdmin } = useAuth();

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  // Cadre badge styling
  const getRoleBadge = () => {
    if (!role) return null;
    const styles: Record<string, string> = {
      ADMIN: 'bg-purple-50 text-purple-900 border-purple-300',
      STATE_OFFICER: 'bg-blue-50 text-blue-900 border-blue-300',
      DISTRICT_OFFICER: 'bg-teal-50 text-teal-900 border-teal-300',
      FIELD_OFFICER: 'bg-emerald-50 text-emerald-900 border-emerald-300',
      ANALYST: 'bg-amber-50 text-amber-900 border-amber-300',
    };
    return (
      <span
        className={`px-2 py-0.5 rounded text-[10px] font-extrabold uppercase border ${
          styles[role] || 'bg-slate-100 text-slate-700 border-slate-300'
        }`}
      >
        {role.replace('_', ' ')}
      </span>
    );
  };

  return (
    <header className="bg-white border-b border-slate-300 sticky top-0 z-40 select-none shadow-xs">
      {/* Top Utility Hierarchy Strip */}
      <div className="bg-slate-100 border-b border-slate-200 px-4 sm:px-6 py-1 flex items-center justify-between text-[11px] text-slate-600">
        <div className="flex items-center space-x-2">
          <span className="font-semibold text-slate-800">JalDrishti Geospatial Decision-Support Portal</span>
          <span className="text-slate-300">|</span>
          <span className="hidden md:inline text-slate-600">
            Aligned with DoLR &amp; MoJS Watershed Guidelines
          </span>
        </div>
        <div className="flex items-center space-x-3 text-[11px]">
          <JalDrishtiLogo size="sm" variant="icon" />
          <span className="text-slate-300">|</span>
          <span className="bg-blue-50 text-blue-900 px-2 py-0.2 rounded border border-blue-200 font-bold">
            SIH 26015 | PROTOTYPE
          </span>
        </div>
      </div>

      {/* Main Header Bar */}
      <div className="px-4 sm:px-6 py-2.5 flex items-center justify-between gap-4">
        {/* Left: JalDrishti Logo */}
        <Link href="/" className="flex items-center space-x-3 group">
          <JalDrishtiLogo size="md" variant="horizontal" />
        </Link>

        {/* Right: Institutional Actions & Officer Profile */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          {/* Diagnostic Report Quick Button */}
          <Link
            href={`/reports?id=${selectedWatershedId}`}
            className="hidden sm:inline-flex items-center space-x-1 px-2.5 py-1.5 text-xs font-semibold text-slate-700 hover:text-blue-900 bg-slate-50 hover:bg-slate-100 border border-slate-300 rounded transition-colors"
            title="Open Diagnostic Report"
          >
            <FileText className="h-3.5 w-3.5 text-slate-500" />
            <span>Report</span>
          </Link>

          {/* Data Ingestion Modal Trigger */}
          {onOpenDataIntegration && (
            <button
              type="button"
              onClick={onOpenDataIntegration}
              className="hidden sm:inline-flex items-center space-x-1 px-2.5 py-1.5 text-xs font-semibold text-slate-700 hover:text-blue-900 bg-slate-50 hover:bg-slate-100 border border-slate-300 rounded transition-colors"
              title="Data Catalog &amp; GIS Ingestion"
            >
              <Database className="h-3.5 w-3.5 text-slate-500" />
              <span>Data Catalog</span>
            </button>
          )}

          {/* Admin User Console (Admin only) */}
          {isAdmin && onOpenAdminModal && (
            <button
              type="button"
              onClick={onOpenAdminModal}
              className="inline-flex items-center space-x-1 px-2.5 py-1.5 text-xs font-bold text-purple-900 bg-purple-50 hover:bg-purple-100 border border-purple-300 rounded transition-colors"
              title="Administration Console"
            >
              <Shield className="h-3.5 w-3.5 text-purple-700" />
              <span>Admin Console</span>
            </button>
          )}

          {/* Alerts Bell */}
          {onOpenAlerts && (
            <button
              type="button"
              onClick={onOpenAlerts}
              className="relative p-1.5 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded border border-slate-200 transition-colors"
              title="View Catchment Alerts"
            >
              <Bell className="h-4 w-4" />
              {alertsCount > 0 && (
                <span className="absolute -top-1 -right-1 h-4 w-4 rounded-full bg-red-600 text-white font-mono text-[9px] font-bold flex items-center justify-center">
                  {alertsCount}
                </span>
              )}
            </button>
          )}

          <div className="h-5 w-px bg-slate-300 hidden sm:block" />

          {/* Officer Profile & Sign-In/Sign-Out */}
          {isAuthenticated && user ? (
            <div className="flex items-center space-x-2">
              <div className="text-right hidden md:block">
                <div className="text-xs font-bold text-slate-900 leading-tight">
                  {user.name}
                </div>
                <div className="flex items-center justify-end space-x-1.5 mt-0.5">
                  {getRoleBadge()}
                </div>
              </div>
              <button
                type="button"
                onClick={handleLogout}
                className="p-1.5 text-slate-600 hover:text-red-700 hover:bg-red-50 rounded border border-slate-200 transition-colors"
                title="Sign Out"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <Link
              href="/login"
              className="inline-flex items-center space-x-1 px-3 py-1.5 bg-blue-900 hover:bg-blue-950 text-white text-xs font-bold rounded shadow-xs transition-colors"
            >
              <LogIn className="h-3.5 w-3.5" />
              <span>Login</span>
            </Link>
          )}
        </div>
      </div>

      {/* Sub-Header Thin Tricolour Accent Line (Saffron → White → Green) */}
      <div className="h-1 w-full flex">
        <div className="h-full w-1/3 bg-amber-600" />
        <div className="h-full w-1/3 bg-slate-200" />
        <div className="h-full w-1/3 bg-emerald-700" />
      </div>
    </header>
  );
};
