'use client';
import React from 'react';
import { Layers, Droplets, Waves, Sprout, Mountain, Hammer, ArrowRight, ShieldCheck, Info } from 'lucide-react';

export interface FeaturePopupData {
  layerType: 'DRAINAGE' | 'WATER_BODIES' | 'LULC' | 'VEGETATION_NDVI' | 'ELEVATION' | 'INTERVENTIONS';
  properties: Record<string, any>;
}

interface FeaturePopupProps {
  data: FeaturePopupData;
  onClose?: () => void;
}

export const FeaturePopup: React.FC<FeaturePopupProps> = ({ data, onClose }) => {
  const { layerType, properties } = data;

  const getHeader = () => {
    switch (layerType) {
      case 'DRAINAGE':
        return {
          title: properties.name || 'Stream Channel',
          subtitle: `Stream Order ${properties.order || 1}`,
          badge: `Length: ${properties.length_km || '—'} km`,
          icon: <Waves className="h-4 w-4 text-sky-600" />,
          color: 'bg-sky-50 border-sky-200 text-sky-900'
        };
      case 'WATER_BODIES':
        return {
          title: properties.name || 'Water Retention Structure',
          subtitle: properties.type || 'Surface Water Body',
          badge: `Cap: ${properties.capacity_tcm || '—'} TCM`,
          icon: <Droplets className="h-4 w-4 text-cyan-600" />,
          color: 'bg-cyan-50 border-cyan-200 text-cyan-900'
        };
      case 'LULC':
        return {
          title: properties.class || 'Land Cover Classification',
          subtitle: 'Sentinel-2 LULC Class',
          badge: `${properties.area_ha || '—'} ha`,
          icon: <Layers className="h-4 w-4 text-emerald-600" />,
          color: 'bg-emerald-50 border-emerald-200 text-emerald-900'
        };
      case 'VEGETATION_NDVI':
        return {
          title: properties.ndvi_class || 'NDVI Canopy Vigor',
          subtitle: `Mean NDVI: ${properties.mean_ndvi || '—'}`,
          badge: `${properties.area_ha || '—'} ha`,
          icon: <Sprout className="h-4 w-4 text-green-700" />,
          color: 'bg-green-50 border-green-200 text-green-900'
        };
      case 'ELEVATION':
        return {
          title: properties.zone_name || 'Hypsometric Contour',
          subtitle: `Elevation: ${properties.contour_m || '—'} m MSL`,
          badge: `Slope: ${properties.slope_pct || '—'}`,
          icon: <Mountain className="h-4 w-4 text-amber-700" />,
          color: 'bg-amber-50 border-amber-200 text-amber-900'
        };
      case 'INTERVENTIONS':
        return {
          title: properties.name || 'Watershed Structure',
          subtitle: properties.type || 'Intervention',
          badge: properties.status || 'Active',
          icon: <Hammer className="h-4 w-4 text-orange-600" />,
          color: 'bg-orange-50 border-orange-200 text-orange-900'
        };
      default:
        return {
          title: 'Spatial Feature',
          subtitle: 'Vector Attribute',
          badge: 'GIS Layer',
          icon: <Info className="h-4 w-4 text-slate-600" />,
          color: 'bg-slate-50 border-slate-200 text-slate-900'
        };
    }
  };

  const header = getHeader();

  return (
    <div className="w-68 bg-white rounded-xl shadow-xl overflow-hidden font-sans text-xs border border-slate-200">
      {/* Header bar */}
      <div className={`p-3 border-b flex items-start justify-between ${header.color}`}>
        <div className="flex items-center space-x-2">
          {header.icon}
          <div>
            <h4 className="font-extrabold text-xs text-slate-900 leading-tight">
              {header.title}
            </h4>
            <span className="text-[10px] text-slate-600 font-medium block">
              {header.subtitle}
            </span>
          </div>
        </div>
        <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-white/80 border border-slate-200 text-slate-800 shadow-xs">
          {header.badge}
        </span>
      </div>

      {/* Attributes table */}
      <div className="p-3 space-y-2 max-h-52 overflow-y-auto">
        {layerType === 'DRAINAGE' && (
          <div className="space-y-1.5 text-[11px]">
            <div className="flex justify-between py-0.5 border-b border-slate-100">
              <span className="text-slate-500">Flow Direction:</span>
              <span className="font-semibold text-slate-800">{properties.flow_direction || 'Down-gradient'}</span>
            </div>
            <div className="flex justify-between py-0.5 border-b border-slate-100">
              <span className="text-slate-500">Channel Gradient:</span>
              <span className="font-semibold text-slate-800">{properties.gradient || '1.5%'}</span>
            </div>
            <div className="flex justify-between py-0.5">
              <span className="text-slate-500">Classification:</span>
              <span className="font-bold text-sky-700">Order {properties.order || 1} Stream</span>
            </div>
          </div>
        )}

        {layerType === 'WATER_BODIES' && (
          <div className="space-y-1.5 text-[11px]">
            <div className="flex justify-between py-0.5 border-b border-slate-100">
              <span className="text-slate-500">Surface Spread:</span>
              <span className="font-semibold text-slate-800">{properties.spread_area_ha || '—'} Hectares</span>
            </div>
            <div className="flex justify-between py-0.5 border-b border-slate-100">
              <span className="text-slate-500">Storage Capacity:</span>
              <span className="font-semibold text-slate-800">{properties.capacity_tcm || '—'} TCM (Thousand m³)</span>
            </div>
            <div className="flex justify-between py-0.5">
              <span className="text-slate-500">Maximum Depth:</span>
              <span className="font-semibold text-slate-800">{properties.max_depth_m || '—'} meters</span>
            </div>
          </div>
        )}

        {layerType === 'LULC' && (
          <div className="space-y-1.5 text-[11px]">
            <div className="flex items-center space-x-2 py-0.5 border-b border-slate-100">
              <span className="h-3 w-3 rounded-full shrink-0" style={{ backgroundColor: properties.color || '#9e9e9e' }} />
              <span className="font-extrabold text-slate-900">{properties.class}</span>
            </div>
            <p className="text-slate-600 text-[10px] leading-relaxed py-0.5">
              {properties.description || 'Land cover parcel mapped from multi-spectral imagery.'}
            </p>
            <div className="flex justify-between py-0.5 border-t border-slate-100">
              <span className="text-slate-500">Estimated Area:</span>
              <span className="font-bold text-slate-800">{properties.area_ha} ha</span>
            </div>
          </div>
        )}

        {layerType === 'VEGETATION_NDVI' && (
          <div className="space-y-1.5 text-[11px]">
            <div className="flex justify-between py-0.5 border-b border-slate-100">
              <span className="text-slate-500">Canopy Status:</span>
              <span className="font-bold text-emerald-800">{properties.status || 'Active Photosynthesis'}</span>
            </div>
            <div className="flex justify-between py-0.5 border-b border-slate-100">
              <span className="text-slate-500">Mean Index:</span>
              <span className="font-mono font-extrabold text-emerald-700">{properties.mean_ndvi}</span>
            </div>
            <div className="flex justify-between py-0.5">
              <span className="text-slate-500">Zone Extent:</span>
              <span className="font-semibold text-slate-800">{properties.area_ha} ha</span>
            </div>
          </div>
        )}

        {layerType === 'ELEVATION' && (
          <div className="space-y-1.5 text-[11px]">
            <div className="flex justify-between py-0.5 border-b border-slate-100">
              <span className="text-slate-500">Topographic Band:</span>
              <span className="font-semibold text-slate-800">{properties.zone_name}</span>
            </div>
            <div className="flex justify-between py-0.5 border-b border-slate-100">
              <span className="text-slate-500">Slope Gradient:</span>
              <span className="font-semibold text-slate-800">{properties.slope_pct}</span>
            </div>
            {properties.treatment && (
              <div className="py-0.5">
                <span className="text-slate-500 block text-[10px]">Recommended Treatment:</span>
                <span className="font-bold text-amber-900 text-[10px]">{properties.treatment}</span>
              </div>
            )}
          </div>
        )}

        {layerType === 'INTERVENTIONS' && (
          <div className="space-y-1.5 text-[11px]">
            <div className="flex justify-between py-0.5 border-b border-slate-100">
              <span className="text-slate-500">Beneficiary Count:</span>
              <span className="font-semibold text-slate-800">{properties.beneficiaries || '—'} farmers</span>
            </div>
            <div className="flex justify-between py-0.5">
              <span className="text-slate-500">Structure Type:</span>
              <span className="font-bold text-orange-800">{properties.type}</span>
            </div>
          </div>
        )}
      </div>

      <div className="px-3 py-1.5 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-400">
        <span>Click anywhere to dismiss</span>
        <span className="font-mono font-semibold text-blue-700">SIH 26015 GIS</span>
      </div>
    </div>
  );
};
