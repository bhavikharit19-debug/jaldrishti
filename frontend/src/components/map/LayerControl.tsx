'use client';
import React, { useState } from 'react';
import { Layers, Eye, EyeOff, Satellite, Map as MapIcon, Sliders } from 'lucide-react';

export interface LayerVisibility {
  boundary: boolean;
  satellite: boolean;
  drainage: boolean;
  waterBodies: boolean;
  lulc: boolean;
  vegetation: boolean;
  elevation: boolean;
  interventions: boolean;
  fieldPhotos: boolean;
}

interface LayerControlProps {
  visibility: LayerVisibility;
  onChange: (key: keyof LayerVisibility, val: boolean) => void;
  counts?: {
    drainageFeatures?: number;
    waterBodies?: number;
    interventions?: number;
    photos?: number;
    lulcClasses?: number;
  };
  showLegend: boolean;
  onToggleLegend: () => void;
}

export const LayerControl: React.FC<LayerControlProps> = ({
  visibility,
  onChange,
  counts,
  showLegend,
  onToggleLegend
}) => {
  const [isOpen, setIsOpen] = useState(true);

  const layersConfig: {
    key: keyof LayerVisibility;
    label: string;
    color: string;
    count?: number;
  }[] = [
    { key: 'boundary', label: 'Watershed Boundary', color: '#1d4ed8' },
    { key: 'lulc', label: 'Land Use / Land Cover (5 Classes)', color: '#8bc34a', count: counts?.lulcClasses || 5 },
    { key: 'drainage', label: 'Drainage Streams (Orders 1-3)', color: '#0284c7', count: counts?.drainageFeatures },
    { key: 'waterBodies', label: 'Surface Water & Reservoirs', color: '#00bcd4', count: counts?.waterBodies },
    { key: 'vegetation', label: 'Vegetation / NDVI Canopy Vigor', color: '#2e7d32' },
    { key: 'elevation', label: 'Elevation & Topographic Slopes', color: '#8d6e63' },
    { key: 'interventions', label: 'Intervention Sites (Check Dams/CCT)', color: '#ea580c', count: counts?.interventions },
    { key: 'fieldPhotos', label: 'Geo-Tagged Field Photo Markers', color: '#9333ea', count: counts?.photos },
  ];

  return (
    <div className="absolute top-4 right-4 z-20 bg-white/95 backdrop-blur-sm rounded-xl border border-slate-200 shadow-lg w-72 overflow-hidden text-xs">
      <div
        className="flex items-center justify-between px-3 py-2.5 bg-slate-50 border-b border-slate-200 cursor-pointer select-none"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center space-x-2">
          <Layers className="h-4 w-4 text-blue-600" />
          <span className="font-bold text-slate-800 uppercase tracking-wide">
            GIS Layer Controls
          </span>
        </div>
        <span className="text-[10px] font-semibold text-slate-500">
          {isOpen ? 'Collapse' : 'Expand'}
        </span>
      </div>

      {isOpen && (
        <div className="p-3 space-y-3">
          {/* Base Map Switcher */}
          <div>
            <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">
              Base Cartography
            </label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => onChange('satellite', false)}
                className={`flex items-center justify-center space-x-1.5 py-1.5 px-2 rounded-md border text-xs font-semibold transition-all ${
                  !visibility.satellite
                    ? 'bg-blue-50 border-blue-500 text-blue-700 shadow-xs'
                    : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                <MapIcon className="h-3.5 w-3.5" />
                <span>Vector Map</span>
              </button>
              <button
                type="button"
                onClick={() => onChange('satellite', true)}
                className={`flex items-center justify-center space-x-1.5 py-1.5 px-2 rounded-md border text-xs font-semibold transition-all ${
                  visibility.satellite
                    ? 'bg-blue-50 border-blue-500 text-blue-700 shadow-xs'
                    : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                <Satellite className="h-3.5 w-3.5" />
                <span>Satellite</span>
              </button>
            </div>
          </div>

          {/* Thematic Overlays */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                Thematic Overlays ({layersConfig.filter(l => visibility[l.key]).length}/{layersConfig.length})
              </label>
              <button
                type="button"
                onClick={onToggleLegend}
                className={`text-[10px] font-semibold px-1.5 py-0.5 rounded transition-colors ${
                  showLegend ? 'bg-blue-100 text-blue-800 font-bold' : 'text-slate-500 hover:bg-slate-100'
                }`}
              >
                {showLegend ? 'Hide Legend' : 'Show Legend'}
              </button>
            </div>

            <div className="space-y-1.5 max-h-56 overflow-y-auto pr-0.5">
              {layersConfig.map(({ key, label, color, count }) => {
                const active = visibility[key];
                return (
                  <label
                    key={key}
                    className="flex items-center justify-between p-1.5 rounded-lg hover:bg-slate-50 cursor-pointer transition-colors border border-transparent hover:border-slate-100"
                  >
                    <div className="flex items-center space-x-2.5 truncate pr-2">
                      <span
                        className="h-2.5 w-2.5 rounded-full shrink-0 border border-black/10"
                        style={{ backgroundColor: color }}
                      />
                      <span className={`truncate text-[11px] font-medium ${active ? 'text-slate-900 font-semibold' : 'text-slate-400'}`}>
                        {label}
                      </span>
                    </div>

                    <div className="flex items-center space-x-2 shrink-0">
                      {count !== undefined && (
                        <span className="text-[10px] px-1.5 py-0.2 bg-slate-100 text-slate-600 rounded font-mono font-semibold">
                          {count}
                        </span>
                      )}
                      <input
                        type="checkbox"
                        checked={active}
                        onChange={(e) => onChange(key, e.target.checked)}
                        className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 h-3.5 w-3.5"
                      />
                    </div>
                  </label>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
