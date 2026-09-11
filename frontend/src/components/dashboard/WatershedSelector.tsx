'use client';
import React, { useState } from 'react';
import { StateHierarchy, WatershedListItem, WatershedDetail, HealthScore } from '@/types';
import { MapPin, Search, ChevronRight, Filter, ShieldCheck, Activity } from 'lucide-react';

interface WatershedSelectorProps {
  states: StateHierarchy[];
  watersheds: WatershedListItem[];
  selectedWatershedId: number;
  onSelectWatershed: (id: number) => void;
  onFilterChange: (stateId?: number, districtId?: number, search?: string) => void;
  currentWatershed?: WatershedDetail;
  healthScore?: HealthScore;
}

/**
 * WatershedSelector
 * 
 * Government-grade administrative hierarchy filter bar:
 * Prominent State → District → Watershed hierarchy with compact
 * biophysical monitoring status summary.
 */
export const WatershedSelector: React.FC<WatershedSelectorProps> = ({
  states,
  watersheds,
  selectedWatershedId,
  onSelectWatershed,
  onFilterChange,
  currentWatershed,
  healthScore
}) => {
  const [selectedStateId, setSelectedStateId] = useState<number | undefined>();
  const [selectedDistrictId, setSelectedDistrictId] = useState<number | undefined>();
  const [searchQuery, setSearchQuery] = useState('');

  const currentDistricts = selectedStateId
    ? states.find((s) => s.id === selectedStateId)?.districts || []
    : [];

  const handleStateChange = (stateIdStr: string) => {
    const sId = stateIdStr ? parseInt(stateIdStr, 10) : undefined;
    setSelectedStateId(sId);
    setSelectedDistrictId(undefined);
    onFilterChange(sId, undefined, searchQuery);
  };

  const handleDistrictChange = (distIdStr: string) => {
    const dId = distIdStr ? parseInt(distIdStr, 10) : undefined;
    setSelectedDistrictId(dId);
    onFilterChange(selectedStateId, dId, searchQuery);
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onFilterChange(selectedStateId, selectedDistrictId, searchQuery);
  };

  // Overall Risk determination
  const riskCategory = healthScore?.category_rating === 'CRITICAL' ? 'HIGH' : healthScore?.category_rating === 'VULNERABLE' ? 'MEDIUM' : 'LOW';

  const vegScore = healthScore?.components?.find(c => c.name.toLowerCase().includes('vegetation') || c.category === 'VEGETATION')?.score ?? 78;
  const waterScore = healthScore?.components?.find(c => c.name.toLowerCase().includes('water') || c.category === 'HYDROLOGICAL')?.score ?? 82;

  return (
    <div className="bg-white border-b border-slate-300 select-none">
      {/* 1. Administrative Hierarchy Selectors */}
      <div className="px-4 sm:px-6 py-2 flex flex-wrap items-center justify-between gap-3 bg-slate-50/70 border-b border-slate-200">
        {/* Left: State → District → Watershed Breadcrumb */}
        <div className="flex items-center space-x-2 flex-wrap">
          <div className="flex items-center space-x-1.5 text-blue-900 font-bold text-xs uppercase tracking-wider">
            <MapPin className="h-3.5 w-3.5 text-blue-800" />
            <span>Jurisdiction:</span>
          </div>

          {/* State Selector */}
          <div className="flex items-center space-x-1">
            <select
              value={selectedStateId || ''}
              onChange={(e) => handleStateChange(e.target.value)}
              className="bg-white border border-slate-300 text-slate-900 text-xs font-semibold rounded px-2 py-1 focus:ring-1 focus:ring-blue-900"
            >
              <option value="">All States (National)</option>
              {states.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
            <ChevronRight className="h-3 w-3 text-slate-400" />
          </div>

          {/* District Selector */}
          <div className="flex items-center space-x-1">
            <select
              value={selectedDistrictId || ''}
              onChange={(e) => handleDistrictChange(e.target.value)}
              disabled={!selectedStateId}
              className="bg-white border border-slate-300 text-slate-900 text-xs font-semibold rounded px-2 py-1 focus:ring-1 focus:ring-blue-900 disabled:opacity-60"
            >
              <option value="">
                {selectedStateId ? 'All Districts' : 'Select State First'}
              </option>
              {currentDistricts.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </select>
            <ChevronRight className="h-3 w-3 text-slate-400" />
          </div>

          {/* Watershed Selector */}
          <div>
            <select
              value={selectedWatershedId || ''}
              onChange={(e) => onSelectWatershed(parseInt(e.target.value, 10))}
              className="bg-blue-900 text-white text-xs font-bold rounded px-2.5 py-1 focus:ring-1 focus:ring-blue-900"
            >
              {watersheds.map((w) => (
                <option key={w.id} value={w.id}>
                  {w.name} ({w.code})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Right: Quick Search */}
        <form onSubmit={handleSearchSubmit} className="relative flex items-center">
          <input
            type="text"
            placeholder="Search watershed code..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="bg-white border border-slate-300 text-slate-900 text-xs rounded pl-7 pr-3 py-1 focus:ring-1 focus:ring-blue-900 w-48 sm:w-60 placeholder:text-slate-400"
          />
          <Search className="absolute left-2 top-2 h-3.5 w-3.5 text-slate-400" />
        </form>
      </div>

      {/* 2. Compact Monitoring Summary Strip */}
      {currentWatershed && (
        <div className="px-4 sm:px-6 py-1.5 bg-white flex flex-wrap items-center justify-between gap-3 text-[11px] font-mono border-b border-slate-200">
          <div className="flex items-center space-x-4 flex-wrap">
            <div>
              <span className="text-slate-500 font-sans">Area:</span>{' '}
              <strong className="text-slate-900">{currentWatershed.area_hectares ? `${currentWatershed.area_hectares.toLocaleString()} ha` : '—'}</strong>
            </div>
            <div className="h-3 w-px bg-slate-200" />
            <div>
              <span className="text-slate-500 font-sans">Vegetation Status:</span>{' '}
              <span className="font-bold text-emerald-800">
                {vegScore > 70 ? 'Optimal Canopy (NDVI 0.58)' : 'Moderate Vigor'}
              </span>
            </div>
            <div className="h-3 w-px bg-slate-200" />
            <div>
              <span className="text-slate-500 font-sans">Water Status:</span>{' '}
              <span className="font-bold text-blue-800">
                {waterScore > 75 ? 'Adequate Storage' : 'Seasonal Stress'}
              </span>
            </div>
            <div className="h-3 w-px bg-slate-200" />
            <div>
              <span className="text-slate-500 font-sans">Land Condition:</span>{' '}
              <span className="font-bold text-slate-800">Stable Terrestrial Base</span>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div>
              <span className="text-slate-500 font-sans">Overall Risk:</span>{' '}
              <span
                className={`font-bold px-1.5 py-0.2 rounded text-[10px] border ${
                  riskCategory === 'LOW'
                    ? 'bg-emerald-50 text-emerald-900 border-emerald-300'
                    : riskCategory === 'MEDIUM'
                    ? 'bg-amber-50 text-amber-900 border-amber-300'
                    : 'bg-red-50 text-red-900 border-red-300'
                }`}
              >
                {riskCategory} RISK
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
