/** @type {import('next').NextConfig} */
function resolveBackendUrl() {
  let raw = process.env.INTERNAL_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
  raw = raw.trim().replace(/\/api\/v1\/?$/, '').replace(/\/+$/, '');

  // 1. If explicit protocol is already provided
  if (raw.startsWith('http://') || raw.startsWith('https://')) {
    return raw;
  }

  // 2. If it is an internal service name without dots (e.g. Render fromService 'jaldrishti-api')
  if (!raw.includes('.')) {
    const port = process.env.BACKEND_PORT || (raw.includes(':') ? '' : ':10000');
    const hostWithPort = raw.includes(':') ? raw : `${raw}${port}`;
    return `http://${hostWithPort}`;
  }

  // 3. If it's a public domain with dots (e.g. 'jaldrishti-api.onrender.com')
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
