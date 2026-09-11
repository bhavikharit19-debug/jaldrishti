'use client';
import React, { useState } from 'react';
import {
  Layers,
  Map as MapIcon,
  Satellite,
  Mountain,
  Eye,
  EyeOff,
  MapPin,
  Compass,
  FileText,
  Sliders,
  CheckSquare,
  Square,
  Activity,
  History,
  ShieldAlert,
  Cpu,
  Hammer,
  Camera,
  Database,
  Printer,
  ChevronDown,
  ChevronRight,
  Info
} from 'lucide-react';
import { WatershedDetail, StateHierarchy, WatershedListItem } from '@/types';
import { LayerVisibility } from '@/components/map/LayerControl';

interface GISControlPanelProps {
  watershed?: WatershedDetail;
  states: StateHierarchy[];
  watersheds: WatershedListItem[];
  selectedWatershedId: number;
  onSelectWatershed: (id: number) => void;
  onFilterChange: (stateId?: number, districtId?: number, search?: string) => void;
  layerVisibility: LayerVisibility;
  onLayerToggle: (key: keyof LayerVisibility, val: boolean) => void;
  onSelectTab: (tab: string) => void;
  onOpenReport?: () => void;
  onOpenDataCatalog?: () => void;
  onOpenPhotoModal?: () => void;
}

/**
 * GISControlPanel
 * 
 * Professional GIS Left Workstation Control Panel:
 * Administrative Location details, Base Cartography switcher,
 * Thematic & Monitoring Layers toggles, GIS Metadata (CRS, Provenance),
 * and quick analytical view triggers.
 */
