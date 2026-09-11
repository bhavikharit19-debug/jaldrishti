/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    let raw = process.env.INTERNAL_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
    // Clean up any trailing /api/v1 or /
    raw = raw.replace(/\/api\/v1\/?$/, '').replace(/\/+$/, '');
    if (!raw.startsWith('http://') && !raw.startsWith('https://')) {
      raw = `https://${raw}`;
    }
    return [
      {
        source: '/api/v1/:path*',
        destination: `${raw}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
