import type { Metadata } from 'next';
import './globals.css';
import { AuthProvider } from '@/context/AuthContext';

export const metadata: Metadata = {
  title: 'JalDrishti — Watershed Monitoring & Geospatial Decision Support System',
  description: 'National watershed monitoring, biophysical indicator tracking, change detection, and intervention decision support platform (SIH 26015).',
  icons: {
    icon: '/jaldrishti-icon.svg',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-100/70 antialiased font-sans text-slate-900">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
