import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  turbopack: {
    root: '.',
  },
  async rewrites() {
    return [
      {
        source: '/api/openclaw/:path*',
        destination: 'http://localhost:8100/api/:path*',
      },
    ];
  },
};

export default nextConfig;
