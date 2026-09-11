'use client';
import React, { useEffect, useState } from 'react';
import { WatershedGISStats } from '@/types';
import { api } from '@/services/api';
import {
  Layers,
  Waves,
  Droplets,
  Sprout,
  Mountain,
  FileCheck2,
  Info,
  ChevronDown,
  ChevronUp,
  Database,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

interface GISIntelligencePanelProps {
  watershedId: number;
}

export const GISIntelligencePanel: React.FC<GISIntelligencePanelProps> = ({ watershedId }) => {
  const [stats, setStats] = useState<WatershedGISStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [showIngestionGuide, setShowIngestionGuide] = useState(false);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    api.getWatershedGISStats(watershedId)
      .then((res) => {
        if (isMounted) setStats(res);
      })
      .catch((err) => console.error('Failed to load GIS statistics:', err))
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [watershedId]);

  if (loading) {
    return (
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-center justify-center text-xs text-slate-400">
        Synthesizing GIS layer intelligence and biophysical indicators...
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  const { lulc, drainage, water_bodies, vegetation, elevation } = stats;

  return (
    <div className="space-y-4">
      {/* Top Banner with Provenance Badge */}
      <div className="bg-white p-4 sm:p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <div className="flex items-center space-x-2">
            <Layers className="h-5 w-5 text-blue-700" />
            <h2 className="text-base font-bold text-slate-900">
              Catchment GIS Intelligence & Geospatial Analytics
            </h2>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-100 text-amber-900 border border-amber-300">
              {stats.data_provenance}
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Thematic layer indicators computed for {stats.watershed_name} ({stats.total_area_ha.toLocaleString()} Hectares).
          </p>
        </div>

        <button
          type="button"
          onClick={() => setShowIngestionGuide(!showIngestionGuide)}
          className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold text-blue-700 bg-blue-50 hover:bg-blue-100 rounded-lg border border-blue-200 transition-colors shrink-0"
        >
          <Database className="h-3.5 w-3.5" />
          <span>{showIngestionGuide ? 'Hide Data Readiness' : 'Government Integration Guide'}</span>
          {showIngestionGuide ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
        </button>
      </div>

      {/* Collapsible Ingestion Readiness Guide */}
      {showIngestionGuide && (
        <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-xs space-y-2">
          <div className="flex items-center justify-between border-b border-slate-200 pb-2">
            <span className="font-bold text-slate-800 uppercase tracking-wider">
              SIH 26015 Data Architecture & Integration Readiness
            </span>
            <span className="text-slate-500 font-mono text-[10px]">Cloud-Ready Geospatial Ingestion</span>
          </div>
          <p className="text-slate-600 leading-relaxed">
            The JalDrishti GIS module uses standardized GeoJSON FeatureCollection endpoints. When official
            government feeds become available, the platform can ingest:
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5 pt-1 text-[11px]">
            <div className="bg-white p-2.5 rounded-lg border border-slate-200">
              <span className="font-bold text-blue-700 block">1. ISRO Bhuvan Spatial Services</span>
              <p className="text-slate-500 mt-1">Connects to Bhuvan WFS/WMS vector layers for micro-watershed boundaries and 1:10K LULC.</p>
            </div>
            <div className="bg-white p-2.5 rounded-lg border border-slate-200">
              <span className="font-bold text-blue-700 block">2. Satellite EO Pipelines</span>
              <p className="text-slate-500 mt-1">Directly accepts Sentinel-2, Landsat-8, or Cartosat multi-spectral GeoTIFF raster feeds for NDVI.</p>
            </div>
            <div className="bg-white p-2.5 rounded-lg border border-slate-200">
              <span className="font-bold text-blue-700 block">3. Authorized Field Uploads</span>
              <p className="text-slate-500 mt-1">Accepts ground telemetry, GPS surveys, and geo-tagged EXIF photos with instant boundary validation.</p>
            </div>
          </div>
        </div>
      )}

      {/* Grid of GIS Layers Intelligence */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* 1. LULC Distribution Card */}
        <div className="bg-white p-4 sm:p-5 rounded-xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
            <div className="flex items-center space-x-2">
              <Layers className="h-4 w-4 text-emerald-600" />
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
                Land Use / Land Cover (LULC 5-Class)
              </h3>
            </div>
            <span className="text-[10px] font-semibold text-slate-500">
              Total: {stats.total_area_ha} ha
            </span>
          </div>

          {/* Multi-segment Progress Bar */}
          <div className="w-full h-4 rounded-full overflow-hidden flex bg-slate-100 shadow-inner">
            {lulc.map((cat, i) => (
              <div
                key={i}
                style={{ width: `${cat.percentage}%`, backgroundColor: cat.color }}
                title={`${cat.category}: ${cat.percentage}% (${cat.area_ha} ha)`}
                className="h-full transition-all duration-500"
              />
            ))}
          </div>

          {/* Categories List */}
          <div className="space-y-2 pt-1">
            {lulc.map((cat, i) => (
              <div key={i} className="flex items-center justify-between text-xs py-1 border-b border-slate-50 last:border-none">
                <div className="flex items-center space-x-2 truncate pr-2">
                  <span className="h-3 w-3 rounded-xs shrink-0" style={{ backgroundColor: cat.color }} />
                  <span className="font-bold text-slate-800">{cat.category}</span>
                  {cat.description && (
                    <span className="text-[10px] text-slate-400 truncate hidden sm:inline">
                      — {cat.description}
                    </span>
                  )}
                </div>
                <div className="text-right shrink-0">
                  <span className="font-extrabold text-slate-900">{cat.percentage}%</span>
                  <span className="text-[10px] text-slate-400 ml-1 font-mono">({cat.area_ha} ha)</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 2. Drainage & Hydrology Card */}
        <div className="bg-white p-4 sm:p-5 rounded-xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
            <div className="flex items-center space-x-2">
              <Waves className="h-4 w-4 text-sky-600" />
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
                Drainage Network & Stream Morphometry
              </h3>
            </div>
            <span className="text-[10px] font-semibold text-slate-500">
              {drainage.total_streams} Stream Segments
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="bg-sky-50/60 p-3 rounded-lg border border-sky-100">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                Total Channel Length
              </span>
              <span className="text-lg font-black text-sky-950 mt-0.5 block">
                {drainage.total_length_km} km
              </span>
              <span className="text-[10px] text-slate-500">Across stream hierarchy</span>
            </div>

            <div className="bg-sky-50/60 p-3 rounded-lg border border-sky-100">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                Drainage Density
              </span>
              <span className="text-lg font-black text-sky-950 mt-0.5 block">
                {drainage.density_km_per_sqkm} km/km²
              </span>
              <span className="text-[10px] text-slate-500">Hydrological runoff index</span>
            </div>
          </div>

          <div className="pt-2">
            <span className="text-[11px] font-bold text-slate-700 block mb-1.5">
              Stream Order Hierarchy (Horton-Strahler):
            </span>
            <div className="grid grid-cols-3 gap-2 text-center text-xs">
              {Object.entries(drainage.order_counts).map(([order, count]) => (
                <div key={order} className="bg-slate-50 p-2 rounded border border-slate-200">
                  <span className="font-extrabold text-blue-800 text-sm block">{count}</span>
                  <span className="text-[10px] text-slate-500 font-medium">{order}</span>
                </div>
              ))}
            </div>
            <div className="mt-2 text-[11px] text-slate-500 flex items-center justify-between">
              <span>Main Watercourse:</span>
              <span className="font-bold text-slate-800">{drainage.primary_stream}</span>
            </div>
          </div>
        </div>

        {/* 3. Water Bodies & Surface Storage Card */}
        <div className="bg-white p-4 sm:p-5 rounded-xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
            <div className="flex items-center space-x-2">
              <Droplets className="h-4 w-4 text-cyan-600" />
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
                Water Bodies & Surface Storage
              </h3>
            </div>
            <span className="text-[10px] font-semibold text-slate-500">
              {water_bodies.total_count} Structures Catalogued
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="bg-cyan-50/60 p-3 rounded-lg border border-cyan-100">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                Cumulative Capacity
              </span>
              <span className="text-lg font-black text-cyan-950 mt-0.5 block">
                {water_bodies.cumulative_capacity_tcm} TCM
              </span>
              <span className="text-[10px] text-slate-500">Thousand Cubic Meters</span>
            </div>

            <div className="bg-cyan-50/60 p-3 rounded-lg border border-cyan-100">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                Water Spread Area
              </span>
              <span className="text-lg font-black text-cyan-950 mt-0.5 block">
                {water_bodies.total_spread_ha} ha
              </span>
              <span className="text-[10px] text-slate-500">Post-monsoon water spread</span>
            </div>
          </div>

          <div className="pt-2">
            <span className="text-[11px] font-bold text-slate-700 block mb-1.5">
              Structures by Category:
            </span>
            <div className="space-y-1 text-xs">
              {Object.entries(water_bodies.structures_by_type).map(([type, cnt]) => (
                <div key={type} className="flex justify-between items-center py-1 border-b border-slate-50 last:border-none">
                  <span className="text-slate-600 font-medium">{type}</span>
                  <span className="font-extrabold text-cyan-800">{cnt} structure{cnt !== 1 ? 's' : ''}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 4. Vegetation / NDVI Canopy Vigor Card */}
        <div className="bg-white p-4 sm:p-5 rounded-xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
            <div className="flex items-center space-x-2">
              <Sprout className="h-4 w-4 text-green-700" />
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
                Vegetation Index (NDVI) & Canopy Vigor
              </h3>
            </div>
            <span className="text-[10px] font-bold px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded">
              {vegetation.vigor_class}
            </span>
          </div>

          <div className="flex items-center space-x-4 bg-emerald-50/50 p-3 rounded-lg border border-emerald-100">
            <div className="text-center shrink-0 pr-3 border-r border-emerald-200">
              <span className="text-[10px] font-bold text-slate-500 uppercase block">Mean NDVI</span>
              <span className="text-2xl font-black text-emerald-900 mt-0.5 block">
                {vegetation.mean_ndvi}
              </span>
              <span className="text-[10px] text-slate-400">Scale (-0.2 to 1.0)</span>
            </div>
            <div className="text-xs text-slate-600 leading-snug">
              Earth Observation index synthesized from Sentinel-2 red and near-infrared reflectance bands.
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center text-xs pt-1">
            <div className="p-2 bg-slate-50 rounded border border-slate-200">
              <span className="font-black text-emerald-800 block">{vegetation.dense_pct}%</span>
              <span className="text-[10px] text-slate-500">Dense (&gt;0.6)</span>
            </div>
            <div className="p-2 bg-slate-50 rounded border border-slate-200">
              <span className="font-black text-green-700 block">{vegetation.moderate_pct}%</span>
              <span className="text-[10px] text-slate-500">Moderate (0.4-0.6)</span>
            </div>
            <div className="p-2 bg-slate-50 rounded border border-slate-200">
              <span className="font-black text-amber-700 block">{vegetation.low_pct}%</span>
              <span className="text-[10px] text-slate-500">Low (0.2-0.4)</span>
            </div>
            <div className="p-2 bg-slate-50 rounded border border-slate-200">
              <span className="font-black text-rose-700 block">{vegetation.sparse_pct}%</span>
              <span className="text-[10px] text-slate-500">Sparse (&lt;0.2)</span>
            </div>
          </div>
        </div>
      </div>

      {/* 5. Topographic Elevation & Relief Profile Card */}
      <div className="bg-white p-4 sm:p-5 rounded-xl border border-slate-200 shadow-sm space-y-3">
        <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
          <div className="flex items-center space-x-2">
            <Mountain className="h-4 w-4 text-amber-700" />
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
              Topographic Elevation & Slope Gradient Analysis
            </h3>
          </div>
          <span className="text-xs text-slate-500 font-semibold">
            Dominant: {elevation.dominant_slope_class}
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="bg-amber-50/50 p-3 rounded-lg border border-amber-100 text-center">
            <span className="text-[10px] font-bold text-slate-500 uppercase block">Elevation Range</span>
            <span className="text-base font-extrabold text-amber-950 mt-0.5 block">
              {elevation.min_elevation_m} — {elevation.max_elevation_m} m
            </span>
            <span className="text-[10px] text-slate-400">Above Mean Sea Level (MSL)</span>
          </div>

          <div className="bg-amber-50/50 p-3 rounded-lg border border-amber-100 text-center">
            <span className="text-[10px] font-bold text-slate-500 uppercase block">Catchment Relief</span>
            <span className="text-base font-extrabold text-amber-950 mt-0.5 block">
              {elevation.relief_m} meters
            </span>
            <span className="text-[10px] text-slate-400">Vertical fall from ridge to outlet</span>
          </div>

          <div className="bg-amber-50/50 p-3 rounded-lg border border-amber-100 text-center">
            <span className="text-[10px] font-bold text-slate-500 uppercase block">Hydrological Gradient</span>
            <span className="text-base font-extrabold text-amber-950 mt-0.5 block">
              {elevation.dominant_slope_class.split(' ')[0]}
            </span>
            <span className="text-[10px] text-slate-400">Slope propensity class</span>
          </div>
        </div>

        {/* Elevation Bands Breakdown Table */}
        {elevation.elevation_bands && elevation.elevation_bands.length > 0 && (
          <div className="pt-2">
            <span className="text-[11px] font-bold text-slate-700 block mb-1.5">
              Hypsometric Elevation Zones & Slopes:
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2">
              {elevation.elevation_bands.map((band, idx) => (
                <div key={idx} className="p-2.5 rounded-lg border border-slate-200 bg-slate-50 text-xs flex flex-col justify-between">
                  <div>
                    <div className="flex items-center space-x-1.5 mb-1">
                      <span className="h-2.5 w-2.5 rounded-xs shrink-0" style={{ backgroundColor: band.color }} />
                      <span className="font-bold text-slate-800 text-[11px]">{band.band_name}</span>
                    </div>
                    <span className="text-[10px] text-slate-500 block font-mono">{band.elevation_range_m}</span>
                  </div>
                  <div className="mt-2 pt-1 border-t border-slate-200/60 flex items-center justify-between text-[10px]">
                    <span className="text-slate-400">{band.slope_class}</span>
                    <span className="font-bold text-slate-700">{band.percentage}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Mandatory Provenance & Disclaimer Notice */}
      <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs text-slate-600 flex items-start space-x-2">
        <Info className="h-4 w-4 text-slate-500 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold text-slate-800">Dataset Provenance: </span>
          {stats.disclaimer}
        </div>
      </div>
    </div>
  );
};
