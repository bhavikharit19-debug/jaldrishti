'use client';
import React from 'react';
import { LayerVisibility } from './LayerControl';
import { Layers, Info, X } from 'lucide-react';

interface MapLegendProps {
  visibility: LayerVisibility;
  isOpen: boolean;
  onClose: () => void;
}

export const MapLegend: React.FC<MapLegendProps> = ({ visibility, isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="absolute bottom-6 left-4 z-20 bg-white/95 backdrop-blur-md rounded-xl border border-slate-200 shadow-xl max-w-xs w-72 max-h-72 overflow-y-auto text-xs">
      <div className="flex items-center justify-between px-3 py-2 bg-slate-50 border-b border-slate-200 sticky top-0 z-10">
        <div className="flex items-center space-x-1.5">
          <Layers className="h-3.5 w-3.5 text-blue-600" />
          <span className="font-bold text-slate-800 uppercase tracking-wide text-[11px]">
            Thematic Map Legend
          </span>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="text-slate-400 hover:text-slate-600 p-0.5 rounded"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      </div>

      <div className="p-3 space-y-3">
        {/* 1. Boundary */}
        {visibility.boundary && (
          <div>
            <span className="font-bold text-slate-700 text-[10px] uppercase tracking-wider block mb-1">
              Perimeter Boundary
            </span>
            <div className="flex items-center space-x-2">
              <span className="h-2 w-5 bg-blue-100 border-2 border-dashed border-blue-700 rounded-xs" />
              <span className="text-slate-600 text-[11px]">Catchment Boundary</span>
            </div>
          </div>
        )}

        {/* 2. LULC */}
        {visibility.lulc && (
          <div>
            <span className="font-bold text-slate-700 text-[10px] uppercase tracking-wider block mb-1">
              Land Use / Land Cover (LULC)
            </span>
            <div className="grid grid-cols-1 gap-1 text-[11px]">
              <div className="flex items-center space-x-2">
                <span className="h-2.5 w-2.5 rounded-xs bg-[#8bc34a]" />
                <span className="text-slate-700">Agriculture (Cropland)</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="h-2.5 w-2.5 rounded-xs bg-[#2e7d32]" />
                <span className="text-slate-700">Forest / Ridge Plantation</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="h-2.5 w-2.5 rounded-xs bg-[#0284c7]" />
                <span className="text-slate-700">Water Inundation</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="h-2.5 w-2.5 rounded-xs bg-[#ff7043]" />
                <span className="text-slate-700">Built-up / Settlement</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="h-2.5 w-2.5 rounded-xs bg-[#d4e157]" />
                <span className="text-slate-700">Barren / Rocky Scrub</span>
              </div>
            </div>
          </div>
        )}

        {/* 3. Drainage */}
        {visibility.drainage && (
          <div>
            <span className="font-bold text-slate-700 text-[10px] uppercase tracking-wider block mb-1">
              Drainage Streams
            </span>
            <div className="space-y-1 text-[11px]">
              <div className="flex items-center space-x-2">
                <span className="h-1 w-5 bg-sky-600 rounded" />
                <span className="text-slate-700">Order 3 (Main Nala / River)</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="h-0.75 w-5 bg-sky-500 rounded" />
                <span className="text-slate-700">Order 2 (Tributary Branch)</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="h-0.5 w-5 bg-sky-400 rounded" />
                <span className="text-slate-700">Order 1 (Upper Gully / Torrent)</span>
              </div>
            </div>
          </div>
        )}

        {/* 4. Water Bodies */}
        {visibility.waterBodies && (
          <div>
            <span className="font-bold text-slate-700 text-[10px] uppercase tracking-wider block mb-1">
              Water Bodies & Storage
            </span>
            <div className="flex items-center space-x-2 text-[11px]">
              <span className="h-2.5 w-4 bg-cyan-400 border border-cyan-600 rounded-xs" />
              <span className="text-slate-700">Percolation Tank / Reservoir</span>
            </div>
          </div>
        )}

        {/* 5. Vegetation / NDVI */}
        {visibility.vegetation && (
          <div>
            <span className="font-bold text-slate-700 text-[10px] uppercase tracking-wider block mb-1">
              Vegetation / NDVI Range
            </span>
            <div className="grid grid-cols-1 gap-1 text-[11px]">
              <div className="flex items-center space-x-2">
                <span className="h-2.5 w-2.5 rounded-xs bg-[#1b5e20]" />
                <span className="text-slate-700">Dense Canopy (&gt;0.6)</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="h-2.5 w-2.5 rounded-xs bg-[#4caf50]" />
                <span className="text-slate-700">Moderate Canopy (0.4-0.6)</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="h-2.5 w-2.5 rounded-xs bg-[#cddc39]" />
                <span className="text-slate-700">Low / Scrub (0.2-0.4)</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="h-2.5 w-2.5 rounded-xs bg-[#ffe082]" />
                <span className="text-slate-700">Sparse / Barren (&lt;0.2)</span>
              </div>
            </div>
          </div>
        )}

        {/* 6. Elevation */}
        {visibility.elevation && (
          <div>
            <span className="font-bold text-slate-700 text-[10px] uppercase tracking-wider block mb-1">
              Topographic Hypsometry
            </span>
            <div className="grid grid-cols-1 gap-1 text-[11px]">
              <div className="flex items-center space-x-2">
                <span className="h-2.5 w-2.5 rounded-xs bg-[#5d4037]" />
                <span className="text-slate-700">Ridge Crest (Steep 15-25%)</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="h-2.5 w-2.5 rounded-xs bg-[#8d6e63]" />
                <span className="text-slate-700">Upper Slopes (8-15%)</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="h-2.5 w-2.5 rounded-xs bg-[#bcaaa4]" />
                <span className="text-slate-700">Valley Plain (3-8%)</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="h-2.5 w-2.5 rounded-xs bg-[#d7ccc8]" />
                <span className="text-slate-700">Stream Bed (1-3%)</span>
              </div>
            </div>
          </div>
        )}

        {/* 7. Interventions & Photos */}
        {(visibility.interventions || visibility.fieldPhotos) && (
          <div>
            <span className="font-bold text-slate-700 text-[10px] uppercase tracking-wider block mb-1">
              Field Features
            </span>
            <div className="space-y-1 text-[11px]">
              {visibility.interventions && (
                <div className="flex items-center space-x-2">
                  <span className="h-2.5 w-2.5 rounded-full bg-orange-600 border border-white shadow-xs" />
                  <span className="text-slate-700">Intervention (Check Dam / CCT)</span>
                </div>
              )}
              {visibility.fieldPhotos && (
                <div className="flex items-center space-x-2">
                  <span className="h-2.5 w-2.5 rounded-full bg-purple-600 border border-white shadow-xs" />
                  <span className="text-slate-700">Geo-Tagged Field Photo</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <div className="p-2 bg-slate-50 border-t border-slate-200 text-[10px] text-slate-500 flex items-center space-x-1">
        <Info className="h-3 w-3 text-blue-600 shrink-0" />
        <span>Click features on map for details</span>
      </div>
    </div>
  );
};
