import React from 'react';

interface JalDrishtiLogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'horizontal' | 'vertical' | 'icon';
  theme?: 'light' | 'dark';
  showTagline?: boolean;
  className?: string;
}

export default function JalDrishtiLogo({
  size = 'md',
  variant = 'horizontal',
  theme = 'light',
  showTagline = true,
  className = ''
}: JalDrishtiLogoProps) {
  // Dimension scale based on size
  const iconDimensions = {
    sm: { w: 32, h: 28 },
    md: { w: 42, h: 36 },
    lg: { w: 56, h: 48 },
    xl: { w: 72, h: 62 }
  }[size];

  const titleSizes = {
    sm: 'text-base',
    md: 'text-lg',
    lg: 'text-2xl',
    xl: 'text-3xl'
  }[size];

  const subtitleSizes = {
    sm: 'text-[9px]',
    md: 'text-[11px]',
    lg: 'text-xs',
    xl: 'text-sm'
  }[size];

  const isDark = theme === 'dark';

  // The JD Monogram with Water-drop & Wave inside the D
  const Monogram = (
    <svg
      width={iconDimensions.w}
      height={iconDimensions.h}
      viewBox="0 0 140 120"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="flex-shrink-0 transition-transform duration-200"
    >
      <defs>
        {/* Saffron Gradient for J */}
        <linearGradient id={`jdSaffron-${theme}`} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#EA580C" />
          <stop offset="100%" stopColor="#F97316" />
        </linearGradient>

        {/* Navy Spine for D */}
        <linearGradient id={`jdNavy-${theme}`} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor={isDark ? "#38BDF8" : "#0F172A"} />
          <stop offset="100%" stopColor={isDark ? "#60A5FA" : "#1E3A8A"} />
        </linearGradient>

        {/* Water Droplet Azure */}
        <linearGradient id={`jdWater-${theme}`} x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#38BDF8" />
          <stop offset="100%" stopColor="#0284C7" />
        </linearGradient>

        {/* Green Watershed Wave */}
        <linearGradient id={`jdGreen-${theme}`} x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#15803D" />
          <stop offset="100%" stopColor="#22C55E" />
        </linearGradient>

        <filter id={`jdShadow-${theme}`} x="-10%" y="-10%" width="120%" height="120%">
          <feDropShadow dx="0" dy="1.5" stdDeviation="1.5" floodColor="#0F172A" floodOpacity="0.15" />
        </filter>
      </defs>

      <g transform="translate(8, 14)" filter={`url(#jdShadow-${theme})`}>
        {/* Letter J (Saffron to Orange) */}
        <path
          d="M 36 20 
             L 36 64 
             C 36 78, 25 86, 12 86 
             C 4 86, -1 83, -4 80 
             L 2 68 
             C 4 70, 7 72, 11 72 
             C 17 72, 23 67, 23 58 
             L 23 20 
             Z"
          fill={`url(#jdSaffron-${theme})`}
        />

        {/* Saffron Accent Dot on J */}
        <circle cx="29.5" cy="9" r="6" fill={`url(#jdSaffron-${theme})`} />

        {/* Letter D Outer Arc */}
        <path
          d="M 44 14 
             L 76 14 
             C 106 14, 126 31, 126 53 
             C 126 75, 106 92, 76 92 
             L 44 92 
             Z"
          fill={isDark ? "#F8FAFC" : `url(#jdNavy-${theme})`}
        />

        {/* Letter D Inner Counter Hole */}
        <path
          d="M 57 27 
             L 74 27 
             C 93 27, 109 38, 109 53 
             C 109 68, 93 79, 74 79 
             L 57 79 
             Z"
          fill={isDark ? "#0F172A" : "#FFFFFF"}
        />

        {/* Water Drop Upper Body (Cyan/Azure) */}
        <path
          d="M 83 33 
             C 83 33, 71 48, 71 58 
             C 71 61, 72 64, 74 66 
             C 79 62, 87 62, 92 66 
             C 94 64, 95 61, 95 58 
             C 95 48, 83 33, 83 33 
             Z"
          fill={`url(#jdWater-${theme})`}
        />

        {/* Water Drop Lower Base (Green Watershed Wave) */}
        <path
          d="M 74 66 
             C 72 68.5, 71 71, 71 73 
             C 71 79.6, 76.4 85, 83 85 
             C 89.6 85, 95 79.6, 95 73 
             C 95 71, 94 68.5, 92 66 
             C 87 62, 79 62, 74 66 
             Z"
          fill={`url(#jdGreen-${theme})`}
        />

        {/* Wave Ripple Line inside Water Drop */}
        <path
          d="M 73 66 Q 83 70, 93 66"
          stroke={isDark ? "#0F172A" : "#FFFFFF"}
          strokeWidth="2"
          strokeLinecap="round"
          fill="none"
        />

        {/* Water Glint */}
        <ellipse
          cx="79"
          cy="48"
          rx="2"
          ry="4"
          transform="rotate(-25 79 48)"
          fill="#FFFFFF"
          opacity="0.7"
        />
      </g>
    </svg>
  );

  if (variant === 'icon') {
    return <div className={`inline-flex items-center ${className}`}>{Monogram}</div>;
  }

  if (variant === 'vertical') {
    return (
      <div className={`flex flex-col items-center text-center ${className}`}>
        {Monogram}
        <div className="mt-2">
          <div className={`${titleSizes} font-black tracking-tight leading-tight`}>
            <span className={isDark ? 'text-white' : 'text-slate-900'}>Jal</span>
            <span className="text-sky-600">Drishti</span>
          </div>
          {/* Saffron, Water Blue, Green Accent Bar */}
          <div className="flex items-center justify-center space-x-1 my-1.5">
            <span className="h-0.5 w-6 bg-orange-600 rounded-full" />
            <span className="h-0.5 w-4 bg-sky-500 rounded-full" />
            <span className="h-0.5 w-6 bg-emerald-600 rounded-full" />
          </div>
          {showTagline && (
            <p className={`${subtitleSizes} font-medium ${isDark ? 'text-slate-300' : 'text-slate-600'} max-w-xs leading-snug`}>
              Watershed Monitoring &amp; Geospatial Decision Support System
            </p>
          )}
        </div>
      </div>
    );
  }

  // Default: Horizontal Lockup
  return (
    <div className={`inline-flex items-center space-x-3 ${className}`}>
      {Monogram}
      <div className="flex flex-col justify-center text-left">
        <div className={`${titleSizes} font-black tracking-tight leading-tight flex items-center space-x-1`}>
          <span className={isDark ? 'text-white' : 'text-slate-900'}>Jal</span>
          <span className="text-sky-600">Drishti</span>
        </div>
        {/* Tricolor-inspired accent bar */}
        <div className="flex items-center space-x-1 my-0.5">
          <span className="h-[2px] w-5 bg-orange-600 rounded-full" />
          <span className="h-[2px] w-3 bg-sky-500 rounded-full" />
          <span className="h-[2px] w-5 bg-emerald-600 rounded-full" />
        </div>
        {showTagline && (
          <p className={`${subtitleSizes} font-medium ${isDark ? 'text-slate-300' : 'text-slate-600'} leading-none tracking-tight whitespace-nowrap`}>
            Watershed Monitoring &amp; Geospatial Decision Support System
          </p>
        )}
      </div>
    </div>
  );
}
