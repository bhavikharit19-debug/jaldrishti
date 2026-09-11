'use client';
import React, { useState } from 'react';
import { FieldPhoto } from '@/types';
import { api } from '@/services/api';
import { Camera, Upload, X, MapPin, Calendar, CheckCircle2, AlertCircle, Eye, Table, Grid } from 'lucide-react';

interface FieldPhotosModalProps {
  watershedId: number;
  photos: FieldPhoto[];
  isOpen: boolean;
  onClose: () => void;
  onPhotoUploaded: () => void;
}

/**
 * FieldPhotosModal
 * 
 * Field Evidence & Ground Truth Verification:
 * Government field-monitoring table with image inspection, GNSS coordinates,
 * category, description, and departmental verification status.
 */
export const FieldPhotosModal: React.FC<FieldPhotosModalProps> = ({
  watershedId,
  photos,
  isOpen,
  onClose,
  onPhotoUploaded
}) => {
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [viewMode, setViewMode] = useState<'table' | 'gallery'>('table');
  const [selectedPhoto, setSelectedPhoto] = useState<FieldPhoto | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string>('ALL');
  const [verificationFilter, setVerificationFilter] = useState<string>('ALL');

  // Form State
  const [photoUrl, setPhotoUrl] = useState('');
  const [category, setCategory] = useState('CHECK_DAM');
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!photoUrl || !latitude || !longitude) return;

    setIsSubmitting(true);
    try {
      await api.uploadPhoto({
        watershed_id: watershedId,
        latitude: parseFloat(latitude),
        longitude: parseFloat(longitude),
        photo_url: photoUrl,
        category,
        description,
        exif_metadata: {
          captured_via: 'Field Officer Inspection Terminal',
          gps_source: 'Differential GNSS Mobile Device'
        }
      });
      onPhotoUploaded();
      setShowUploadForm(false);
      setPhotoUrl('');
      setDescription('');
    } catch (err) {
      console.error('Photo upload failed:', err);
      alert('Failed to ingest field inspection record.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const filteredPhotos = photos.filter((p) => {
    if (categoryFilter !== 'ALL' && p.category !== categoryFilter) return false;
    if (verificationFilter !== 'ALL' && p.verification_status !== verificationFilter) return false;
    return true;
  });

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-xs flex items-center justify-center p-4 select-none font-sans">
      <div className="bg-white border border-slate-300 rounded shadow-2xl max-w-5xl w-full max-h-[90vh] flex flex-col overflow-hidden">
        {/* Modal Header */}
        <div className="px-5 py-3 border-b border-slate-300 flex items-center justify-between bg-slate-100">
          <div className="flex items-center space-x-2">
            <Camera className="h-4 w-4 text-blue-900" />
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
              Field Evidence &amp; Ground Truth Register ({photos.length} Records)
            </h2>
            <span className="text-[10px] font-mono font-bold bg-amber-50 text-amber-900 border border-amber-300 px-2 py-0.5 rounded">
              DEMO FIELD EVIDENCE
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <button
              type="button"
              onClick={() => setViewMode(viewMode === 'table' ? 'gallery' : 'table')}
              className="px-2.5 py-1 bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 rounded text-xs font-semibold flex items-center space-x-1"
            >
              {viewMode === 'table' ? <Grid className="h-3.5 w-3.5" /> : <Table className="h-3.5 w-3.5" />}
              <span>{viewMode === 'table' ? 'Gallery View' : 'Table View'}</span>
            </button>
            <button
              type="button"
              onClick={() => setShowUploadForm(!showUploadForm)}
              className="px-3 py-1 bg-blue-900 hover:bg-blue-950 text-white rounded text-xs font-bold flex items-center space-x-1"
            >
              <Upload className="h-3.5 w-3.5" />
              <span>{showUploadForm ? 'View Register' : 'Ingest Photo'}</span>
            </button>
            <button
              type="button"
              onClick={onClose}
              className="p-1 text-slate-400 hover:text-slate-700"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Filter Strip */}
        <div className="px-5 py-2 bg-slate-50 border-b border-slate-200 flex flex-wrap items-center justify-between gap-2 text-xs">
          <div className="flex items-center space-x-3 flex-wrap gap-2">
            <div className="flex items-center space-x-1">
              <span className="text-slate-500 font-semibold">Category:</span>
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="bg-white border border-slate-300 rounded px-2 py-0.5 font-semibold text-slate-800"
              >
                <option value="ALL">All Categories</option>
                <option value="CHECK_DAM">Check Dam</option>
                <option value="FARM_POND">Farm Pond</option>
                <option value="PERCOLATION_TANK">Percolation Tank</option>
                <option value="PLANTATION">Plantation / CCT</option>
                <option value="DESILTATION">Desiltation</option>
                <option value="EROSION">Erosion Zone</option>
              </select>
            </div>

            <div className="flex items-center space-x-1">
              <span className="text-slate-500 font-semibold">Verification:</span>
              <select
                value={verificationFilter}
                onChange={(e) => setVerificationFilter(e.target.value)}
                className="bg-white border border-slate-300 rounded px-2 py-0.5 font-semibold text-slate-800"
              >
                <option value="ALL">All Statuses</option>
                <option value="VERIFIED">VERIFIED</option>
                <option value="PENDING">PENDING</option>
                <option value="REJECTED">REJECTED</option>
              </select>
            </div>
          </div>

          <span className="text-[11px] text-slate-500 font-mono">
            Showing {filteredPhotos.length} of {photos.length} records
          </span>
        </div>

        {/* Modal Body */}
        <div className="p-5 overflow-y-auto flex-1">
          {showUploadForm ? (
            <form onSubmit={handleSubmit} className="space-y-3 max-w-lg mx-auto bg-slate-50 p-5 rounded border border-slate-300 text-xs">
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wide border-b border-slate-200 pb-2">
                Ingest Geo-Tagged Field Photograph
              </h3>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Photograph Object Storage URI / URL *
                </label>
                <input
                  type="url"
                  required
                  placeholder="https://images.unsplash.com/... or storage://bucket/..."
                  value={photoUrl}
                  onChange={(e) => setPhotoUrl(e.target.value)}
                  className="w-full bg-white border border-slate-300 rounded p-2 text-xs text-slate-900"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-slate-700 mb-1">
                    Latitude (°N) *
                  </label>
                  <input
                    type="number"
                    step="0.000001"
                    required
                    placeholder="19.0482"
                    value={latitude}
                    onChange={(e) => setLatitude(e.target.value)}
                    className="w-full bg-white border border-slate-300 rounded p-2 text-xs text-slate-900 font-mono"
                  />
                </div>
                <div>
                  <label className="block font-bold text-slate-700 mb-1">
                    Longitude (°E) *
                  </label>
                  <input
                    type="number"
                    step="0.000001"
                    required
                    placeholder="74.6053"
                    value={longitude}
                    onChange={(e) => setLongitude(e.target.value)}
                    className="w-full bg-white border border-slate-300 rounded p-2 text-xs text-slate-900 font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Feature Category *
                </label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full bg-white border border-slate-300 rounded p-2 text-xs text-slate-900 font-semibold"
                >
                  <option value="CHECK_DAM">Check Dam Structure</option>
                  <option value="FARM_POND">Farm Pond / Storage</option>
                  <option value="PERCOLATION_TANK">Percolation Tank</option>
                  <option value="PLANTATION">Ridge Afforestation / CCT</option>
                  <option value="DESILTATION">Nala Desiltation Site</option>
                  <option value="EROSION">Soil Erosion Scour Zone</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Field Officer Observation &amp; Remarks
                </label>
                <textarea
                  rows={2}
                  placeholder="Record water holding level, structural integrity, siltation status..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full bg-white border border-slate-300 rounded p-2 text-xs text-slate-900"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowUploadForm(false)}
                  className="px-3 py-1.5 border border-slate-300 rounded text-xs font-semibold text-slate-700 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-1.5 bg-blue-900 hover:bg-blue-950 text-white rounded text-xs font-bold"
                >
                  {isSubmitting ? 'Ingesting Record...' : 'Submit Field Observation'}
                </button>
              </div>
            </form>
          ) : viewMode === 'table' ? (
            <div className="space-y-4">
              {/* Government Field-Monitoring Table */}
              <div className="overflow-x-auto border border-slate-200 rounded">
                <table className="w-full text-left text-xs text-slate-800 divide-y divide-slate-200">
                  <thead className="bg-slate-50 text-[10px] font-bold text-slate-600 uppercase tracking-wider">
                    <tr>
                      <th className="py-2 px-3">Photo</th>
                      <th className="py-2 px-3">Date</th>
                      <th className="py-2 px-3">GNSS Coordinates</th>
                      <th className="py-2 px-3">Category</th>
                      <th className="py-2 px-3">Field Observation</th>
                      <th className="py-2 px-3">Verification</th>
                      <th className="py-2 px-3">Source</th>
                      <th className="py-2 px-3">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 text-xs">
                    {filteredPhotos.map((photo) => (
                      <tr
                        key={photo.id}
                        onClick={() => setSelectedPhoto(photo)}
                        className={`hover:bg-slate-50 cursor-pointer transition-colors ${
                          selectedPhoto?.id === photo.id ? 'bg-blue-50/60' : ''
                        }`}
                      >
                        <td className="py-2 px-3">
                          <img
                            src={photo.photo_url}
                            alt={photo.category}
                            className="h-10 w-12 object-cover rounded border border-slate-300"
                          />
                        </td>
                        <td className="py-2 px-3 font-mono text-[11px] whitespace-nowrap">
                          {new Date(photo.captured_at).toLocaleDateString()}
                        </td>
                        <td className="py-2 px-3 font-mono text-[11px] text-slate-600 whitespace-nowrap">
                          {photo.latitude.toFixed(4)}°N, {photo.longitude.toFixed(4)}°E
                        </td>
                        <td className="py-2 px-3 font-bold text-blue-900 font-mono text-[11px]">
                          {photo.category}
                        </td>
                        <td className="py-2 px-3 text-[11px] text-slate-700 max-w-[200px] truncate" title={photo.description}>
                          {photo.description}
                        </td>
                        <td className="py-2 px-3 whitespace-nowrap">
                          <span
                            className={`px-1.5 py-0.2 rounded text-[9px] font-extrabold border ${
                              photo.verification_status === 'VERIFIED'
                                ? 'bg-emerald-50 text-emerald-900 border-emerald-300'
                                : 'bg-amber-50 text-amber-900 border-amber-300'
                            }`}
                          >
                            {photo.verification_status}
                          </span>
                        </td>
                        <td className="py-2 px-3 text-[11px] text-slate-500 font-mono whitespace-nowrap">
                          {photo.source_type}
                        </td>
                        <td className="py-2 px-3 whitespace-nowrap">
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedPhoto(photo);
                            }}
                            className="p-1 text-blue-900 hover:text-blue-950"
                            title="Inspect Photograph"
                          >
                            <Eye className="h-4 w-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Selected Photo Inspector Detail Box */}
              {selectedPhoto && (
                <div className="p-4 bg-slate-50 border border-slate-300 rounded flex flex-col md:flex-row gap-4 items-start">
                  <div className="w-full md:w-64 flex-shrink-0">
                    <img
                      src={selectedPhoto.photo_url}
                      alt={selectedPhoto.category}
                      className="w-full h-44 object-cover rounded border border-slate-300 shadow-xs"
                    />
                  </div>
                  <div className="flex-1 space-y-1.5 text-xs text-slate-800">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-950 uppercase tracking-wide">
                        {selectedPhoto.category} • Ground Truth Evidence
                      </span>
                      <span className="font-mono text-[10px] text-slate-500">
                        Record ID: #{selectedPhoto.id}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 font-mono text-[11px] pt-1">
                      <div>
                        <span className="text-slate-500 block font-sans">Date Captured:</span>
                        <strong>{new Date(selectedPhoto.captured_at).toLocaleString()}</strong>
                      </div>
                      <div>
                        <span className="text-slate-500 block font-sans">Coordinates:</span>
                        <strong>{selectedPhoto.latitude.toFixed(5)}°N, {selectedPhoto.longitude.toFixed(5)}°E</strong>
                      </div>
                      <div>
                        <span className="text-slate-500 block font-sans">Verification:</span>
                        <strong className="text-emerald-800">{selectedPhoto.verification_status}</strong>
                      </div>
                    </div>
                    <div className="pt-2 border-t border-slate-200">
                      <span className="font-bold text-slate-700 block">Inspection Notes:</span>
                      <p className="text-slate-600 mt-0.5 leading-relaxed">{selectedPhoto.description}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            /* Gallery View */
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
              {filteredPhotos.map((photo) => (
                <div
                  key={photo.id}
                  className="bg-white rounded border border-slate-300 overflow-hidden shadow-2xs flex flex-col justify-between"
                >
                  <div className="relative h-40 bg-slate-900">
                    <img
                      src={photo.photo_url}
                      alt={photo.category}
                      className="h-full w-full object-cover"
                    />
                    <span className="absolute top-2 right-2 text-[9px] font-extrabold px-1.5 py-0.2 rounded bg-slate-900/80 text-white">
                      {photo.verification_status}
                    </span>
                  </div>
                  <div className="p-3 space-y-1 text-xs">
                    <div className="font-bold text-slate-900">{photo.category}</div>
                    <p className="text-slate-600 text-[11px] line-clamp-2">{photo.description}</p>
                    <div className="pt-1 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-400 font-mono">
                      <span>{photo.latitude.toFixed(4)}°N, {photo.longitude.toFixed(4)}°E</span>
                      <span>{new Date(photo.captured_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
