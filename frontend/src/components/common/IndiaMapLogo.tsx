'use client';
import React from 'react';

interface IndiaMapLogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showText?: boolean;
  className?: string;
  variant?: 'light' | 'dark';
}

/**
 * IndiaMapLogo
 * 
 * Official vector emblem for JalDrishti:
 * Combines the geographic silhouette of India with internal watershed
 * and dendritic river drainage networks, accented with restrained Indian Tricolour
 * and institutional deep navy cartographic styling.
 */
export default function IndiaMapLogo({
  size = 'md',
  showText = true,
  className = '',
  variant = 'light'
}: IndiaMapLogoProps) {
  const sizeMap = {
    sm: { icon: 'w-7 h-7', title: 'text-sm', sub: 'text-[9px]' },
    md: { icon: 'w-10 h-10', title: 'text-lg', sub: 'text-[10px]' },
    lg: { icon: 'w-14 h-14', title: 'text-2xl', sub: 'text-xs' },
    xl: { icon: 'w-20 h-20', title: 'text-3xl', sub: 'text-sm' },
  };

  const currentSize = sizeMap[size];
  const isDark = variant === 'dark';

  return (
    <div className={`flex items-center space-x-3 select-none ${className}`}>
      {/* India Map + Watershed Drainage Vector Icon */}
      <div className={`relative ${currentSize.icon} flex-shrink-0 flex items-center justify-center`}>
        <svg
          viewBox="0 0 100 120"
          className="w-full h-full drop-shadow-xs"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            {/* Subtle Indian Tricolour Gradient */}
            <linearGradient id="indiaTricolourGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#ea580c" stopOpacity="0.85" />
              <stop offset="42%" stopColor="#ffffff" stopOpacity="0.95" />
              <stop offset="65%" stopColor="#ffffff" stopOpacity="0.95" />
              <stop offset="100%" stopColor="#15803d" stopOpacity="0.85" />
            </linearGradient>

            {/* River Drainage Blue Accent */}
            <linearGradient id="drainageGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#0284c7" />
              <stop offset="100%" stopColor="#1e3a8a" />
            </linearGradient>
          </defs>

          {/* Outer Boundary Silhouette of India */}
          <path
            d="M 48 4
               C 42 7, 39 12, 40 18
               C 35 18, 30 22, 28 28
               C 22 30, 18 36, 17 44
               C 15 50, 10 52, 9 58
               C 9 63, 14 65, 18 64
               C 22 64, 25 61, 28 65
               C 32 72, 38 82, 44 94
               C 48 102, 50 114, 52 116
               C 54 114, 56 102, 60 94
               C 66 82, 72 72, 76 65
               C 79 61, 82 64, 86 64
               C 90 65, 95 63, 95 58
               C 94 52, 89 50, 87 44
               C 86 36, 82 30, 76 28
               C 74 22, 69 18, 64 18
               C 65 12, 62 7, 56 4
               Z"
            fill="url(#indiaTricolourGrad)"
            stroke="#1e3a8a"
            strokeWidth="2.2"
            strokeLinejoin="round"
            className="filter"
          />

          {/* Northern Crown & Central Ridge Accent */}
          <path
            d="M 48 6 L 52 14 L 56 6"
            stroke="#c2410c"
            strokeWidth="1.2"
            strokeLinecap="round"
          />

          {/* Watershed Drainage Network (Ganga-Brahmaputra, Narmada, Godavari, Krishna tributaries) */}
          <g stroke="url(#drainageGrad)" strokeLinecap="round" opacity="0.85">
            {/* Northern Main River Trunk */}
            <path d="M 40 22 Q 48 28, 56 34 Q 68 38, 80 44" strokeWidth="1.6" fill="none" />
            {/* Northern Tributaries */}
            <path d="M 46 16 Q 48 24, 56 34" strokeWidth="0.9" fill="none" />
            <path d="M 64 26 Q 62 32, 56 34" strokeWidth="0.9" fill="none" />
            <path d="M 74 34 Q 72 40, 80 44" strokeWidth="0.8" fill="none" />

            {/* Central Watershed Divide (Narmada / Tapti) */}
            <path d="M 28 54 Q 38 52, 48 50 Q 60 52, 70 54" strokeWidth="1.4" fill="none" />

            {/* Southern Peninsular River Trunk (Godavari & Krishna Basin) */}
            <path d="M 36 66 Q 48 72, 58 76 Q 66 82, 72 86" strokeWidth="1.5" fill="none" />
            <path d="M 42 80 Q 48 88, 52 102" strokeWidth="1.3" fill="none" />
            {/* Secondary Southern Catchment Ribs */}
            <path d="M 38 74 Q 44 76, 48 72" strokeWidth="0.8" fill="none" />
            <path d="M 58 76 Q 54 84, 52 92" strokeWidth="0.8" fill="none" />
          </g>

          {/* Central Ashoka Chakra Motif Geometry (Center Heart of Subcontinent) */}
          <g transform="translate(52, 50)" opacity="0.75">
            <circle cx="0" cy="0" r="4.5" fill="#ffffff" stroke="#1e3a8a" strokeWidth="1" />
            <circle cx="0" cy="0" r="1.5" fill="#1e3a8a" />
            {/* Fine spoke rays */}
            <line x1="0" y1="-4.2" x2="0" y2="4.2" stroke="#1e3a8a" strokeWidth="0.5" />
            <line x1="-4.2" y1="0" x2="4.2" y2="0" stroke="#1e3a8a" strokeWidth="0.5" />
            <line x1="-3" y1="-3" x2="3" y2="3" stroke="#1e3a8a" strokeWidth="0.5" />
            <line x1="-3" y1="3" x2="3" y2="-3" stroke="#1e3a8a" strokeWidth="0.5" />
          </g>

          {/* Peninsular Hydro Convergence Droplet at Southern Cape */}
          <path
            d="M 52 108 C 49 108, 47 111, 47 113 C 47 115.5, 52 119, 52 119 C 52 119, 57 115.5, 57 113 C 57 111, 55 108, 52 108 Z"
            fill="#0284c7"
            stroke="#ffffff"
            strokeWidth="0.6"
          />
        </svg>
      </div>

      {/* Brand Text Elements */}
      {showText && (
        <div className="flex flex-col leading-tight">
          <div className="flex items-center space-x-1.5">
            <span
              className={`font-black tracking-tight font-serif ${currentSize.title} ${
                isDark ? 'text-white' : 'text-slate-950'
              }`}
            >
              JalDrishti
            </span>
            <span className="inline-flex items-center px-1.5 py-0.2 rounded text-[9px] font-extrabold uppercase tracking-widest bg-blue-50 text-blue-900 border border-blue-200">
              GIS Portal
            </span>
          </div>
          <span
            className={`font-bold tracking-tight uppercase ${currentSize.sub} ${
              isDark ? 'text-blue-200' : 'text-slate-600'
            }`}
          >
            Watershed Monitoring &amp; Geospatial Decision Support System
          </span>
        </div>
      )}
    </div>
  );
}
