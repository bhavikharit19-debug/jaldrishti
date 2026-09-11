'use client';
import React from 'react';
import Link from 'next/link';
import { Droplets, Shield, HelpCircle, Info, ExternalLink } from 'lucide-react';
import JalDrishtiLogo from '@/components/common/JalDrishtiLogo';

interface InstitutionalHeaderProps {
  onOpenAbout?: () => void;
  onOpenHelp?: () => void;
}

export default function InstitutionalHeader({ onOpenAbout, onOpenHelp }: InstitutionalHeaderProps) {
  return (
    <header className="bg-white border-b border-slate-300 shadow-sm z-10 select-none">
      {/* Top Institutional Accent Line (Tricolor + Deep Navy accent) */}
      <div className="h-1 w-full flex">
        <div className="h-full w-1/3 bg-amber-600" />
        <div className="h-full w-1/3 bg-slate-200" />
        <div className="h-full w-1/3 bg-emerald-700" />
      </div>

      {/* Top Utility Hierarchy Bar */}
      <div className="bg-slate-100 border-b border-slate-200 px-4 sm:px-8 py-1 flex items-center justify-between text-[11px] text-slate-600 font-medium">
        <div className="flex items-center space-x-2">
          <span className="font-semibold text-slate-800">JalDrishti Geospatial Decision-Support Portal</span>
          <span className="text-slate-300">|</span>
          <span className="hidden md:inline text-slate-600">Aligned with DoLR &amp; MoJS Guidelines</span>
        </div>
        <div className="flex items-center space-x-4 text-[11px]">
          <span className="bg-blue-50 text-blue-800 px-2 py-0.5 rounded border border-blue-200 font-semibold">
            SIH PROBLEM 26015
          </span>
          <span className="hidden sm:inline text-slate-500">Watershed Decision Support</span>
        </div>
      </div>

      {/* Main Header Container */}
      <div className="px-4 sm:px-8 py-3 flex flex-wrap items-center justify-between gap-4">
        {/* Left: Department & System Brand */}
        <div className="flex items-center space-x-3">
          <JalDrishtiLogo size="md" variant="horizontal" />
        </div>

        {/* Right: Institutional Navigation Links */}
        <nav className="flex items-center space-x-2 sm:space-x-3 text-xs">
          <Link
            href="/"
            className="px-2.5 py-1.5 text-slate-700 hover:text-blue-900 hover:bg-slate-100 rounded transition-colors font-medium"
          >
            Home
          </Link>
          <button
            type="button"
            onClick={onOpenAbout}
            className="px-2.5 py-1.5 text-slate-700 hover:text-blue-900 hover:bg-slate-100 rounded transition-colors font-medium flex items-center space-x-1"
          >
            <Info className="h-3.5 w-3.5 text-slate-500" />
            <span>About</span>
          </button>
          <button
            type="button"
            onClick={onOpenHelp}
            className="px-2.5 py-1.5 text-slate-700 hover:text-blue-900 hover:bg-slate-100 rounded transition-colors font-medium flex items-center space-x-1"
          >
            <HelpCircle className="h-3.5 w-3.5 text-slate-500" />
            <span>Help</span>
          </button>
          <div className="h-4 w-px bg-slate-300" />
          <div className="px-3 py-1 bg-blue-900 text-white rounded text-xs font-semibold tracking-wide flex items-center space-x-1.5 shadow-sm">
            <Shield className="h-3.5 w-3.5 text-blue-200" />
            <span>LOGIN PORTAL</span>
          </div>
        </nav>
      </div>
    </header>
  );
}
