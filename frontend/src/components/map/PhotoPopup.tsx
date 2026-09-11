'use client';
import React from 'react';
import { FieldPhoto } from '@/types';
import { Camera, Calendar, MapPin, CheckCircle2, AlertCircle } from 'lucide-react';

interface PhotoPopupProps {
  photo: FieldPhoto;
  onClose?: () => void;
}

export const PhotoPopup: React.FC<PhotoPopupProps> = ({ photo, onClose }) => {
  return (
    <div className="w-64 bg-white rounded-lg overflow-hidden font-sans text-xs">
      <div className="relative h-32 w-full bg-slate-800">
        <img
          src={photo.photo_url}
          alt={photo.category}
          className="h-full w-full object-cover"
        />
        <div className="absolute top-2 right-2">
          <span
            className={`px-2 py-0.5 rounded text-[10px] font-bold shadow-sm ${
              photo.verification_status === 'VERIFIED'
                ? 'bg-emerald-600 text-white'
                : 'bg-amber-500 text-white'
            }`}
          >
            {photo.verification_status}
          </span>
        </div>
      </div>

      <div className="p-3">
        <div className="flex items-center justify-between text-slate-500 text-[10px] mb-1">
          <span className="font-bold text-blue-700 uppercase tracking-wider">{photo.category}</span>
          <span className="flex items-center">
            <Calendar className="h-3 w-3 mr-1" />
            {new Date(photo.captured_at).toLocaleDateString()}
          </span>
        </div>

        <p className="text-slate-800 font-medium line-clamp-3 mb-2">
          {photo.description || 'Field photograph documented during watershed survey.'}
        </p>

        <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-400">
          <div className="flex items-center">
            <MapPin className="h-3 w-3 mr-0.5 text-slate-500" />
            <span>
              {photo.latitude.toFixed(4)}, {photo.longitude.toFixed(4)}
            </span>
          </div>
          <span className="text-slate-600 font-semibold">{photo.uploader_role}</span>
        </div>
      </div>
    </div>
  );
};
