'use client';
import React from 'react';
import { useAuth } from '@/context/AuthContext';
import {
  Map as MapIcon,
  MapPin,
  Camera,
  Layers,
  History,
  Activity,
  Cpu,
  ShieldAlert,
  Hammer,
  FileText,
  Database,
  Users
} from 'lucide-react';
import Link from 'next/link';

interface SidebarNavProps {
  activeSection: string;
  onSelectSection: (section: string) => void;
  onOpenAdminModal?: () => void;
  onOpenDataModal?: () => void;
  onOpenPhotoModal?: () => void;
  selectedWatershedId?: number;
}

/**
 * SidebarNav
 * 
 * Government-style horizontal sub-navigation bar:
 * Compact professional icons, clear rectangular tabs, role indicators.
 */
export const SidebarNav: React.FC<SidebarNavProps> = ({
  activeSection,
  onSelectSection,
  onOpenAdminModal,
  onOpenDataModal,
  onOpenPhotoModal,
  selectedWatershedId = 1
}) => {
  const { isAdmin } = useAuth();

  const navItems = [
    { id: 'gis_intelligence', label: 'GIS Map Workstation', icon: MapIcon },
    { id: 'indicators', label: 'Biophysical Indicators', icon: Activity },
    { id: 'photos', label: 'Field Evidence', icon: Camera, action: onOpenPhotoModal },
    { id: 'change', label: 'Change Detection', icon: History },
    { id: 'predictions', label: 'Predictive Assessment', icon: Cpu },
    { id: 'risks', label: 'Risk Assessment', icon: ShieldAlert },
    { id: 'interventions', label: 'Intervention Monitoring', icon: Hammer },
    { id: 'recommendations', label: 'Watershed Decision Support', icon: Layers },
    { id: 'data_catalog', label: 'Data Sources & Ingestion', icon: Database, action: onOpenDataModal },
  ];

  return (
    <nav className="bg-white border-b border-slate-300 px-4 sm:px-6 py-1.5 overflow-x-auto flex items-center justify-between text-xs select-none">
      <div className="flex items-center space-x-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeSection === item.id;
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => {
                if (item.action) {
                  item.action();
                } else {
                  onSelectSection(item.id);
                }
              }}
              className={`px-2.5 py-1.5 rounded font-bold flex items-center space-x-1.5 transition-colors whitespace-nowrap text-[11px] uppercase tracking-wider ${
                isActive
                  ? 'bg-blue-900 text-white shadow-xs'
                  : 'text-slate-700 hover:text-slate-950 hover:bg-slate-100 border border-transparent'
              }`}
            >
              <Icon className={`h-3.5 w-3.5 ${isActive ? 'text-blue-200' : 'text-slate-500'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>

      <div className="flex items-center space-x-2 flex-shrink-0 pl-2">
        <Link
          href={`/reports?id=${selectedWatershedId}`}
          className="px-2.5 py-1 text-slate-700 hover:text-blue-900 font-bold text-[11px] uppercase tracking-wider flex items-center space-x-1 border border-slate-300 rounded hover:bg-slate-50 transition-colors"
        >
          <FileText className="h-3.5 w-3.5 text-slate-500" />
          <span>Reports</span>
        </Link>
        {isAdmin && onOpenAdminModal && (
          <button
            type="button"
            onClick={onOpenAdminModal}
            className="px-2 py-1 text-purple-900 font-bold text-[11px] uppercase tracking-wider flex items-center space-x-1 border border-purple-300 bg-purple-50 hover:bg-purple-100 rounded transition-colors"
          >
            <Users className="h-3.5 w-3.5 text-purple-700" />
            <span>Admin</span>
          </button>
        )}
      </div>
    </nav>
  );
};
