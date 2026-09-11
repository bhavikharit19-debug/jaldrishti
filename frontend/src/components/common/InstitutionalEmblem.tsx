'use client';
import React from 'react';

interface InstitutionalEmblemProps {
  className?: string;
  variant?: 'light' | 'dark';
  compact?: boolean;
}

/**
 * InstitutionalEmblem
 * 
 * Renders a subtle, respectful "सत्यमेव जयते" typography element
 * with Ashoka Chakra geometry and transparent SIH 26015 Prototype demarcation.
 */
export default function InstitutionalEmblem({
  className = '',
  variant = 'light',
  compact = false
}: InstitutionalEmblemProps) {
  const isDark = variant === 'dark';
  const strokeColor = isDark ? '#fbbf24' : '#1e3a8a';
  const textColor = isDark ? '#fef08a' : '#0f172a';
  const subtextColor = isDark ? '#94a3b8' : '#64748b';

  return (
    <div className={`inline-flex items-center select-none ${className}`}>
      <svg
        viewBox="0 0 170 32"
        className={compact ? 'h-6 w-auto' : 'h-8 w-auto'}
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-label="सत्यमेव जयते - SIH 26015 Prototype System"
        role="img"
      >
        {/* Cartographic Watershed Ripple & 24-Spoke Wheel Motif */}
        <g transform="translate(4, 2)">
          {/* Outer watershed contour ripple */}
          <path
            d="M 14,2 C 22,2 26,7 26,14 C 26,21 21,26 14,26 C 7,26 2,21 2,14 C 2,7 6,2 14,2 Z"
            stroke={strokeColor}
            strokeWidth="0.8"
            strokeDasharray="1.5,1"
            opacity="0.6"
          />
          {/* Intermediate geometry ring */}
          <circle cx="14" cy="14" r="10" stroke={strokeColor} strokeWidth="1.2" />
          {/* Inner Hub */}
          <circle cx="14" cy="14" r="2.5" fill={strokeColor} />
          {/* 24-Spoke Radial Geometry */}
          {[0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330].map((deg) => (
            <line
              key={deg}
              x1="14"
              y1="14"
              x2={14 + 9.5 * Math.cos((deg * Math.PI) / 180)}
              y2={14 + 9.5 * Math.sin((deg * Math.PI) / 180)}
              stroke={strokeColor}
              strokeWidth="0.8"
            />
          ))}
        </g>

        {/* Original Vector Typography */}
        <g transform="translate(38, 0)">
          {/* "सत्यमेव जयते" Devanagari Lettering */}
          <text
            x="0"
            y="17"
            fill={textColor}
            fontFamily="'Noto Serif Devanagari', 'Tiro Devanagari Hindi', 'Georgia', serif"
            fontWeight="bold"
            fontSize="13.5"
            letterSpacing="0.08em"
          >
            सत्यमेव जयते
          </text>

          {/* Prototype System Demarcation */}
          {!compact && (
            <text
              x="0"
              y="28"
              fill={subtextColor}
              fontFamily="monospace, ui-monospace, sans-serif"
              fontWeight="600"
              fontSize="7.5"
              letterSpacing="0.04em"
            >
              SIH 26015 | Prototype System
            </text>
          )}
        </g>
      </svg>
    </div>
  );
}
