'use client';
import React from 'react';

/**
 * GISBackground
 * 
 * Renders a subtle, low-contrast cartographic/GIS vector background
 * inspired by Indian institutional geospatial portals (Bhuvan/SRISHTI-DRISHTI).
 * Features elevation contours, dendritic drainage channels, watershed boundaries,
 * coordinate reference grid (EPSG:4326), and cartographic orientation markers.
 */
export default function GISBackground() {
  return (
    <div
      aria-hidden="true"
      className="fixed inset-0 pointer-events-none select-none z-0 overflow-hidden bg-slate-100/80"
    >
      <svg
        className="w-full h-full text-slate-400/30"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 1600 1000"
        preserveAspectRatio="xMidYMid slice"
      >
        <defs>
          {/* Subtle grid pattern for coordinate reference system */}
          <pattern id="gis-grid" width="160" height="160" patternUnits="userSpaceOnUse">
            <path
              d="M 160 0 L 0 0 0 160"
              fill="none"
              stroke="currentColor"
              strokeWidth="0.5"
              strokeDasharray="2 6"
              className="text-slate-400/40"
            />
            {/* Fine sub-grid ticks */}
            <circle cx="80" cy="80" r="1" fill="currentColor" className="text-slate-400/50" />
            <circle cx="0" cy="0" r="1.5" fill="currentColor" className="text-slate-500/60" />
          </pattern>
        </defs>

        {/* Background Grid */}
        <rect width="100%" height="100%" fill="url(#gis-grid)" />

        {/* Catchment / Watershed Boundary Polygons (Faint dashed polygons) */}
        <g className="text-blue-900/[0.07] stroke-current" fill="none" strokeWidth="1.5" strokeDasharray="6 4">
          {/* Primary Watershed Boundary A (Hiware Bazar catchment) */}
          <path d="M 220 180 C 310 140, 480 160, 560 240 C 640 320, 680 460, 620 580 C 560 700, 420 780, 290 740 C 160 700, 120 540, 140 380 C 160 220, 180 190, 220 180 Z" />
          
          {/* Sub-Catchment Boundary B */}
          <path d="M 620 280 C 720 210, 890 230, 990 320 C 1090 410, 1120 560, 1040 680 C 960 800, 810 830, 700 780 C 590 730, 570 600, 590 480 C 600 380, 570 310, 620 280 Z" />
          
          {/* Sub-Catchment Boundary C */}
          <path d="M 1040 220 C 1160 170, 1340 200, 1440 310 C 1540 420, 1550 590, 1470 710 C 1390 830, 1230 860, 1120 790 C 1010 720, 990 560, 1010 420 C 1020 310, 990 240, 1040 220 Z" />
        </g>

        {/* Elevation Contour Lines (50m - 100m intervals) */}
        <g className="text-slate-800/[0.06] stroke-current" fill="none" strokeWidth="1">
          {/* 600m Contour */}
          <path d="M -50 300 Q 250 200, 500 350 T 1050 400 T 1650 320" />
          {/* 650m Contour */}
          <path d="M -50 380 Q 280 280, 540 420 T 1100 480 T 1650 400" strokeDasharray="4 2" />
          {/* 700m Contour */}
          <path d="M -50 460 Q 320 360, 580 500 T 1140 560 T 1650 490" />
          {/* 750m Contour */}
          <path d="M -50 540 Q 350 440, 620 580 T 1180 640 T 1650 580" strokeDasharray="4 2" />
          {/* 800m Ridge Contour */}
          <path d="M -50 620 Q 380 520, 660 660 T 1220 720 T 1650 670" strokeWidth="1.2" />
          {/* Hilltop Enclosure 850m */}
          <ellipse cx="440" cy="510" rx="90" ry="50" transform="rotate(-15 440 510)" />
          <ellipse cx="1280" cy="460" rx="120" ry="65" transform="rotate(10 1280 460)" />
        </g>

        {/* Dendritic Drainage Stream Network (Flow vectors) */}
        <g className="text-blue-700/[0.08] stroke-current" fill="none" strokeLinecap="round">
          {/* Main Thalweg / Primary Stream Channel */}
          <path d="M 440 510 Q 400 420, 360 360 Q 310 280, 280 120" strokeWidth="2.2" />
          {/* Tributary 1 */}
          <path d="M 520 460 Q 450 410, 400 420" strokeWidth="1.4" />
          {/* Tributary 2 */}
          <path d="M 320 470 Q 340 410, 360 360" strokeWidth="1.2" />
          {/* First-Order Gullies */}
          <path d="M 540 520 Q 530 480, 520 460" strokeWidth="0.8" />
          <path d="M 480 390 Q 430 400, 400 420" strokeWidth="0.8" />

          {/* East Catchment Stream */}
          <path d="M 1280 460 Q 1180 390, 1100 320 Q 1020 250, 960 100" strokeWidth="2.2" />
          <path d="M 1360 520 Q 1310 470, 1280 460" strokeWidth="1.3" />
          <path d="M 1220 370 Q 1170 350, 1100 320" strokeWidth="1.1" />
        </g>

        {/* Water Body / Percolation Tank polygon */}
        <g className="text-blue-800/[0.08]">
          <path
            d="M 380 370 C 370 355, 395 340, 415 350 C 435 360, 430 385, 410 390 C 390 395, 385 380, 380 370 Z"
            fill="currentColor"
          />
          <path
            d="M 1120 330 C 1105 315, 1135 300, 1155 312 C 1175 325, 1165 350, 1145 352 C 1125 355, 1125 340, 1120 330 Z"
            fill="currentColor"
          />
        </g>

        {/* Coordinate Grid Labels (Institutional Lat/Long markings) */}
        <g className="fill-slate-600/40 text-[10px] font-mono select-none">
          {/* Latitudes */}
          <text x="24" y="165">19°12'00"N</text>
          <text x="24" y="325">19°10'00"N</text>
          <text x="24" y="485">19°08'00"N</text>
          <text x="24" y="645">19°06'00"N</text>
          <text x="24" y="805">19°04'00"N</text>

          {/* Longitudes */}
          <text x="165" y="980">74°32'00"E</text>
          <text x="325" y="980">74°34'00"E</text>
          <text x="485" y="980">74°36'00"E</text>
          <text x="645" y="980">74°38'00"E</text>
          <text x="805" y="980">74°40'00"E</text>
          <text x="965" y="980">74°42'00"E</text>
          <text x="1125" y="980">74°44'00"E</text>
          <text x="1285" y="980">74°46'00"E</text>
          <text x="1445" y="980">74°48'00"E</text>

          {/* Right edge CRS & Datum info */}
          <text x="1460" y="40" textAnchor="end" className="text-[11px] font-semibold tracking-wider">
            CRS: EPSG:4326 (WGS 84)
          </text>
          <text x="1460" y="56" textAnchor="end" className="text-[9px]">
            CONTOUR INTERVAL: 50M | DATUM: MSL
          </text>
        </g>

        {/* Cartographic North Arrow (Top Right) */}
        <g transform="translate(1520, 80)" className="text-slate-600/30">
          <circle cx="0" cy="0" r="22" fill="none" stroke="currentColor" strokeWidth="1" />
          <polygon points="0,-18 5,0 0,-4" fill="currentColor" />
          <polygon points="0,18 -5,0 0,4" fill="none" stroke="currentColor" strokeWidth="0.8" />
          <polygon points="0,-18 -5,0 0,-4" fill="none" stroke="currentColor" strokeWidth="0.8" />
          <text x="0" y="-22" textAnchor="middle" className="fill-slate-600/60 font-bold text-[10px] font-sans">
            N
          </text>
        </g>

        {/* Cartographic Scale Bar (Bottom Right) */}
        <g transform="translate(1380, 940)" className="text-slate-600/40">
          <rect x="0" y="0" width="120" height="4" fill="none" stroke="currentColor" strokeWidth="1" />
          <rect x="0" y="0" width="30" height="4" fill="currentColor" />
          <rect x="60" y="0" width="30" height="4" fill="currentColor" />
          <text x="0" y="-4" className="text-[8px] font-mono fill-current">0</text>
          <text x="30" y="-4" className="text-[8px] font-mono fill-current">1.25</text>
          <text x="60" y="-4" className="text-[8px] font-mono fill-current">2.5</text>
          <text x="120" y="-4" className="text-[8px] font-mono fill-current">5.0 km</text>
        </g>
      </svg>
    </div>
  );
}