export default function GISControlPanel({
  watershed,
  states,
  watersheds,
  selectedWatershedId,
  onSelectWatershed,
  onFilterChange,
  layerVisibility,
  onLayerToggle,
  onSelectTab,
  onOpenReport,
  onOpenDataCatalog,
  onOpenPhotoModal
}: GISControlPanelProps) {
  // Accordion section collapse states
  const [openSections, setOpenSections] = useState({
    location: true,
    baseMap: true,
    thematic: true,
    monitoring: true,
    analysis: true,
    metadata: true
  });

  const toggleSection = (section: keyof typeof openSections) => {
    setOpenSections((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  const thematicLayers: {
    key: keyof LayerVisibility;
    label: string;
    code: string;
    color: string;
    resolution: string;
    source: string;
  }[] = [
    {
      key: 'boundary',
      label: 'Watershed Boundary',
      code: 'WS_BND',
      color: '#1e3a8a',
      resolution: 'Vector Polygon',
      source: 'Survey of India / DoLR'
    },
    {
      key: 'lulc',
      label: 'Land Use / Land Cover (5 Classes)',
      code: 'LULC_2024',
      color: '#65a30d',
      resolution: '10m Multi-Spectral',
      source: 'Sentinel-2 / NRSC Bhuvan'
    },
    {
      key: 'drainage',
      label: 'Drainage Streams (Orders 1-3)',
      code: 'STR_NET',
      color: '#0284c7',
      resolution: 'Dendritic Thalweg',
      source: 'DEM Hydrological Flow'
    },
    {
      key: 'waterBodies',
      label: 'Surface Water & Reservoirs',
      code: 'WTR_BOD',
      color: '#06b6d4',
      resolution: 'NDWI Mask',
      source: 'Copernicus / NRSC'
    },
    {
      key: 'vegetation',
      label: 'Vegetation Canopy / NDVI Vigor',
      code: 'NDVI_VIG',
      color: '#15803d',
      resolution: '10m Gridded',
      source: 'Sentinel-2 NDVI Composite'
    },
    {
      key: 'elevation',
      label: 'Topographic Elevation & Contours',
      code: 'DEM_TOPO',
      color: '#854d0e',
      resolution: '30m SRTM / CartoDEM',
      source: 'ISRO CartoDEM'
    }
  ];

  const monitoringLayers: {
    key: keyof LayerVisibility;
    label: string;
    code: string;
    color: string;
    source: string;
  }[] = [
    {
      key: 'interventions',
      label: 'Intervention Sites (Check Dams/CCT)',
      code: 'INT_SITES',
      color: '#ea580c',
      source: 'Department Sanction Registry'
    },
    {
      key: 'fieldPhotos',
      label: 'Geo-Tagged Field Photos',
      code: 'FLD_SURV',
      color: '#9333ea',
      source: 'Ground Truth Mobile Inspections'
    }
  ];

  return (
    <aside className="w-80 bg-white border-r border-slate-300 flex flex-col h-full overflow-y-auto text-xs select-none shadow-xs">
      {/* Header Bar */}
      <div className="px-3 py-2.5 bg-slate-100 border-b border-slate-300 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Layers className="h-4 w-4 text-blue-900" />
          <span className="font-bold uppercase tracking-wider text-slate-900 text-[11px]">
            GIS Control Panel
          </span>
        </div>
        <span className="text-[10px] font-mono font-semibold bg-blue-50 text-blue-900 px-1.5 py-0.5 rounded border border-blue-200">
          EPSG:4326
        </span>
      </div>

      <div className="divide-y divide-slate-200">
        {/* 1. ADMINISTRATIVE LOCATION HIERARCHY */}
        <div>
          <button
            type="button"
            onClick={() => toggleSection('location')}
            className="w-full px-3 py-2 bg-slate-50 hover:bg-slate-100 flex items-center justify-between text-left font-bold text-slate-800 text-[11px] uppercase tracking-wide transition-colors"
          >
            <div className="flex items-center space-x-1.5">
              <MapPin className="h-3.5 w-3.5 text-blue-800" />
              <span>Location &amp; Hierarchy</span>
            </div>
            {openSections.location ? <ChevronDown className="h-3.5 w-3.5 text-slate-500" /> : <ChevronRight className="h-3.5 w-3.5 text-slate-500" />}
          </button>

          {openSections.location && (
            <div className="p-3 space-y-2 bg-white">
              {/* Watershed Dropdown Quick Switcher */}
              <div>
                <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">
                  Active Micro-Watershed:
                </label>
                <select
                  value={selectedWatershedId}
                  onChange={(e) => onSelectWatershed(Number(e.target.value))}
                  className="w-full px-2 py-1.5 bg-slate-50 border border-slate-300 rounded font-semibold text-slate-900 text-xs focus:ring-1 focus:ring-blue-900"
                >
                  {watersheds.map((ws) => (
                    <option key={ws.id} value={ws.id}>
                      {ws.name} ({ws.code})
                    </option>
                  ))}
                </select>
              </div>

              {/* Administrative Details Table */}
              {watershed && (
                <div className="p-2 bg-slate-50 rounded border border-slate-200 font-mono text-[11px] space-y-1">
                  <div className="flex justify-between">
                    <span className="text-slate-500">State:</span>
                    <span className="font-bold text-slate-900">{watershed.state_name || 'State'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">District:</span>
                    <span className="font-bold text-slate-900">{watershed.district_name || 'District'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Catchment Area:</span>
                    <span className="font-bold text-blue-900">
                      {watershed.area_hectares ? `${watershed.area_hectares.toLocaleString()} ha` : '—'}
                    </span>
                  </div>
                  {watershed.river_basin && (
                    <div className="flex justify-between">
                      <span className="text-slate-500">River Basin:</span>
                      <span className="font-bold text-slate-800">{watershed.river_basin}</span>
                    </div>
                  )}
                  {watershed.agro_climatic_zone && (
                    <div className="flex justify-between">
                      <span className="text-slate-500">Agro-Climatic Zone:</span>
                      <span className="font-semibold text-slate-700 truncate max-w-[140px]" title={watershed.agro_climatic_zone}>
                        {watershed.agro_climatic_zone}
                      </span>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* 2. BASE CARTOGRAPHY */}
        <div>
          <button
            type="button"
            onClick={() => toggleSection('baseMap')}
            className="w-full px-3 py-2 bg-slate-50 hover:bg-slate-100 flex items-center justify-between text-left font-bold text-slate-800 text-[11px] uppercase tracking-wide transition-colors"
          >
            <div className="flex items-center space-x-1.5">
              <Compass className="h-3.5 w-3.5 text-blue-800" />
              <span>Base Cartography</span>
            </div>
            {openSections.baseMap ? <ChevronDown className="h-3.5 w-3.5 text-slate-500" /> : <ChevronRight className="h-3.5 w-3.5 text-slate-500" />}
          </button>

          {openSections.baseMap && (
            <div className="p-3 bg-white">
              <div className="grid grid-cols-2 gap-1.5">
                <button
                  type="button"
                  onClick={() => onLayerToggle('satellite', false)}
                  className={`py-1.5 px-2 rounded border text-[11px] font-bold flex items-center justify-center space-x-1.5 transition-all ${
                    !layerVisibility.satellite
                      ? 'bg-blue-900 text-white border-blue-900 shadow-xs'
                      : 'bg-slate-50 hover:bg-slate-100 text-slate-700 border-slate-300'
                  }`}
                >
                  <MapIcon className="h-3 w-3" />
                  <span>Vector Map</span>
                </button>
                <button
                  type="button"
                  onClick={() => onLayerToggle('satellite', true)}
                  className={`py-1.5 px-2 rounded border text-[11px] font-bold flex items-center justify-center space-x-1.5 transition-all ${
                    layerVisibility.satellite
                      ? 'bg-blue-900 text-white border-blue-900 shadow-xs'
                      : 'bg-slate-50 hover:bg-slate-100 text-slate-700 border-slate-300'
                  }`}
                >
                  <Satellite className="h-3 w-3" />
                  <span>Satellite RGB</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* 3. THEMATIC GIS LAYERS */}
        <div>
          <button
            type="button"
            onClick={() => toggleSection('thematic')}
            className="w-full px-3 py-2 bg-slate-50 hover:bg-slate-100 flex items-center justify-between text-left font-bold text-slate-800 text-[11px] uppercase tracking-wide transition-colors"
          >
            <div className="flex items-center space-x-1.5">
              <Sliders className="h-3.5 w-3.5 text-blue-800" />
              <span>Thematic GIS Layers</span>
            </div>
            {openSections.thematic ? <ChevronDown className="h-3.5 w-3.5 text-slate-500" /> : <ChevronRight className="h-3.5 w-3.5 text-slate-500" />}
          </button>

          {openSections.thematic && (
            <div className="p-2 space-y-1 bg-white">
              {thematicLayers.map((lyr) => {
                const isChecked = layerVisibility[lyr.key];
                return (
                  <div
                    key={lyr.key}
                    onClick={() => onLayerToggle(lyr.key, !isChecked)}
                    className="p-1.5 rounded hover:bg-slate-50 cursor-pointer flex items-start space-x-2 border border-transparent hover:border-slate-200 transition-colors"
                  >
                    <div className="pt-0.5 text-blue-900">
                      {isChecked ? <CheckSquare className="h-3.5 w-3.5 text-blue-900" /> : <Square className="h-3.5 w-3.5 text-slate-400" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <span className={`text-[11px] font-semibold truncate ${isChecked ? 'text-slate-950 font-bold' : 'text-slate-600'}`}>
                          {lyr.label}
                        </span>
                        <div
                          className="h-2.5 w-2.5 rounded-full flex-shrink-0 ml-1 border border-slate-300"
                          style={{ backgroundColor: lyr.color }}
                        />
                      </div>
                      <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono mt-0.5">
                        <span>{lyr.resolution}</span>
                        <span className="truncate max-w-[110px]" title={lyr.source}>{lyr.source}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* 4. MONITORING & FIELD INSPECTION LAYERS */}
        <div>
          <button
            type="button"
            onClick={() => toggleSection('monitoring')}
            className="w-full px-3 py-2 bg-slate-50 hover:bg-slate-100 flex items-center justify-between text-left font-bold text-slate-800 text-[11px] uppercase tracking-wide transition-colors"
          >
            <div className="flex items-center space-x-1.5">
              <Camera className="h-3.5 w-3.5 text-purple-700" />
              <span>Monitoring &amp; Ground Truth</span>
            </div>
            {openSections.monitoring ? <ChevronDown className="h-3.5 w-3.5 text-slate-500" /> : <ChevronRight className="h-3.5 w-3.5 text-slate-500" />}
          </button>

          {openSections.monitoring && (
            <div className="p-2 space-y-1 bg-white">
              {monitoringLayers.map((lyr) => {
                const isChecked = layerVisibility[lyr.key];
                return (
                  <div
                    key={lyr.key}
                    onClick={() => onLayerToggle(lyr.key, !isChecked)}
                    className="p-1.5 rounded hover:bg-slate-50 cursor-pointer flex items-start space-x-2 border border-transparent hover:border-slate-200 transition-colors"
                  >
                    <div className="pt-0.5 text-blue-900">
                      {isChecked ? <CheckSquare className="h-3.5 w-3.5 text-blue-900" /> : <Square className="h-3.5 w-3.5 text-slate-400" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <span className={`text-[11px] font-semibold truncate ${isChecked ? 'text-slate-950 font-bold' : 'text-slate-600'}`}>
                          {lyr.label}
                        </span>
                        <div
                          className="h-2.5 w-2.5 rounded-full flex-shrink-0 ml-1 border border-slate-300"
                          style={{ backgroundColor: lyr.color }}
                        />
                      </div>
                      <div className="text-[10px] text-slate-400 font-mono mt-0.5">
                        {lyr.source}
                      </div>
                    </div>
                  </div>
                );
              })}

              <div className="pt-2 px-1 flex items-center space-x-2">
                <button
                  type="button"
                  onClick={onOpenPhotoModal}
                  className="flex-1 py-1.5 px-2 bg-purple-50 hover:bg-purple-100 text-purple-900 border border-purple-200 rounded font-semibold text-[11px] flex items-center justify-center space-x-1"
                >
                  <Camera className="h-3.5 w-3.5" />
                  <span>Upload Field Photo</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* 5. GIS ANALYSIS & WORKFLOW SHORTCUTS */}
        <div>
          <button
            type="button"
            onClick={() => toggleSection('analysis')}
            className="w-full px-3 py-2 bg-slate-50 hover:bg-slate-100 flex items-center justify-between text-left font-bold text-slate-800 text-[11px] uppercase tracking-wide transition-colors"
          >
            <div className="flex items-center space-x-1.5">
              <Activity className="h-3.5 w-3.5 text-emerald-700" />
              <span>Analysis &amp; Decision Tools</span>
            </div>
            {openSections.analysis ? <ChevronDown className="h-3.5 w-3.5 text-slate-500" /> : <ChevronRight className="h-3.5 w-3.5 text-slate-500" />}
          </button>

          {openSections.analysis && (
            <div className="p-2 space-y-1 bg-white">
              <button
                type="button"
                onClick={() => onSelectTab('change')}
                className="w-full py-1.5 px-2 text-left hover:bg-slate-50 rounded text-slate-700 hover:text-blue-900 flex items-center space-x-2 text-[11px] font-medium"
              >
                <History className="h-3.5 w-3.5 text-blue-700" />
                <span>Historical Change Detection</span>
              </button>
              <button
                type="button"
                onClick={() => onSelectTab('predictions')}
                className="w-full py-1.5 px-2 text-left hover:bg-slate-50 rounded text-slate-700 hover:text-blue-900 flex items-center space-x-2 text-[11px] font-medium"
              >
                <Cpu className="h-3.5 w-3.5 text-blue-700" />
                <span>Predictive Assessment</span>
              </button>
              <button
                type="button"
                onClick={() => onSelectTab('risks')}
                className="w-full py-1.5 px-2 text-left hover:bg-slate-50 rounded text-slate-700 hover:text-blue-900 flex items-center space-x-2 text-[11px] font-medium"
              >
                <ShieldAlert className="h-3.5 w-3.5 text-amber-700" />
                <span>Hazard Risk Matrix</span>
              </button>
              <button
                type="button"
                onClick={() => onSelectTab('recommendations')}
                className="w-full py-1.5 px-2 text-left hover:bg-slate-50 rounded text-slate-700 hover:text-blue-900 flex items-center space-x-2 text-[11px] font-medium"
              >
                <Hammer className="h-3.5 w-3.5 text-emerald-700" />
                <span>Decision Support &amp; DPR</span>
              </button>
              <button
                type="button"
                onClick={onOpenReport}
                className="w-full py-1.5 px-2 text-left hover:bg-slate-50 rounded text-slate-700 hover:text-blue-900 flex items-center space-x-2 text-[11px] font-medium"
              >
                <Printer className="h-3.5 w-3.5 text-slate-600" />
                <span>Compile Diagnostic Report</span>
              </button>
            </div>
          )}
        </div>

        {/* 6. GEOSPATIAL METADATA & PROVENANCE */}
        <div>
          <button
            type="button"
            onClick={() => toggleSection('metadata')}
            className="w-full px-3 py-2 bg-slate-50 hover:bg-slate-100 flex items-center justify-between text-left font-bold text-slate-800 text-[11px] uppercase tracking-wide transition-colors"
          >
            <div className="flex items-center space-x-1.5">
              <Info className="h-3.5 w-3.5 text-slate-600" />
              <span>Metadata &amp; Provenance</span>
            </div>
            {openSections.metadata ? <ChevronDown className="h-3.5 w-3.5 text-slate-500" /> : <ChevronRight className="h-3.5 w-3.5 text-slate-500" />}
          </button>

          {openSections.metadata && (
            <div className="p-2.5 bg-slate-50 font-mono text-[10px] text-slate-600 space-y-1">
              <div>CRS: <strong className="text-slate-900">EPSG:4326 (WGS 84)</strong></div>
              <div>PROVENANCE: <span className="text-emerald-700 font-bold">DEMO / SEEDED DATA</span></div>
              <div>GIGW COMPLIANCE: <strong className="text-slate-900">LEVEL AA (3.0)</strong></div>
              <div>COORDINATES: <span className="text-blue-900">19°05'N, 74°38'E</span></div>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
