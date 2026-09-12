/** @type {import('next').NextConfig} */
function resolveBackendUrl() {
  const defaultBackend = process.env.NODE_ENV === 'production' 
    ? 'https://jaldrishti-api-3a8q.onrender.com' 
    : 'http://127.0.0.1:8000';
  let raw = process.env.INTERNAL_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || defaultBackend;
  raw = raw.trim().replace(/\/api\/v1\/?$/, '').replace(/\/+$/, '');

  // 1. If explicit protocol is already provided
  if (raw.startsWith('http://') || raw.startsWith('https://')) {
    return raw;
  }

  // 2. Local development without protocol
  if (raw.startsWith('localhost') || raw.startsWith('127.0.0.1')) {
    return `http://${raw}`;
  }

  // 3. Render service slug without dots (e.g. 'jaldrishti-api-3a8q')
  if (!raw.includes('.')) {
    return `https://${raw}.onrender.com`;
  }

  // 4. Domain with dots (e.g. 'jaldrishti-api-3a8q.onrender.com')
  return `https://${raw}`;
}

const nextConfig = {
  async rewrites() {
    const destination = resolveBackendUrl();
    return [
      {
        source: '/api/v1/:path*',
        destination: `${destination}/api/v1/:path*`,
      },
      {
        source: '/uploads/:path*',
        destination: `${destination}/uploads/:path*`,
      },
    ];
  },
};

export default nextConfig;
