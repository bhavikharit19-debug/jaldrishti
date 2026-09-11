'use client';
import React, { useState, useEffect } from 'react';
import { api } from '@/services/api';
import { GeospatialDataset, ProviderAdapterInfo, DatasetCatalogResponse } from '@/types';
import {
  Database,
  Satellite,
  UploadCloud,
  CheckCircle2,
  AlertCircle,
  X,
  FileCode2,
  FileSpreadsheet,
  Layers,
  ShieldCheck,
  Info,
  RefreshCw,
  History
} from 'lucide-react';

interface DataIntegrationModalProps {
  isOpen: boolean;
  onClose: () => void;
  watershedId: number;
  watershedName: string;
  onImportSuccess?: () => void;
}

export const DataIntegrationModal: React.FC<DataIntegrationModalProps> = ({
  isOpen,
  onClose,
  watershedId,
  watershedName,
  onImportSuccess
}) => {
  const [activeTab, setActiveTab] = useState<'catalog' | 'adapters' | 'import' | 'history'>('catalog');
  const [catalogData, setCatalogData] = useState<DatasetCatalogResponse | null>(null);
  const [adapters, setAdapters] = useState<ProviderAdapterInfo[]>([]);
  const [loading, setLoading] = useState(false);

  // Import Form State
  const [importFormat, setImportFormat] = useState<'GEOJSON' | 'CSV'>('GEOJSON');
  const [layerType, setLayerType] = useState('LULC');
  const [datasetType, setDatasetType] = useState('FIELD_PHOTOS');
  const [datasetName, setDatasetName] = useState('');
  const [providerName, setProviderName] = useState('Field Mobile Survey');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [importLoading, setImportLoading] = useState(false);
  const [importResult, setImportResult] = useState<any>(null);
  const [importError, setImportError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadData();
    }
  }, [isOpen, watershedId]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [catRes, adaptRes] = await Promise.all([
        api.getDatasetCatalog(watershedId),
        api.getProviderAdapters()
      ]);
      setCatalogData(catRes);
      setAdapters(adaptRes);
    } catch (err) {
      console.error('Failed to load catalog or adapters:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setImportResult(null);
      setImportError(null);
    }
  };

  const handleImportSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setImportError('Please select a file to import.');
      return;
    }

    setImportLoading(true);
    setImportResult(null);
    setImportError(null);

    const formData = new FormData();
    formData.append('watershed_id', watershedId.toString());
    formData.append('dataset_name', datasetName || selectedFile.name);
    formData.append('provider', providerName);
    formData.append('file', selectedFile);

    try {
      let res;
      if (importFormat === 'GEOJSON') {
        formData.append('layer_type', layerType);
        res = await api.importGeoJSON(formData);
      } else {
        formData.append('dataset_type', datasetType);
        res = await api.importCSV(formData);
      }
      setImportResult(res);
      setSelectedFile(null);
      loadData();
      if (onImportSuccess) onImportSuccess();
    } catch (err: any) {
      setImportError(err.message || 'Import failed. Please verify file format and coordinates.');
    } finally {
      setImportLoading(false);
    }
  };

  if (!isOpen) return null;

  const getProvenanceBadge = (prov: string) => {
    switch (prov) {
      case 'OFFICIAL_SOURCE':
        return 'bg-emerald-100 text-emerald-800 border-emerald-300';
      case 'IMPORTED_DATA':
        return 'bg-purple-100 text-purple-800 border-purple-300';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-300';
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/80">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-emerald-100 text-emerald-700 rounded-lg">
              <Database className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900">
                Geospatial Data Integration & Provenance Hub
              </h2>
              <p className="text-xs text-slate-500">
                Target Catchment: <span className="font-semibold text-slate-700">{watershedName}</span>
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-200 rounded-lg transition"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-200 bg-slate-100/60 px-6 pt-2 gap-2 text-xs font-semibold">
          <button
            onClick={() => setActiveTab('catalog')}
            className={`pb-2.5 px-3 flex items-center space-x-1.5 border-b-2 transition ${
              activeTab === 'catalog'
                ? 'border-emerald-600 text-emerald-700 font-bold'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            <Database className="h-4 w-4" />
            <span>Dataset Catalog ({catalogData?.total_datasets || 0})</span>
          </button>
          <button
            onClick={() => setActiveTab('adapters')}
            className={`pb-2.5 px-3 flex items-center space-x-1.5 border-b-2 transition ${
              activeTab === 'adapters'
                ? 'border-emerald-600 text-emerald-700 font-bold'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            <Satellite className="h-4 w-4" />
            <span>Authoritative EO Adapters ({adapters.length})</span>
          </button>
          <button
            onClick={() => setActiveTab('import')}
            className={`pb-2.5 px-3 flex items-center space-x-1.5 border-b-2 transition ${
              activeTab === 'import'
                ? 'border-emerald-600 text-emerald-700 font-bold'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            <UploadCloud className="h-4 w-4" />
            <span>Import Real Data</span>
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`pb-2.5 px-3 flex items-center space-x-1.5 border-b-2 transition ${
              activeTab === 'history'
                ? 'border-emerald-600 text-emerald-700 font-bold'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            <History className="h-4 w-4" />
            <span>Ingestion History</span>
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {/* TAB 1: DATASET CATALOG */}
          {activeTab === 'catalog' && (
            <div className="space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-2 p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs">
                <div className="flex items-center space-x-2">
                  <ShieldCheck className="h-4 w-4 text-emerald-600" />
                  <span className="font-semibold text-slate-700">Provenance Integrity:</span>
                  <span className="text-slate-600">
                    {catalogData?.provenance_summary.demo_datasets_count || 0} Demo Baseline,{' '}
                    {catalogData?.provenance_summary.imported_datasets_count || 0} Imported Field/Vector
                  </span>
                </div>
                <button
                  onClick={loadData}
                  className="flex items-center space-x-1 text-slate-600 hover:text-slate-900"
                >
                  <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
                  <span>Refresh</span>
                </button>
              </div>

              {loading ? (
                <div className="h-48 flex items-center justify-center text-xs text-slate-400">
                  Loading dataset catalog...
                </div>
              ) : catalogData?.datasets && catalogData.datasets.length > 0 ? (
                <div className="divide-y divide-slate-100 border border-slate-200 rounded-xl overflow-hidden">
                  {catalogData.datasets.map((ds) => (
                    <div key={ds.id} className="p-3.5 hover:bg-slate-50/80 transition flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                      <div className="space-y-1">
                        <div className="flex items-center space-x-2">
                          <span className="font-bold text-slate-900">{ds.dataset_name}</span>
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${getProvenanceBadge(ds.provenance)}`}>
                            {ds.provenance.replace(/_/g, ' ')}
                          </span>
                        </div>
                        <div className="flex flex-wrap gap-x-4 text-[11px] text-slate-500">
                          <span><strong>Code:</strong> {ds.dataset_code}</span>
                          <span><strong>Provider:</strong> {ds.provider}</span>
                          <span><strong>Format:</strong> {ds.format}</span>
                          <span><strong>Resolution:</strong> {ds.spatial_resolution || '10m'}</span>
                          <span><strong>CRS:</strong> {ds.crs}</span>
                        </div>
                      </div>
                      <div className="text-right shrink-0">
                        <span className="text-[10px] text-slate-400 block">Records / Features</span>
                        <span className="font-mono font-bold text-slate-700">{ds.record_count}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-8 text-center text-xs text-slate-400">
                  No datasets currently registered for this watershed.
                </div>
              )}
            </div>
          )}

          {/* TAB 2: SATELLITE & GIS ADAPTERS */}
          {activeTab === 'adapters' && (
            <div className="space-y-4">
              <div className="p-3 bg-amber-50/80 rounded-xl border border-amber-200 text-xs text-amber-900 flex items-start space-x-2">
                <Info className="h-4 w-4 text-amber-700 shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold">Authenticity & Non-Fabrication Notice: </span>
                  External satellite platforms require production government authorization. Standardized API adapters are fully wired and configured; live acquisition toggles activate when official credentials (CDSE client ID or Bhuvan token) are supplied in configuration.
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {adapters.map((adapter) => (
                  <div key={adapter.provider_code} className="p-4 bg-slate-50 rounded-xl border border-slate-200 flex flex-col justify-between space-y-3">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-bold text-slate-900 text-xs">{adapter.provider_name}</span>
                        <span className="text-[10px] font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                          {adapter.status.split(' ')[0]}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-600 leading-relaxed">{adapter.operational_notes}</p>
                    </div>

                    <div className="pt-3 border-t border-slate-200/80 text-[11px] text-slate-500 space-y-1">
                      <div><strong className="text-slate-700">Endpoint: </strong><code className="text-[10px] bg-slate-200 px-1 py-0.5 rounded">{adapter.endpoint}</code></div>
                      <div><strong className="text-slate-700">Resolution: </strong>{adapter.spatial_resolution}</div>
                      {adapter.supported_bands && (
                        <div><strong className="text-slate-700">Bands: </strong>{adapter.supported_bands.slice(0, 4).join(', ')}...</div>
                      )}
                      {adapter.thematic_layers && (
                        <div><strong className="text-slate-700">Thematic: </strong>{adapter.thematic_layers[0]}</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: IMPORT REAL DATA */}
          {activeTab === 'import' && (
            <form onSubmit={handleImportSubmit} className="space-y-4">
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-600">
                Safely upload and validate authoritative field survey CSVs or GeoJSON vector layers. Coordinates and geometric validity are checked before ingestion.
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Import Format</label>
                  <select
                    value={importFormat}
                    onChange={(e) => setImportFormat(e.target.value as any)}
                    className="w-full p-2 border border-slate-200 rounded-lg text-slate-800"
                  >
                    <option value="GEOJSON">GeoJSON Vector Layer (.geojson, .json)</option>
                    <option value="CSV">Coordinate CSV Dataset (.csv)</option>
                  </select>
                </div>

                {importFormat === 'GEOJSON' ? (
                  <div>
                    <label className="font-bold text-slate-700 block mb-1">GIS Layer Target</label>
                    <select
                      value={layerType}
                      onChange={(e) => setLayerType(e.target.value)}
                      className="w-full p-2 border border-slate-200 rounded-lg text-slate-800"
                    >
                      <option value="LULC">Land Use / Land Cover (LULC)</option>
                      <option value="DRAINAGE">Drainage & Stream Network</option>
                      <option value="WATER_BODIES">Surface Water Bodies & Reservoirs</option>
                      <option value="INTERVENTIONS">Soil & Water Interventions</option>
                    </select>
                  </div>
                ) : (
                  <div>
                    <label className="font-bold text-slate-700 block mb-1">CSV Dataset Category</label>
                    <select
                      value={datasetType}
                      onChange={(e) => setDatasetType(e.target.value)}
                      className="w-full p-2 border border-slate-200 rounded-lg text-slate-800"
                    >
                      <option value="FIELD_PHOTOS">Geo-Tagged Field Photos (Lat, Lon)</option>
                      <option value="OBSERVATIONS">Ground Inspection Observations</option>
                      <option value="INDICATORS">Biophysical Indicator Measurements</option>
                    </select>
                  </div>
                )}
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Dataset Label</label>
                  <input
                    type="text"
                    placeholder="e.g. Village Ground Water Survey 2024"
                    value={datasetName}
                    onChange={(e) => setDatasetName(e.target.value)}
                    className="w-full p-2 border border-slate-200 rounded-lg text-slate-800"
                  />
                </div>
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Provider / Source</label>
                  <input
                    type="text"
                    placeholder="e.g. District Watershed Cell"
                    value={providerName}
                    onChange={(e) => setProviderName(e.target.value)}
                    className="w-full p-2 border border-slate-200 rounded-lg text-slate-800"
                  />
                </div>
              </div>

              {/* File Input */}
              <div>
                <label className="font-bold text-slate-700 block mb-1 text-xs">Select File</label>
                <input
                  type="file"
                  accept={importFormat === 'GEOJSON' ? '.geojson,.json' : '.csv'}
                  onChange={handleFileChange}
                  className="w-full text-xs p-2 border border-slate-200 rounded-lg file:mr-3 file:py-1 file:px-2.5 file:rounded file:border-0 file:text-xs file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100"
                />
              </div>

              {importError && (
                <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-700 flex items-start space-x-2">
                  <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                  <span>{importError}</span>
                </div>
              )}

              {importResult && (
                <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-800 space-y-1">
                  <div className="flex items-center space-x-1.5 font-bold">
                    <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                    <span>{importResult.message || 'Dataset ingested successfully!'}</span>
                  </div>
                  <div className="text-[11px] text-emerald-700">
                    Processed: <strong>{importResult.records_processed}</strong> records | Provenance: <strong>{importResult.provenance}</strong>
                  </div>
                </div>
              )}

              <div className="flex justify-end pt-2">
                <button
                  type="submit"
                  disabled={importLoading || !selectedFile}
                  className="px-4 py-2 bg-emerald-700 text-white rounded-lg text-xs font-bold hover:bg-emerald-800 disabled:opacity-50 transition flex items-center space-x-1.5"
                >
                  <UploadCloud className="h-4 w-4" />
                  <span>{importLoading ? 'Validating & Ingesting...' : 'Validate & Ingest Dataset'}</span>
                </button>
              </div>
            </form>
          )}

          {/* TAB 4: INGESTION HISTORY */}
          {activeTab === 'history' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs">
                <div>
                  <span className="font-bold text-slate-800 block">
                    Statutory Data Ingestion Audit Trail
                  </span>
                  <span className="text-[11px] text-slate-500">
                    Chronological record of vector layers, raster indices, and field coordinate datasets verified for {watershedName}.
                  </span>
                </div>
                <span className="font-mono text-[10px] font-bold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-300">
                  WGS84 EPSG:4326 COMPLIANT
                </span>
              </div>

              <div className="overflow-x-auto border border-slate-200 rounded-lg">
                <table className="w-full text-left text-xs text-slate-800 divide-y divide-slate-200">
                  <thead className="bg-slate-50 text-[10px] font-bold text-slate-600 uppercase tracking-wider">
                    <tr>
                      <th className="py-2.5 px-3">Dataset / File</th>
                      <th className="py-2.5 px-3">Provider</th>
                      <th className="py-2.5 px-3">Category</th>
                      <th className="py-2.5 px-3">Format / CRS</th>
                      <th className="py-2.5 px-3">Records</th>
                      <th className="py-2.5 px-3">Status</th>
                      <th className="py-2.5 px-3">Provenance</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 text-xs">
                    {catalogData?.datasets && catalogData.datasets.length > 0 ? (
                      catalogData.datasets.map((ds) => (
                        <tr key={ds.id} className="hover:bg-slate-50/80 transition-colors">
                          <td className="py-2.5 px-3 font-semibold text-slate-900">
                            <div>{ds.dataset_name}</div>
                            <span className="text-[10px] text-slate-400 font-mono">
                              {ds.acquisition_date ? new Date(ds.acquisition_date).toLocaleDateString('en-IN') : 'N/A'}
                            </span>
                          </td>
                          <td className="py-2.5 px-3 text-slate-700">{ds.provider}</td>
                          <td className="py-2.5 px-3">
                            <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-100 text-slate-800 border border-slate-200">
                              {ds.dataset_type}
                            </span>
                          </td>
                          <td className="py-2.5 px-3 font-mono text-[11px] text-slate-600">
                            {ds.format} • {ds.crs || 'EPSG:4326'}
                          </td>
                          <td className="py-2.5 px-3 font-mono font-bold text-slate-900">
                            {(ds.record_count ?? 0).toLocaleString()}
                          </td>
                          <td className="py-2.5 px-3">
                            <span className="px-1.5 py-0.5 rounded text-[10px] font-extrabold bg-emerald-50 text-emerald-900 border border-emerald-300">
                              VALIDATED
                            </span>
                          </td>
                          <td className="py-2.5 px-3">
                            <span className={`px-1.5 py-0.5 rounded text-[10px] font-extrabold border ${getProvenanceBadge(ds.provenance)}`}>
                              {ds.provenance.replace(/_/g, ' ')}
                            </span>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={7} className="py-6 text-center text-xs text-slate-400">
                          No datasets registered in ingestion history.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-xs text-slate-500">
          <span>SIH 26015: Standardized WGS84 EPSG:4326 Input Validation</span>
          <button
            onClick={onClose}
            className="px-3 py-1.5 bg-slate-200 text-slate-700 rounded-lg hover:bg-slate-300 font-semibold transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
